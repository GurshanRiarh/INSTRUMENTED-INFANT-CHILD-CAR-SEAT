#!/usr/bin/env python3
"""Build full V3 tile and hub schematics from the shared PSM symbol library."""
import os, copy, uuid, math
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from kiutils.items.schitems import (SchematicSymbol, LocalLabel, SymbolProjectInstance,
    SymbolProjectPath, Connection, NoConnect, Text)
from kiutils.items.common import Position, Stroke, Effects, Font, Justify

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS='/home/zeus/.local/share/flatpak/app/org.kicad.KiCad/x86_64/stable/active/files/share/kicad/demos'
IO=os.path.join(DEMOS,'cm5_minima','IO.kicad_sch')
CSI=os.path.join(DEMOS,'jetson-agx-thor-baseboard','csi.kicad_sch')
LIBFILE=os.path.join(BASE,'hardware','libraries','psm-symbols.kicad_sym')

io=Schematic.from_file(IO)
csi=Schematic.from_file(CSI)
lib=SymbolLib.from_file(LIBFILE)
sym={x.entryName:x for x in lib.symbols}
for x in sym.values(): x.libraryNickname='PSM'

tpl_io=[x for x in io.schematicSymbols if 'Conn_01x10' in x.libId][0]
tpl_mux=[x for x in csi.schematicSymbols if '9548' in str(x.libId)][0]
tpl_r=[x for x in io.schematicSymbols if 'CM5IO:R'==x.libId][0]
tpl_c=[x for x in io.schematicSymbols if 'CM5IO:C'==x.libId][0]
tpl_led=[x for x in io.schematicSymbols if x.libId=='CM5IO:LED'][0]

class Builder:
    def __init__(self,title,rev='V3.0',paper='A2'):
        self.s=copy.deepcopy(io)
        self.s.paper.paperSize=paper
        self.s.titleBlock.title=title
        self.s.titleBlock.company='Carleton University - Instrumented Infant-Child Car Seat'
        self.s.titleBlock.revision=rev
        self.s.titleBlock.comments={}
        self.s.schematicSymbols=[]; self.s.globalLabels=[]; self.s.labels=[]
        self.s.graphicalItems=[]; self.s.junctions=[]; self.s.noConnects=[]
        self.s.busEntries=[]; self.s.hierarchicalLabels=[]; self.s.texts=[]; self.s.textBoxes=[]
        self.s.libSymbols=[]
    def lib(self,name):
        if name not in self.s.libSymbols: self.s.libSymbols.append(sym[name])
        return sym[name]
    def pin_of(self,libsym,num):
        for u in libsym.units:
            for p in u.pins:
                if str(p.number)==str(num): return p
        raise KeyError((libsym.entryName,num))
    def endpoint(self,x,y,pin): return (x+pin.position.X, y-pin.position.Y)
    def outward(self,pin):
        a=pin.position.angle or 0
        return {0:180,90:270,180:0,270:90}.get(a,90)
    def add(self,tpl,libsym,libid,ref,val,x,y,footprint='',ref_dx=-12,ref_dy=-18):
        ss=copy.deepcopy(tpl); ss.uuid=str(uuid.uuid4())
        ss.position=Position(x,y,0); ss.mirror=None; ss.unit=1
        ss.libraryNickname='PSM'; ss.entryName=libid.split(':',1)[1]
        ss.libName=None; ss.libId=libid
        ss.properties=[copy.deepcopy(p) for p in tpl.properties]
        for p in ss.properties:
            if p.key=='Reference':
                p.value=ref; p.position=Position(x+ref_dx,y+ref_dy,0)
                p.effects=Effects(font=Font(height=1.27,width=1.27),hide=False)
            elif p.key=='Value':
                p.value=val; p.position=Position(x+ref_dx,y-ref_dy,0)
                p.effects=Effects(font=Font(height=1.27,width=1.27),hide=True)
            else:
                if p.key=='Footprint': p.value=footprint
                p.effects=Effects(font=Font(height=1.0,width=1.0),hide=True)
        ss.pins={str(p.number):str(uuid.uuid4()) for u in libsym.units for p in u.pins}
        ss.instances=[SymbolProjectInstance(name='',paths=[SymbolProjectPath(sheetInstancePath='/',reference=ref,unit=1)])]
        self.s.schematicSymbols.append(ss); return ss
    def connect(self,libsym,x,y,num,netname,length=2.54):
        pin=self.pin_of(libsym,num); ex,ey=self.endpoint(x,y,pin)
        a=self.outward(pin); dx=math.cos(math.radians(a))*length; dy=-math.sin(math.radians(a))*length
        nx,ny=ex+dx,ey+dy
        self.s.graphicalItems.append(Connection(type='wire',points=[Position(ex,ey),Position(nx,ny)],
            stroke=Stroke(width=0),uuid=str(uuid.uuid4())))
        self.s.labels.append(LocalLabel(text=netname,position=Position(nx,ny,90 if a in (90,270) else 0),uuid=str(uuid.uuid4())))
    def nc(self,libsym,x,y,num):
        pin=self.pin_of(libsym,num); ex,ey=self.endpoint(x,y,pin)
        self.s.noConnects.append(NoConnect(position=Position(ex,ey),uuid=str(uuid.uuid4())))
    def note(self,txt,x,y,size=1.8):
        self.s.texts.append(Text(text=txt,position=Position(x,y,0),
            effects=Effects(font=Font(height=size,width=size),justify=Justify(horizontally='left')),uuid=str(uuid.uuid4())))
    def save(self,path):
        os.makedirs(os.path.dirname(path),exist_ok=True); self.s.to_file(path); print('wrote',path)

# ---------------- V3 tile ----------------
b=Builder('PSM V3 Sensor Tile - Schematic')
u=b.lib('VCNL4030X01'); c=b.lib('C'); r=b.lib('R'); j6=b.lib('Conn_01x06')
coords=[(76.2,76.2),(177.8,76.2),(76.2,177.8),(177.8,177.8)]
for i,(x,y) in enumerate(coords,1):
    b.add(tpl_io,u,'PSM:VCNL4030X01',f'U{i}',f'VCNL4030X01 {["0x60","0x51","0x40","0x41"][i-1]}',x,y,'psm:VCNL4030X01')
    b.connect(u,x,y,1,'3V3'); b.connect(u,x,y,2,'SCL'); b.connect(u,x,y,3,'GND')
    b.connect(u,x,y,4,'3V3'); b.connect(u,x,y,5,f'IR_K{i}'); b.connect(u,x,y,6,f'IR_K{i}')
    b.connect(u,x,y,7,'INT_N'); b.connect(u,x,y,8,'SDA')
# caps: C1-C4 VDD, C5-C8 IR, C9 bulk
for i in range(1,5):
    x=289.56+((i-1)%2)*50.8; y=76.2+((i-1)//2)*50.8
    b.add(tpl_c,c,'PSM:C',f'C{i}','100n',x,y,'psm:C_0603_1608Metric')
    b.connect(c,x,y,1,'3V3'); b.connect(c,x,y,2,'GND')
for i in range(5,9):
    x=289.56+((i-5)%2)*50.8; y=177.8+((i-5)//2)*50.8
    b.add(tpl_c,c,'PSM:C',f'C{i}','100n',x,y,'psm:C_0603_1608Metric')
    b.connect(c,x,y,1,'3V3'); b.connect(c,x,y,2,'GND')
b.add(tpl_c,c,'PSM:C','C9','22u',365.76,127.0,'psm:C_0805_2012Metric')
b.connect(c,365.76,127.0,1,'3V3'); b.connect(c,365.76,127.0,2,'GND')
# pull-ups
for i,(net,val) in enumerate([('SDA','10k'),('SCL','10k'),('INT_N','10k')],1):
    x=457.2; y=76.2+(i-1)*38.1
    b.add(tpl_r,r,'PSM:R',f'R{i}',val,x,y,'psm:R_0603_1608Metric')
    b.connect(r,x,y,1,'3V3'); b.connect(r,x,y,2,net)
# tile connector
jx,jy=457.2,228.6
b.add(tpl_io,j6,'PSM:Conn_01x06','J1','TILE_IF',jx,jy,'psm:PinHeader_1x06_P1.27mm_Vertical')
for n,net in [(1,'3V3'),(2,'GND'),(3,'SDA'),(4,'SCL'),(5,'INT_N')]: b.connect(j6,jx,jy,n,net)
b.nc(j6,jx,jy,6)
b.note('PSM V3 SENSOR TILE - 2x2 VCNL4030X01',60,40,4.0)
b.note('U1=0x60  U2=0x51  U3=0x40  U4=0x41 (factory address variants).',60,52,2.0)
b.note('IR cathode (5) and LDR (6) are tied together per sensor; 100nF on VDD and IR anode; 22uF tile bulk.',60,62,1.7)
b.note('J1: 1=3V3 2=GND 3=SDA 4=SCL 5=INT_N 6=NC. Sealing ring and conformal coat are PCB-level.',60,500,1.7)
b.save(os.path.join(BASE,'hardware','psm-v3','tile','psm-v3-tile.kicad_sch'))

# ---------------- V3 hub ----------------
b=Builder('PSM V3 Hub - Schematic')
mux=b.lib('PCA9548A'); usb=b.lib('USBLC6-2SC6'); led=b.lib('LED'); c=b.lib('C'); r=b.lib('R'); j6=b.lib('Conn_01x06'); j10=b.lib('Conn_01x10')
# mux
mx,my=120.65,127.0
b.add(tpl_mux,mux,'PSM:PCA9548A','U1','PCA9548A 0x70',mx,my,'psm:TSSOP-24_4.4x7.8mm_P0.65mm',-14,-22)
for n,net in [(1,'GND'),(2,'GND'),(3,'MUX_RST'),(21,'GND'),(22,'SCL'),(23,'SDA'),(24,'3V3'),(12,'GND')]:
    b.connect(mux,mx,my,n,net)
for ch,(sd,sc) in enumerate([(4,5),(6,7),(8,9),(10,11)]):
    b.connect(mux,mx,my,sd,f'SDA_C{ch}'); b.connect(mux,mx,my,sc,f'SCL_C{ch}')
for n in (13,14,15,16,17,18,19,20): b.nc(mux,mx,my,n)
# host header
hx,hy=59.69,304.8
b.add(tpl_io,j10,'PSM:Conn_01x10','J1','HOST_IF',hx,hy,'psm:PinHeader_2x05_P2.54mm_Vertical')
for n,net in [(1,'3V3'),(2,'GND'),(3,'SDA'),(4,'SCL'),(5,'INT_N'),(6,'MUX_RST'),(8,'GND')]: b.connect(j10,hx,hy,n,net)
for n in (7,9,10,'MP'): b.nc(j10,hx,hy,n)
# tile ports
for i,y in enumerate([76.2,139.7,203.2,266.7]):
    x=457.2
    b.add(tpl_io,j6,'PSM:Conn_01x06',f'J{i+2}',f'TILE_{i}',x,y,'psm:PinHeader_1x06_P1.27mm_Vertical')
    for n,net in [(1,'3V3'),(2,'GND'),(3,f'SDA_C{i}'),(4,f'SCL_C{i}'),(5,'INT_N')]: b.connect(j6,x,y,n,net)
    b.nc(j6,x,y,6)
# ESD, LED
ex,ey=304.8,304.8
b.add(tpl_io,usb,'PSM:USBLC6-2SC6','U2','USBLC6-2SC6',ex,ey,'psm:SOT-23-6')
for n,net in [(1,'SDA'),(2,'GND'),(3,'SCL'),(4,'SCL'),(5,'3V3'),(6,'SDA')]: b.connect(usb,ex,ey,n,net)
lx,ly=381.0,304.8
b.add(tpl_led,led,'PSM:LED','D1','POWER',lx,ly,'psm:LED_0603_1608Metric')
b.connect(led,lx,ly,1,'GND'); b.connect(led,lx,ly,2,'LED_A')
# resistors
for i,(ref,val,net) in enumerate([('R1','2.2k','SDA'),('R2','2.2k','SCL'),('R3','10k','MUX_RST'),('R4','10k','INT_N'),('R5','1k','LED_A')],1):
    x=304.8+((i-1)%2)*50.8; y=355.6+((i-1)//2)*38.1
    b.add(tpl_r,r,'PSM:R',ref,val,x,y,'psm:R_0603_1608Metric')
    b.connect(r,x,y,1,'3V3'); b.connect(r,x,y,2,net)
# caps
for i,(ref,val,fp) in enumerate([('C1','100n','psm:C_0603_1608Metric'),('C2','10u','psm:C_0805_2012Metric'),
                                 ('C3','100n','psm:C_0603_1608Metric'),('C4','100n','psm:C_0603_1608Metric'),
                                 ('C5','100n','psm:C_0603_1608Metric'),('C6','100n','psm:C_0603_1608Metric'),
                                 ('C7','100n','psm:C_0603_1608Metric')],1):
    x=406.4+((i-1)%2)*50.8; y=355.6+((i-1)//2)*38.1
    b.add(tpl_c,c,'PSM:C',ref,val,x,y,fp)
    b.connect(c,x,y,1,'3V3'); b.connect(c,x,y,2,'GND')
b.note('PSM V3 HUB - ONE PCA9548A, FOUR TILE PORTS',60,40,4.0)
b.note('U1 0x70: A0/A1/A2=0; channels 0-3 -> J2-J5; channels 4-7 spare.',60,52,1.9)
b.note('J1 host: 1=3V3 2=GND 3=SDA 4=SCL 5=INT_N 6=MUX_RST 7=5V(NC) 8=GND 9/10=NC.',60,62,1.6)
b.note('Tile ports J2-J5: 1=3V3 2=GND 3=SDA_Cn 4=SCL_Cn 5=INT_N 6=NC.',60,500,1.7)
b.note('U2 USBLC6-2SC6 protects upstream SDA/SCL; 2.2k pull-ups; 10k reset/INT; 1k LED.',60,512,1.7)
b.save(os.path.join(BASE,'hardware','psm-v3','hub','psm-v3-hub.kicad_sch'))
