# Hardware projects

| Project | KiCad files | Fabrication |
|---|---|---|
| PSM V1 (thesis baseline) | `psm-v1/psm-v1.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | `psm-v1/fab/` |
| PSM V3 sensor tile | `psm-v3/tile/psm-v3-tile.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | `psm-v3/tile/fab/` |
| PSM V3 hub | `psm-v3/hub/psm-v3-hub.kicad_pro`, `.kicad_sch`, `.kicad_pcb` | `psm-v3/hub/fab/` |

The shared libraries are in `libraries/`:

- `libraries/psm.pretty/` — custom footprints (`VCNL4020`, `VCNL4030X01`) plus
  the standard footprints copied into the project so the boards are
  self-contained.
- `libraries/psm-symbols.kicad_sym` — project symbols used by all three
  schematics.

Each project has its own `fp-lib-table` and `sym-lib-table` with relative
paths, so opening the `.kicad_pro` file is enough.

## Reproducing the boards

The generators are kept in `../scripts/`. They were run inside the KiCad
Flatpak, for example:

```bash
flatpak run --command=python3 org.kicad.KiCad scripts/make_footprints.py
flatpak run --command=python3 org.kicad.KiCad scripts/build_v1.py
# route the exported .dsn with Freerouting, then:
flatpak run --command=python3 org.kicad.KiCad scripts/finish_v1.py
flatpak run --command=python3 org.kicad.KiCad scripts/build_schematic.py
flatpak run --command=python3 org.kicad.KiCad scripts/build_schematic_v3.py
flatpak run --command=python3 org.kicad.KiCad scripts/set_fab_options.py
flatpak run --command=python3 org.kicad.KiCad scripts/export_bom.py
```

Freerouting 2.5.0 was used for routing:

```bash
java -jar freerouting.jar -de psm-v1.dsn -do psm-v1.ses -mp 100 -mt 8
```

The `.dsn`/`.ses` files are intermediates and are not committed. The routed
`.kicad_pcb` files are committed.

## Validation

```bash
kicad-cli pcb drc --severity-all --output drc.rpt psm-v1/psm-v1.kicad_pcb
kicad-cli sch erc --output erc.rpt psm-v1/psm-v1.kicad_sch
kicad-cli pcb drc --severity-all --output drc.rpt psm-v3/tile/psm-v3-tile.kicad_pcb
kicad-cli sch erc --output erc.rpt psm-v3/tile/psm-v3-tile.kicad_sch
kicad-cli pcb drc --severity-all --output drc.rpt psm-v3/hub/psm-v3-hub.kicad_pcb
kicad-cli sch erc --output erc.rpt psm-v3/hub/psm-v3-hub.kicad_sch
```

Current result: 0 DRC violations and 0 unconnected items on all three PCBs;
0 ERC violations on all three schematics; 0 schematic-to-PCB netlist
mismatches (see `docs/validation.md`).

## Fabrication outputs

Each `fab/` folder contains:

- Gerbers: F.Cu, B.Cu, F.Mask, B.Mask, F.Silkscreen, Edge.Cuts
- Excellon drill files (PTH and NPTH)
- Pick-and-place CSV (`*-pos.csv`)
- PDF and SVG previews

*These are prototype files. Review the stack-up notes in
[docs/fabrication.md](../docs/fabrication.md) before ordering.*
