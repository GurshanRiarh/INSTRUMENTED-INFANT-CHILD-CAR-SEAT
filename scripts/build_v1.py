#!/usr/bin/env python3
"""Build the PSM V1 baseline board (Selzler thesis reproduction).

Run inside the KiCad Flatpak:
  flatpak run --command=python3 org.kicad.KiCad scripts/build_v1.py
"""
import os
import pcbnew

MM = pcbnew.FromMM
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(BASE, "hardware", "libraries", "psm.pretty")
OUT = os.path.join(BASE, "hardware", "psm-v1")
BOARD = os.path.join(OUT, "psm-v1.kicad_pcb")
DSN = os.path.join(OUT, "psm-v1.dsn")

W = 101.6  # 4 inches, thesis board
H = 101.6

board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(0.2))          # polyimide flex, prototype
ds.m_MinClearance = MM(0.20)
ds.m_TrackMinWidth = MM(0.12)
ds.m_ViasMinSize = MM(0.60)
ds.m_ViasMinAnnularWidth = MM(0.15)
ds.m_CopperEdgeClearance = MM(0.30)
board.SetCopperLayerCount(2)

# ---------- board outline ----------
def edge(x1, y1, x2, y2):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    s.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
    s.SetLayer(pcbnew.Edge_Cuts)
    s.SetWidth(MM(0.10))
    board.Add(s)

for a, b in [((0, 0), (W, 0)), ((W, 0), (W, H)), ((W, H), (0, H)), ((0, H), (0, 0))]:
    edge(a[0], a[1], b[0], b[1])

# ---------- nets ----------
nets = {}
def net(name):
    if name not in nets:
        n = pcbnew.NETINFO_ITEM(board, name)
        board.Add(n)
        nets[name] = n
    return nets[name]

for name in ["GND", "3V3", "5V", "SDA", "SCL", "INT_N", "MUX_RST"]:
    net(name)
for i in range(1, 17):
    net(f"IR_A{i}")
    net(f"SDA_C{i}")
    net(f"SCL_C{i}")

# ---------- helpers ----------
def place(libname, ref, value, x, y, angle=0.0, footprint=None):
    fp = pcbnew.FootprintLoad(LIB, footprint or libname)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    if angle:
        fp.SetOrientationDegrees(angle)
    # centre the footprint on its pads (headers have origin at pin 1)
    pads = list(fp.Pads())
    if pads:
        xs = [p.GetPosition().x for p in pads]
        ys = [p.GetPosition().y for p in pads]
        cx = (min(xs) + max(xs)) // 2
        cy = (min(ys) + max(ys)) // 2
        fp.Move(pcbnew.VECTOR2I(MM(x) - cx, MM(y) - cy))
    fp.SetReference(ref)
    fp.SetValue(value)
    board.Add(fp)
    # move reference above the part; keep value on fab layer
    fp.Reference().SetPosition(pcbnew.VECTOR2I(MM(x), MM(y - 3.6)))
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetPosition(pcbnew.VECTOR2I(MM(x), MM(y + 3.6)))
    fp.Value().SetLayer(pcbnew.F_Fab)
    return fp

def pad(fp, num):
    p = fp.FindPadByNumber(str(num))
    if p is None:
        raise RuntimeError(f"{fp.GetReference()} has no pad {num}")
    return p

def connects(fp, mapping):
    for num, name in mapping.items():
        pad(fp, num).SetNet(net(name))

# ---------- sensor grid ----------
# 4x4 array, 25.4 mm pitch, centred on a 4" board
coords = [12.7, 38.1, 63.5, 88.9]
sensors = []
idx = 1
for r, y in enumerate(coords):
    for c, x in enumerate(coords):
        u = place("VCNL4020", f"U{idx}", "VCNL4020", x, y, 0.0)
        # pin 1 IR anode -> IR_Ax through 10R; 2 SDA; 3 INT; 4 SCL;
        # 5 VDD 3V3; 8/9 GND; 6/7/10 no connect
        connects(u, {
            1: f"IR_A{idx}", 2: f"SDA_C{idx}", 3: "INT_N",
            4: f"SCL_C{idx}", 5: "3V3", 8: "GND", 9: "GND",
        })
        sensors.append((idx, u, x, y))
        idx += 1

# per-sensor decoupling (100n) and IR anode series resistor (10R)
for i, u, x, y in sensors:
    c = place("C_0603_1608Metric", f"C{i}", "100n", x, y + 5.5, 0.0)
    connects(c, {1: "3V3", 2: "GND"})
    r = place("R_0603_1608Metric", f"R{i}", "10R", x + 5.5, y, 90.0)
    connects(r, {1: "3V3", 2: f"IR_A{i}"})

# ---------- multiplexers ----------
# U17 left edge, U18 right edge. PCA9548A PW/TSSOP-24.
u17 = place("TSSOP-24_4.4x7.8mm_P0.65mm", "U17", "PCA9548A", 5.8, 50.8, 90.0)
u18 = place("TSSOP-24_4.4x7.8mm_P0.65mm", "U18", "PCA9548A", 95.8, 50.8, 90.0)

# common side
for u, a0, a1, a2 in [(u17, 0, 0, 0), (u18, 1, 0, 0)]:
    pad(u, 1).SetNet(net("GND" if a0 == 0 else "3V3"))   # A0
    pad(u, 2).SetNet(net("GND" if a1 == 0 else "3V3"))   # A1
    pad(u, 3).SetNet(net("MUX_RST"))                     # /RESET
    pad(u, 12).SetNet(net("GND"))                        # GND
    pad(u, 21).SetNet(net("GND" if a2 == 0 else "3V3"))  # A2
    pad(u, 22).SetNet(net("SCL"))                        # SCL
    pad(u, 23).SetNet(net("SDA"))                        # SDA
    pad(u, 24).SetNet(net("3V3"))                        # VCC

# channel mapping: U17 ch0..7 -> sensors 1..8; U18 -> 9..16
# PCA9548A pin map: SDn/SCn pairs
ch_pins = [(4, 5), (6, 7), (8, 9), (10, 11), (13, 14), (15, 16), (17, 18), (19, 20)]
for mux, start in [(u17, 1), (u18, 9)]:
    for ch, (sd, sc) in enumerate(ch_pins):
        s = start + ch
        pad(mux, sd).SetNet(net(f"SDA_C{s}"))
        pad(mux, sc).SetNet(net(f"SCL_C{s}"))

# ---------- header / pull-ups / bulk ----------
j1 = place("PinHeader_2x05_P2.54mm_Vertical", "J1", "Tiva_IF", 50.8, 95.0, 0.0)
connects(j1, {1: "3V3", 2: "GND", 3: "SDA", 4: "SCL", 5: "INT_N",
              6: "MUX_RST", 7: "5V", 8: "GND"})

rp1 = place("R_0603_1608Metric", "R17", "4.7k", 28.0, 96.5, 0.0)
connects(rp1, {1: "3V3", 2: "SDA"})
rp2 = place("R_0603_1608Metric", "R18", "4.7k", 33.0, 96.5, 0.0)
connects(rp2, {1: "3V3", 2: "SCL"})
rr = place("R_0603_1608Metric", "R19", "10k", 38.0, 96.5, 0.0)
connects(rr, {1: "3V3", 2: "MUX_RST"})
ri = place("R_0603_1608Metric", "R20", "10k", 68.0, 96.5, 0.0)
connects(ri, {1: "3V3", 2: "INT_N"})
c17 = place("C_0805_2012Metric", "C17", "22u", 18.0, 96.5, 0.0)
connects(c17, {1: "3V3", 2: "GND"})
c18 = place("C_0805_2012Metric", "C18", "22u", 82.0, 96.5, 0.0)
connects(c18, {1: "3V3", 2: "GND"})
c19 = place("C_0603_1608Metric", "C19", "100n", 23.0, 96.5, 0.0)
connects(c19, {1: "3V3", 2: "GND"})
c20 = place("C_0603_1608Metric", "C20", "100n", 78.0, 96.5, 0.0)
connects(c20, {1: "3V3", 2: "GND"})

# test points
for ref, x, name in [("TP1", 8.0, "3V3"), ("TP2", 12.0, "GND"),
                     ("TP3", 86.0, "SDA"), ("TP4", 90.0, "SCL"),
                     ("TP5", 94.0, "INT_N")]:
    tp = place("TestPoint_Pad_D1.5mm", ref, name, x, 92.0, 0.0)
    connects(tp, {1: name})

# mounting holes (NPTH)
for ref, x, y in [("H1", 5.0, 5.0), ("H2", 96.6, 5.0),
                  ("H3", 5.0, 96.6), ("H4", 96.6, 96.6)]:
    fp = pcbnew.FootprintLoad(LIB, "MountingHole_3.2mm_M3")
    fp.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    fp.SetReference(ref)
    fp.SetValue("M3")
    board.Add(fp)

# ---------- silkscreen ----------
def text(txt, x, y, size=2.0, layer=pcbnew.F_SilkS):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(size * 0.15))
    board.Add(t)

text("PSM V1  -  CARLETON 16x VCNL4020", 50.8, 2.2, 2.2)
text("4x4 ARRAY / 25.4 mm PITCH", 50.8, 8.5, 1.4)
text("FLEX 0.2 mm POLYIMIDE - PROTOTYPE", 50.8, 5.0, 1.2, pcbnew.F_Fab)

# ---------- save + DSN ----------
os.makedirs(OUT, exist_ok=True)
pcbnew.SaveBoard(BOARD, board)
pcbnew.ExportSpecctraDSN(board, DSN)
print("saved", BOARD)
print("exported", DSN)
print("footprints", len(board.GetFootprints()), "nets", board.GetNetCount())
