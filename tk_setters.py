# coding=utf-8


class TkSetters:

    def __init__(self, sythesizers):
        self.sythesizers = sythesizers
        self.volume = 0.003
        self.voices = 3
        self.grain_len = 10
        self.grain_sd = 0.001
        self.sine_freq = 0
        self.sustain = 20
        self.volume_decay_speed = 10
        self.spread_speed = 3
        self.spread_direction = 1
        self.detuning_start = 1200
        self.detuning_end = 1
        self.detuning_speed = 300

    def set_volume(self, val):
        self.volume = int(val)/10000

    def set_voices(self, val):
        self.voices = int(val)
        for syn in self.sythesizers:
            syn.grain_nr = self.voices
            syn.reload_grains()

    def set_grain_len(self, val):
        self.grain_len = int(val)
        for syn in self.sythesizers:
            syn.grain_len = self.grain_len
            syn.reload_grains()

    def set_grain_sd(self, val):
        self.grain_sd = int(val)
        for syn in self.sythesizers:
            syn.grain_sd = self.grain_sd
            syn.reload_grains()

    def set_sine_freq(self, val):
        self.sine_freq = int(val)
        for syn in self.sythesizers:
            syn.sine_freq = self.sine_freq
            syn.reload_grains()

    def set_sustain(self, val):
        self.sustain = int(val)
        for syn in self.sythesizers:
            syn.volume_module.sustain = self.sustain/100

    def set_volume_decay_speed(self, val):
        self.volume_decay_speed = int(val)
        for syn in self.sythesizers:
            syn.volume_module.decay_speed = self.volume_decay_speed/10

    def set_spread_speed(self, val):
        self.spread_speed = int(val)
        for syn in self.sythesizers:
            syn.appearing_module.appearing_speed = self.spread_speed/30

    def set_spread_direction_dispersing(self):
        self.spread_direction = 1
        for syn in self.sythesizers:
            syn.appearing_module.direction = self.spread_direction

    def set_spread_direction_collecting(self):
        self.spread_direction = -1
        for syn in self.sythesizers:
            syn.appearing_module.direction = self.spread_direction

    def set_detuning_start(self, val):
        self.detuning_start = int(val)
        for syn in self.sythesizers:
            syn.detuning_module.detuning_start = self.detuning_start

    def set_detuning_end(self, val):
        self.detuning_end = int(val)
        for syn in self.sythesizers:
            syn.detuning_module.detuning_end = self.detuning_end

    def set_detuning_speed(self, val):
        self.detuning_speed = int(val)
        for syn in self.sythesizers:
            syn.detuning_module.detuning_speed = self.detuning_speed



