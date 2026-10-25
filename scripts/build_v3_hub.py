#!/usr/bin/env python3
"""Build the PSM V3 hub: one PCA9548A, four tile ports, host I2C header."""
import os, pcbnew
MM=pcbnew.FromMM
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB=os.path.join(BASE,'hardware','libraries','psm.pretty')
OUT=os.path.join(BASE,'hardware','psm-v3','hub')
BOARD=os.path.join(OUT,'psm-v3-hub.kicad_pcb'); DSN=os.path.join(OUT,'psm-v3-hub.dsn')
W,H=60.0,40.0

b=pcbnew.BOARD(); ds=b.GetDesignSettings()
ds.SetBoardThickness(MM(1.6)); ds.m_MinClearance=MM(0.15); ds.m_TrackMinWidth=MM(0.12)
ds.m_ViasMinSize=MM(0.60); ds.m_ViasMinAnnularWidth=MM(0.15); ds.m_CopperEdgeClearance=MM(0.30)
b.SetCopperLayerCount(2)
for a,c in [((0,0),(W,0)),((W,0),(W,H)),((W,H),(0,H)),((0,H),(0,0))]:
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(c[0]),MM(c[1])))
    s.SetLayer(pcbnew.Edge_Cuts); s.SetWidth(MM(0.1)); b.Add(s)

nets={}
def net(name):
    if name not in nets:
        n=pcbnew.NETINFO_ITEM(b,name); b.Add(n); nets[name]=n
    return nets[name]
for n in ['GND','3V3','SDA','SCL','INT_N','MUX_RST','LED_A']:
    net(n)
for i in range(4):
    net(f'SDA_C{i}'); net(f'SCL_C{i}')

def place(libname,ref,value,x,y,angle=0.0,footprint=None):
    fp=pcbnew.FootprintLoad(LIB,footprint or libname)
    fp.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y)))
    if angle: fp.SetOrientationDegrees(angle)
    pads=list(fp.Pads())
    if pads:
        xs=[p.GetPosition().x for p in pads]; ys=[p.GetPosition().y for p in pads]
        fp.Move(pcbnew.VECTOR2I(MM(x)-(min(xs)+max(xs))//2, MM(y)-(min(ys)+max(ys))//2))
    fp.SetReference(ref); fp.SetValue(value)
    fp.Reference().SetPosition(pcbnew.VECTOR2I(MM(x),MM(y-3.6))); fp.Reference().SetLayer(pcbnew.F_Fab)
    fp.Value().SetPosition(pcbnew.VECTOR2I(MM(x),MM(y+3.6))); fp.Value().SetLayer(pcbnew.F_Fab)
    b.Add(fp); return fp
def p(fp,n): return fp.FindPadByNumber(str(n))
def conn(fp,mapping):
    for n,name in mapping.items(): p(fp,n).SetNet(net(name))

# mux
u1=place('TSSOP-24_4.4x7.8mm_P0.65mm','U1','PCA9548A',18.0,20.0,0.0)
conn(u1,{1:'GND',2:'GND',3:'MUX_RST',12:'GND',21:'GND',22:'SCL',23:'SDA',24:'3V3'})
# channels 0..3 -> tile ports J2..J5
ch=[(4,5),(6,7),(8,9),(10,11)]
for i,(sd,sc) in enumerate(ch):
    p(u1,sd).SetNet(net(f'SDA_C{i}')); p(u1,sc).SetNet(net(f'SCL_C{i}'))

# host header
j1=place('PinHeader_2x05_P2.54mm_Vertical','J1','HOST_IF',10.0,31.0,90.0)
conn(j1,{1:'3V3',2:'GND',3:'SDA',4:'SCL',5:'INT_N',6:'MUX_RST',8:'GND'})

# tile ports
ports=[]
for i,y in enumerate([8.0,17.0,26.0,35.0]):
    j=place('PinHeader_1x06_P1.27mm_Vertical',f'J{i+2}',f'TILE_{i}',55.0,y,0.0)
    conn(j,{1:'3V3',2:'GND',3:f'SDA_C{i}',4:f'SCL_C{i}',5:'INT_N'})
    ports.append(j)

# ESD array on upstream I2C (USBLC6-2SC6: 1/6 SDA, 3/4 SCL, 2 GND, 5 VDD)
u2=place('SOT-23-6','U2','USBLC6-2SC6',30.0,34.5,0.0)
conn(u2,{1:'SDA',2:'GND',3:'SCL',4:'SCL',5:'3V3',6:'SDA'})

# pull-ups / reset / LED
r1=place('R_0603_1608Metric','R1','2.2k',30.0,25.0); conn(r1,{1:'3V3',2:'SDA'})
r2=place('R_0603_1608Metric','R2','2.2k',35.0,25.0); conn(r2,{1:'3V3',2:'SCL'})
r3=place('R_0603_1608Metric','R3','10k',30.0,30.0); conn(r3,{1:'3V3',2:'MUX_RST'})
r4=place('R_0603_1608Metric','R4','10k',35.0,30.0); conn(r4,{1:'3V3',2:'INT_N'})
r5=place('R_0603_1608Metric','R5','1k',40.0,34.5); conn(r5,{1:'3V3',2:'LED_A'})
d1=place('LED_0603_1608Metric','D1','POWER',45.0,34.5); conn(d1,{1:'GND',2:'LED_A'})

# decoupling
c1=place('C_0603_1608Metric','C1','100n',18.0,14.0); conn(c1,{1:'3V3',2:'GND'})
c2=place('C_0805_2012Metric','C2','10u',23.0,14.0); conn(c2,{1:'3V3',2:'GND'})
c3=place('C_0603_1608Metric','C3','100n',30.0,28.0); conn(c3,{1:'3V3',2:'GND'})
for i,y in enumerate([8.0,17.0,26.0,35.0]):
    c=place('C_0603_1608Metric',f'C{i+4}','100n',48.0,y); conn(c,{1:'3V3',2:'GND'})

# test points
for ref,x,name in [('TP1',20.0,'3V3'),('TP2',24.0,'GND'),('TP3',28.0,'SDA'),
                   ('TP4',32.0,'SCL'),('TP5',36.0,'INT_N'),('TP6',40.0,'MUX_RST')]:
    tp=place('TestPoint_Pad_D1.5mm',ref,name,x,3.0); conn(tp,{1:name})

# mounting holes
for ref,x,y in [('H1',3.0,3.0),('H2',3.0,20.0)]:
    fp=pcbnew.FootprintLoad(LIB,'MountingHole_3.2mm_M3')
    fp.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y))); fp.SetReference(ref); fp.SetValue('M3')
    fp.Reference().SetVisible(False); b.Add(fp)

# gasket guide
for a,c in [((1.5,1.5),(58.5,1.5)),((58.5,1.5),(58.5,38.5)),((58.5,38.5),(1.5,38.5)),((1.5,38.5),(1.5,1.5))]:
    s=pcbnew.PCB_SHAPE(b); s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(pcbnew.VECTOR2I(MM(a[0]),MM(a[1]))); s.SetEnd(pcbnew.VECTOR2I(MM(c[0]),MM(c[1])))
    s.SetLayer(pcbnew.Dwgs_User); s.SetWidth(MM(0.2)); b.Add(s)

def text(txt,x,y,size=1.4,layer=pcbnew.F_SilkS):
    t=pcbnew.PCB_TEXT(b); t.SetText(txt); t.SetPosition(pcbnew.VECTOR2I(MM(x),MM(y)))
    t.SetLayer(layer); t.SetTextSize(pcbnew.VECTOR2I(MM(size),MM(size))); t.SetTextThickness(MM(size*0.15)); b.Add(t)
text('PSM V3 HUB',30.0,1.0,1.3)
text('PCA9548A 0x70  /  4 TILE PORTS',30.0,38.7,1.1)
text('3V3 ONLY - GASKET / CONFORMAL COAT',30.0,20.0,0.8,pcbnew.F_Fab)

os.makedirs(OUT,exist_ok=True)
pcbnew.SaveBoard(BOARD,b); pcbnew.ExportSpecctraDSN(b,DSN)
print('saved',BOARD); print('exported',DSN); print('footprints',len(b.GetFootprints()),'nets',b.GetNetCount())
