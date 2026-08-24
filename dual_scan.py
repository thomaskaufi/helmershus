#!/usr/bin/env python3
import threading
import serial

BAUD = 115200
PORTS = [
    "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_BBAUb2A7N12-if00-port0",
    "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CKALb153608-if00-port0",
]


def listen(port):
    name = port.rsplit("_", 1)[-1].split("-")[0]
    ser = serial.Serial(port, BAUD, timeout=1)
    print(f"open {name}", flush=True)
    while True:
        line = ser.readline().decode("ascii", errors="replace").strip()
        if line:
            print(f"{name} {line}", flush=True)


for p in PORTS:
    threading.Thread(target=listen, args=(p,), daemon=True).start()

threading.Event().wait()
