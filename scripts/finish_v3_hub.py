#!/usr/bin/env python3
import os, pcbnew
MM=pcbnew.FromMM
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,'hardware','psm-v3','hub')
BOARD=os.path.join(OUT,'psm-v3-hub.kicad_pcb'); SES=os.path.join(OUT,'psm-v3-hub.ses')
b=pcbnew.LoadBoard(BOARD); b.GetDesignSettings().m_TrackMinWidth=MM(0.12); b.GetDesignSettings().m_CopperEdgeClearance=MM(0.30)
pcbnew.ImportSpecctraSES(b,SES)
gnd=None
for name,n in b.GetNetsByName().items():
    if str(name)=='GND': gnd=n; break
z=pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(gnd)
z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
z.SetMinThickness(MM(0.25)); z.SetLocalClearance(MM(0.15))
z.SetThermalReliefGap(MM(0.25)); z.SetThermalReliefSpokeWidth(MM(0.50))
o=z.Outline(); o.NewOutline()
for x,y in [(0.5,0.5),(59.5,0.5),(59.5,39.5),(0.5,39.5)]: o.Append(MM(x),MM(y))
b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD,b); print('saved',BOARD,'tracks',len(b.GetTracks()))
