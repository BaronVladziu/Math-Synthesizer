# coding=utf-8

import numpy as np
import pyaudio


class Synthesizer:

    def __init__(self, freq, fs):
        self.freq = freq
        self.fs = fs
        self.sample_nr = 0

    def get_sample(self):
        self.sample_nr += 1
        return np.sin(2*np.pi*self.freq/self.fs*(self.sample_nr - 1))





if __name__ == '__main__':
    p = pyaudio.PyAudio()

    volume = 0.5     # range [0.0, 1.0]
    fs = 44100       # sampling rate, Hz, must be integer
    chunk = fs       # in samples
    f = 440.0        # sine frequency, Hz, may be float


    syn440 = Synthesizer(f, fs)

    # for paFloat32 sample values must be in range [-1.0, 1.0]
    stream = p.open(format=pyaudio.paFloat32,
                    frames_per_buffer=chunk,
                    channels=1,
                    rate=fs,
                    output=True)

    while True:
        # generate samples, note conversion to float32 array
        samples = np.zeros(chunk).astype(np.float32)
        for i in range(chunk):
            samples[i] = syn440.get_sample().astype(np.float32)
        print(len(samples))

        # play. May repeat with different volume values (if done interactively)
        stream.write(volume*samples)

        if not stream.is_active():
            stream.stop_stream()
            stream.close()
            p.terminate()
