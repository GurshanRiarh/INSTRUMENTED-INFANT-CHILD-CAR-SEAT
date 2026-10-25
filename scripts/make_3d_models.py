#!/usr/bin/env python3
"""Generate approximate STEP models for the custom PSM sensor footprints.

Run with the CadQuery-equipped venv:
    /tmp/opencode/kicad-venv/bin/python scripts/make_3d_models.py
"""
import os
import cadquery as cq

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT1 = os.path.join(BASE, 'hardware', 'libraries', 'psm.3dshapes')
OUT2 = os.path.join(BASE, 'hardware', 'psm-v3', 'libraries', 'psm.3dshapes')

def sensor(name, L, W, H, win_w, win_h, win_x=0.0, win_y=0.0):
    body = (cq.Workplane('XY').box(L, W, H).translate((0, 0, H / 2)))
    window = (cq.Workplane('XY').box(win_w, win_h, 0.05)
              .translate((win_x, win_y, H + 0.025)))
    marker = (cq.Workplane('XY').cylinder(0.08, 0.18)
              .translate((-L / 2 + 0.35, -W / 2 + 0.35, H + 0.01)))
    assy = cq.Assembly(name=name)
    assy.add(body, name='body', color=cq.Color(0.10, 0.10, 0.10))
    assy.add(window, name='window', color=cq.Color(0.55, 0.04, 0.04))
    assy.add(marker, name='pin1', color=cq.Color(0.85, 0.85, 0.80))
    for out in (OUT1, OUT2):
        os.makedirs(out, exist_ok=True)
        assy.save(os.path.join(out, name + '.step'), exportType='STEP')
    print('wrote', name)

sensor('VCNL4020', 4.9, 2.4, 0.83, 1.1, 0.55)
sensor('VCNL4030X01', 4.0, 2.36, 0.75, 1.0, 0.50)
