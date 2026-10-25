#!/usr/bin/env python3
"""Import the Freerouting session, add a GND plane, and save the V1 board."""
import os, pcbnew
MM = pcbnew.FromMM
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, "hardware", "psm-v1")
BOARD = os.path.join(OUT, "psm-v1.kicad_pcb")
SES = os.path.join(OUT, "psm-v1.ses")

board = pcbnew.LoadBoard(BOARD)
for _z in list(board.Zones()):
    board.Remove(_z)
board.GetDesignSettings().m_TrackMinWidth = MM(0.12)
board.GetDesignSettings().m_CopperEdgeClearance = MM(0.30)
pcbnew.ImportSpecctraSES(board, SES)

# GND zone on the back copper, inset 0.5 mm from the board edge
gnd = None
for name, net in board.GetNetsByName().items():
    if str(name) == "GND":
        gnd = net
        break
if gnd is None:
    raise RuntimeError("GND net not found")

zone = pcbnew.ZONE(board)
zone.SetLayer(pcbnew.B_Cu)
zone.SetNet(gnd)
zone.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
zone.SetMinThickness(MM(0.25))
zone.SetLocalClearance(MM(0.20))
zone.SetThermalReliefGap(MM(0.25))
zone.SetThermalReliefSpokeWidth(MM(0.50))
outline = zone.Outline()
outline.NewOutline()
for x, y in [(0.5, 0.5), (101.1, 0.5), (101.1, 101.1), (0.5, 101.1)]:
    outline.Append(MM(x), MM(y))
board.Add(zone)

filler = pcbnew.ZONE_FILLER(board)
filler.Fill(board.Zones())
pcbnew.SaveBoard(BOARD, board)
print("saved", BOARD)
print("tracks", len(board.GetTracks()), "zones", len(board.Zones()))
