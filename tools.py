# coding=utf-8

import numpy as np
import random
import matplotlib.pyplot as plt


def gaussian(x, m, sd):
    return np.exp(-np.power(x - m, 2.) / (2 * np.power(sd, 2.)))


def cents2ratio(x):
    return np.power(2, x/1200)


class Grain:

    def __init__(self, fs):
        self.fs = fs
        self.last_grain_idx = 0.0
        self.period = 0.0

        length_ms = 10
        sd = 0.002
        # sine_freq = 1000

        len_samples = length_ms / 1000 * self.fs
        samples = np.arange(start=0, stop=len_samples)

        # sine = np.sin(2 * np.pi * sine_freq / self.fs * samples)
        noise = np.random.normal(0, 1, int(len_samples))

        self.grain = noise * gaussian(samples, len_samples/2, sd*self.fs)

    def start(self):
        self.last_grain_idx = 0.0
        self.period = 0.0

    def update(self, freq, mistuning_module=None):
        self.last_grain_idx += self.period
        self.period = self.fs / freq
        if mistuning_module is not None:
            self.period *= cents2ratio(random.uniform(-mistuning_module.act_mistuning,
                                                      mistuning_module.act_mistuning))

    def fill_bufor(self, bufor, sample_nr, freq,
                   appearing_module=None, mistuning_module=None, volume_module=None):
        while int(self.last_grain_idx + self.period) + len(self.grain) < int(sample_nr + len(bufor)):
            if appearing_module is None or random.uniform(0, 1) < appearing_module.appearing_prob:
                bufor[int(self.last_grain_idx - sample_nr + self.period):
                      int(self.last_grain_idx - sample_nr + self.period) + len(self.grain)]\
                    += volume_module.volume * self.grain
            self.update(freq, mistuning_module)


class MistuningModule:

    def __init__(self, fs):
        self.fs = fs

        self.start_mistuning = 1200  # cents
        self.end_mistuning = 1  # cents
        self.tuning_speed = 3

        self.act_mistuning = self.start_mistuning

    def start(self):
        self.act_mistuning = self.start_mistuning

    def update(self, sample_nr):
        if self.act_mistuning > self.end_mistuning:
            self.act_mistuning = self.start_mistuning*np.power(0.01, sample_nr/self.fs*self.tuning_speed)


class AppearingModule:

    def __init__(self, fs):
        self.fs = fs

        self.appearing_speed = 100
        self.appearing_prob = 1

    def update(self, sample_nr):
        self.appearing_prob = 1 - np.power(0.01, sample_nr / self.fs * self.appearing_speed)


class VolumeModule:

    def __init__(self, fs):
        self.fs = fs

        self.decay_speed = 1
        self.volume = 1.0

    def update(self, sample_nr):
        self.volume = 0.5 + 0.5*np.power(0.01, sample_nr / self.fs * self.decay_speed)


