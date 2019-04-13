# coding=utf-8

import rtmidi
import pyaudio
import numpy as np
from synthesizer import Synthesizer


midiin = rtmidi.RtMidiIn()


def print_message(midi):
    if midi.isNoteOn():
        print('ON: ', midi.getNoteNumber(), midi2freq(midi.getNoteNumber()), midi.getVelocity())
    elif midi.isNoteOff():
        print('OFF:', midi.getNoteNumber())
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

    p = pyaudio.PyAudio()

    volume = 0.1  # range [0.0, 1.0]
    fs = 44100  # sampling rate, Hz, must be integer
    chunk = 1024  # in samples
    f = 440.0  # sine frequency, Hz, may be float

    synthesizers = list()
    is_note_on = list()
    for i in range(108):
        synthesizers.append(Synthesizer(midi2freq(i), fs))
        is_note_on.append(False)

    # for paFloat32 sample values must be in range [-1.0, 1.0]
    stream = p.open(format=pyaudio.paFloat32,
                    frames_per_buffer=chunk,
                    channels=1,
                    rate=fs,
                    output=True)

    while True:
        m = midiin.getMessage(1)  # some timeout in ms
        if m:
            print_message(m)
            if m.isNoteOn():
                is_note_on[m.getNoteNumber()] = True
            else:
                is_note_on[m.getNoteNumber()] = False

        # generate samples, note conversion to float32 array
        samples = np.zeros(chunk).astype(np.float32)
        for i in range(chunk):
            for note_nr, syn in enumerate(synthesizers):
                if is_note_on[note_nr]:
                    samples[i] += syn.get_sample().astype(np.float32)

        # play. May repeat with different volume values (if done interactively)
        stream.write(volume * samples)

        if not stream.is_active():
            stream.stop_stream()
            stream.close()
            p.terminate()
else:
    print('NO MIDI INPUT PORTS!')
