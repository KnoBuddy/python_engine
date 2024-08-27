import random
import math
import pygame

from concurrent.futures import ThreadPoolExecutor

class Particle:
    def __init__(self, x, y, z, container_rect, temperature, pressure_ratio=1.0, angle_offset=0):
        self.x = x
        self.y = y
        self.z = z
        self.container_rect = container_rect
        self.temperature = temperature
        self.angle_offset = angle_offset
        self.pressure_ratio = pressure_ratio
        self.alpha = 255  # Start fully opaque
        self.exiting = False  # Track if the particle is exiting the container
        self.set_velocity()

    def set_velocity(self):
        # Speed is proportional to the square root of the temperature and pressure ratio
        speed = math.sqrt(self.temperature / 100.0) * self.pressure_ratio
        angle_xy = random.uniform(-math.pi / 6, math.pi / 6) + self.angle_offset  # Adjust the angle for V shape
        angle_z = random.uniform(-math.pi / 8, math.pi / 8)  # Limit the z angle to keep it within the container
        self.vx = speed * math.cos(angle_xy)
        self.vy = speed * math.sin(angle_xy)
        self.vz = speed * math.sin(angle_z)
        
    def update_velocity(self, new_temperature):
        # Update speed based on new temperature without changing direction
        self.temperature = new_temperature
        speed = math.sqrt(self.temperature / 100.0) * self.pressure_ratio
        direction_xy = math.atan2(self.vy, self.vx)
        direction_z = math.atan2(self.vz, math.sqrt(self.vx**2 + self.vy**2))
        self.vx = speed * math.cos(direction_xy)
        self.vy = speed * math.sin(direction_xy)
        self.vz = speed * math.sin(direction_z)

    def move(self):
        if not self.exiting:
            self.x += self.vx
            self.y += self.vy
            self.z += self.vz

            # Bounce off the container walls (2D projection for the UI, but modeled in 3D)
            if self.x <= self.container_rect.left:
                self.vx = abs(self.vx)  # Ensure the velocity is directed inward
                self.x = self.container_rect.left
            elif self.x >= self.container_rect.right:
                self.vx = -abs(self.vx)  # Ensure the velocity is directed inward
                self.x = self.container_rect.right

            if self.y <= self.container_rect.top:
                self.vy = abs(self.vy)
                self.y = self.container_rect.top
            elif self.y >= self.container_rect.bottom:
                self.vy = -abs(self.vy)
                self.y = self.container_rect.bottom

            container_depth = self.container_rect.width  # Assuming the container is cubic in shape
            if self.z <= -container_depth / 2:
                self.vz = abs(self.vz)
                self.z = -container_depth / 2
            elif self.z >= container_depth / 2:
                self.vz = -abs(self.vz)
                self.z = container_depth / 2

    def move_outward(self):
        if self.exiting:
            # Move towards the right and slightly spread out (V-shape)
            self.x += self.vx * 2  # Move faster when exiting the container
            self.y += self.vy * 2
            if self.x >= self.container_rect.right + 10:  # Fade out only after fully exiting
                self.alpha = max(self.alpha - 5, 0)

    def collide_with(self, other):
        # Simple elastic collision model
        dx = self.x - other.x
        dy = self.y - other.y
        dz = self.z - other.z
        distance = math.sqrt(dx**2 + dy**2 + dz**2)
        if distance == 0:
            return

        # Normal vector
        nx = dx / distance
        ny = dy / distance
        nz = dz / distance

        # Relative velocity
        dvx = self.vx - other.vx
        dvy = self.vy - other.vy
        dvz = self.vz - other.vz

        # Dot product of relative velocity and normal vector
        dot = dvx * nx + dvy * ny + dvz * nz

        # Elastic collision response
        self.vx -= dot * nx
        self.vy -= dot * ny
        self.vz -= dot * nz
        other.vx += dot * nx
        other.vy += dot * ny
        other.vz += dot * nz

    def draw(self, screen):
        if self.alpha > 0:
            # Create a surface for the particle to apply transparency
            particle_surface = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, (0, 0, 255, self.alpha), (2, 2), 2)
            screen.blit(particle_surface, (int(self.x), int(self.y)))


class UIDiagnostics:
    def __init__(self, gas_sim, clock):
        self.gas_sim = gas_sim
        self.font = pygame.font.SysFont(None, 36)
        self.fps_font = pygame.font.SysFont(None, 24)
        self.clock = clock

        self.container_rect = pygame.Rect(295, 195, 210, 210)
        self.inner_rect = pygame.Rect(300, 200, 200, 200)

        self.particles = self.create_particles()

        self.valve_left_rect = pygame.Rect(self.inner_rect.left - 10, self.inner_rect.centery - 15, 10, 30)
        self.valve_right_rect = pygame.Rect(self.inner_rect.right, self.inner_rect.centery - 15, 10, 30)
        self.valve_open = False
        self.valve_right_open = False
        self.particles_moving_outward = []

        self.buttons = {
            'increase_volume': pygame.Rect(600, 100, 150, 40),
            'decrease_volume': pygame.Rect(600, 150, 150, 40),
            'increase_temp': pygame.Rect(600, 200, 150, 40),
            'decrease_temp': pygame.Rect(600, 250, 150, 40),
            'add_gas': pygame.Rect(600, 300, 150, 40),
            'release_gas': pygame.Rect(600, 350, 150, 40)
        }

    def create_particles(self, count=None, near_valve=False, pressure_ratio=1.0):
        if count is None:
            # Calculate the number of particles based on a fraction of Avogadro's number
            moles = self.gas_sim.mass / 0.032  # Molar mass of O2 is 32g/mol
            avogadro_number = 6.022e23
            count = int(moles * avogadro_number * 1e-23)  # Use the 1e-23 scaling factor

        if near_valve:
            return [Particle(self.valve_left_rect.right, 
                             self.valve_left_rect.centery,
                             random.uniform(-self.inner_rect.width / 2, self.inner_rect.width / 2),
                             self.inner_rect, self.gas_sim.temperature, 
                             angle_offset=random.uniform(-0.2, 0.2), 
                             pressure_ratio=pressure_ratio) for _ in range(count)]
        else:
            return [Particle(random.uniform(self.inner_rect.left, self.inner_rect.right),
                             random.uniform(self.inner_rect.top, self.inner_rect.bottom),
                             random.uniform(-self.inner_rect.width / 2, self.inner_rect.width / 2),
                             self.inner_rect, self.gas_sim.temperature) for _ in range(count)]

    def add_gas_via_valve(self, mass):
        self.valve_open = True
        pressure_ratio = 2.0
        moles = mass / 0.032  # Molar mass of O2 is 32g/mol
        avogadro_number = 6.022e23
        count = int(moles * avogadro_number * 1e-23)  # Calculate the number of particles based on the mass

        new_particles = self.create_particles(count=count, near_valve=True, pressure_ratio=pressure_ratio)
        self.particles.extend(new_particles)

        self.gas_sim.add_gas(mass)
        self.valve_open = False

    def release_gas_via_valve(self, mass):
        self.valve_right_open = True

        moles = mass / 0.032  # Molar mass of O2 is 32g/mol
        avogadro_number = 6.022e23
        num_particles_to_remove = int(moles * avogadro_number * 1e-23)  # Calculate the correct number of particles to remove

        particles_with_distance = []
        for particle in self.particles:
            distance = math.sqrt((particle.x - self.valve_right_rect.left) ** 2 + (particle.y - self.valve_right_rect.centery) ** 2)
            particles_with_distance.append((particle, distance))

        particles_with_distance.sort(key=lambda p: p[1])

        particles_to_release = [p[0] for p in particles_with_distance[:num_particles_to_remove]]

        for particle in particles_to_release:
            self.particles.remove(particle)
            particle.exiting = True
            direction = math.atan2(self.valve_right_rect.centery - particle.y, self.valve_right_rect.left - particle.x)
            particle.vx = 2.0 * math.cos(direction)
            particle.vy = 2.0 * math.sin(direction)
            self.particles_moving_outward.append(particle)

        self.gas_sim.release_gas(mass)
        self.valve_right_open = False

    def update(self):
        # Update container size based on volume
        scale = self.gas_sim.volume / 10.0
        self.inner_rect.width = int(200 * scale)
        self.inner_rect.height = int(200 * scale)
        self.container_rect.width = self.inner_rect.width + 10
        self.container_rect.height = self.inner_rect.height + 10

        # Divide particles into smaller groups for multithreading
        num_threads = 16  # Number of threads to use
        chunk_size = len(self.particles) // num_threads
        particle_chunks = [self.particles[i:i + chunk_size] for i in range(0, len(self.particles), chunk_size)]

        def update_chunk(particles):
            for i, particle in enumerate(particles):
                for j in range(i + 1, len(particles)):
                    particle.collide_with(particles[j])
                particle.move()

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            executor.map(update_chunk, particle_chunks)

        # Update particles moving outward
        for particle in self.particles_moving_outward:
            particle.move_outward()

        # Remove particles that are fully faded out
        self.particles_moving_outward = [p for p in self.particles_moving_outward if p.alpha > 0]

    def draw(self, screen):
        # Draw temperature, pressure, volume diagnostics in white
        temperature_text = self.font.render(f"Temperature: {self.gas_sim.temperature} K", True, (255, 255, 255))
        pressure_text = self.font.render(f"Pressure: {self.gas_sim.pressure:.2f} Pa", True, (255, 255, 255))
        volume_text = self.font.render(f"Volume: {self.gas_sim.volume} m^3", True, (255, 255, 255))
        mass_text = self.font.render(f"Mass: {self.gas_sim.mass} kg", True, (255, 255, 255))
        fps_text = self.fps_font.render(f"FPS: {int(self.clock.get_fps())}", True, (255, 255, 255))  # FPS text

        screen.blit(temperature_text, (20, 20))
        screen.blit(pressure_text, (20, 60))
        screen.blit(volume_text, (20, 100))
        screen.blit(mass_text, (20, 140))
        screen.blit(fps_text, (20, 180))  # Draw FPS on screen

        # Draw the gas container outline (slightly larger)
        pygame.draw.rect(screen, (255, 255, 255), self.container_rect, 2)

        # Draw the particles inside the container
        for particle in self.particles:
            particle.draw(screen)

        # Draw the particles moving outward
        for particle in self.particles_moving_outward:
            particle.draw(screen)

        # Draw the left valve on the left side
        valve_color = (0, 255, 0) if self.valve_open else (255, 0, 0)
        pygame.draw.rect(screen, valve_color, self.valve_left_rect)

        # Draw the right valve on the right side
        valve_right_color = (0, 255, 0) if self.valve_right_open else (255, 0, 0)
        pygame.draw.rect(screen, valve_right_color, self.valve_right_rect)

        # Draw buttons
        for key, rect in self.buttons.items():
            pygame.draw.rect(screen, (0, 255, 0), rect)
            button_text = key.replace('_', ' ').title()
            screen.blit(self.font.render(button_text, True, (0, 0, 0)), (rect.x + 10, rect.y + 5))

    def update_particles(self):
        # Recreate particles if the mass or temperature changes significantly
        self.particles = self.create_particles()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            for key, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    if key == 'increase_volume':
                        self.gas_sim.change_volume(1.0)
                    elif key == 'decrease_volume':
                        self.gas_sim.change_volume(-1.0)
                    elif key == 'increase_temp':
                        self.gas_sim.change_temperature(10)
                        self.update_particles()  # Update particle speeds when temperature changes
                    elif key == 'decrease_temp':
                        self.gas_sim.change_temperature(-10)
                        self.update_particles()  # Update particle speeds when temperature changes
                    elif key == 'add_gas':
                        self.add_gas_via_valve(0.1)  # Add gas via valve
                    elif key == 'release_gas':
                        self.release_gas_via_valve(0.1)  # Release gas via right valve
