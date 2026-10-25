// Parametric 2x2 silicone dome mold for the PSM V3 tile.
// This is a starting point, not a validated production mold.
// Render with OpenSCAD, then print/machine and polish the cavity surfaces.

$fn = 64;

tile        = 30.0;   // tile size, mm
pitch       = 12.7;   // sensor pitch, mm
edge        = 1.5;    // tray wall thickness, mm
base        = 2.0;    // mold base thickness, mm
dome_d      = 10.0;   // cavity diameter, mm
dome_depth  = 3.0;    // cavity depth, mm
dome_squash = 0.65;   // vertical scale of the spherical cavity
pour_lip    = 3.0;    // extra tray height above the silicone
clearance   = 0.2;    // cavity-to-cavity clearance check

outer = tile + 2*edge;
height = base + dome_depth + pour_lip;

difference() {
    cube([outer, outer, height], center = false);

    // silicone tray cavity
    translate([edge, edge, base])
        cube([tile, tile, height - base + 0.1], center = false);

    // four dome cavities
    for (ix = [0:1]) {
        for (iy = [0:1]) {
            cx = edge + (tile - pitch)/2 + ix*pitch;
            cy = edge + (tile - pitch)/2 + iy*pitch;
            translate([cx, cy, base])
                scale([1, 1, dome_squash])
                    sphere(d = dome_d);
        }
    }
}

// Pour lip / handling rim
translate([0, 0, height])
    difference() {
        cube([outer, outer, 1.2], center = false);
        translate([edge/2, edge/2, -0.1])
            cube([outer - edge, outer - edge, 1.4], center = false);
    }

// Optional label boss (remove or relocate as needed)
translate([outer/2, edge/2, height + 0.2])
    linear_extrude(height = 1.0)
        text("PSM V3 2x2", size = 3.0, halign = "center", valign = "center");
