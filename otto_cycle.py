from engine import Engine
from sound_module import EngineSound
import math

class OttoCycle(Engine):
    def __init__(self, crank_radius, rod_length, piston_width, piston_height, crank_center_x, crank_center_y):
        super().__init__(crank_radius, rod_length, piston_width, piston_height, crank_center_x, crank_center_y)
        self.pressure = 1.0
        self.combustion_pressure = 5.0
        self.sound = EngineSound()

    def update_pressure(self):
        if 0 < self.theta < math.pi / 2:  # Intake phase
            self.pressure += 0.01
        elif math.pi / 2 < self.theta < math.pi:  # Compression phase
            self.pressure += 0.02
        elif math.pi < self.theta < 3 * math.pi / 2:  # Ignition phase
            self.pressure -= 0.02
        elif 3 * math.pi / 2 < self.theta < 2 * math.pi:  # Exhaust phase
            self.pressure -= 0.01

        self.pressure = max(1.0, min(self.combustion_pressure, self.pressure))

    def update_sound(self):
        if 0 < self.theta < math.pi / 2:  # Intake phase
            self.sound.play_cycle('intake')
        elif math.pi / 2 < self.theta < math.pi:  # Compression phase
            self.sound.play_cycle('compression')
        elif math.pi < self.theta < 3 * math.pi / 2:  # Ignition phase
            self.sound.play_cycle('ignition')
        elif 3 * math.pi / 2 < self.theta < 2 * math.pi:  # Exhaust phase
            self.sound.play_cycle('exhaust')
