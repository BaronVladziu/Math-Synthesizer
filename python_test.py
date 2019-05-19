# coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav


# input
fs = 44100
f1 = 100
f2 = 3

# generating signals
x = np.arange(start=0, stop=3*fs)
sine1 = np.sin(2*np.pi*f1/fs*x)
sine2 = np.sin(2*np.pi*f2/fs*x)
sine3 = sine1*sine2

# printing
plt.subplot(3, 1, 1)
plt.plot(x, sine1)
plt.subplot(3, 1, 2)
plt.plot(x, sine2)
plt.subplot(3, 1, 3)
plt.plot(x, sine3)

# saving wave
wav.write('test_wav.wav', fs, sine3)
