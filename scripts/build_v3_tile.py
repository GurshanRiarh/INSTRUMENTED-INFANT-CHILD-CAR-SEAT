#!/usr/bin/env python3
"""Build the PSM V3 sensor tile: 4x VCNL4030X01 on a 30 x 30 mm flex tile."""
import os, pcbnew
MM = pcbnew.FromMM
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(BASE, "hardware", "libraries", "psm.pretty")
OUT = os.path.join(BASE, "hardware", "psm-v3", "tile")
BOARD = os.path.join(OUT, "psm-v3-tile.kicad_pcb")
DSN = os.path.join(OUT, "psm-v3-tile.dsn")

W = H = 30.0
board = pcbnew.BOARD()
ds = board.GetDesignSettings()
ds.SetBoardThickness(MM(0.2))
ds.m_MinClearance = MM(0.15)
ds.m_TrackMinWidth = MM(0.12)
ds.m_ViasMinSize = MM(0.60)
ds.m_ViasMinAnnularWidth = MM(0.15)
ds.m_CopperEdgeClearance = MM(0.30)
board.SetCopperLayerCount(2)

for a,b in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
    s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]),MM(b[1])))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); board.Add(s)

nets={}
def net(name):
    if name not in nets:
        n=pcbnew.NETINFO_ITEM(board,name); board.Add(n); nets[name]=n
    return nets[name]
for n in ["GND","3V3","SDA","SCL","INT_N","NC"]:
    net(n)
for i in range(1,5):
    net(f"IR_K{i}")

def place(libname, ref, value, x, y, angle=0.0, footprint=None):
    fp=pcbnew.FootprintLoad(LIB, footprint or libname)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y)))
    if angle: fp.SetOrientationDegrees(angle)
    pads=list(fp.Pads())
    if pads:
        xs=[p.GetPosition().x for p in pads]; ys=[p.GetPosition().y for p in pads]
        fp.Move(pcbnew.VECTOR2I(MM(x)-(min(xs)+max(xs))//2, MM(y)-(min(ys)+max(ys))//2))
    fp.SetReference(ref); fp.SetValue(value)
    fp.Reference().SetPosition(pcbnew.VECTOR2I(MM(x),MM(y-3.0)))
    fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetPosition(pcbnew.VECTOR2I(MM(x),MM(y+3.0)))
    fp.Value().SetLayer(pcbnew.F_Fab)
    board.Add(fp); return fp

def p(fp,n): return fp.FindPadByNumber(str(n))
def conn(fp,mapping):
    for n,name in mapping.items(): p(fp,n).SetNet(net(name))

# 2x2 sensor grid, 12.7 mm pitch
coords=[8.65,21.35]
addr=["0x60","0x51","0x40","0x41"]
idx=1
for y in coords:
    for x in coords:
        u=place("VCNL4030X01",f"U{idx}",f"VCNL4030X01 {addr[idx-1]}",x,y)
        conn(u,{1:"3V3",2:"SCL",3:"GND",4:"3V3",5:f"IR_K{idx}",6:f"IR_K{idx}",7:"INT_N",8:"SDA"})
        idx+=1

# VDD decoupling
for i,(x,y) in enumerate([(8.65,8.65),(21.35,8.65),(8.65,21.35),(21.35,21.35)],1):
    c=place("C_0603_1608Metric",f"C{i}","100n",x,y+3.8)
    conn(c,{1:"3V3",2:"GND"})
# IR anode decoupling
for i,(x,y) in enumerate([(12.5,8.65),(25.2,8.65),(11.5,23.0),(25.2,21.35)],1):
    c=place("C_0603_1608Metric",f"C{i+4}","100n",x,y)
    conn(c,{1:"3V3",2:"GND"})
c9=place("C_0805_2012Metric","C9","22u",15.0,20.0)
conn(c9,{1:"3V3",2:"GND"})

# optional local I2C pull-ups (10k) and INT pull-up
r1=place("R_0603_1608Metric","R1","10k",15.0,17.5); conn(r1,{1:"3V3",2:"SDA"})
r2=place("R_0603_1608Metric","R2","10k",15.0,15.5); conn(r2,{1:"3V3",2:"SCL"})
r3=place("R_0603_1608Metric","R3","10k",15.0,13.5); conn(r3,{1:"3V3",2:"INT_N"})

# tile connector: 3V3, GND, SDA, SCL, INT, NC
j=place("PinHeader_1x06_P1.27mm_Vertical","J1","TILE_IF",15.0,26.0)
conn(j,{1:"3V3",2:"GND",3:"SDA",4:"SCL",5:"INT_N",6:"NC"})

# 2.2 mm mounting holes
for ref,x,y in [("H1",3.0,3.0),("H2",27.0,3.0),("H3",3.0,27.0),("H4",27.0,27.0)]:
    fp=pcbnew.FootprintLoad(LIB,"MountingHole_2.2mm_M2")
    fp.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y))); fp.SetReference(ref); fp.SetValue("M2")
    fp.Reference().SetVisible(False)
    board.Add(fp)

# sealing ring guide on Dwgs.User
def shape_rect(x1,y1,x2,y2,layer,width):
    for a,b in [((x1,y1),(x2,y1)),((x2,y1),(x2,y2)),((x2,y2),(x1,y2)),((x1,y2),(x1,y1))]:
        s=pcbnew.PCB_SHAPE(board); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
        s.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(b[0]),MM(b[1])))
        s.SetLayer(layer); s.SetWidth(MM(width)); board.Add(s)
shape_rect(1.5,1.5,28.5,28.5,pcbnew.Dwgs_User,0.2)

def text(txt,x,y,size=1.0,layer=pcbnew.F_SilkS):
    t=pcbnew.PCB_TEXT(board); t.SetText(txt); t.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y)))
    t.SetLayer(layer); t.SetTextSize(pcbnew.VECTOR2I(MM(size),MM(size))); t.SetTextThickness(MM(size*0.15)); board.Add(t)
text("PSM V3 TILE",15,1.0,1.2)
text("SEAL RING / CONFORMAL COAT",15,28.0,0.9,pcbnew.F_Fab)
text("4x VCNL4030X01  ADDR 0x60/0x51/0x40/0x41",15,15.0,0.7,pcbnew.F_Fab)

os.makedirs(OUT,exist_ok=True)
pcbnew.SaveBoard(BOARD,board); pcbnew.ExportSpecctraDSN(board,DSN)
print("saved",BOARD); print("exported",DSN)
print("footprints",len(board.GetFootprints()),"nets",board.GetNetCount())
