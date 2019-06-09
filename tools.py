# coding=utf-8

import numpy as np
import random
import matplotlib.pyplot as plt


def gaussian(x, m, sd):
    return np.exp(-np.power(x - m, 2.) / (2 * np.power(sd, 2.)))


def cents2ratio(x):
    return np.power(2, x/1200)


class Grain:

    def __init__(self, fs, length_ms, sd):
        self.fs = fs
        self.last_grain_idx = 0.0
        self.period = 0.0

        sine_freq = 1000

        len_samples = length_ms / 1000 * self.fs
        samples = np.arange(start=0, stop=len_samples)

        # signal = np.sin(2 * np.pi * sine_freq / self.fs * samples)
        signal = np.random.normal(0, 1, int(len_samples))

        self.grain = signal * gaussian(samples, len_samples/2, sd*self.fs)
        # self.grain = signal

    def start(self):
        self.last_grain_idx = 0.0
        self.period = 0.0

    def update(self, freq, detuning_module=None):
        self.last_grain_idx += self.period
        self.period = self.fs / freq
        if detuning_module is not None:
            self.period *= cents2ratio(random.uniform(-detuning_module.act_detuning,
                                                      detuning_module.act_detuning))

    def fill_bufor(self, bufor, sample_nr, freq,
                   appearing_module=None, mistuning_module=None, volume_module=None):
        while int(self.last_grain_idx + self.period) + len(self.grain) < int(sample_nr + len(bufor)):
            if appearing_module is None or random.uniform(0, 1) < appearing_module.appearing_prob:
                bufor[int(self.last_grain_idx - sample_nr + self.period):
                      int(self.last_grain_idx - sample_nr + self.period) + len(self.grain)]\
                    += volume_module.volume * self.grain
            self.update(freq, mistuning_module)


class DetuningModule:

    def __init__(self, fs, tk_setters):
        self.fs = fs

        self.detuning_start = tk_setters.detuning_start  # cents
        self.detuning_end = tk_setters.detuning_end  # cents
        self.detuning_speed = tk_setters.detuning_speed

        self.act_detuning = self.detuning_start

    def start(self):
        self.act_detuning = self.detuning_start

    def update(self, sample_nr):
        if self.detuning_start > self.detuning_end:
            if self.act_detuning > self.detuning_end:
                self.act_detuning = self.detuning_start*np.power(0.01, sample_nr/self.fs*self.detuning_speed)
            else:
                self.act_detuning = self.detuning_end
        else:
            if self.act_detuning < self.detuning_end:
                self.act_detuning = (self.detuning_start + self.detuning_end) * (1 - np.power(0.01, sample_nr/self.fs*self.detuning_speed))
            else:
                self.act_detuning = self.detuning_end



class AppearingModule:

    def __init__(self, fs, tk_setters):
        self.fs = fs

        self.appearing_speed = tk_setters.spread_speed/30
        self.direction = tk_setters.spread_direction

        self.appearing_prob = 1

    def update(self, sample_nr):
        if self.direction == 1:
            self.appearing_prob = np.power(0.01, sample_nr / self.fs * self.appearing_speed)
        else:
            self.appearing_prob = 1 - np.power(0.01, sample_nr / self.fs * self.appearing_speed)


class VolumeModule:

    def __init__(self, fs, tk_setters):
        self.fs = fs

        self.decay_speed = tk_setters.volume_decay_speed/10
        self.sustain = tk_setters.sustain/100

        self.volume = 1.0

    def update(self, sample_nr):
        self.volume = self.sustain + (1 - self.sustain)*np.power(0.01, sample_nr / self.fs * self.decay_speed)


