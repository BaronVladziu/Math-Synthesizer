# coding=utf-8

import rtmidi
import numpy as np
from synthesizer import Synthesizer, GranularSynthesizer
import sounddevice as sd
import matplotlib.pyplot as plt
import scipy.io.wavfile as wav
from tkinter import *
from tk_setters import *


midiin = rtmidi.RtMidiIn()

def print_value(val):
    print(val)

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
    tk_setters = TkSetters(synthesizers)
    for i in range(97):
        synthesizers.append(GranularSynthesizer(midi2freq(i), fs, tk_setters))

    stream = sd.OutputStream(fs, chunk, channels=1)

    tk = Tk()
    frm = Frame(tk, bd=16, relief='sunken')
    frm.grid()

    w = Scale(tk, from_=1, to=5, label='Voices', orient=HORIZONTAL, command=tk_setters.set_voices,
              length=600, tickinterval=1)
    w.set(tk_setters.voices)
    w.grid(row=0, column=0, columnspan=4)

    w = Scale(tk, from_=10, to=30, label='Grain length [ms]', orient=HORIZONTAL, command=tk_setters.set_grain_len,
                  length=600, tickinterval=10, resolution=10)
    w.set(tk_setters.grain_len)
    w.grid(row=1, column=0, columnspan=4)

    w = Scale(tk, from_=1, to=20, label='Grain sd', orient=HORIZONTAL, command=tk_setters.set_grain_sd,
              length=600, tickinterval=1, resolution=1)
    w.set(tk_setters.grain_sd)
    w.grid(row=2, column=0, columnspan=4)

    w = Scale(tk, from_=0, to=100, label='Sustain [%]', orient=HORIZONTAL, command=tk_setters.set_sustain,
                  length=600, tickinterval=10)
    w.set(tk_setters.sustain)
    w.grid(row=3, column=0, columnspan=4)

    w = Scale(tk, from_=0, to=300, label='Decay speed', orient=HORIZONTAL, command=tk_setters.set_volume_decay_speed,
              length=600, tickinterval=20)
    w.set(tk_setters.volume_decay_speed)
    w.grid(row=4, column=0, columnspan=4)

    w = Scale(tk, from_=0, to=300, label='Spread speed', orient=HORIZONTAL, command=tk_setters.set_spread_speed,
              length=600, tickinterval=20)
    w.set(tk_setters.spread_speed)
    w.grid(row=5, column=0, columnspan=4)

    Label(tk, text='Spread direction:').grid(row=6, column=0)
    spread_direction_var = IntVar()
    w = Radiobutton(tk, text="Dispersing", variable=spread_direction_var, value=0,
                    command=tk_setters.set_spread_direction_dispersing)
    w.select()
    w.grid(row=6, column=1)
    Radiobutton(tk, text="Backward", variable=spread_direction_var, value=1,
                command=tk_setters.set_spread_direction_collecting).grid(row=6, column=2)

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
            tk.update_idletasks()
            tk.update()

else:
    print('NO MIDI INPUT PORTS!')
