#!/usr/bin/env python3
import os, json, pcbnew
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
paths=['hardware/psm-v1/psm-v1.kicad_pcb','hardware/psm-v3/tile/psm-v3-tile.kicad_pcb','hardware/psm-v3/hub/psm-v3-hub.kicad_pcb']
out={}
for path in paths:
    b=pcbnew.LoadBoard(os.path.join(BASE,path)); d={}
    for fp in b.GetFootprints():
        ref=fp.GetReference()
        for p in fp.Pads():
            net=p.GetNetname()
            if net: d[f'{ref}.{p.GetNumber()}']=net.lstrip('/')
    out[path]=d
with open(os.path.join(BASE,'.pcb-nets.json'),'w') as f: json.dump(out,f,indent=1)
print('wrote .pcb-nets.json')
