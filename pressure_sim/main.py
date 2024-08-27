import cProfile
import pstats
import pygame
from gas import GasSimulation
from ui import UIDiagnostics

# Initialize Pygame and create a screen
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Gas Simulation")

# Initialize gas simulation and clock
gas_sim = GasSimulation(initial_volume=10.0, initial_temperature=300, initial_mass=10.0)
clock = pygame.time.Clock()
ui = UIDiagnostics(gas_sim, clock)

# Profiling function
def run_simulation():
    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            ui.handle_event(event)

        # Update the gas simulation and UI
        gas_sim.update()
        ui.update()

        # Draw the UI diagnostics
        screen.fill((0, 0, 0))  # Clear screen with black color
        ui.draw(screen)

        pygame.display.flip()  # Update the display
        clock.tick(60)  # Limit to 60 frames per second

    pygame.quit()

# Profile the simulation
profiler = cProfile.Profile()
profiler.enable()
run_simulation()
profiler.disable()

# Save the profiling results to a file
with open("profile_results.txt", "w") as f:
    ps = pstats.Stats(profiler, stream=f)
    ps.strip_dirs().sort_stats("cumulative").print_stats(50)
