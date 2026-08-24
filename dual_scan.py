#!/usr/bin/env python3
import threading
import serial
import paho.mqtt.client as mqtt

BAUD = 115200
PORTS = [
    "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_BBAUb2A7N12-if00-port0",
    "/dev/serial/by-id/usb-Prolific_Technology_Inc._USB-Serial_Controller_CKALb153608-if00-port0",
]
philosophy_end = 20 #Filosofibøger fra 1 til og med...
debug_toggle = True #print debug beskeder...
send_MQTT = True #send beskeder til MQTT broker...

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC_OUT = "helmerID"
client = None


def mqtt_connect(client, userdata, flags, reason_code, properties):
    if debug_toggle:
        print("mqtt ok", flush=True)


def mqtt_start():
    global client
    try:
        client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
        client.on_connect = mqtt_connect
        client.connect(BROKER, PORT, keepalive=60)
        client.loop_start()
    except Exception as e:
        client = None
        print(f"mqtt start failed: {e}", flush=True)


def mqtt_send(id):
    global client
    if client is None:
        return
    try:
        client.publish(TOPIC_OUT, id, qos=2, retain=False)
        if debug_toggle:
            print("message sendt", flush=True)
    except Exception as e:
        print(f"mqtt send failed: {e}", flush=True)


print(f"""


************************************************
RUNNING dual_scan.py,
debug_toggle mode is {debug_toggle}
send_MQTT is {send_MQTT}
""")
if debug_toggle:
    print("XR[PB/PU###] - PU = picked up, PB = put back\nX001A[BOOL] - 0 is something placed, 1 is something picked up")


def handler(line):
    event = line[3:5]
    tag_id = int(line[5:-1])
    if event == "PB":
        print(tag_id, flush=True)
        if send_MQTT:
            mqtt_send(tag_id)
    elif event == "PU" and tag_id <= philosophy_end:
        print(0, flush=True)
        if send_MQTT:
            mqtt_send(0)


def listen(port):
    name = port.rsplit("_", 1)[-1].split("-")[0]
    try:
        ser = serial.Serial(port, BAUD, timeout=1)
    except (serial.SerialException, OSError) as e:
        print(f"skip {name}: {e}", flush=True)
        return
    print(f"open {name}", flush=True)
    while True:
        try:
            line = ser.readline().decode("ascii", errors="replace").strip()
        except (serial.SerialException, OSError) as e:
            print(f"lost {name}: {e}", flush=True)
            return
        if not line:
            continue
        if debug_toggle:
            print(f"{name} {line}", flush=True)
        if line.startswith("XR["):
            handler(line)


if send_MQTT:
    mqtt_start()

for p in PORTS:
    threading.Thread(target=listen, args=(p,), daemon=True).start()

threading.Event().wait()
