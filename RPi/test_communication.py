#!/usr/bin/env python3
"""
Test script to diagnose communication issues between Raspberry Pi and ESP32
"""

import serial
import json
import time
import sys

def test_serial_communication():
    """Test serial communication with ESP32"""
    
    # Determine the correct serial port
    if len(sys.argv) > 1:
        port = sys.argv[1]
    else:
        # Try common ports
        ports_to_try = ['/dev/ttyAMA0', '/dev/serial0', '/dev/ttyUSB0']
        port = None
        
        for p in ports_to_try:
            try:
                test_ser = serial.Serial(p, 115200, timeout=1)
                test_ser.close()
                port = p
                print(f"Found working port: {port}")
                break
            except:
                continue
    
    if not port:
        print("No working serial port found. Please specify port manually:")
        print("python test_communication.py /dev/ttyAMA0")
        return
    
    print(f"Testing communication on {port}")
    
    try:
        # Open serial connection
        ser = serial.Serial(port, 115200, timeout=2)
        print(f"Connected to {port}")
        
        # Clear any existing data
        ser.reset_input_buffer()
        ser.reset_output_buffer()
        
        # Send a test command
        test_command = {"T": 1001}
        ser.write((json.dumps(test_command) + '\n').encode('utf-8'))
        print(f"Sent test command: {test_command}")
        
        # Wait for response
        time.sleep(1)
        
        # Read available data
        if ser.in_waiting > 0:
            raw_data = ser.read(ser.in_waiting)
            print(f"Raw data received: {raw_data}")
            
            # Try to decode
            try:
                decoded = raw_data.decode('utf-8', errors='ignore')
                print(f"Decoded data: {decoded}")
                
                # Try to parse JSON
                lines = decoded.strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            json_data = json.loads(line)
                            print(f"Valid JSON: {json_data}")
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e} for line: {line}")
            except Exception as e:
                print(f"Decode error: {e}")
        else:
            print("No data received")
        
        # Test reading for 10 seconds
        print("\nListening for data for 10 seconds...")
        start_time = time.time()
        while time.time() - start_time < 10:
            if ser.in_waiting > 0:
                raw_data = ser.read(ser.in_waiting)
                try:
                    decoded = raw_data.decode('utf-8', errors='ignore')
                    print(f"Received: {decoded.strip()}")
                except Exception as e:
                    print(f"Decode error: {e}")
            time.sleep(0.1)
        
        ser.close()
        print("Test completed")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_serial_communication()
