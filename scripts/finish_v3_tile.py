#!/usr/bin/env python3
import os, pcbnew
MM=pcbnew.FromMM
BASE=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=os.path.join(BASE,'hardware','psm-v3','tile')
BOARD=os.path.join(OUT,'psm-v3-tile.kicad_pcb'); SES=os.path.join(OUT,'psm-v3-tile.ses')
b=pcbnew.LoadBoard(BOARD)
for _z in list(b.Zones()):
    b.Remove(_z)
b.GetDesignSettings().m_TrackMinWidth=MM(0.12)
b.GetDesignSettings().m_CopperEdgeClearance=MM(0.30)
pcbnew.ImportSpecctraSES(b,SES)
gnd=None
for name,n in b.GetNetsByName().items():
    if str(name)=='GND': gnd=n; break
z=pcbnew.ZONE(b); z.SetLayer(pcbnew.B_Cu); z.SetNet(gnd)
z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
z.SetMinThickness(MM(0.20)); z.SetLocalClearance(MM(0.15))
z.SetThermalReliefGap(MM(0.20)); z.SetThermalReliefSpokeWidth(MM(0.40))
o=z.Outline(); o.NewOutline()
for x,y in [(0.5,0.5),(29.5,0.5),(29.5,29.5),(0.5,29.5)]: o.Append(MM(x),MM(y))
b.Add(z)
pcbnew.ZONE_FILLER(b).Fill(b.Zones())
pcbnew.SaveBoard(BOARD,b)
print('saved',BOARD,'tracks',len(b.GetTracks()))
