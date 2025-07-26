#!/usr/bin/env python3
import keyboard
from src.dynamixel_controller import DynamixelController
from src.input_handler import InputHandler
from src.network_handler import NetworkHandler
from src.utils import getch

def main():
    input_handler = InputHandler()
    motor_controller = DynamixelController()
    network_handler = NetworkHandler(input_handler)
    
    try:
        if not motor_controller.initialize():
            return
        
        keyboard.on_press(input_handler.on_key_press)
        
        # Connect to server as a client
        if network_handler.connect_to_server():
            network_handler.start_udp_listener()
        else:
            print("Proceeding with keyboard control only")
        
        print("Press 'w', 's', 'a', 'd' or arrow keys to control the Dynamixel motors.")
        print("Press 'q' or 'esc' to quit.")
        
        input_handler.reset_speeds()
        motor_controller.move_to_middle_position(input_handler)
        
        import time
        while True:
            motor_controller.check_bounds_and_stop(input_handler)
            motor_controller.update_motor_speeds(input_handler)
            
            if input_handler.escaped:
                print("Exiting...")
                break
            
            # No delay - true real-time response
                
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        print("Cleaning up...")
        motor_controller.cleanup()
        network_handler.stop()

if __name__ == "__main__":
    main()