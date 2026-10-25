# Fabrication and assembly notes

These notes are a starting point for a prototype build. They are not a
qualified manufacturing specification. Confirm all dimensions, stack-ups, and
process compatibility with the fabricator before ordering.

## PSM V1 — 4×4 flexible mat

| Item | Suggested value |
|---|---|
| Size | 101.6 × 101.6 mm |
| Substrate | 0.2 mm polyimide (flex), 2-layer |
| Copper | 1 oz (35 µm) both sides |
| Surface finish | ENIG |
| Coverlay | Polyimide coverlay, openings over sensor pads and connector |
| Min trace / clearance | 0.12 mm / 0.15 mm (design rules) |
| Vias | 0.30 mm drill / 0.60 mm pad, through |
| Via treatment | Tent + plug (request in fab notes) |
| Stiffeners | 0.8–1.6 mm FR4 behind J1 and U17/U18 for connector/mux reliability |
| Assembly | Lead-free SMT; low-temperature profile for flex |
| Silkscreen | F.Silkscreen only |

The 4×4 sensor grid is at 25.4 mm pitch. The silicone cavity layer must clear
the sensor packages and the passives placed in the gaps. The V1 board is a
reconstruction; verify the dome pitch and cavity diameter against the
original hardware before making the mold.

## PSM V3 — sensor tile

| Item | Suggested value |
|---|---|
| Size | 30 × 30 mm |
| Substrate | 0.2 mm polyimide flex, 2-layer |
| Copper | 1 oz |
| Finish | ENIG |
| Min trace / clearance | 0.12 mm / 0.15 mm |
| Vias | 0.30/0.60 mm, tent + plug |
| Sealing | 1.5 mm sealing-ring guide on `Dwgs.User`; gasket or silicone seal |
| Coating | Conformal coat both sides; mask sensor optical apertures and connector contacts |
| Connector | 1×6, 1.27 mm header (prototype); replace with keyed/sealed connector for vehicle use |
| Mounting | Four 2.2 mm holes; use soft washers or a compliant gasket |

The V3 tile has four VCNL4030X01 sensors at 0x60/0x51/0x40/0x41. The four
order codes are different factory address options, not a substitution.

## PSM V3 — hub

| Item | Suggested value |
|---|---|
| Size | 60 × 40 mm |
| Substrate | 1.6 mm FR4, 2-layer |
| Finish | ENIG |
| Min trace / clearance | 0.12 mm / 0.15 mm |
| Vias | 0.30/0.60 mm, tent + plug |
| Sealing | Gasket outline on `Dwgs.User`; conformal coat |
| Connectors | 1×6, 1.27 mm tile ports; 2×5, 2.54 mm host header |
| Mounting | Two M3 holes |

The hub has one PCA9548A at 0x70, an ESD array on SDA/SCL, 2.2 kΩ upstream
pull-ups, and 10 kΩ reset/INT pull-ups. The four tile ports use mux channels
0–3. Channels 4–7 are spare.

## Silicone cavity layer

The thesis used Smooth-On **Ecoflex 00-50** silicone with black cavity walls
and a white reflective ceiling. The following process is a starting point:

1. Mix Parts A and B by weight according to the datasheet (1:1 for Ecoflex
   00-50). Mix slowly to limit air entrainment.
2. Vacuum degas the mixed silicone in a vacuum chamber. Pull vacuum until the
   foam collapses and bubble evolution stops (typically a few minutes at
   roughly −90 kPa). Do not let the silicone cure in the chamber.
3. Pour the black silicone into the mold first to form the cavity walls.
   Cure according to the datasheet.
4. Pour the white silicone over the cured black layer to form the reflective
   ceiling. Cure fully.
5. Demold. Inspect each cavity for bubbles, flash, and incomplete fill.
6. Bond the silicone layer to the PCB with a thin, uniform silicone adhesive
   (for example Sil-Poxy or a compatible addition-cure silicone). Align each
   cavity to its sensor. Avoid adhesive in the optical path.
7. Cure, then measure the optical response and pressure linearity. Reject
   tiles with a shifted cavity or a visible bubble in the ceiling.

`mechanical/tile_mold.scad` is a parametric 2×2 mold. It is a starting point,
not a validated mold: adjust the dome diameter, depth, wall thickness, and
venting for the actual silicone and sensor package. A production mold should
be machined or SLA-printed with a smooth optical surface and a proper vacuum
port/degassing procedure.

## Waterproofing

The following measures are implemented or specified:

- Sealing-ring guide on the tile and hub (`Dwgs.User`).
- Ground ring and via tenting/plugging options in the board settings.
- ENIG finish (flat, corrosion-resistant).
- Conformal-coat instructions with optical-aperture masking.
- Recommendation to replace prototype headers with keyed, sealed connectors.

These measures do **not** establish an ingress-protection rating. A sealed
enclosure, gasket compression test, and IP test are required before claiming
water resistance.

## Assembly order

1. Inspect bare boards and confirm the stack-up/finish.
2. Solder the sensors first, then passives, then connectors. Use a stencil
   and reflow for the QFN/VDFN parts.
3. Do not ultrasonic-clean the flex boards. Use a no-clean process or a
   controlled wash compatible with the coverlay.
4. Program/verify the I²C addresses before potting or coating.
5. Apply conformal coat with the sensor apertures and connector contacts
   masked.
6. Fit the gasket/sealing ring and test the mechanical fit in the car seat.
7. Record the serial number and the measured baseline values for each tile.

## Safety and certification

The boards are research prototypes. They are **not** certified to CMVSS
213.1, are **not** medical devices, and must not be used as a substitute for a
certified child restraint. Do not modify the seat harness or structural
components. Verify that the added mat thickness does not change harness fit,
and perform a physical fit check before any vehicle use.
