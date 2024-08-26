import pygame
import math

class Engine:
    def __init__(self, crank_radius, rod_length, piston_width, piston_height, crank_center_x, crank_center_y):
        self.crank_radius = crank_radius
        self.rod_length = rod_length
        self.piston_width = piston_width
        self.piston_height = piston_height
        self.crank_center_x = crank_center_x
        self.crank_center_y = crank_center_y
        self.theta = 0
    
    def update_angle(self, angular_velocity, speed_factor):
        self.theta += angular_velocity * speed_factor / 60
        if self.theta > 2 * math.pi:
            self.theta -= 2 * math.pi

    def draw_crankshaft(self, screen):
        crank_x = self.crank_center_x + self.crank_radius * math.cos(self.theta)
        crank_y = self.crank_center_y + self.crank_radius * math.sin(self.theta)
        pygame.draw.line(screen, (200, 200, 200), (self.crank_center_x, self.crank_center_y), (crank_x, crank_y), 5)
        return crank_x, crank_y

    def draw_piston(self, screen, crank_x, crank_y):
        dx = crank_x - self.crank_center_x
        piston_y = self.crank_center_y - math.sqrt(self.rod_length**2 - dx**2)
        pygame.draw.line(screen, (200, 200, 200), (crank_x, crank_y), (self.crank_center_x, piston_y), 5)
        pygame.draw.rect(screen, (0, 0, 255), (self.crank_center_x - self.piston_width // 2, piston_y - self.piston_height, self.piston_width, self.piston_height))

    def draw_cylinder_head(self, screen):
        head_x = self.crank_center_x - self.piston_width // 2
        head_y = self.crank_center_y - self.rod_length - self.piston_height - 20
        pygame.draw.rect(screen, (200, 200, 200), (head_x, head_y, self.piston_width, 20))
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 20, head_y + 10), 10)
        pygame.draw.circle(screen, (0, 0, 0), (head_x + 40, head_y + 10), 10)

    def draw_engine(self, screen):
        # Draw the entire engine components
        crank_x, crank_y = self.draw_crankshaft(screen)
        self.draw_piston(screen, crank_x, crank_y)
        self.draw_crankshaft(screen)
        self.draw_crankshaft(screen)
        self.draw_cylinder_head(screen)