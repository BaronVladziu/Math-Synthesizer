# coding=utf-8

import rtmidi
import numpy as np
from synthesizer import Synthesizer, GranularSynthesizer
import sounddevice as sd
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav


midiin = rtmidi.RtMidiIn()


def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getNoteNumber(), midi2freq(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('OFF:', midi.getNoteNumber(), midi2freq(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isController():
        print('CONTROLLER', midi.getControllerNumber(), midi.getControllerValue())


def midi2freq(midi_nr):
    ref_freq = 440.0
    ref_midi = 69
    return np.power(2, (midi_nr - ref_midi)/12)*ref_freq


ports = range(midiin.getPortCount())
if ports:
    for i in ports:
        print("Port", i, ':', midiin.getPortName(i))
    midiin.openPort(1)

    volume = 0.002  # range [0.0, 1.0]
    fs = 44100  # sampling rate, Hz, must be integer
    chunk = 128  # in samples

    synthesizers = list()
    for i in range(97):
        synthesizers.append(GranularSynthesizer(midi2freq(i), fs))

    stream = sd.OutputStream(fs, chunk, channels=1)

    with stream:
        # nr_synthesized_chunks = 0
        # buf_size_in_chunks = 10000
        # bufor = np.zeros(buf_size_in_chunks * chunk)
        while True:
            m = midiin.getMessage(1)  # some timeout in ms
            if m:
                print_message(m)
                if m.isNoteOn():
                    synthesizers[m.getNoteNumber()].start()
                else:
                    synthesizers[m.getNoteNumber()].stop()

            # generate samples, note conversion to float32 array
            samples = np.zeros(chunk).astype(np.float32)
            for note_nr, syn in enumerate(synthesizers):
                # if note_nr == 96:
                samples += syn.get_chunk(chunk).astype(np.float32)
            # for value in samples:
            #     print("{0:.5f}".format(volume * value))

            stream.write(volume * samples)
            # bufor[nr_synthesized_chunks * chunk : (nr_synthesized_chunks+1) * chunk] = volume * samples
            # nr_synthesized_chunks += 1
            #
            # # printing
            # if nr_synthesized_chunks == buf_size_in_chunks:
            #     nr_synthesized_chunks = 0
            #     wav.write('bufor.wav', fs, bufor)
            #     plt.plot(bufor)
            #     plt.show()


else:
    print('NO MIDI INPUT PORTS!')
