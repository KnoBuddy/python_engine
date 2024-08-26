import pygame
import math
from engine import Engine
from ui_module import UI
from otto_cycle import OttoCycle

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1400, 800
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Initialize UI and Engine
ui = UI()
engine = OttoCycle(crank_radius=100, rod_length=200, piston_width=60, piston_height=100, crank_center_x=width // 2, crank_center_y=height // 2 - 50)

# Main loop
running = True
rpm = 1000
rpm_input_active = False
rpm_input_value = str(rpm)
rpm_previous_value = rpm_input_value

speed_factor = 1.0
speed_input_active = False
speed_input_value = str(speed_factor)
speed_previous_value = speed_input_value

while running:
    screen.fill((255, 255, 255))
    
    # Draw RPM and Speed sliders to get the clickable rects
    rpm_text_box_rect, rpm_clickable_rect = ui.draw_slider(screen, (width // 2 - 200, height - 150), 400, 10, 10, rpm, 0, 5000, 'RPM', rpm_input_value, rpm_input_active)
    speed_text_box_rect, speed_clickable_rect = ui.draw_slider(screen, (width // 2 - 200, height - 80), 400, 10, 10, speed_factor, 0.01, 1.0, 'Speed', speed_input_value, speed_input_active)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Handle clicks on text boxes
            rpm_input_active, speed_input_active, rpm_input_value, speed_input_value = ui.handle_mouse_click(
                event, rpm_text_box_rect, speed_text_box_rect, rpm_input_value, speed_input_value, rpm_input_active, speed_input_active, rpm_previous_value, speed_previous_value
            )
            print(f"Clicked: RPM Active: {rpm_input_active}, Speed Active: {speed_input_active}")  # Diagnostic print

        elif event.type == pygame.KEYDOWN:
            # Handle text input in the text boxes
            if rpm_input_active:
                rpm_input_active, rpm_input_value = ui.handle_text_input(event, rpm_input_active, rpm_input_value)
                print(f"RPM Input Value: {rpm_input_value}")  # Diagnostic print
                if not rpm_input_active:
                    try:
                        rpm = int(rpm_input_value)
                    except ValueError:
                        rpm = 0
                    rpm_previous_value = rpm_input_value

            if speed_input_active:
                speed_input_active, speed_input_value = ui.handle_text_input(event, speed_input_active, speed_input_value)
                print(f"Speed Input Value: {speed_input_value}")  # Diagnostic print
                if not speed_input_active:
                    try:
                        speed_factor = float(speed_input_value)
                    except ValueError:
                        speed_factor = 0.01
                    speed_previous_value = speed_input_value

        # Handle slider movement and update text accordingly
        new_rpm, new_speed_factor = ui.handle_slider_movement(event, rpm_clickable_rect, speed_clickable_rect, rpm, speed_factor)

        if new_rpm != rpm:
            rpm = new_rpm
            rpm_input_value = str(int(rpm))
            rpm_previous_value = rpm_input_value  # Update previous value when slider is moved

        if new_speed_factor != speed_factor:
            speed_factor = new_speed_factor
            speed_input_value = f"{speed_factor:.2f}"
            speed_previous_value = speed_input_value  # Update previous value when slider is moved

    # Revert text if input box is deactivated
    rpm_input_value, speed_input_value = ui.revert_text_if_inactive(
        rpm_input_active, speed_input_active, rpm_input_value, speed_input_value, rpm_previous_value, speed_previous_value
    )

    # Calculate angular velocity (rad/s)
    angular_velocity = (rpm / 60.0) * 2 * math.pi  # Convert RPM to radians per second
    engine.update_angle(angular_velocity, speed_factor)
    engine.update_pressure()

    # Draw engine components
    engine.draw_engine(screen)
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
