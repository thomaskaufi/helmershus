#!/usr/bin/env python3
import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200

ser = serial.Serial(PORT, BAUD, timeout=1)
print(f"Listening on {PORT} @ {BAUD}")

while True:
    line = ser.readline().decode("ascii", errors="replace").strip()
    if line:
        print(line)
