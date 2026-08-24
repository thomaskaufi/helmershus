#!/usr/bin/env python3
import threading
import serial

BAUD = 115200
PORTS = [
    "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_BBAUb2A7N12-if00-port0",
    "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CKALb153608-if00-port0",
]
philosophy_end = 20 #Filosofibøger fra 1 til og med...
DEBUG = True


def handler(line):
    event = line[3:5]
    tag_id = int(line[5:-1])
    if event == "PB":
        print(tag_id, flush=True)
    elif event == "PU" and tag_id <= philosophy_end:
        print(0, flush=True)


def listen(port):
    name = port.rsplit("_", 1)[-1].split("-")[0]
    ser = serial.Serial(port, BAUD, timeout=1)
    print(f"open {name}", flush=True)
    while True:
        line = ser.readline().decode("ascii", errors="replace").strip()
        if not line:
            continue
        if DEBUG:
            print(f"{name} {line}", flush=True)
        if line.startswith("XR["):
            handler(line)


for p in PORTS:
    threading.Thread(target=listen, args=(p,), daemon=True).start()

threading.Event().wait()
