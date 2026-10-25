# Consolidated BOM

Prices and stock are not included. Order codes are the manufacturer part
numbers; verify package and address variant before ordering.

## PSM V1 — thesis baseline

| Qty | References | Value / MPN | Footprint | Notes |
|---:|---|---|---|---|
| 16 | U1–U16 | **VCNL4020-GS08** | `VCNL4020` (4.9 × 2.4 mm, 10-pad) | NRND; use for thesis baseline only |
| 2 | U17, U18 | **PCA9548APW** | `TSSOP-24_4.4x7.8mm_P0.65mm` | 0x70 / 0x71 |
| 18 | C1–C16, C19, C20 | 100 nF, 16 V, X7R, 0603 | `C_0603_1608Metric` | VDD + mux decoupling |
| 16 | R1–R16 | 10 Ω, 1%, 0603 | `R_0603_1608Metric` | IR-anode series |
| 2 | C17, C18 | 22 µF, 10 V, X5R, 0805 | `C_0805_2012Metric` | bulk |
| 2 | R17, R18 | 4.7 kΩ, 0603 | `R_0603_1608Metric` | upstream I²C pull-ups |
| 2 | R19, R20 | 10 kΩ, 0603 | `R_0603_1608Metric` | MUX_RST / INT_N pull-ups |
| 1 | J1 | 2×5, 2.54 mm header | `PinHeader_2x05_P2.54mm_Vertical` | host interface |
| 4 | H1–H4 | M3 mounting hole | `MountingHole_3.2mm_M3` | NPTH |
| 5 | TP1–TP5 | 1.5 mm test pad | `TestPoint_Pad_D1.5mm` | 3V3 / GND / SDA / SCL / INT_N |

PCB: 101.6 × 101.6 mm, 0.2 mm polyimide flex, 2 layers, 1 oz Cu, ENIG,
via tenting/plugging requested, stiffener behind J1 and U17/U18.

## PSM V3 sensor tile

| Qty | References | Value / MPN | Footprint | Notes |
|---:|---|---|---|---|
| 1 | U1 | **VCNL4030X01-GS08** | `VCNL4030X01` (4.0 × 2.36 mm, 8-pad) | 0x60 |
| 1 | U2 | **VCNL40301X01-GS08** | `VCNL4030X01` | 0x51 |
| 1 | U3 | **VCNL40302X01-GS08** | `VCNL4030X01` | 0x40 |
| 1 | U4 | **VCNL40303X01-GS08** | `VCNL4030X01` | 0x41 |
| 8 | C1–C8 | 100 nF, 16 V, X7R, 0603 | `C_0603_1608Metric` | VDD + IR-anode decoupling |
| 1 | C9 | 22 µF, 10 V, X5R, 0805 | `C_0805_2012Metric` | tile bulk |
| 3 | R1–R3 | 10 kΩ, 0603 | `R_0603_1608Metric` | local I²C/INT pull-ups |
| 1 | J1 | 1×6, 1.27 mm header | `PinHeader_1x06_P1.27mm_Vertical` | tile port |
| 4 | H1–H4 | M2 mounting hole | `MountingHole_2.2mm_M2` | NPTH |

PCB: 30 × 30 mm, 0.2 mm polyimide flex, 2 layers, ENIG, sealing ring,
conformal coat. **Four different sensor order codes are required**; they are
the same die with different factory I²C addresses.

## PSM V3 hub

| Qty | References | Value / MPN | Footprint | Notes |
|---:|---|---|---|---|
| 1 | U1 | **PCA9548APW** | `TSSOP-24_4.4x7.8mm_P0.65mm` | 0x70 |
| 1 | U2 | **USBLC6-2SC6** | `SOT-23-6` | ESD protection on SDA/SCL |
| 1 | D1 | green LED, 0603 | `LED_0603_1608Metric` | power indicator |
| 6 | C1, C3–C7 | 100 nF, 16 V, X7R, 0603 | `C_0603_1608Metric` | decoupling |
| 1 | C2 | 10 µF, 10 V, X5R, 0805 | `C_0805_2012Metric` | bulk |
| 2 | R1, R2 | 2.2 kΩ, 0603 | `R_0603_1608Metric` | upstream I²C pull-ups |
| 2 | R3, R4 | 10 kΩ, 0603 | `R_0603_1608Metric` | MUX_RST / INT_N |
| 1 | R5 | 1 kΩ, 0603 | `R_0603_1608Metric` | LED series |
| 4 | J2–J5 | 1×6, 1.27 mm header | `PinHeader_1x06_P1.27mm_Vertical` | tile ports |
| 1 | J1 | 2×5, 2.54 mm header | `PinHeader_2x05_P2.54mm_Vertical` | host interface |
| 6 | TP1–TP6 | 1.5 mm test pad | `TestPoint_Pad_D1.5mm` | 3V3/GND/SDA/SCL/INT/MUX_RST |
| 2 | H1, H2 | M3 mounting hole | `MountingHole_3.2mm_M3` | NPTH |

PCB: 60 × 40 mm, 1.6 mm FR4, 2 layers, ENIG, gasket outline and conformal
coat.

## Assembly notes

- The V3 tile VCNL4030X01 footprint intentionally omits the exposed pad (EP).
  Pin 3 is the electrical GND. For a production thermal design, add an EP with
  a laser-cut stencil and a verified 0.1 mm clearance.
- The V1 VCNL4020 is NRND. Do not start a new production build from the V1
  BOM; use V3 for new work.
- The tile connector and hub connector are simple 1.27 mm pin headers. For a
  wearable/car-seat build, replace them with a keyed, sealed 6-pin connector
  (for example JST SH or an FPC connector) and update the footprint.
