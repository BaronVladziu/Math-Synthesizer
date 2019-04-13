# coding=utf-8

import numpy as np


class Synthesizer:

    def __init__(self, freq, fs):
        self.freq = freq
        self.fs = fs
        self.sample_nr = 0

    def get_chunk(self, chunk_size):
        samples = np.arange(start=self.sample_nr, stop=self.sample_nr + chunk_size)
        self.sample_nr += chunk_size
        return np.sin(2*np.pi*self.freq/self.fs*samples)
