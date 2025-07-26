#!/usr/bin/env python3
from config.config import SPEED_INCREMENT

class InputHandler:
    def __init__(self):
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.escaped = False
        self.speed_change = False
        self.horizontal_bound_exceeded = False
        self.vertical_bound_exceeded = False
        self.mode = "MANUAL"  # Default mode
        self.camera_width = 800  # Camera resolution
        self.camera_height = 600
        self.center_box_width = 200  # Width of center dead zone (pixels)
        self.center_box_height = 150  # Height of center dead zone (pixels)
        # Simple horizontal lines for vertical control
        self.upper_line_offset = 80  # Distance above center for upper line
        self.lower_line_offset = 80  # Distance below center for lower line
        
        # Simple control parameters
        self.auto_speed = 30  # Fixed speed for auto mode movements
        self.min_auto_speed = 5  # Minimum speed to prevent stalling
        self.max_auto_speed = 30  # Maximum speed for fast movements
    
    def on_key_press(self, event):
        if event.name == 'w' or event.name == 'up':
            self.vertical_speed -= SPEED_INCREMENT
            self.speed_change = True
            print("Up/W pressed")
        elif event.name == 's' or event.name == 'down':
            self.vertical_speed += SPEED_INCREMENT
            self.speed_change = True
            print("Down/S pressed")
        elif event.name == 'a' or event.name == 'left':
            self.horizontal_speed += SPEED_INCREMENT
            self.speed_change = True
            print("Left/A pressed")
        elif event.name == 'd' or event.name == 'right':
            self.horizontal_speed -= SPEED_INCREMENT
            self.speed_change = True
            print("Right/D pressed")
        elif event.name == 'esc' or event.name == 'q':
            print("Escape/Q pressed, exiting...")
            self.escaped = True
            return False
    
    def on_udp_message(self, data):
        message = data.decode('utf-8')
        print(f"Received UDP message: {message}")
        
        # Parse messages with colons
        if ':' in message:
            parts = message.split(':')
            command_type = parts[0]
            
            # Handle mode changes
            if command_type == 'MODE_CHANGED':
                self.mode = parts[1]
                print(f"Mode changed to: {self.mode}")
                if self.mode == "AUTO":
                    self.reset_speeds()  # Stop motors when switching to AUTO
                return
            
            # Handle object detection in AUTO mode
            elif command_type == 'OBJECT_SELECTED' or command_type == 'SELECTED_COORDS':
                if self.mode == "AUTO":
                    self._handle_object_tracking(message)
                return
            
            # Handle touch miss - stop motors immediately
            elif command_type == 'TOUCH_MISS':
                print("TOUCH_MISS received - stopping motors")
                self.horizontal_speed = 0
                self.vertical_speed = 0
                self.speed_change = True
                return
            
            # Handle manual button presses (works in any mode)
            elif command_type == 'BUTTON_PRESSED':
                direction = parts[1].lower()
                if direction == 'up':
                    self.vertical_speed -= SPEED_INCREMENT
                    self.speed_change = True
                    print("Up arrow pressed via UDP")
                elif direction == 'down':
                    self.vertical_speed += SPEED_INCREMENT
                    self.speed_change = True
                    print("Down arrow pressed via UDP")
                elif direction == 'left':
                    self.horizontal_speed += SPEED_INCREMENT
                    self.speed_change = True
                    print("Left arrow pressed via UDP")
                elif direction == 'right':
                    self.horizontal_speed -= SPEED_INCREMENT
                    self.speed_change = True
                    print("Right arrow pressed via UDP")
                elif direction == 'esc' or direction == 'stop':
                    print("Stop/Escape pressed via UDP")
                    self.escaped = True
                    return False
        
        # Handle simple messages (backward compatibility) - works in any mode
        else:
            if message.lower() == 'up':
                self.vertical_speed -= SPEED_INCREMENT
                self.speed_change = True
                print("Up arrow pressed via UDP")
            elif message.lower() == 'down':
                self.vertical_speed += SPEED_INCREMENT
                self.speed_change = True
                print("Down arrow pressed via UDP")
            elif message.lower() == 'left':
                self.horizontal_speed += SPEED_INCREMENT
                self.speed_change = True
                print("Left arrow pressed via UDP")
            elif message.lower() == 'right':
                self.horizontal_speed -= SPEED_INCREMENT
                self.speed_change = True
                print("Right arrow pressed via UDP")
            elif message.lower() == 'esc':
                print("Escape pressed via UDP, exiting...")
                self.escaped = True
                return False
    
    def _handle_object_tracking(self, message):
        """Handle object tracking in AUTO mode"""
        try:
            # Parse: SELECTED_COORDS:ID:0:X:273:Y:306:FRAME:388
            parts = message.split(':')
            
            # Find X and Y values (these are already the center coordinates)
            x_center = None
            y_center = None
            
            for i, part in enumerate(parts):
                if part == 'X' and i + 1 < len(parts):
                    x_center = int(parts[i + 1])
                elif part == 'Y' and i + 1 < len(parts):
                    y_center = int(parts[i + 1])
            
            if x_center is not None and y_center is not None:
                self._center_object(x_center, y_center)
            
        except Exception as e:
            print(f"Error parsing object tracking message: {e}")
    
    def _center_object(self, x_center, y_center):
        """Proportional control to keep object in center with smooth approach"""
        camera_center_x = self.camera_width // 2
        camera_center_y = self.camera_height // 2
        
        # Define center box boundaries
        box_left = camera_center_x - self.center_box_width // 2
        box_right = camera_center_x + self.center_box_width // 2
        
        # Define vertical lines
        upper_line = camera_center_y - self.upper_line_offset
        lower_line = camera_center_y + self.lower_line_offset
        
        print(f"Object at ({x_center}, {y_center})")
        print(f"Center box: ({box_left}-{box_right}), Lines: {upper_line}-{lower_line}")
        
        # Reset speeds
        self.horizontal_speed = 0
        self.vertical_speed = 0
        
        # Proportional horizontal control
        if x_center < box_left:
            # Distance from left edge of center box
            distance = box_left - x_center
            # Maximum distance for scaling (half camera width)
            max_distance = camera_center_x
            # Calculate proportional speed (closer = slower)
            speed_ratio = min(distance / max_distance, 1.0)
            speed = int(self.min_auto_speed + (self.max_auto_speed - self.min_auto_speed) * speed_ratio)
            self.horizontal_speed = speed  # Move right
            print(f"Object left of center box (dist: {distance}) - moving right at speed {speed}")
        elif x_center > box_right:
            # Distance from right edge of center box
            distance = x_center - box_right
            # Maximum distance for scaling (half camera width)
            max_distance = camera_center_x
            # Calculate proportional speed (closer = slower)
            speed_ratio = min(distance / max_distance, 1.0)
            speed = int(self.min_auto_speed + (self.max_auto_speed - self.min_auto_speed) * speed_ratio)
            self.horizontal_speed = -speed  # Move left
            print(f"Object right of center box (dist: {distance}) - moving left at speed {speed}")
        else:
            print("Object horizontally centered")
        
        # Proportional vertical control
        if y_center < upper_line:
            # Distance from upper line
            distance = upper_line - y_center
            # Maximum distance for scaling (half camera height)
            max_distance = camera_center_y
            # Calculate proportional speed (closer = slower)
            speed_ratio = min(distance / max_distance, 1.0)
            speed = int(self.min_auto_speed + (self.max_auto_speed - self.min_auto_speed) * speed_ratio)
            self.vertical_speed = -speed  # Move up
            print(f"Object above upper line (dist: {distance}) - moving up at speed {speed}")
        elif y_center > lower_line:
            # Distance from lower line
            distance = y_center - lower_line
            # Maximum distance for scaling (half camera height)
            max_distance = camera_center_y
            # Calculate proportional speed (closer = slower)
            speed_ratio = min(distance / max_distance, 1.0)
            speed = int(self.min_auto_speed + (self.max_auto_speed - self.min_auto_speed) * speed_ratio)
            self.vertical_speed = speed  # Move down
            print(f"Object below lower line (dist: {distance}) - moving down at speed {speed}")
        else:
            print("Object vertically centered")
        
        if self.horizontal_speed != 0 or self.vertical_speed != 0:
            self.speed_change = True
            print(f"AUTO mode: H={self.horizontal_speed}, V={self.vertical_speed}")
        else:
            print("AUTO mode: Object centered")
    
    def set_camera_resolution(self, width, height):
        """Set camera resolution for centering calculations"""
        self.camera_width = width
        self.camera_height = height
        print(f"Camera resolution set to {width}x{height}")
    
    def set_center_box_size(self, width, height):
        """Set the size of the center dead zone box"""
        self.center_box_width = width
        self.center_box_height = height
        print(f"Center box size set to {width}x{height}")
    
    def reset_speeds(self):
        self.horizontal_speed = 0
        self.vertical_speed = 0
        self.speed_change = False