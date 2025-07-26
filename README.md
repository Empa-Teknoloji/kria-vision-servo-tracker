# Dynamixel Motor Controller

A Python-based control system for Dynamixel XL430-W250-T servo motors with keyboard input, network communication, and advanced motor control features.

## Features

- **Real-time Motor Control**: Keyboard-driven control with customizable speed settings
- **Network Communication**: Client-server architecture for remote motor control
- **Position Limits**: Configurable safety boundaries to prevent motor damage
- **PID Control**: Built-in PID tuning and preset management
- **Motor Testing**: Comprehensive testing utilities for motor diagnostics
- **Safety Features**: Emergency stop and limit checking

## Hardware Requirements

- Dynamixel XL430-W250-T servo motors
- USB2Dynamixel adapter or U2D2
- Compatible computer with USB port

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/motor_controller.git
   cd motor_controller
   ```

2. Install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Connect your Dynamixel motors via USB2Dynamixel adapter

4. Update device configuration in `config.py` if needed

## Quick Start

### Basic Usage

```python
from dynamixel_controller import DynamixelController

# Initialize controller
controller = DynamixelController()

# Set position limits (in degrees)
controller.set_position_limits(1, -90, 90)  # Motor ID 1
controller.set_position_limits(2, -90, 90)  # Motor ID 2

# Control motors
controller.control_by_velocity(1, 30)   # 30 RPM
controller.control_by_velocity(2, -20)  # -20 RPM (reverse)

# Stop and cleanup
controller.stop_all_motors()
controller.close_connection()
```

### Run the Main Application

```bash
python main.py
```

Use keyboard controls:
- `W/S`: Motor 1 forward/backward
- `A/D`: Motor 2 left/right
- `Q`: Quit application
- `+/-`: Adjust motor speed

## Project Structure

```
motor_controller/
├── main.py                 # Main application entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/                   # Source code
│   ├── __init__.py
│   ├── dynamixel_controller.py # Core motor control class
│   ├── input_handler.py        # Keyboard input management
│   ├── network_handler.py      # Network communication
│   ├── utils.py               # Utility functions
│   ├── pid_tuner.py           # PID control tuning
│   └── pid_presets.py         # Predefined PID settings
├── config/                # Configuration files
│   ├── __init__.py
│   └── config.py          # Configuration settings
└── tests/                 # Test files
    ├── __init__.py
    ├── motor_tester.py        # Motor testing utilities
    └── test_motor_directions.py # Direction testing
```

## Configuration

Edit `config/config.py` to customize:

```python
# Serial connection settings
DEVICE_NAME = '/dev/ttyUSB0'  # Linux/Mac
# DEVICE_NAME = 'COM3'        # Windows
BAUDRATE = 57600

# Motor parameters
MOTOR_IDS = [1, 2]
MAX_VELOCITY = 50  # RPM
POSITION_LIMITS = {
    1: (-90, 90),   # Motor 1 limits in degrees
    2: (-90, 90)    # Motor 2 limits in degrees
}
```

## Network Control

The system supports client-server architecture for remote control:

1. **Server Mode**: One instance controls motors directly
2. **Client Mode**: Remote instances send commands to server

Configure network settings in `src/network_handler.py`.

## PID Tuning

Use the built-in PID tuner for optimal motor performance:

```bash
python src/pid_tuner.py
```

Or use predefined presets:

```python
from src.pid_presets import PIDPresets
presets = PIDPresets()
presets.apply_preset('smooth_motion', motor_id=1)
```

## Testing

Test motor functionality:

```bash
python tests/motor_tester.py      # General motor tests
python tests/test_motor_directions.py  # Direction testing
```

## Motor Specifications

- **Model**: Dynamixel XL430-W250-T
- **Position Range**: 0-4095 (0-360°)
- **Position Resolution**: 0.088° per unit
- **Velocity Unit**: 0.229 RPM per unit
- **Communication**: TTL Half Duplex
- **Default Baud Rate**: 57600 bps

## Troubleshooting

### Common Issues

1. **Permission Denied**: 
   ```bash
   sudo usermod -a -G dialout $USER
   # Then logout and login again
   ```

2. **Motor Not Found**: Check connections and motor IDs in `config/config.py`

3. **Import Errors**: Ensure all dependencies are installed:
   ```bash
   pip install --upgrade dynamixel-sdk
   ```

4. **Communication Errors**: Verify baud rate and device path

### Debug Mode

Enable debug logging in your code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built using the [Dynamixel SDK](https://github.com/ROBOTIS-GIT/DynamixelSDK)
- Robotis for the excellent Dynamixel servo motors