#!/usr/bin/env python3
"""Bring-up scan for the PSM V1 and V3 boards.

Requires smbus2 on the host (Raspberry Pi):
    pip install smbus2

Examples:
    python3 i2c_scan.py --board v1
    python3 i2c_scan.py --board v3 --bus 1
"""
from __future__ import annotations

import argparse
import sys

try:
    from smbus2 import SMBus
except ImportError:  # pragma: no cover
    print("smbus2 is required: pip install smbus2", file=sys.stderr)
    raise

PCA9548A = 0x70
VCNL4020 = 0x13
VCNL4030_VARIANTS = (0x60, 0x51, 0x40, 0x41)


def ack(bus: SMBus, address: int) -> bool:
    try:
        bus.read_byte(address)
        return True
    except OSError:
        return False


def select_channel(bus: SMBus, mux: int, channel: int) -> None:
    bus.write_byte(mux, 1 << channel)


def scan_v1(bus: SMBus) -> int:
    print("PSM V1: muxes 0x70/0x71, sensors at 0x13 on each channel")
    missing = 0
    for mux in (0x70, 0x71):
        if not ack(bus, mux):
            print(f"  mux 0x{mux:02X}: NOT FOUND")
            missing += 1
            continue
        print(f"  mux 0x{mux:02X}: found")
        for ch in range(8):
            select_channel(bus, mux, ch)
            ok = ack(bus, VCNL4020)
            print(f"    ch{ch}: 0x{VCNL4020:02X} {'ok' if ok else 'MISSING'}")
            missing += 0 if ok else 1
    return missing


def scan_v3(bus: SMBus, mux: int = PCA9548A) -> int:
    print(f"PSM V3: mux 0x{mux:02X}, tiles on channels 0-3")
    if not ack(bus, mux):
        print(f"  mux 0x{mux:02X}: NOT FOUND")
        return 1
    missing = 0
    for ch in range(4):
        select_channel(bus, mux, ch)
        found = []
        for addr in VCNL4030_VARIANTS:
            if ack(bus, addr):
                found.append(f"0x{addr:02X}")
        print(f"  tile ch{ch}: {', '.join(found) if found else 'no sensors'}")
        missing += 4 - len(found)
    return missing


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", choices=("v1", "v3"), required=True)
    ap.add_argument("--bus", type=int, default=1)
    ap.add_argument("--mux", type=lambda x: int(x, 0), default=PCA9548A)
    args = ap.parse_args()

    with SMBus(args.bus) as bus:
        missing = scan_v1(bus) if args.board == "v1" else scan_v3(bus, args.mux)
    print(f"\nmissing devices: {missing}")
    return 0 if missing == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
