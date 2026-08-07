#!/usr/bin/env python3
import re
import serial

PORT = "/dev/ttyUSB0"
BAUD = 115200

PLACED = re.compile(r"XR\[PB(\d+)\]")
REMOVED = re.compile(r"XR\[PU(\d+)\]")

ser = serial.Serial(PORT, BAUD, timeout=1)

while True:
    line = ser.readline().decode("ascii", errors="replace").strip()
    if not line:
        continue

    placed = PLACED.search(line)
    if placed:
        print(int(placed.group(1)), flush=True)
        continue

    removed = REMOVED.search(line)
    if removed:
        print(0, flush=True)
