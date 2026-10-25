# Firmware bring-up

`i2c_scan.py` is a minimal Raspberry Pi bring-up script for the PSM boards.
It does not implement sensing, calibration, filtering, or the BLE/app stack.

## Requirements

- Raspberry Pi with I²C enabled (`raspi-config` → Interface Options → I2C).
- `smbus2` (`pip install smbus2`).
- The PSM board connected to the Pi's I²C bus (3.3 V logic).

## V1

```bash
python3 i2c_scan.py --board v1 --bus 1
```

Expected: muxes 0x70 and 0x71, and sensor 0x13 on every one of their eight
channels.

## V3

```bash
python3 i2c_scan.py --board v3 --bus 1
```

Expected: mux 0x70 and the four tile addresses 0x60/0x51/0x40/0x41 on each of
channels 0–3.

## Next firmware steps

- Configure the VCNL4020/VCNL4030X01 proximity parameters (current, averaging,
  integration time).
- Timestamp samples and stream them over the chosen transport (MQTT, BLE, or a
  local log).
- Implement the calibration, filtering, respiration/heart-rate estimation,
  and quality flags described in the proposal.
- Log raw and processed data separately; label inferences as inferences.
