#!/usr/bin/env python3
"""UPS HAT (E): soft-poweroff when USB-C input is lost; arm MCU auto-wake."""

import os
import sys
import time

from smbus2 import SMBus

MCU_ADDR = 0x2D
MCU_BOOT_REG = 0x01
MCU_BOOT_ENABLE = 0x55

STATE_REG = 0x02
VBUS_REG = 0x10

VBUS_OK_MV = 4000
POLL_SEC = 1
LOST_COUNT = 3  # ~3s debounce


def read_vbus_mv(bus: SMBus) -> int:
    data = bus.read_i2c_block_data(MCU_ADDR, VBUS_REG, 2)
    return data[0] | (data[1] << 8)


def read_state(bus: SMBus) -> int:
    return bus.read_i2c_block_data(MCU_ADDR, STATE_REG, 1)[0]


def usb_present(bus: SMBus) -> bool:
    """True when HAT Type-C input looks powered."""
    vbus = read_vbus_mv(bus)
    state = read_state(bus)
    charging = bool(state & 0xC0)  # charging / fast charging
    return vbus >= VBUS_OK_MV or charging


def arm_autoboot(bus: SMBus) -> None:
    """Arm MCU wake-on-power. Call only immediately before poweroff."""
    bus.write_byte_data(MCU_ADDR, MCU_BOOT_REG, MCU_BOOT_ENABLE)


def main() -> None:
    print("[UPS] HAT (E) power-loss monitor starting", flush=True)
    try:
        bus = SMBus(1)
    except OSError as e:
        print(f"[UPS] cannot open I2C bus 1: {e}", file=sys.stderr, flush=True)
        sys.exit(1)

    lost = 0
    try:
        while True:
            try:
                ok = usb_present(bus)
            except OSError as e:
                print(f"[UPS] I2C read failed: {e}", file=sys.stderr, flush=True)
                time.sleep(POLL_SEC)
                continue

            if ok:
                if lost:
                    print("[UPS] USB-C input restored", flush=True)
                lost = 0
            else:
                lost += 1
                print(f"[UPS] USB-C input lost ({lost}/{LOST_COUNT})", flush=True)

            if lost >= LOST_COUNT:
                print("[UPS] arming MCU auto-boot, then poweroff", flush=True)
                try:
                    arm_autoboot(bus)
                except OSError as e:
                    print(f"[UPS] failed to arm MCU: {e}", file=sys.stderr, flush=True)
                bus.close()
                os.system("poweroff")
                sys.exit(0)

            time.sleep(POLL_SEC)
    finally:
        try:
            bus.close()
        except Exception:
            pass


if __name__ == "__main__":
    main()
