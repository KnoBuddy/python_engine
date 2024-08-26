import pygame
import math

# Initialize Pygame
pygame.init()

# Set up display
width, height = 1400, 800  # Updated window size
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Engine parameters
crank_radius = 100  # Crank radius
rod_length = 200  # Connecting rod length
piston_width = 60
piston_height = 100
crank_center_x = width // 2
crank_center_y = height // 2 - 50

# RPM parameters
max_rpm = 5000  # Maximum RPM
rpm = 1000  # Initial RPM
rpm_slider_width = 400
rpm_slider_height = 10
rpm_indicator_radius = 10
rpm_slider_pos = (width // 2 - rpm_slider_width // 2, height - 150)  # Centered RPM slider position
rpm_input_active = False  # Flag to track if RPM text input is active
rpm_input_value = str(rpm)
rpm_previous_value = rpm_input_value

# Simulation speed parameters
speed_factor = 1.0  # Start at real-time
max_speed_factor = 1.0  # Real-time speed
min_speed_factor = 0.01  # 1/100th speed
speed_slider_width = 400
speed_slider_height = 10
speed_indicator_radius = 10
speed_slider_pos = (width // 2 - speed_slider_width // 2, height - 80)  # Centered Speed slider position
speed_input_active = False  # Flag to track if speed text input is active
speed_input_value = str(speed_factor)
speed_previous_value = speed_input_value

# Simulation parameters
theta = 0  # Crankshaft angle

# Combustion parameters
pressure = 1.0  # Initial pressure (normalized)
combustion_pressure = 5.0  # Max pressure during combustion

def draw_crankshaft(theta):
    # Calculate crank position
    crank_x = crank_center_x + crank_radius * math.cos(theta)
    crank_y = crank_center_y + crank_radius * math.sin(theta)
    
    # Draw crankshaft
    pygame.draw.line(screen, GRAY, (crank_center_x, crank_center_y), (crank_x, crank_y), 5)
    
    return crank_x, crank_y

def draw_piston(crank_x, crank_y):
    # Calculate piston position based on crank position and rod length
    dx = crank_x - crank_center_x
    piston_y = crank_center_y - math.sqrt(rod_length**2 - dx**2)
    
    # Draw connecting rod
    pygame.draw.line(screen, GRAY, (crank_x, crank_y), (crank_center_x, piston_y), 5)
    
    # Draw piston
    piston_x = crank_center_x - piston_width // 2
    pygame.draw.rect(screen, BLUE, (piston_x, piston_y - piston_height, piston_width, piston_height))

def draw_cylinder_head():
    # Draw cylinder head (top of the cylinder)
    head_x = crank_center_x - piston_width // 2
    head_y = crank_center_y - rod_length - piston_height - 20
    pygame.draw.rect(screen, GRAY, (head_x, head_y, piston_width, 20))
    
    # Draw valves (simple representation)
    valve_radius = 10
    pygame.draw.circle(screen, BLACK, (head_x + 20, head_y + 10), valve_radius)
    pygame.draw.circle(screen, BLACK, (head_x + 40, head_y + 10), valve_radius)

def update_pressure(theta):
    global pressure
    # Simplified model: Increase pressure on compression and combustion, decrease during exhaust
    if 0 < theta < math.pi:  # Compression phase
        pressure += 0.02
    elif math.pi < theta < 2 * math.pi:  # Expansion phase
        pressure -= 0.02
    pressure = max(1.0, min(combustion_pressure, pressure))  # Clamp pressure to physical limits

def draw_slider(slider_pos, slider_width, slider_height, indicator_radius, value, min_value, max_value, label, input_value, input_active):
    # Draw slider background
    pygame.draw.rect(screen, GRAY, (slider_pos[0], slider_pos[1] - slider_height // 2, slider_width, slider_height))
    
    # Calculate the position of the indicator based on value
    indicator_pos_x = slider_pos[0] + ((value - min_value) / (max_value - min_value)) * slider_width
    indicator_pos_y = slider_pos[1]
    
    # Draw the indicator
    pygame.draw.circle(screen, RED, (int(indicator_pos_x), int(indicator_pos_y)), indicator_radius)
    
    # Display the current value with manual input
    font = pygame.font.SysFont(None, 24)
    if input_active:
        value_text = font.render(input_value, True, RED)
    else:
        value_text = font.render(input_value, True, BLACK)
    screen.blit(value_text, (slider_pos[0] + slider_width + 20, slider_pos[1] - slider_height // 2))
    
    # Display the label
    label_text = font.render(label, True, BLACK)
    screen.blit(label_text, (slider_pos[0] - 60, slider_pos[1] - slider_height // 2))

    return value_text.get_rect(topleft=(slider_pos[0] + slider_width + 20, slider_pos[1] - slider_height // 2))

def adjust_value(pos, slider_pos, slider_width, min_value, max_value):
    # Adjust value based on mouse position
    relative_pos = pos[0] - slider_pos[0]
    new_value = max(min_value, min(max_value, (relative_pos / slider_width) * (max_value - min_value) + min_value))
    return new_value

def handle_text_input(event, input_active, input_value, allowed_chars="0123456789."):
    # Handle text input for the active input box
    if input_active:
        if event.key == pygame.K_BACKSPACE:
            input_value = input_value[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            return False, input_value  # Return false to deactivate input and keep the value
        else:
            char = event.unicode
            if char in allowed_chars:
                input_value += char
    return input_active, input_value

# Main loop
running = True
while running:
    screen.fill(WHITE)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            rpm_rect = draw_slider(rpm_slider_pos, rpm_slider_width, rpm_slider_height, rpm_indicator_radius, rpm, 0, max_rpm, 'RPM', rpm_input_value, rpm_input_active)
            speed_rect = draw_slider(speed_slider_pos, speed_slider_width, speed_slider_height, speed_indicator_radius, speed_factor, min_speed_factor, max_speed_factor, 'Speed', speed_input_value, speed_input_active)
            if rpm_rect.collidepoint(mouse_pos):
                rpm_input_active = True
                rpm_input_value = ''  # Clear the text box
            else:
                rpm_input_active = False
                rpm_input_value = rpm_previous_value  # Restore previous value if clicked away
            if speed_rect.collidepoint(mouse_pos):
                speed_input_active = True
                speed_input_value = ''  # Clear the text box
            else:
                speed_input_active = False
                speed_input_value = speed_previous_value  # Restore previous value if clicked away
        elif event.type == pygame.KEYDOWN:
            if rpm_input_active:
                rpm_input_active, rpm_input_value = handle_text_input(event, rpm_input_active, rpm_input_value)
                if not rpm_input_active:  # Only convert and apply value when Enter is pressed
                    try:
                        rpm = int(rpm_input_value)
                    except ValueError:
                        rpm = 0
                    rpm = max(0, min(max_rpm, rpm))
                    rpm_previous_value = rpm_input_value  # Update the previous value
            if speed_input_active:
                speed_input_active, speed_input_value = handle_text_input(event, speed_input_active, speed_input_value)
                if not speed_input_active:  # Only convert and apply value when Enter is pressed
                    try:
                        speed_factor = float(speed_input_value)
                    except ValueError:
                        speed_factor = min_speed_factor
                    speed_factor = max(min_speed_factor, min(max_speed_factor, speed_factor))
                    speed_previous_value = speed_input_value  # Update the previous value
        elif event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION:
            if pygame.mouse.get_pressed()[0]:  # If the left mouse button is pressed
                mouse_pos = pygame.mouse.get_pos()
                if rpm_slider_pos[0] <= mouse_pos[0] <= rpm_slider_pos[0] + rpm_slider_width and \
                   rpm_slider_pos[1] - rpm_indicator_radius <= mouse_pos[1] <= rpm_slider_pos[1] + rpm_indicator_radius:
                    rpm = adjust_value(mouse_pos, rpm_slider_pos, rpm_slider_width, 0, max_rpm)
                    rpm_input_value = str(int(rpm))
                    rpm_previous_value = rpm_input_value  # Update previous value when slider is moved
                if speed_slider_pos[0] <= mouse_pos[0] <= speed_slider_pos[0] + speed_slider_width and \
                   speed_slider_pos[1] - speed_indicator_radius <= mouse_pos[1] <= speed_slider_pos[1] + speed_indicator_radius:
                    speed_factor = adjust_value(mouse_pos, speed_slider_pos, speed_slider_width, min_speed_factor, max_speed_factor)
                    speed_input_value = f"{speed_factor:.2f}"
                    speed_previous_value = speed_input_value  # Update previous value when slider is moved

    # Calculate angular velocity (rad/s)
    angular_velocity = (rpm / 60.0) * 2 * math.pi  # Convert RPM to radians per second

    # Update crankshaft angle
    theta += angular_velocity * speed_factor / 60  # Apply speed factor and time scaling
    if theta > 2 * math.pi:
        theta -= 2 * math.pi
    
    # Update pressure (this will be used for sound generation later)
    update_pressure(theta)
    
    # Draw engine components
    crank_x, crank_y = draw_crankshaft(theta)
    draw_piston(crank_x, crank_y)
    draw_cylinder_head()
    
    # Draw RPM and Speed sliders
    rpm_rect = draw_slider(rpm_slider_pos, rpm_slider_width, rpm_slider_height, rpm_indicator_radius, rpm, 0, max_rpm, 'RPM', rpm_input_value, rpm_input_active)
    speed_rect = draw_slider(speed_slider_pos, speed_slider_width, speed_slider_height, speed_indicator_radius, speed_factor, min_speed_factor, max_speed_factor, 'Speed', speed_input_value, speed_input_active)
    
    # Update the display
    pygame.display.flip()
    
    # Frame rate
    clock.tick(60)

pygame.quit()

