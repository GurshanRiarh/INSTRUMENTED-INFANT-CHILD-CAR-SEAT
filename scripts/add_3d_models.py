#!/usr/bin/env python3
import os, pcbnew
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODELS={'VCNL4020':'${KIPRJMOD}/../libraries/psm.3dshapes/VCNL4020.step',
        'VCNL4030X01':'${KIPRJMOD}/../libraries/psm.3dshapes/VCNL4030X01.step'}
for rel in ['hardware/psm-v1/psm-v1.kicad_pcb',
            'hardware/psm-v3/tile/psm-v3-tile.kicad_pcb',
            'hardware/psm-v3/hub/psm-v3-hub.kicad_pcb']:
    p=os.path.join(BASE,rel); b=pcbnew.LoadBoard(p)
    ds=b.GetDesignSettings(); ds.m_TrackMinWidth=pcbnew.FromMM(0.12)
    ds.m_MinClearance=pcbnew.FromMM(0.15); ds.m_CopperEdgeClearance=pcbnew.FromMM(0.30)
    count=0
    for fp in b.GetFootprints():
        name=str(fp.GetFPID().GetLibItemName())
        if name in MODELS and len(fp.Models())==0:
            m=pcbnew.FP_3DMODEL(); m.m_Filename=MODELS[name]; fp.Add3DModel(m); count+=1
    pcbnew.SaveBoard(p,b); print('updated',rel,count)
