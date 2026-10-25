#!/usr/bin/env python3
import os, csv, pcbnew
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
boards=[
 ('hardware/psm-v1/psm-v1.kicad_pcb','hardware/psm-v1/bom.csv'),
 ('hardware/psm-v3/tile/psm-v3-tile.kicad_pcb','hardware/psm-v3/tile/bom.csv'),
 ('hardware/psm-v3/hub/psm-v3-hub.kicad_pcb','hardware/psm-v3/hub/bom.csv'),
]
for board_path,out in boards:
    b=pcbnew.LoadBoard(os.path.join(BASE,board_path))
    groups={}
    for fp in b.GetFootprints():
        ref=fp.GetReference(); val=fp.GetValue(); fpid=str(fp.GetFPID().GetLibItemName())
        key=(val,fpid)
        groups.setdefault(key,[]).append(ref)
    with open(os.path.join(BASE,out),'w',newline='') as f:
        w=csv.writer(f); w.writerow(['Quantity','References','Value','Footprint'])
        for (val,fpid),refs in sorted(groups.items(), key=lambda x:(x[0][0],x[0][1])):
            w.writerow([len(refs),' '.join(sorted(refs)),val,fpid])
    print('wrote',out,'groups',len(groups))
