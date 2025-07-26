#!/usr/bin/env python3
import time
from dynamixel_sdk import *
from config.config import *
from .utils import getch

class DynamixelController:
    def __init__(self):
        self.portHandler = PortHandler(DEVICENAME)
        self.packetHandler = PacketHandler(PROTOCOL_VERSION)
        
    def initialize(self):
        if not self.portHandler.openPort():
            print("Failed to open the port")
            print("Press any key to terminate...")
            getch()
            return False
        
        print("Succeeded to open the port")
        
        if not self.portHandler.setBaudRate(BAUDRATE):
            print("Failed to change the baudrate")
            print("Press any key to terminate...")
            getch()
            return False
        
        print("Succeeded to change the baudrate")
        
        # Set operating mode to velocity control for both motors
        if not self.set_operating_mode(DXL_ID_1):
            return False
        if not self.set_operating_mode(DXL_ID_2):
            return False
        
        if not self.enable_torque(DXL_ID_1):
            return False
        print("Dynamixel 1 has been successfully connected")
        
        if not self.enable_torque(DXL_ID_2):
            return False
        print("Dynamixel 2 has been successfully connected")
        
        return True
    
    def set_operating_mode(self, dxl_id):
        # Disable torque first
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        
        # Set to velocity control mode (1)
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, dxl_id, 11, 1  # Operating mode address = 11, velocity mode = 1
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            return False
        
        print(f"Motor {dxl_id} set to velocity control mode")
        return True
    
    def enable_torque(self, dxl_id):
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_ENABLE
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            return False
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            return False
        return True
    
    def disable_torque(self, dxl_id):
        dxl_comm_result, dxl_error = self.packetHandler.write1ByteTxRx(
            self.portHandler, dxl_id, ADDR_TORQUE_ENABLE, TORQUE_DISABLE
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print("Dynamixel has been successfully disconnected")
    
    def read_present_position(self, dxl_id):
        dxl_present_position, dxl_comm_result, dxl_error = self.packetHandler.read4ByteTxRx(
            self.portHandler, dxl_id, ADDR_PRESENT_POSITION
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
            return 0
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
            return 0
        else:
            if dxl_present_position > DXL_MAXIMUM_POSITION_VALUE:
                dxl_present_position = dxl_present_position - (DXL_MAXIMUM_POSITION_VALUE + 1) * 2
        return dxl_present_position
    
    def set_goal_velocity(self, dxl_id, velocity):
        # Convert velocity to proper format for Dynamixel (signed 32-bit)
        if velocity < 0:
            velocity = velocity + 4294967296  # Convert negative to unsigned 32-bit
        
        dxl_comm_result, dxl_error = self.packetHandler.write4ByteTxRx(
            self.portHandler, dxl_id, ADDR_GOAL_VELOCITY, int(velocity)
        )
        if dxl_comm_result != COMM_SUCCESS:
            print("%s" % self.packetHandler.getTxRxResult(dxl_comm_result))
        elif dxl_error != 0:
            print("%s" % self.packetHandler.getRxPacketError(dxl_error))
        else:
            print(f"Motor {dxl_id} speed set to {velocity}")
    
    def move_to_middle_position(self, input_handler):
        input_handler.reset_speeds()
        print("Moving to middle position")
        
        dxl_position_1 = self.read_present_position(DXL_ID_1)
        dxl_position_2 = self.read_present_position(DXL_ID_2)
        
        if input_handler.horizontal_bound_exceeded:
            input_handler.horizontal_bound_exceeded = False
            middle_pos_1 = (dxl_limit_points_1[1] + dxl_limit_points_1[0]) / 2
            if dxl_position_1 > middle_pos_1:
                self.set_goal_velocity(DXL_ID_1, -POSITION_RETURN_SPEED)
            else:
                self.set_goal_velocity(DXL_ID_1, POSITION_RETURN_SPEED)
        
        if input_handler.vertical_bound_exceeded:
            input_handler.vertical_bound_exceeded = False
            middle_pos_2 = (dxl_limit_points_2[1] + dxl_limit_points_2[0]) / 2
            if dxl_position_2 > middle_pos_2:
                self.set_goal_velocity(DXL_ID_2, -POSITION_RETURN_SPEED)
            else:
                self.set_goal_velocity(DXL_ID_2, POSITION_RETURN_SPEED)
        
        time.sleep(0.5)
        self.set_goal_velocity(DXL_ID_1, 0)
        self.set_goal_velocity(DXL_ID_2, 0)
    
    def check_bounds_and_stop(self, input_handler):
        dxl_position_1 = self.read_present_position(DXL_ID_1)
        dxl_position_2 = self.read_present_position(DXL_ID_2)
        
        if (dxl_position_2 < dxl_limit_points_2[0] or 
            dxl_position_2 > dxl_limit_points_2[1]):
            input_handler.vertical_speed = 0
            self.set_goal_velocity(DXL_ID_2, 0)
            print(f"Motor 2 out of bounds: {dxl_position_2}")
            input_handler.vertical_bound_exceeded = True
            self.move_to_middle_position(input_handler)
        
        if (dxl_position_1 < dxl_limit_points_1[0] or 
            dxl_position_1 > dxl_limit_points_1[1]):
            input_handler.horizontal_speed = 0
            self.set_goal_velocity(DXL_ID_1, 0)
            print(f"Motor 1 out of bounds: {dxl_position_1}")
            input_handler.horizontal_bound_exceeded = True
            self.move_to_middle_position(input_handler)
    
    def update_motor_speeds(self, input_handler):
        if input_handler.speed_change:
            self.set_goal_velocity(DXL_ID_1, input_handler.horizontal_speed)
            self.set_goal_velocity(DXL_ID_2, input_handler.vertical_speed)
            input_handler.speed_change = False
    
    def cleanup(self):
        self.disable_torque(DXL_ID_1)
        self.disable_torque(DXL_ID_2)
        self.portHandler.closePort()