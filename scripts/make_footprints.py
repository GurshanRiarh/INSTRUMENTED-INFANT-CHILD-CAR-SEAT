import pcbnew
import os, math

MM = pcbnew.FromMM
LIB = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "hardware", "libraries", "psm.pretty")

def new_fp(name, descr, tags, attr=pcbnew.FP_SMD):
    fp = pcbnew.FOOTPRINT(None)
    fp.SetFPID(pcbnew.LIB_ID("psm", name))
    fp.SetReference("REF**")
    fp.SetValue(name)
    fp.SetAttributes(attr)
    fp.SetLibDescription(descr)
    fp.SetKeywords(tags)
    fp.SetLayer(pcbnew.F_Cu)
    return fp

def add_pad(fp, number, x, y, w, h, shape=pcbnew.PAD_SHAPE_RECT, drill=None, layers=None, roundrect=0.0):
    p = pcbnew.PAD(fp)
    p.SetNumber(str(number))
    p.SetShape(shape)
    p.SetSize(pcbnew.VECTOR2I(MM(w), MM(h)))
    p.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    if shape == pcbnew.PAD_SHAPE_ROUNDRECT:
        p.SetRoundRectRadiusRatio(roundrect)
    if drill is not None:
        p.SetDrillSize(pcbnew.VECTOR2I(MM(drill[0]), MM(drill[1])))
        p.SetAttribute(pcbnew.PAD_ATTRIB_PTH)
        p.SetLayerSet(pcbnew.LSET.AllCuMask() | pcbnew.LSET.AllTechMask())
    else:
        p.SetAttribute(pcbnew.PAD_ATTRIB_SMD)
        ls = pcbnew.LSET()
        ls.AddLayer(pcbnew.F_Cu); ls.AddLayer(pcbnew.F_Paste); ls.AddLayer(pcbnew.F_Mask)
        p.SetLayerSet(ls)
    fp.Add(p)
    return p

def line(fp, x1,y1,x2,y2, layer=pcbnew.F_SilkS, width=0.12):
    s = pcbnew.PCB_SHAPE(fp)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(x1), MM(y1)))
    s.SetEnd(pcbnew.VECTOR2I(MM(x2), MM(y2)))
    s.SetLayer(layer)
    s.SetWidth(MM(width))
    fp.Add(s)

def rect(fp, x1,y1,x2,y2, layer=pcbnew.F_SilkS, width=0.12):
    line(fp,x1,y1,x2,y1,layer,width); line(fp,x2,y1,x2,y2,layer,width)
    line(fp,x2,y2,x1,y2,layer,width); line(fp,x1,y2,x1,y1,layer,width)

def text(fp, txt, x, y, layer=pcbnew.F_SilkS, size=1.0, thick=0.15):
    t = pcbnew.PCB_TEXT(fp)
    t.SetText(txt)
    t.SetPosition(pcbnew.VECTOR2I(MM(x), MM(y)))
    t.SetLayer(layer)
    t.SetTextSize(pcbnew.VECTOR2I(MM(size), MM(size)))
    t.SetTextThickness(MM(thick))
    fp.Add(t)

def vcnl4020():
    fp = new_fp("VCNL4020", "Vishay VCNL4020 IR proximity/ambient light sensor, 4.9x2.4x0.83 mm, 10-pad VDFN", "VCNL4020 proximity IR sensor")
    # 5 pads per side, 0.685 mm pitch, row spacing 1.6 mm, pad 0.65 x 0.45 mm
    xs = [-1.37 + i*0.685 for i in range(5)]
    for i,x in enumerate(xs):
        add_pad(fp, i+1, x, -0.8, 0.40, 0.80)
    for i,x in enumerate(xs):
        add_pad(fp, 10-i, x, 0.8, 0.40, 0.80)
    rect(fp, -2.70, -1.50, 2.70, 1.50, layer=pcbnew.F_Fab)
    # pin 1 marker stays on silk, outside the pads
    line(fp, -2.95, -1.75, -2.35, -1.15)
    text(fp, "VCNL4020", 0, 1.8, layer=pcbnew.F_Fab, size=0.8, thick=0.12)
    return fp

def vcnl4030():
    fp = new_fp("VCNL4030X01", "Vishay VCNL4030X01 IR proximity/ambient light sensor, 4.0x2.36x0.75 mm, 8-pad QFN + EP", "VCNL4030X01 proximity IR sensor")
    xs = [-0.975 + i*0.65 for i in range(4)]
    for i,x in enumerate(xs):
        add_pad(fp, i+1, x, -0.9, 0.40, 0.70)
    for i,x in enumerate(xs):
        add_pad(fp, 8-i, x, 0.9, 0.40, 0.70)
    rect(fp, -2.25, -1.45, 2.25, 1.45, layer=pcbnew.F_Fab)
    line(fp, -2.50, -1.70, -1.95, -1.15)
    text(fp, "VCNL4030X01", 0, 1.75, layer=pcbnew.F_Fab, size=0.75, thick=0.12)
    return fp

for fn, obj in [("VCNL4020", vcnl4020()), ("VCNL4030X01", vcnl4030())]:
    path = os.path.join(LIB, fn + ".kicad_mod")
    io = pcbnew.PCB_IO_KICAD_SEXPR()
    io.FootprintSave(path, obj)
    print("saved", path)
