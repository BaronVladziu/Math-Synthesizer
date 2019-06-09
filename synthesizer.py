# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
from scipy import signal
import random
from tools import *


class Synthesizer:

    def __init__(self, freq, fs):
        self.freq = freq
        self.fs = fs
        self.sample_nr = 0
        self.is_active = False

    def start(self):
        self.sample_nr = 0
        self.is_active = True

    def stop(self):
        self.is_active = False

    def get_chunk(self, chunk_size):
        if self.is_active:
            samples = np.arange(start=self.sample_nr, stop=self.sample_nr + chunk_size)
            self.sample_nr += chunk_size
            return np.sin(2*np.pi*self.freq/self.fs*samples)
        else:
            return np.zeros(chunk_size)


class GranularSynthesizer:

    def __init__(self, freq, fs, tk_setters):
        self.freq = freq
        self.fs = fs
        self.sample_nr = 0
        self.is_active = False
        self.bufor = np.zeros(2205)

        self.grain_nr = tk_setters.voices
        self.grain_len = tk_setters.grain_len
        self.grain_sd = 0.001
        self.grains = None
        self.reload_grains()

        self.mistuning_module = MistuningModule(self.fs, tk_setters)
        self.appearing_module = AppearingModule(self.fs, tk_setters)
        self.volume_module = VolumeModule(self.fs, tk_setters)

        # # plot
        # if self.freq == 110:
        #     self.bufor = np.zeros(len(self.bufor))
        #     self.fill_bufor()
        #     plt.plot(self.grains[0].grain)
        #     plt.show()
        #     plt.plot(self.bufor)
        #     plt.show()

    def reload_grains(self):
        self.grains = list()
        for i in range(self.grain_nr):
            self.grains.append(Grain(self.fs, self.grain_len, self.grain_sd))

    def start(self):
        self.sample_nr = 0
        self.is_active = True
        for grain in self.grains:
            grain.start()

        self.mistuning_module.start()

        self.fill_bufor()

    def stop(self):
        self.is_active = False
        window = np.linspace(start=1, stop=0, num=len(self.bufor))
        self.bufor *= window

    def get_chunk(self, chunk_size):
        result = self.bufor[:chunk_size]
        self.bufor = np.concatenate([self.bufor[chunk_size:], np.zeros(chunk_size)])
        if self.is_active:
            self.sample_nr += chunk_size
            self.fill_bufor()
        elif len(result) < chunk_size:
            result = np.concatenate([result, np.zeros(chunk_size - len(result))])
        return result

    def fill_bufor(self):
        self.mistuning_module.update(self.sample_nr)
        self.appearing_module.update(self.sample_nr)
        self.volume_module.update(self.sample_nr)

        for grain in self.grains:
            grain.fill_bufor(self.bufor, self.sample_nr, self.freq,
                             self.appearing_module, self.mistuning_module, self.volume_module)
