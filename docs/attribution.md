# Third-party attribution

This repository contains original PCB/schematic/documentation work combined
with standard KiCad library elements and one symbol adapted from an Antmicro
demo. The original thesis and proposal PDFs are not committed.

## KiCad libraries

The custom footprint library `hardware/libraries/psm.pretty/` contains copies
of standard KiCad footprints (resistors, capacitors, headers, mounting holes,
test points, LED, SOT-23-6, TSSOP-24) plus original `VCNL4020` and
`VCNL4030X01` footprints. The standard KiCad footprints are distributed under
the KiCad library license (CC-BY-SA 4.0 with the KiCad library exception).
See <https://www.kicad.org/libraries/license/>.

The V1 schematic uses symbol shapes based on:
- `Connector_Generic:Conn_01x10_MountingPin`, `Device:R`, and `Device:C` from
  the KiCad `cm5_minima` demo/schematic (KiCad libraries).
- A 24-channel I²C switch symbol from the KiCad `jetson-agx-thor-baseboard`
  `csi.kicad_sch` demo, originally `PI4MSD5V9548AZDEX` by Antmicro
  (Apache-2.0). The symbol was renamed and its pin numbers/names were remapped
  to the TI PCA9548A pinout for this project. The original Antmicro metadata
  is retained in the embedded symbol properties for traceability.

## Datasheets and application notes

- Vishay VCNL4020 datasheet, document 83476.
- Vishay VCNL4030X01 datasheet, document 84250.
- Vishay application note "Designing the VCNL4030X01 Into an Application",
  document 84424.
- Texas Instruments PCA9548A datasheet, SCPS143G.
- RSSelzler, M.A.Sc. thesis, Carleton University, 2018.
- Capstone proposal, Instrumented Infant-Child Car Seat, 2026.

## Fonts and tools

The KiCad-generated PDFs use the fonts available to KiCad. The SVG diagrams
use DejaVu Sans (if installed) or the viewer's sans-serif fallback. No font
files are redistributed.
