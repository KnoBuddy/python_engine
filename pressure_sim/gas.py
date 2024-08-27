class GasSimulation:
    def __init__(self, initial_volume, initial_temperature, initial_mass, R=8.314):
        self.volume = initial_volume
        self.temperature = initial_temperature
        self.mass = initial_mass
        self.R = R
        self.pressure = self.calculate_pressure()

    def calculate_pressure(self):
        # Calculate pressure using the ideal gas law: PV = nRT => P = (nRT)/V
        moles = self.mass / 0.02897  # Molar mass of air in kg/mol
        pressure = (moles * self.R * self.temperature) / self.volume
        return pressure

    def update(self):
        # Update pressure based on current volume, temperature, and mass
        self.pressure = self.calculate_pressure()

    def change_volume(self, delta_volume):
        self.volume += delta_volume
        self.update()

    def change_temperature(self, delta_temperature):
        self.temperature += delta_temperature
        self.update()
        for particle in self.ui.particles:  # Access the particles through the UI
            particle.update_velocity(self.temperature)

    def add_gas(self, mass):
        self.mass += mass
        self.update()

    def release_gas(self, mass):
        self.mass = max(self.mass - mass, 0)
        self.update()
