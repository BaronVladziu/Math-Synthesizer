# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt


def gaussian(x, m, sd):
    return np.exp(-np.power(x - m, 2.) / (2 * np.power(sd, 2.)))


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

    def __init__(self, freq, fs):
        self.freq = freq
        self.fs = fs
        self.sample_nr = 0
        self.is_active = False
        self.last_grain_idx = 0.0
        self.buf_size = 4410
        self.bufor = np.zeros(self.buf_size)

        # grain
        self.grain_period = self.fs / self.freq
        grain_length_ms = 50
        grain_sd = 0.001
        sine_freq = self.freq

        grain_len_samples = grain_length_ms / 1000 * self.fs
        samples = np.arange(start=0, stop=grain_len_samples)
        sine = np.sin(2 * np.pi * sine_freq / self.fs * samples)
        noise = np.random.normal(0, 1, int(grain_len_samples))
        self.grain = noise * gaussian(samples, grain_len_samples/2, grain_sd*self.fs)

        # # plot
        # if self.freq == 440:
        #     self.bufor = np.zeros(self.buf_size)
        #     self.fill_bufor()
        #     plt.plot(self.grain)
        #     plt.show()
        #     plt.plot(self.bufor)
        #     plt.show()

    def start(self):
        self.sample_nr = 0
        self.is_active = True
        self.bufor = np.zeros(self.buf_size)
        self.last_grain_idx = 0.0
        self.fill_bufor()

    def stop(self):
        self.is_active = False

    def get_chunk(self, chunk_size):
        if self.is_active:
            result = self.bufor[:chunk_size]
            self.bufor = np.concatenate([self.bufor[chunk_size:], np.zeros(chunk_size)])
            self.sample_nr += chunk_size
            self.fill_bufor()
            return result
        else:
            return np.zeros(chunk_size)

    def fill_bufor(self):
        # print(self.last_grain_idx, self.grain_period, len(self.grain), self.sample_nr, self.buf_size)
        while int(self.last_grain_idx + self.grain_period) + len(self.grain) < int(self.sample_nr + self.buf_size):
            self.bufor[int(self.last_grain_idx - self.sample_nr + self.grain_period):int(self.last_grain_idx - self.sample_nr + self.grain_period) + len(self.grain)] += self.grain
            self.last_grain_idx += self.grain_period

