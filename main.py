# coding=utf-8

import rtmidi
import queue
import sys
import numpy as np
from synthesizer import Synthesizer
import sounddevice as sd


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


def callback(outdata, frames, time, status):
    if status.output_underflow:
        print('Output underflow: increase blocksize?', file=sys.stderr)
        raise sd.CallbackAbort
    assert not status
    try:
        data = q.get_nowait()
    except queue.Empty:
        print('Buffer is empty: increase buffersize?', file=sys.stderr)
        raise sd.CallbackAbort
    if len(data) < len(outdata):
        outdata[:len(data)] = data
        outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
        raise sd.CallbackStop
    else:
        outdata[:] = data


ports = range(midiin.getPortCount())
if ports:
    for i in ports:
        print("Port", i, ':', midiin.getPortName(i))
    midiin.openPort(1)

    volume = 0.1  # range [0.0, 1.0]
    fs = 44100  # sampling rate, Hz, must be integer
    chunk = 128  # in samples

    synthesizers = list()
    is_note_on = list()
    for i in range(128):
        synthesizers.append(Synthesizer(midi2freq(i), fs))
        is_note_on.append(False)

    stream = sd.OutputStream(fs, chunk, channels=1)

    with stream:
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
            for note_nr, syn in enumerate(synthesizers):
                if is_note_on[note_nr]:
                    samples += syn.get_chunk(chunk).astype(np.float32)

            stream.write(volume * samples)

else:
    print('NO MIDI INPUT PORTS!')
