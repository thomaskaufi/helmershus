#!/usr/bin/env python3
import mercury

URI = "tmr://192.168.1.100"  # change to reader IP
REGION = "EU3"
ANTENNA = 1
POWER = 1500  # centi-dBm
WINDOW_MS = 500

reader = mercury.Reader(URI)
reader.set_region(REGION)
reader.set_read_plan([ANTENNA], "GEN2", read_power=POWER)

while True:
    tags = [t.epc.decode() if isinstance(t.epc, bytes) else str(t.epc) for t in reader.read(WINDOW_MS)]
    if tags:
        print(tags)
