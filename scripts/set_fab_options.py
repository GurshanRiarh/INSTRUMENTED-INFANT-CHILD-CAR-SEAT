#!/usr/bin/env python3
import os, pcbnew
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for p in ['hardware/psm-v1/psm-v1.kicad_pcb','hardware/psm-v3/tile/psm-v3-tile.kicad_pcb','hardware/psm-v3/hub/psm-v3-hub.kicad_pcb']:
    b=pcbnew.LoadBoard(os.path.join(BASE,p)); ds=b.GetDesignSettings()
    ds.m_TrackMinWidth=pcbnew.FromMM(0.12)
    ds.m_MinClearance=pcbnew.FromMM(0.15)
    ds.m_CopperEdgeClearance=pcbnew.FromMM(0.30)
    for attr in ['m_TentViasFront','m_TentViasBack','m_CoverViasFront','m_CoverViasBack','m_PlugViasFront','m_PlugViasBack']:
        if hasattr(ds,attr): setattr(ds,attr,True)
    pcbnew.SaveBoard(os.path.join(BASE,p),b)
    print('set fab options',p)
