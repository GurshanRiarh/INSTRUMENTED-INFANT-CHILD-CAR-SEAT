#!/usr/bin/env python3
"""Generate simple SVG block diagrams for the repository/docs."""
import os
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,'docs')
os.makedirs(OUT,exist_ok=True)

def svg(w,h,body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3" orient="auto" markerUnits="strokeWidth">
    <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
  </marker>
  <style>
    text {{ font-family: "DejaVu Sans", Arial, sans-serif; fill: #111; }}
    .box {{ fill: #f7f9fc; stroke: #2c3e50; stroke-width: 1.5; rx: 6; }}
    .box2 {{ fill: #eef6ee; stroke: #2e7d32; stroke-width: 1.5; rx: 6; }}
    .box3 {{ fill: #fff4e5; stroke: #b26a00; stroke-width: 1.5; rx: 6; }}
    .wire {{ stroke: #333; stroke-width: 1.6; fill: none; marker-end: url(#arrow); }}
    .line {{ stroke: #333; stroke-width: 1.4; fill: none; }}
    .small {{ font-size: 12px; }}
    .tiny {{ font-size: 10.5px; fill: #444; }}
    .title {{ font-size: 20px; font-weight: bold; }}
    .h {{ font-size: 15px; font-weight: bold; }}
  </style>
</defs>
{body}
</svg>
'''

def box(x,y,w,h,lines,cls='box',hsize=15):
    s=f'<rect class="{cls}" x="{x}" y="{y}" width="{w}" height="{h}"/>\n'
    ty=y+22
    for i,l in enumerate(lines):
        size=hsize if i==0 else 12.5
        weight='bold' if i==0 else 'normal'
        s+=f'<text x="{x+w/2}" y="{ty}" text-anchor="middle" font-size="{size}" font-weight="{weight}">{l}</text>\n'
        ty+=18 if i==0 else 15
    return s

def arrow(x1,y1,x2,y2,label='',dash=False):
    dashattr=' stroke-dasharray="5,4"' if dash else ''
    s=f'<line class="wire" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}"{dashattr}/>\n'
    if label:
        s+=f'<text x="{(x1+x2)/2}" y="{(y1+y2)/2-6}" text-anchor="middle" font-size="11" fill="#444">{label}</text>\n'
    return s

# ---------------- system architecture ----------------
b=''
b+=f'<text x="20" y="30" class="title">Instrumented Infant-Child Car Seat - Data Path</text>\n'
b+=f'<text x="20" y="50" class="tiny">Research prototype. V1 is the thesis reproduction; V3 is the modular sensor upgrade.</text>\n'
b+=box(20,80,200,150,['Seat sensing','PSM V1: 16x VCNL4020','or PSM V3: 4 tiles / 16x VCNL4030X01','OV5640 RGB camera','AMG8833 8x8 thermal','Orbbec Astra Pro RGB-D'],'box')
b+=box(270,80,190,120,['ESP32-S3 edge node','OV5640 over DVP','AMG8833 over I2C','JPEG + timestamp','Wi-Fi / MQTT publisher'],'box2')
b+=box(270,250,190,110,['Raspberry Pi 4B hub','PSM over I2C + mux','Astra Pro over USB','Timestamp sync + fusion','BLE GATT server'],'box2')
b+=box(510,80,200,115,['iPhone app','BLE service layer','Alert state machine','Drive-safe UI','Trip / alert history'],'box3')
b+=box(510,245,200,95,['In-vehicle output','CarPlay (target)','or mounted-phone drive-safe mode','No live video while moving'],'box3')
b+=box(740,150,150,110,['Caregiver','Vitals + status','Escalating alerts','Emergency contacts'],'box')
b+=arrow(220,155,270,140,'DVP / I2C')
b+=arrow(365,200,365,250,'Wi-Fi / MQTT')
b+=arrow(460,305,510,305,'BLE')
b+=arrow(610,195,610,245,'CarPlay / phone UI')
b+=arrow(710,292,740,250,'notifications')
b+=f'<text x="20" y="420" class="h">Design note</text>\n'
b+=f'<text x="20" y="440" class="small">The Pi owns acquisition and fusion. The phone owns the alert state machine and escalation. The PSM is not a certified medical device.</text>\n'
b+=f'<text x="20" y="458" class="small">V1 uses two PCA9548A muxes (0x70/0x71) for 16 VCNL4020 sensors. V3 uses one PCA9548A (0x70) for up to 8 tiles.</text>\n'
open(os.path.join(OUT,'system-architecture.svg'),'w').write(svg(920,480,b))

# ---------------- V1 connection diagram ----------------
b=''
b+=f'<text x="20" y="30" class="title">PSM V1 - Electrical Architecture (thesis baseline)</text>\n'
b+=f'<text x="20" y="50" class="tiny">16x Vishay VCNL4020 (fixed 7-bit address 0x13), 2x PCA9548A 8-channel I2C switch, Tiva/LaunchPad header.</text>\n'
b+=box(20,80,180,95,['Host header J1','2x5, 2.54 mm','3V3, GND, SDA, SCL','INT_N, MUX_RST, 5V'],'box3')
b+=box(240,82,180,90,['U17 PCA9548A','7-bit address 0x70','A0/A1/A2 = 0','channels 0-7'],'box2')
b+=box(240,200,180,90,['U18 PCA9548A','7-bit address 0x71','A0 = 1; A1/A2 = 0','channels 0-7'],'box2')
b+=box(480,75,400,105,['Sensors U1-U8 (via U17)','U1..U8 = VCNL4020 @ 0x13','SCL/SDA per channel; INT_N shared','IR anode: 3V3 through 10R; 100nF + 22uF'],'box')
b+=box(480,195,400,105,['Sensors U9-U16 (via U18)','U9..U16 = VCNL4020 @ 0x13','SCL/SDA per channel; INT_N shared','IR anode: 3V3 through 10R; 100nF + 22uF'],'box')
b+=arrow(200,120,240,120,'3V3/GND/SDA/SCL')
b+=arrow(200,140,240,240,'same bus')
b+=arrow(420,120,480,120,'ch 0-7')
b+=arrow(420,240,480,240,'ch 0-7')
b+=f'<text x="20" y="340" class="h">Channel map</text>\n'
b+=f'<text x="20" y="360" class="small">U17 ch0..7 -> U1..U8     U18 ch0..7 -> U9..U16</text>\n'
b+=f'<text x="20" y="378" class="small">Each VCNL4020: 1 IR anode, 2 SDA, 3 INT, 4 SCL, 5 VDD, 8/9 GND, 6/7/10 NC.</text>\n'
b+=f'<text x="20" y="396" class="small">Pull-ups: 4.7k on upstream SDA/SCL; 10k on MUX_RST and INT_N. 22uF bulk + 100nF per sensor.</text>\n'
b+=f'<text x="20" y="414" class="small">Board: 101.6 x 101.6 mm, 4x4 grid at 25.4 mm pitch, 0.2 mm polyimide flex, 2 layers.</text>\n'
open(os.path.join(OUT,'psm-v1-architecture.svg'),'w').write(svg(900,440,b))

# ---------------- V3 topology ----------------
b=''
b+=f'<text x="20" y="30" class="title">PSM V3 - Modular Tile Topology (Prannav improvements)</text>\n'
b+=f'<text x="20" y="50" class="tiny">One mux, four 2x2 tiles, four factory I2C addresses per tile. Expandable to 8 tiles / 32 sensors.</text>\n'
b+=box(20,85,180,100,['Host header J1','2x5, 2.54 mm','3V3, GND, SDA, SCL','INT_N, MUX_RST, 5V'],'box3')
b+=box(250,85,190,100,['U1 PCA9548A','address 0x70','A0/A1/A2 = 0','channels 0-7 (0-3 used)'],'box2')
b+=box(490,75,390,120,['Tile port J2..J5 (one per tile)','6-pin, 1.27 mm: 3V3 / GND / SDA / SCL / INT_N / NC','Each tile bus is one mux channel','Tile cable length kept short; upstream 2.2k pull-ups'],'box2')
b+=box(250,245,630,115,['Tile (x4): 4x VCNL4030X01','U1 0x60  |  U2 0x51  |  U3 0x40  |  U4 0x41','All share SDA/SCL/INT_N on the tile; IR cathode + LDR tied per sensor','22uF + 100nF per tile; 100nF per sensor VDD and IR anode'],'box')
b+=arrow(200,135,250,135,'I2C')
b+=arrow(440,135,490,135,'ch 0-3')
b+=arrow(685,195,685,245,'4 sensors / tile')
b+=f'<text x="20" y="390" class="h">Why this is an improvement</text>\n'
b+=f'<text x="20" y="410" class="small">V1: 2 muxes, 16 channels, fixed 0x13 sensors. V3: 1 mux, 4 channels, four addresses per tile.</text>\n'
b+=f'<text x="20" y="428" class="small">Tiles can be placed on the car-seat contour and replaced individually; the hub supports up to 8 tiles.</text>\n'
b+=f'<text x="20" y="446" class="small">Tile: 30 x 30 mm, 0.2 mm flex, sealing ring + conformal coat. Hub: 60 x 40 mm, 1.6 mm FR4.</text>\n'
open(os.path.join(OUT,'psm-v3-topology.svg'),'w').write(svg(900,470,b))
print('wrote diagrams')
