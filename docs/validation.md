# Validation

## Tools

| Tool | Version |
|---|---|
| KiCad | 10.0.7 (Flatpak) |
| Freerouting | 2.5.0 (JAR, Java 26) |

## Results

| Design | Check | Result | Report |
|---|---|---|---|
| PSM V1 PCB | DRC (`--severity-all`) | **0 violations, 0 unconnected** | `hardware/psm-v1/drc.rpt` |
| PSM V1 schematic | ERC | **0 violations** | `hardware/psm-v1/erc-v1.rpt` |
| PSM V3 tile PCB | DRC (`--severity-all`) | **0 violations, 0 unconnected** | `hardware/psm-v3/tile/drc.rpt` |
| PSM V3 hub PCB | DRC (`--severity-all`) | **0 violations, 0 unconnected** | `hardware/psm-v3/hub/drc.rpt` |

The DRC reports also list KiCad's "ignored checks" (for example, test points
and mounting holes without courtyards). These are informational; no errors or
warnings remain.

## Reproduce

```bash
# V1
kicad-cli pcb drc --severity-all --output hardware/psm-v1/drc.rpt hardware/psm-v1/psm-v1.kicad_pcb
kicad-cli sch erc --output hardware/psm-v1/erc-v1.rpt hardware/psm-v1/psm-v1.kicad_sch

# V3
kicad-cli pcb drc --severity-all --output hardware/psm-v3/tile/drc.rpt hardware/psm-v3/tile/psm-v3-tile.kicad_pcb
kicad-cli pcb drc --severity-all --output hardware/psm-v3/hub/drc.rpt hardware/psm-v3/hub/psm-v3-hub.kicad_pcb
```

## Routing workflow

1. Build the placement and export a Specctra DSN with the Python generators.
2. Route with Freerouting:

   ```bash
   java -jar freerouting.jar -de board.dsn -do board.ses -mp 100 -mt 8
   ```

3. Import the SES session into the board with `pcbnew.ImportSpecctraSES`.
4. Add the GND zone on B.Cu, refill zones, and save.
5. Run DRC. The committed boards are the post-route, zone-filled results.

The autorouter output should still be reviewed for signal integrity, return
paths, flex bend areas, and connector strain relief. DRC does not check those.

## What is not validated

- No fabrication, assembly, or electrical test has been performed.
- No signal-integrity, thermal, vibration, EMC, or flex-fatigue simulation.
- No silicone sample characterization.
- No medical or automotive certification.
