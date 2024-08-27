import pygame

class EngineSound:
    def __init__(self, sample_rate=44100):
        self.sample_rate = sample_rate
        pygame.mixer.init(frequency=self.sample_rate)
        self.channels = {
            'intake': pygame.mixer.Channel(0),
            'compression': pygame.mixer.Channel(1),
            'ignition': pygame.mixer.Channel(2),
            'exhaust': pygame.mixer.Channel(3)
        }
        self.sounds = {
            'intake': pygame.mixer.Sound('sounds/intake.wav'),
            'compression': pygame.mixer.Sound('sounds/compression.wav'),
            'ignition': pygame.mixer.Sound('sounds/ignition.wav'),
            'exhaust': pygame.mixer.Sound('sounds/exhaust.wav')
        }

    def play_cycle(self, phase):
        self.channels[phase].play(self.sounds[phase])

    def adjust_volume(self, volume):
        for phase in self.sounds:
            self.sounds[phase].set_volume(volume)