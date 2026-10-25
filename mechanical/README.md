# Mechanical / silicone notes

`tile_mold.scad` is a parametric OpenSCAD starting point for a 2×2 silicone
dome mold matching the 30 mm V3 tile. It is not a validated mold.

## What the mold does

- Four spherical/domed cavities at the V3 sensor pitch (12.7 mm).
- A shallow tray to contain the silicone.
- A handling rim and a label boss.

## What it does not do

- It does not model the exact optical cavity shape from Selzler's thesis.
- It does not include a vacuum chamber, vacuum port, or degassing fixture.
- It does not model the PCB sealing ring, sensor package height, or adhesive
  bond line.

## Suggested process

1. Print/machine the mold in a material compatible with Ecoflex 00-50
   (SLA/rigid resin or machined aluminum; polish the cavity surfaces).
2. Mix Ecoflex 00-50 Parts A and B 1:1 by weight, slowly.
3. Vacuum degas the mixture until bubble evolution stops (roughly −90 kPa for
   a few minutes). Do not cure in the vacuum chamber.
4. Pour the black wall layer first, cure, then pour the white reflective
   ceiling layer. Cure fully.
5. Demold and inspect for bubbles, flash, and incomplete fill.
6. Bond to the PCB with a thin silicone adhesive, aligning each cavity to its
   sensor. Keep adhesive out of the optical path.
7. Measure the optical response and pressure linearity; compare against the
   thesis baseline.

The thesis identified trapped air bubbles and relative movement between the
silicone layer and the PCB as repeatability problems. Vacuum degassing and a
permanent bond address those issues but must be validated experimentally.

## Safety

Use silicone and solvents according to their SDS. Vacuum chambers and
pressurized equipment must be operated by trained personnel. Do not use the
mold or silicone near the infant until fully cured and cleaned.
