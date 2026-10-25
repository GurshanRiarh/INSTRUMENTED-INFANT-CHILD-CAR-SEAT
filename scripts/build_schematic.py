#!/usr/bin/env python3
"""Build a documentation schematic for PSM V1 from KiCad 9 demo symbols.

The schematic is a readable connection-level diagram. The PCB is the
authoritative netlist. Per-sensor decoupling/IR resistors are noted in text
and are present on the PCB.
"""
import os, copy, uuid, math
from kiutils.schematic import Schematic
from kiutils.symbol import SymbolLib
from kiutils.items.schitems import (SchematicSymbol, LocalLabel, GlobalLabel,
    SymbolProjectInstance, SymbolProjectPath, Connection, NoConnect)
from kiutils.items.common import Position, Stroke, Effects, Font, Justify

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEMOS='/home/zeus/.local/share/flatpak/app/org.kicad.KiCad/x86_64/stable/active/files/share/kicad/demos'
IO=os.path.join(DEMOS,'cm5_minima','IO.kicad_sch')
CSI=os.path.join(DEMOS,'jetson-agx-thor-baseboard','csi.kicad_sch')
OUT=os.path.join(BASE,'hardware','psm-v1','psm-v1.kicad_sch')

io=Schematic.from_file(IO)
s=copy.deepcopy(io)
s.paper.paperSize='A1'
s.titleBlock.title='PSM V1 - Connection-Level Schematic'
s.titleBlock.company='Carleton University - Instrumented Infant-Child Car Seat'
s.titleBlock.revision='V1.0'
s.titleBlock.comments={}
s.schematicSymbols=[]; s.globalLabels=[]; s.labels=[]; s.graphicalItems=[]
s.junctions=[]; s.noConnects=[]; s.busEntries=[]; s.hierarchicalLabels=[]
s.texts=[]; s.textBoxes=[]

# --- custom sensor symbol ---
sensor_sym=copy.deepcopy([x for x in io.libSymbols if x.entryName=='Conn_01x10_MountingPin'][0])
sensor_sym.libraryNickname='PSM'; sensor_sym.entryName='VCNL4020'
for u in sensor_sym.units:
    u.entryName=u.entryName.replace('Conn_01x10_MountingPin','VCNL4020')
for p in sensor_sym.properties:
    if p.key=='Reference': p.value='U'
    if p.key=='Value': p.value='VCNL4020'
    if p.key=='Description': p.value='Vishay VCNL4020 IR proximity sensor'

# --- PSM copies of generic symbols
hdr_sym=copy.deepcopy([x for x in io.libSymbols if x.entryName=='Conn_01x10_MountingPin'][0])
hdr_sym.libraryNickname='PSM'; hdr_sym.entryName='Conn_01x10'
for u in hdr_sym.units: u.entryName=u.entryName.replace('Conn_01x10_MountingPin','Conn_01x10')
for p in hdr_sym.properties:
    if p.key=='Reference': p.value='J'
    if p.key=='Value': p.value='Conn_01x10'
r_sym=copy.deepcopy([x for x in io.libSymbols if x.entryName=='R'][0])
r_sym.libraryNickname='PSM'; r_sym.entryName='R'
for u in r_sym.units: u.entryName=u.entryName.replace('R','R')
c_sym=copy.deepcopy([x for x in io.libSymbols if x.entryName=='C'][0])
c_sym.libraryNickname='PSM'; c_sym.entryName='C'
for u in c_sym.units: u.entryName=u.entryName.replace('C','C')

# --- custom mux symbol from csi (PI4MSD5V9548AZDEX, 25 pins) ---
csi=Schematic.from_file(CSI)
mux_sym=copy.deepcopy([x for x in csi.libSymbols if '9548' in x.entryName][0])
mux_sym.libraryNickname='PSM'; mux_sym.entryName='PCA9548A'
for u in mux_sym.units:
    u.entryName=u.entryName.replace('PI4MSD5V9548AZDEX','PCA9548A')
for p in mux_sym.properties:
    if p.key=='Reference': p.value='U'
    if p.key=='Value': p.value='PCA9548A'
    if p.key=='Description': p.value='PCA9548A 8-channel I2C switch'
# remap old pin numbers to PCA9548A pin numbers
remap={
 '21':('24','VCC'), '20':('23','SDA'), '19':('22','SCL'), '24':('3','~RESET'),
 '22':('1','A0'), '23':('2','A1'), '18':('21','A2'), '25':('25','EP'), '9':('12','GND'),
 '1':('4','SD0'), '2':('5','SC0'), '3':('6','SD1'), '4':('7','SC1'),
 '5':('8','SD2'), '6':('9','SC2'), '7':('10','SD3'), '8':('11','SC3'),
 '10':('13','SD4'), '11':('14','SC4'), '12':('15','SD5'), '13':('16','SC5'),
 '14':('17','SD6'), '15':('18','SC6'), '16':('19','SD7'), '17':('20','SC7'),
}
for u in mux_sym.units:
    for pin in u.pins:
        if pin.number in remap:
            pin.number, pin.name = remap[pin.number]
            if pin.number in ('12','24','25'):
                pin.electricalType='passive'

s.libSymbols.append(sensor_sym); s.libSymbols.append(mux_sym)
s.libSymbols.append(hdr_sym); s.libSymbols.append(r_sym); s.libSymbols.append(c_sym)

# templates
tpl_io=[x for x in io.schematicSymbols if 'Conn_01x10' in x.libId][0]
tpl_mux=[x for x in csi.schematicSymbols if '9548' in str(x.libId)][0]
tpl_r=[x for x in io.schematicSymbols if 'CM5IO:R'==x.libId][0]
tpl_c=[x for x in io.schematicSymbols if 'CM5IO:C'==x.libId][0]

def pin_of(libsym,num):
    for u in libsym.units:
        for p in u.pins:
            if str(p.number)==str(num): return p
    raise KeyError((libsym.entryName,num))

def endpoint(x,y,pin):
    return (x+pin.position.X, y-pin.position.Y)

def outward(pin):
    ang=(pin.position.angle or 0)
    if ang==0: return 180
    if ang==90: return 270
    if ang==180: return 0
    return 90

def add_instance(tpl, libsym, libid, ref, val, x, y, footprint=''):
    ss=copy.deepcopy(tpl); ss.uuid=str(uuid.uuid4())
    ss.position=Position(x,y,0); ss.mirror=None; ss.unit=1
    ss.libraryNickname=libid.split(':')[0]; ss.entryName=libid.split(':')[1]
    ss.libName=None; ss.libId=libid
    ss.properties=[copy.deepcopy(p) for p in tpl.properties]
    for p in ss.properties:
        if p.key=='Reference':
            p.value=ref
            p.position=Position(x-12.0,y-18.0,0)
            p.effects=Effects(font=Font(height=1.27,width=1.27),hide=False)
        elif p.key=='Value':
            p.value=val
            p.position=Position(x-12.0,y+18.0,0)
            p.effects=Effects(font=Font(height=1.27,width=1.27),hide=True)
        else:
            if p.key=='Footprint': p.value=footprint
            p.effects=Effects(font=Font(height=1.0,width=1.0),hide=True)
    ss.pins={str(p.number):str(uuid.uuid4()) for u in libsym.units for p in u.pins}
    ss.instances=[SymbolProjectInstance(name='', paths=[SymbolProjectPath(sheetInstancePath='/', reference=ref, unit=1)])]
    s.schematicSymbols.append(ss)
    return ss

def label_at(x,y,text,vertical=False):
    lab=LocalLabel(text=text, position=Position(x,y,90 if vertical else 0), uuid=str(uuid.uuid4()))
    s.labels.append(lab)

def connect(inst, libsym, x, y, pin_num, netname, length=2.54):
    pin=pin_of(libsym,pin_num); ex,ey=endpoint(x,y,pin)
    ang=outward(pin); dx=math.cos(math.radians(ang))*length; dy=-math.sin(math.radians(ang))*length
    nx,ny=ex+dx,ey+dy
    s.graphicalItems.append(Connection(type='wire', points=[Position(ex,ey),Position(nx,ny)],
        stroke=Stroke(width=0), uuid=str(uuid.uuid4())))
    label_at(nx,ny,netname,vertical=(ang in (90,270)))

def nc(inst, libsym, x, y, pin_num):
    pin=pin_of(libsym,pin_num); ex,ey=endpoint(x,y,pin)
    s.noConnects.append(NoConnect(position=Position(ex,ey), uuid=str(uuid.uuid4())))

# --- sensors ---
coords=[76.2,127.0,177.8,228.6]
idx=1
for row,y in enumerate(coords):
    for col,x in enumerate(coords):
        inst=add_instance(tpl_io, sensor_sym, 'PSM:VCNL4020', f'U{idx}', 'VCNL4020', x, y, 'psm:VCNL4020')
        connect(inst,sensor_sym,x,y,1,f'IR_A{idx}')
        connect(inst,sensor_sym,x,y,2,f'SDA_C{idx}')
        connect(inst,sensor_sym,x,y,3,'INT_N')
        connect(inst,sensor_sym,x,y,4,f'SCL_C{idx}')
        connect(inst,sensor_sym,x,y,5,'3V3')
        connect(inst,sensor_sym,x,y,8,'GND')
        connect(inst,sensor_sym,x,y,9,'GND')
        for n in (6,7,10,'MP'): nc(inst,sensor_sym,x,y,n)
        idx+=1

# --- muxes ---
muxes=[('U17','0x70',0,1),('U18','0x71',1,9)]
for ref,addr,a0,start in muxes:
    x=330.2; y=88.9 if ref=='U17' else 190.5
    inst=add_instance(tpl_mux, mux_sym, 'PSM:PCA9548A', ref, f'PCA9548A {addr}', x, y, 'psm:TSSOP-24_4.4x7.8mm_P0.65mm')
    connect(inst,mux_sym,x,y,1,'3V3' if a0 else 'GND')
    connect(inst,mux_sym,x,y,2,'GND')
    connect(inst,mux_sym,x,y,3,'MUX_RST')
    connect(inst,mux_sym,x,y,21,'GND')
    connect(inst,mux_sym,x,y,22,'SCL')
    connect(inst,mux_sym,x,y,23,'SDA')
    connect(inst,mux_sym,x,y,24,'3V3')
    connect(inst,mux_sym,x,y,12,'GND')
    connect(inst,mux_sym,x,y,25,'GND')
    # channels
    chpins=[(4,5),(6,7),(8,9),(10,11),(13,14),(15,16),(17,18),(19,20)]
    for ch,(sd,sc) in enumerate(chpins):
        sn=start+ch
        connect(inst,mux_sym,x,y,sd,f'SDA_C{sn}')
        connect(inst,mux_sym,x,y,sc,f'SCL_C{sn}')

# --- header ---
inst=add_instance(tpl_io, hdr_sym, 'PSM:Conn_01x10', 'J1', 'HOST_IF', 457.2, 127.0, 'psm:PinHeader_2x05_P2.54mm_Vertical')
for n,netname in [(1,'3V3'),(2,'GND'),(3,'SDA'),(4,'SCL'),(5,'INT_N'),(6,'MUX_RST'),(8,'GND')]:
    connect(inst,hdr_sym,457.2,127.0,n,netname)
for n in (7,9,10,'MP'): nc(inst,hdr_sym,457.2,127.0,n)

# --- support passives ---
def passive(tpl, sym, libid, ref, val, x, y, n1, n2):
    inst=add_instance(tpl, sym, libid, ref, val, x, y, 'psm:R_0603_1608Metric' if 'R' in libid else 'psm:C_0603_1608Metric')
    connect(inst,sym,x,y,1,n1); connect(inst,sym,x,y,2,n2)
passive(tpl_r,r_sym,'PSM:R','R17','4.7k',457.2,177.8,'3V3','SDA')
passive(tpl_r,r_sym,'PSM:R','R18','4.7k',482.6,177.8,'3V3','SCL')
passive(tpl_r,r_sym,'PSM:R','R19','10k',457.2,203.2,'3V3','MUX_RST')
passive(tpl_r,r_sym,'PSM:R','R20','10k',482.6,203.2,'3V3','INT_N')
passive(tpl_c,c_sym,'PSM:C','C17','22u',457.2,228.6,'3V3','GND')
passive(tpl_c,c_sym,'PSM:C','C18','22u',482.6,228.6,'3V3','GND')

# IR anode series resistors (one per sensor)
for i in range(1,17):
    col=(i-1)%4; row=(i-1)//4
    passive(tpl_r,r_sym,'PSM:R',f'R{i}','10R', 539.75+col*38.1, 63.5+row*38.1, '3V3', f'IR_A{i}')

# notes
from kiutils.items.schitems import Text
def note(txt,x,y,size=1.6):
    s.texts.append(Text(text=txt, position=Position(x,y,0), effects=Effects(font=Font(height=size,width=size), justify=Justify(horizontally='left')), uuid=str(uuid.uuid4())))
note('PSM V1 - CONNECTION-LEVEL SCHEMATIC (thesis baseline)', 60, 40, 4.0)
note('16x VCNL4020 on 4x4 array; 2x PCA9548A; Tiva/LaunchPad header. PCB is authoritative for passives and routing.', 60, 52, 2.0)
note('Per sensor: 100nF local decoupling, 10R IR-anode series resistor. 22uF bulk per mux/header.', 60, 62, 1.7)
note('U17 channels 0-7 -> U1..U8; U18 channels 0-7 -> U9..U16.', 60, 520, 2.0)
note('VCNL4020: 1 IR anode, 2 SDA, 3 INT, 4 SCL, 5 VDD, 8/9 GND, 6/7/10 NC.', 60, 532, 1.7)

os.makedirs(os.path.dirname(OUT),exist_ok=True)
# write standalone PSM symbol library
libdir=os.path.join(BASE,'hardware','libraries'); os.makedirs(libdir,exist_ok=True)
libsymbols=[]
for sym in [hdr_sym,r_sym,c_sym,sensor_sym,mux_sym]:
    z=copy.deepcopy(sym); z.libraryNickname=None; libsymbols.append(z)
lib=SymbolLib(version='20231120', generator='kicad_symbol_editor', symbols=libsymbols)
lib.to_file(os.path.join(libdir,'psm-symbols.kicad_sym'))
with open(os.path.join(BASE,'hardware','psm-v1','sym-lib-table'),'w') as f:
    f.write('(sym_lib_table\n  (version 7)\n  (lib (name "PSM")(type "KiCad")(uri "${KIPRJMOD}/../libraries/psm-symbols.kicad_sym")(options "")(descr "PSM project symbols"))\n)\n')
s.to_file(OUT)
print('wrote',OUT)
