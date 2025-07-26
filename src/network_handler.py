#!/usr/bin/env python3
import socket
import threading
import time
from config.config import UDP_IP, UDP_PORT, UDP_LISTEN_INTERVAL

class NetworkHandler:
    def __init__(self, input_handler):
        self.input_handler = input_handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_address = (UDP_IP, UDP_PORT)
        self.running = False
        self.thread = None
        self.connected = False
        print(f"UDP client initialized for server {UDP_IP}:{UDP_PORT}")
    
    def connect_to_server(self):
        print(f"Setting up UDP client for server at {UDP_IP}:{UDP_PORT}")
        try:
            # Send a simple "hi" message to the server
            self.sock.sendto(b"hi", self.server_address)
            print("Sent 'hi' message to server")
            
            self.sock.settimeout(None)  # Remove any timeout
            self.connected = True
            print("UDP client ready to receive messages from server")
            return True
        except Exception as e:
            print(f"Failed to setup UDP client: {e}")
            return False
    
    def start_udp_listener(self):
        if not self.connected:
            print("Not connected to server, UDP listener not started")
            return
            
        self.sock.setblocking(False)
        self.running = True
        self.thread = threading.Thread(target=self._udp_listener_thread)
        self.thread.daemon = True
        self.thread.start()
        print("UDP listener started")
    
    def _udp_listener_thread(self):
        while self.running:
            self._udp_listener()
            time.sleep(UDP_LISTEN_INTERVAL)
    
    def _udp_listener(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            # Only accept messages from the configured server
            if addr[0] == UDP_IP:
                self.input_handler.on_udp_message(data)
        except BlockingIOError:
            pass
    
    def send_status_to_server(self, status):
        if self.connected:
            try:
                self.sock.sendto(status.encode(), self.server_address)
            except Exception as e:
                print(f"Failed to send status to server: {e}")
    
    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
        self.sock.close()
        print("UDP client disconnected")