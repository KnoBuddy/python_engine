import pygame

class UI:
    def __init__(self):
        self.font = pygame.font.SysFont(None, 24)
        self.red = (255, 0, 0)
        self.black = (0, 0, 0)
        self.gray = (200, 200, 200)
        self.box_color = (150, 150, 150)
        self.active_slider = None  # Track which slider is active

    def draw_slider(self, screen, slider_pos, slider_width, slider_height, indicator_radius, value, min_value, max_value, label, input_value, input_active):
        # Draw slider background
        pygame.draw.rect(screen, self.gray, (slider_pos[0], slider_pos[1] - slider_height // 2, slider_width, slider_height))
        
        # Calculate the position of the indicator based on value
        indicator_pos_x = slider_pos[0] + ((value - min_value) / (max_value - min_value)) * slider_width
        indicator_pos_y = slider_pos[1]
        
        # Draw the indicator
        pygame.draw.circle(screen, self.red, (int(indicator_pos_x), int(indicator_pos_y)), indicator_radius)
        
        # Draw the text entry box
        text_box_rect = pygame.Rect(slider_pos[0] + slider_width + 10, slider_pos[1] - slider_height, 80, 30)
        pygame.draw.rect(screen, self.box_color, text_box_rect, 2)
        
        # Display the current value with manual input
        value_text = self.font.render(input_value, True, self.red if input_active else self.black)
        screen.blit(value_text, (slider_pos[0] + slider_width + 20, slider_pos[1] - slider_height // 2))
        
        # Display the label
        label_text = self.font.render(label, True, self.black)
        screen.blit(label_text, (slider_pos[0] - 60, slider_pos[1] - slider_height // 2))

        return text_box_rect

    def adjust_value(self, pos, slider_pos, slider_width, min_value, max_value):
        # Adjust value based on mouse position
        relative_pos = pos[0] - slider_pos[0]
        return max(min_value, min(max_value, (relative_pos / slider_width) * (max_value - min_value) + min_value))

    def handle_text_input(self, event, input_active, input_value, allowed_chars="0123456789."):
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

    def handle_mouse_click(self, event, rpm_text_box_rect, speed_text_box_rect, rpm_input_value, speed_input_value, rpm_input_active, speed_input_active):
        mouse_pos = event.pos
        if rpm_text_box_rect.collidepoint(mouse_pos):
            rpm_input_active = True
            rpm_input_value = ''  # Clear the text box
        else:
            rpm_input_active = False
        if speed_text_box_rect.collidepoint(mouse_pos):
            speed_input_active = True
            speed_input_value = ''  # Clear the text box
        else:
            speed_input_active = False
        return rpm_input_active, speed_input_active, rpm_input_value, speed_input_value

    def revert_text_if_inactive(self, rpm_input_active, speed_input_active, rpm_input_value, speed_input_value, rpm_previous_value, speed_previous_value):
        if not rpm_input_active:
            rpm_input_value = rpm_previous_value  # Revert to previous value
        if not speed_input_active:
            speed_input_value = speed_previous_value  # Revert to previous value
        return rpm_input_value, speed_input_value

    def handle_slider_movement(self, event, rpm_slider_rect, speed_slider_rect, rpm, speed_factor):
        mouse_pos = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if rpm_slider_rect.collidepoint(mouse_pos):
                self.active_slider = 'rpm'
            elif speed_slider_rect.collidepoint(mouse_pos):
                self.active_slider = 'speed'

        if event.type == pygame.MOUSEMOTION and pygame.mouse.get_pressed()[0]:  # If dragging
            if self.active_slider == 'rpm':
                rpm = self.adjust_value(mouse_pos, rpm_slider_rect.topleft, rpm_slider_rect.width, 0, 5000)
            elif self.active_slider == 'speed':
                speed_factor = self.adjust_value(mouse_pos, speed_slider_rect.topleft, speed_slider_rect.width, 0.01, 1.0)

        if event.type == pygame.MOUSEBUTTONUP:
            self.active_slider = None  # Reset active slider when mouse is released

        return rpm, speed_factor
