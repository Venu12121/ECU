import serial
import time
import numpy as np
from scipy.signal import savgol_filter

# Initializes serial connection to ECU
ecu_port = 'COM3'  #  ECU's serial port
baud_rate = 115200
ser = serial.Serial(ecu_port, baud_rate, timeout=1)

def read_data():
    data = {}
    if ser.in_waiting:
        line = ser.readline().decode('utf-8').rstrip()
        parts = line.split(',')
        data['rpm'] = float(parts[0])
        data['temperature'] = float(parts[1])
        data['throttle'] = float(parts[2])
    return data

def write_data(throttle, fuel_injection, ignition_timing):
    command = f"{throttle},{fuel_injection},{ignition_timing}\n"
    ser.write(command.encode())

def smooth_data(data, window_size=51, poly_order=3):
    return savgol_filter(data, window_size, poly_order)

def optimize_engine_params(rpm, throttle, temperature):
    fuel_injection = 0
    ignition_timing = 0
    if rpm > 6000:
        throttle = max(0, throttle - 5)
        ignition_timing -= 2
    elif temperature > 90:
        throttle = max(0, throttle - 2)
        fuel_injection -= 1
    else:
        throttle = min(100, throttle + 1)
        fuel_injection += 1
    return throttle, fuel_injection, ignition_timing

# Main loop for real-time monitoring and control
while True:
    data = read_data()
    if data:
        rpm = data['rpm']
        temperature = data['temperature']
        throttle = data['throttle']
        
        throttle, fuel_injection, ignition_timing = optimize_engine_params(rpm, throttle, temperature)
        
        write_data(throttle, fuel_injection, ignition_timing)
        
    time.sleep(0.1)
