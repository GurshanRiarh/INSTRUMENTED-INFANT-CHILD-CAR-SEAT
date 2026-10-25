# Test plan

This is a bring-up and characterization plan for the PSM hardware. It follows
the thesis experiments where possible. Pass/fail thresholds marked **TBD** must
be fixed after baseline data is collected.

## 1. Visual and continuity

- Inspect for solder bridges, tombstoned parts, and damaged flex.
- Check 3V3-to-GND resistance before power-up (expect > 1 kΩ; no dead short).
- Verify each sensor's VDD and GND pads are continuous.
- Verify the mux address pins: U17 A0/A1/A2 = low; U18 A0 = high, A1/A2 = low.
- Check the header pinout against the table in the README.

## 2. Power-up

- Apply 3.3 V with a current limit (for example 100 mA).
- Measure the 3.3 V rail and the current draw.
- Confirm the V3 hub power LED is on.
- Check that no regulator/part overheats.

## 3. I²C bring-up

Use `firmware/i2c_scan.py` on a Raspberry Pi (or adapt the calls to the Tiva
or ESP32).

V1:

1. Scan the upstream bus; expect **0x70** and **0x71** only.
2. For each mux, select channels 0–7 one at a time.
3. On each selected channel, expect **0x13** (VCNL4020).
4. Read the VCNL4020 product ID / proximity registers and confirm a changing
   value when a hand approaches the sensor.

V3:

1. Scan the hub bus; expect **0x70**.
2. Select mux channels 0–3, one per tile.
3. On a tile channel, expect **0x60, 0x51, 0x40, 0x41** (one per sensor).
4. Confirm that unplugging a tile removes only that channel's devices.

If a channel scans but a sensor does not respond, check the mux channel
selection, the tile cable, and the sensor's address variant.

## 4. Pressure and linearity

Follow the thesis method:

- Place known weights on a hard circular platen over the mat.
- Record 60 s unloaded baseline, then load, then unload.
- Use the mean over a 50 s window after a 5 s settling delay.
- Fit measured pressure vs. applied pressure.

Target: the thesis reported R² = 0.995 over 0.02–0.35 psi with the VCNL4020
Dome prototype. The V3 sensor/silicone combination must be characterized
separately; do not assume the same coefficients.

## 5. Creep, drift, and repeatability

- Short-term: four 1-minute loads with 1/2/5-minute unloaded intervals; compute
  the coefficient of variation.
- Long-term: apply a fixed load for at least 8–11 hours; compute rise time,
  creep, and drift using the thesis definitions:
  - **creep** = long-term change (30 min → end of run)
  - **drift** = short-window variation (for example 1-minute standard
    deviation divided by mean)

## 6. Respiration

- Place the mat under a seated adult's upper back or under the infant manikin.
- Pace breathing with a metronome at 12 and 20 breaths/min.
- Sum the sensor channels (or use a selected subset for a full-body mat).
- Apply a 1 s moving average and peak detection.
- Compare the estimated interval/rate against the metronome.

The thesis used a single adult subject; repeat with multiple participants and
with the manikin before drawing conclusions.

## 7. Thermal and environmental

- V3: compare the AMG8833 skin-temperature trend with a reference thermometer
  on a stable target; check noise and warm-up drift.
- Run the full system for at least 2 hours; log temperature, current, packet
  loss, and resets.
- Test in a stationary vehicle with windows closed/open and with the HVAC on.
- Do not claim core-temperature accuracy from the 8×8 array.

## 8. Flex and connector reliability

- Bend the tile and V1 flex around the expected car-seat radius, repeatedly.
- Inspect for cracked traces, delamination, and connector movement.
- Add strain relief to the cable; do not rely on the header solder joints.
- Run a continuity check after the bend cycles.

## 9. Vehicle test (supervised, stationary first)

- Verify operation from the vehicle USB supply, including engine start.
- Check for brownouts/resets and Wi-Fi/BLE coexistence.
- Test lighting changes, vibration, and cabin temperature.
- Only perform road testing with a second person operating/observing the
  equipment; do not interact with a screen while driving.

## 10. Data logging

For every test record:

- board revision and serial number
- sensor/tile position and address
- firmware/script version
- sample rate and filter settings
- calibration baseline
- reference instrument and its uncertainty
- raw data file and processed result

## Acceptance criteria (initial)

| Quantity | Initial target |
|---|---|
| I²C scan | all expected addresses found |
| V1 pressure linearity | R² ≥ 0.99 over 0.02–0.35 psi (thesis target) |
| Respiration | within ±2 breaths/min of the paced rate after filtering |
| V3 tile continuity | all four sensors respond on their mux channel |
| Long run | 2 h without reset/crash/data loss |
| Flex bend | no continuity loss after the agreed bend cycles |

These are engineering targets, not clinical or safety limits.
