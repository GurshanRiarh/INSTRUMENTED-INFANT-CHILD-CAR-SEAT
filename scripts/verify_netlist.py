#!/usr/bin/env python3
"""Compare schematic netlists with PCB pad nets for each project."""
import os, subprocess, re, sys, tempfile
import sexpdata, json

BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECTS=[
 ('hardware/psm-v1/psm-v1.kicad_sch','hardware/psm-v1/psm-v1.kicad_pcb'),
 ('hardware/psm-v3/tile/psm-v3-tile.kicad_sch','hardware/psm-v3/tile/psm-v3-tile.kicad_pcb'),
 ('hardware/psm-v3/hub/psm-v3-hub.kicad_sch','hardware/psm-v3/hub/psm-v3-hub.kicad_pcb'),
]

def atom(x):
    if isinstance(x, sexpdata.Symbol): return str(x)
    return x

def walk(node, tag):
    if isinstance(node, list) and node and atom(node[0])==tag:
        yield node
    if isinstance(node, list):
        for c in node:
            yield from walk(c, tag)

def sch_map(sch_path):
    out=os.path.join(BASE,'.netlist-tmp.net')
    cmd=['flatpak','run','--command=kicad-cli','org.kicad.KiCad','sch','export','netlist',
         '--format','kicadsexpr','--output',out,sch_path]
    subprocess.run(cmd,cwd=BASE,check=True,stdout=subprocess.DEVNULL)
    data=sexpdata.loads(open(out,encoding='utf-8').read())
    m={}
    for net in walk(data,'net'):
        name=None; nodes=[]
        for x in net[1:]:
            if isinstance(x,list) and atom(x[0])=='name': name=atom(x[1])
            if isinstance(x,list) and atom(x[0])=='node':
                ref=pin=None
                for y in x[1:]:
                    if isinstance(y,list) and atom(y[0])=='ref': ref=atom(y[1])
                    if isinstance(y,list) and atom(y[0])=='pin': pin=atom(y[1])
                if ref and pin: nodes.append((ref,pin))
        if name:
            name=name.lstrip('/')
            for n in nodes: m[n]=name
    os.remove(out)
    return m

def pcb_map(pcb_path):
    data=json.load(open(os.path.join(BASE,'.pcb-nets.json')))
    d=data[pcb_path]
    return {tuple(k.split('.',1)):v for k,v in d.items()}

bad=0
for sch,pcb in PROJECTS:
    print('==',pcb)
    sm=sch_map(sch); pm=pcb_map(pcb)
    common_refs={r for r,_ in sm} & {r for r,_ in pm}
    # schematic -> PCB
    for (ref,pin),net in sorted(sm.items()):
        if ref not in common_refs: continue
        if net.startswith('unconnected-'): continue
        pnet=pm.get((ref,pin))
        if pnet is None:
            print(f'  missing PCB pad {ref}.{pin} (schematic net {net})'); bad+=1
        elif pnet!=net:
            print(f'  MISMATCH {ref}.{pin}: schematic={net} pcb={pnet}'); bad+=1
    # PCB -> schematic (only pads that have a net)
    for (ref,pin),net in sorted(pm.items()):
        if ref not in common_refs: continue
        if net.startswith('unconnected-'): continue
        snet=sm.get((ref,pin))
        if snet is None:
            print(f'  PCB net without schematic node {ref}.{pin} = {net}'); bad+=1
        elif snet!=net:
            print(f'  MISMATCH {ref}.{pin}: pcb={net} schematic={snet}'); bad+=1
    print(f'  schematic nodes {len(sm)}, PCB pads with nets {len(pm)}, common refs {len(common_refs)}')
print('mismatches',bad)
sys.exit(0 if bad==0 else 1)
