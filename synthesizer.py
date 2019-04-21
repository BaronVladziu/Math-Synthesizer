# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt


def gaussian(x, m, sd):
    return np.exp(-np.power(x - m, 2.) / (2 * np.power(sd, 2.)))


def cents2ratio(x):
    return np.power(2, x/1200)


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
        self.last_grain1_idx = 0.0
        self.last_grain2_idx = 0.0
        self.last_grain3_idx = 0.0
        self.buf_size = 4410
        self.bufor = np.zeros(self.buf_size)
        self.mistuning = 2  # cents

        # grain
        self.grain2_period = self.fs / self.freq
        self.grain1_period = self.grain2_period / cents2ratio(self.mistuning)
        self.grain3_period = self.grain2_period * cents2ratio(self.mistuning)
        grain_length_ms = 50
        grain_sd = 0.005
        # sine_freq = self.freq

        grain_len_samples = grain_length_ms / 1000 * self.fs
        samples = np.arange(start=0, stop=grain_len_samples)
        # sine = np.sin(2 * np.pi * sine_freq / self.fs * samples)
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
        self.last_grain1_idx = 0.0
        self.last_grain2_idx = 0.0
        self.last_grain3_idx = 0.0
        self.fill_bufor()

    def stop(self):
        self.is_active = False
        window = np.linspace(start=1, stop=0, num=self.buf_size)
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
        # print(self.last_grain1_idx, self.grain1_period, len(self.grain), self.sample_nr, self.buf_size)
        # print(self.last_grain2_idx, self.grain2_period, len(self.grain), self.sample_nr, self.buf_size)
        while int(self.last_grain1_idx + self.grain1_period) + len(self.grain) < int(self.sample_nr + self.buf_size):
            self.bufor[int(self.last_grain1_idx - self.sample_nr + self.grain1_period):int(self.last_grain1_idx - self.sample_nr + self.grain1_period) + len(self.grain)] += self.grain
            self.last_grain1_idx += self.grain1_period
        while int(self.last_grain2_idx + self.grain2_period) + len(self.grain) < int(self.sample_nr + self.buf_size):
            self.bufor[int(self.last_grain2_idx - self.sample_nr + self.grain2_period):int(self.last_grain2_idx - self.sample_nr + self.grain2_period) + len(self.grain)] += self.grain
            self.last_grain2_idx += self.grain2_period
        while int(self.last_grain3_idx + self.grain3_period) + len(self.grain) < int(self.sample_nr + self.buf_size):
            self.bufor[int(self.last_grain3_idx - self.sample_nr + self.grain3_period):int(self.last_grain3_idx - self.sample_nr + self.grain3_period) + len(self.grain)] += self.grain
            self.last_grain3_idx += self.grain3_period

