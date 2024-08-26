from engine import Engine
import math

class OttoCycle(Engine):
    def __init__(self, crank_radius, rod_length, piston_width, piston_height, crank_center_x, crank_center_y):
        super().__init__(crank_radius, rod_length, piston_width, piston_height, crank_center_x, crank_center_y)
        self.pressure = 1.0
        self.combustion_pressure = 5.0

    def update_pressure(self):
        if 0 < self.theta < math.pi:  # Compression phase
            self.pressure += 0.02
        elif math.pi < self.theta < 2 * math.pi:  # Expansion phase
            self.pressure -= 0.02
        self.pressure = max(1.0, min(self.combustion_pressure, self.pressure))