# Design notes and assumptions

## What was reconstructed

The thesis describes the PSM architecture, sensor type, silicone construction,
metrology experiments, and respiration demonstration. It does **not** include
a complete schematic, netlist, BOM, PCB layout, or mechanical drawing. The V1
KiCad design is therefore a reconstruction from:

- the thesis text (Ch. 3–7),
- the Vishay VCNL4020 datasheet (pinout, package, application circuit),
- the TI PCA9548A datasheet (pinout, address pins, channel mapping),
- the proposal's description of the V1/V2 hardware.

Assumptions that should be checked against the physical V1/V2 hardware:

| Item | Assumption used here | Why |
|---|---|---|
| Sensor pitch | 25.4 mm (1 inch) | 4 sensors on a 4-inch board with even margins; the thesis does not give the pitch. |
| Board outline | 101.6 × 101.6 mm square | Thesis calls the prototype "four by four inches". |
| Mux part | PCA9548A (TSSOP-24) | Thesis says "multiplexer block"; proposal names PCA9548. |
| Mux addresses | 0x70 (U17), 0x71 (U18) | A0 tied low/high; A1/A2 low. |
| VCNL4020 address | 0x13 | Datasheet fixed 7-bit address. |
| IR anode network | 10 Ω series + 100 nF per sensor, 22 µF bulk | Datasheet application circuit. |
| Host connector | 2×5, 2.54 mm | Tiva/LaunchPad-compatible; thesis does not give the connector. |
| Flex stack-up | 0.2 mm polyimide, 2 layers | Thesis calls it a flexible PCB; no stack-up is published. |

## V1 → V3 mapping (Prannav's proposal points)

1. **Sensor replacement.** VCNL4020 is marked "not for new designs" by Vishay.
   V3 uses **VCNL4030X01**, which is AEC-Q101 qualified, has a 16-bit proximity
   channel, and is available in four factory I²C addresses.
2. **Communication architecture.** V1 uses two 8-channel muxes because every
   VCNL4020 is at 0x13. V3 gives each tile four sensors with four distinct
   addresses, so one mux channel serves four sensors. One PCA9548A supports
   four tiles now and up to eight tiles (32 sensors) later.
3. **Mechanical architecture.** V1 is a fixed 4×4 mat. V3 is a set of 2×2
   tiles that can follow the car-seat contour and be replaced individually.
   The tile is 30 × 30 mm; the hub is 60 × 40 mm.
4. **Waterproofing.** The tile carries a 1.5 mm sealing-ring guide on
   `Dwgs.User`, a ground ring, via tenting/plugging, ENIG finish, and a
   conformal-coat note. The hub has a gasket outline. These are design
   measures, not an IP rating.
5. **Silicone manufacturing.** `mechanical/tile_mold.scad` is a parametric
   starting point for a 2×2 dome mold. The process notes call for vacuum
   degassing before pouring; the thesis identified trapped air bubbles as a
   repeatability problem.
6. **KiCad deliverables.** The repository contains editable projects, custom
   libraries, BOMs, Gerbers, drill files, position files, and PDF/SVG
   previews.

## Decisions made to resolve proposal ambiguities

- **One mat vs two mats.** The proposal says one mat on the seat back and
  another on the seat bottom, but also budgets for 16 sensors total. The
  thesis baseline is one 4×4 mat. V1 is therefore **one 4×4 mat**. V3 tiles
  are modular, so a second mat (or additional contour tiles) can be added
  without redesigning the hub; the hub supports up to eight tiles.
- **Alert logic owner.** The PCB does not implement alert logic. The intended
  split is: Raspberry Pi computes fused vitals and quality; the phone owns the
  alert state machine and escalation. This resolves the proposal's
  Pi-vs-phone contradiction at the hardware boundary.
- **Camera roles.** The PSM hardware is independent of the camera split. The
  V1/V3 boards only implement the pressure modality.
- **Calibration baseline.** The PCB does not define the baseline. The test
  plan uses an empty-seat baseline for occupancy and an infant-seated
  comfortable-posture baseline for posture, with a separate per-infant thermal
  baseline.

## Open issues / next steps

- Draw full V3 tile and hub schematics (currently topology diagram + BOM +
  PCB nets).
- Add the VCNL4030X01 exposed pad back for a production thermal design, with a
  stencil and verified clearance.
- Replace the 1.27 mm headers with keyed, sealed connectors for a vehicle
  build.
- Add flex stiffeners and strain relief; run a bend-fatigue test.
- Measure the actual V1/V2 sample rate, I²C rise times, and mux channel
  settling.
- Characterize the silicone dome optical response and pressure linearity with
  the V3 sensor.
- Validate the design against the car-seat harness geometry; the prototype is
  not certified.

## Schematic scope

The V1 schematic is a connection-level drawing: it shows the 16 sensors, the
two muxes, the host header, the 16 IR-anode series resistors, the upstream
pull-ups, and the bulk capacitors. The 16 local 100 nF decoupling capacitors
are omitted from the drawing to keep it readable; they are present in the
PCB and BOM. The PCB is the authoritative netlist for fabrication.
