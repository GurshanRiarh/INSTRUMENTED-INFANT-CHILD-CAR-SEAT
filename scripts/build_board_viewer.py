#!/usr/bin/env python3
"""Generate a self-contained board-viewer.html for the PSM V1/V3 designs.

Requires: KiCad CLI (Flatpak), rsvg-convert, ImageMagick (magick).
"""
import os, sys, json, base64, subprocess, tempfile, shutil

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(BASE, '.board-viewer-tmp')
OUT = os.path.join(BASE, 'board-viewer.html')
KICAD = ['flatpak', 'run', '--command=kicad-cli', 'org.kicad.KiCad', 'pcb', 'export', 'svg']

BOARDS = {
    'v1': {
        'name': 'PSM V1',
        'sub': 'Thesis baseline',
        'pcb': 'hardware/psm-v1/psm-v1.kicad_pcb',
        'specs': [('101.6 × 101.6', 'mm'), ('2', 'copper layers'), ('0.2', 'mm polyimide flex'),
                  ('16', 'VCNL4020 sensors'), ('2', 'PCA9548A muxes'), ('68', 'footprints')],
        'note': 'The V1 board reproduces the 4×4 thesis PSM: 16 VCNL4020 sensors at 0x13 on two PCA9548A muxes (0x70/0x71).',
        'captions': {
            'top': ('Top view', '16× VCNL4020 in a 4×4 grid at 25.4 mm pitch, two PCA9548A muxes at the edges, and the 2×5 host header at the bottom.'),
            'bottom': ('Bottom view', 'Ground plane on B.Cu with the signal crossovers. Add stiffeners behind the header and muxes if the flex will be plugged repeatedly.'),
            'fcu': ('Top copper', 'Sensor I²C fan-out, 3V3 distribution, 10 Ω IR-anode networks, and the two mux banks.'),
            'bcu': ('Bottom copper', 'GND plane and crossovers. Minimum track 0.12 mm, clearance 0.15 mm.'),
            'silk': ('Front silkscreen', 'Board identity and array note. Reference designators live on the fab layer to keep the optical area clean.'),
            'outline': ('Board outline', '101.6 × 101.6 mm (4 in square) with 3.2 mm M3 mounting holes at the corners.'),
            'iso': ('3D angled', 'Angled render of the V1 flex mat. The two PCA9548A muxes sit at the edges; the 2×5 host header is at the bottom. The silicone layer is not modeled.'),
            'top3d': ('3D top', 'Top render: 16 approximate VCNL4020 packages, two muxes, the header, and the passive network. The flex is shown flat.'),
            'bottom3d': ('3D bottom', 'Bottom render: no parts; through-hole header pins and vias are visible. The flex is shown flat.'),
        },
    },
    'tile': {
        'name': 'PSM V3 tile',
        'sub': 'Modular sensor tile',
        'pcb': 'hardware/psm-v3/tile/psm-v3-tile.kicad_pcb',
        'specs': [('30 × 30', 'mm'), ('2', 'copper layers'), ('0.2', 'mm polyimide flex'),
                  ('4', 'VCNL4030X01 sensors'), ('21', 'footprints'), ('4', 'M2 holes')],
        'note': 'Each tile carries four VCNL4030X01 sensors at the four factory addresses 0x60/0x51/0x40/0x41. One mux channel serves a whole tile.',
        'captions': {
            'top': ('Top view', 'Four VCNL4030X01 sensors in a 2×2 grid, local pull-ups, decoupling, and the 6-pin 1.27 mm tile connector.'),
            'bottom': ('Bottom view', 'Ground plane and routing on B.Cu. The sealing-ring guide is on Dwgs.User; vias are tented/plugged.'),
            'fcu': ('Top copper', 'The four sensor buses, IR-anode decoupling, and the tile connector.'),
            'bcu': ('Bottom copper', 'GND plane and crossovers. The tile is 30 × 30 mm on 0.2 mm polyimide flex.'),
            'silk': ('Front silkscreen', 'Tile identity and the sealing/coating note.'),
            'outline': ('Board outline', '30 × 30 mm outline with four 2.2 mm M2 holes. Panelize with fiducials for assembly.'),
            'iso': ('3D angled', 'Angled render of one 30 × 30 mm tile with four VCNL4030X01 sensors and the 1.27 mm tile connector.'),
            'top3d': ('3D top', 'Top render: four sensor packages, decoupling, pull-ups, and the tile connector.'),
            'bottom3d': ('3D bottom', 'Bottom render: the flex is shown flat; the sealing ring is a PCB guide, not a 3D part.'),
        },
    },
    'hub': {
        'name': 'PSM V3 hub',
        'sub': 'One mux, four tile ports',
        'pcb': 'hardware/psm-v3/hub/psm-v3-hub.kicad_pcb',
        'specs': [('60 × 40', 'mm'), ('2', 'copper layers'), ('1.6', 'mm FR4'),
                  ('1', 'PCA9548A mux'), ('4', 'tile ports'), ('28', 'footprints')],
        'note': 'The hub has one PCA9548A at 0x70, four tile ports on channels 0–3, an ESD array on the upstream I²C, and a host header.',
        'captions': {
            'top': ('Top view', 'PCA9548A at 0x70, USBLC6 ESD array, four tile ports on channels 0–3, host header, and power LED.'),
            'bottom': ('Bottom view', 'GND plane and routing. The gasket outline is on Dwgs.User; use a sealed enclosure for vehicle work.'),
            'fcu': ('Top copper', 'Upstream I²C, four tile-channel buses, ESD, pull-ups, and power filtering.'),
            'bcu': ('Bottom copper', 'GND plane and crossovers. The hub is 60 × 40 mm on 1.6 mm FR4.'),
            'silk': ('Front silkscreen', 'Hub identity and the tile-port labels.'),
            'outline': ('Board outline', '60 × 40 mm outline with two M3 mounting holes. Add panel fiducials for factory assembly.'),
            'iso': ('3D angled', 'Angled render of the hub: PCA9548A, ESD array, four tile ports, and the host header.'),
            'top3d': ('3D top', 'Top render: the one-mux hub with four tile ports on channels 0–3.'),
            'bottom3d': ('3D bottom', 'Bottom render: the gasket outline and mounting holes; the enclosure is not modeled.'),
        },
    },
}

VIEWS = [
    ('top', 'Top', ['F.Cu', 'F.SilkS', 'Edge.Cuts'], False, 1400),
    ('bottom', 'Bottom', ['B.Cu', 'B.SilkS', 'Edge.Cuts'], True, 1400),
    ('fcu', 'Top copper', ['F.Cu', 'Edge.Cuts'], False, 1400),
    ('bcu', 'Bottom copper', ['B.Cu', 'Edge.Cuts'], True, 1400),
    ('silk', 'Silkscreen', ['F.SilkS', 'Edge.Cuts'], False, 1400),
    ('outline', 'Outline', ['Edge.Cuts'], False, 1400),
]

VIEWS3D = [
    ('iso', '3D angled', 'top', '-35,0,35', True, 1200, 1000),
    ('top3d', '3D top', 'top', None, False, 1200, 1200),
    ('bottom3d', '3D bottom', 'bottom', None, False, 1200, 1200),
]

SCHEMS = {
    'v1': ('PSM V1 — full schematic', '16 sensors, two PCA9548A muxes, R1–R20, C1–C20, and J1. ERC: 0 violations.',
           'docs/psm-v1-schematic.png', 'docs/psm-v1-schematic.pdf'),
    'tile': ('PSM V3 tile — full schematic', 'U1–U4, C1–C9, R1–R3, and J1. ERC: 0 violations.',
             'docs/psm-v3-tile-schematic.png', 'docs/psm-v3-tile-schematic.pdf'),
    'hub': ('PSM V3 hub — full schematic', 'U1, U2, D1, C1–C7, R1–R5, and J1–J5. ERC: 0 violations.',
            'docs/psm-v3-hub-schematic.png', 'docs/psm-v3-hub-schematic.pdf'),
}

def run(cmd, **kw):
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, **kw)

def make_webp(board_key, view_key, layers, mirror, width):
    board = BOARDS[board_key]
    svg = os.path.join(TMP, f'{board_key}-{view_key}.svg')
    png = os.path.join(TMP, f'{board_key}-{view_key}.png')
    webp = os.path.join(TMP, f'{board_key}-{view_key}.webp')
    cmd = KICAD + ['--output', svg, '--layers', ','.join(layers),
                   '--page-size-mode', '2', '--exclude-drawing-sheet',
                   '--mode-single', '--scale', '1']
    if mirror:
        cmd.append('--mirror')
    cmd.append(os.path.join(BASE, board['pcb']))
    run(cmd)
    run(['rsvg-convert', '-f', 'png', '-w', str(width), '-o', png, svg])
    run(['magick', png, '-quality', '84', webp])
    w, h = subprocess.check_output(['magick', 'identify', '-format', '%w %h', png], text=True).split()
    data = base64.b64encode(open(webp, 'rb').read()).decode('ascii')
    return {'src': 'data:image/webp;base64,' + data, 'w': int(w), 'h': int(h)}

def make_3d(board_key, view_key, side, rotate, perspective, width, height):
    board = BOARDS[board_key]
    png = os.path.join(TMP, f'{board_key}-{view_key}.png')
    webp = os.path.join(TMP, f'{board_key}-{view_key}.webp')
    cmd = ['flatpak', 'run', '--command=kicad-cli', 'org.kicad.KiCad', 'pcb', 'render',
           '--output', png, '--side', side, '--width', str(width), '--height', str(height),
           '--quality', 'high', '--background', 'transparent']
    if rotate:
        cmd += ['--rotate', rotate]
    if perspective:
        cmd += ['--perspective']
    cmd.append(os.path.join(BASE, board['pcb']))
    run(cmd)
    run(['magick', png, '-quality', '82', webp])
    data = base64.b64encode(open(webp, 'rb').read()).decode('ascii')
    return {'src': 'data:image/webp;base64,' + data, 'w': width, 'h': height}

def image_data_uri(path):
    return 'data:image/png;base64,' + base64.b64encode(open(path, 'rb').read()).decode('ascii')

def build_data():
    data = {}
    for key, board in BOARDS.items():
        views = {}
        for vk, label, side, rotate, perspective, width, height in VIEWS3D:
            print('render 3d', key, vk)
            views[vk] = make_3d(key, vk, side, rotate, perspective, width, height)
            views[vk]['t'], views[vk]['c'] = board['captions'][vk]
        for vk, label, layers, mirror, width in VIEWS:
            print('render', key, vk)
            views[vk] = make_webp(key, vk, layers, mirror, width)
            views[vk]['t'], views[vk]['c'] = board['captions'][vk]
        data[key] = {
            'name': board['name'], 'sub': board['sub'], 'note': board['note'],
            'specs': board['specs'], 'views': views,
        }
    schems = {}
    for key, (title, cap, png, pdf) in SCHEMS.items():
        w, h = subprocess.check_output(['magick', 'identify', '-format', '%w %h', os.path.join(BASE, png)], text=True).split()
        schems[key] = {'t': title, 'c': cap, 'src': image_data_uri(os.path.join(BASE, png)),
                       'w': int(w), 'h': int(h), 'pdf': pdf}
    return data, schems

HTML = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>PSM Board Viewer</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Barlow+Semi+Condensed:wght@500;600;700&family=Barlow:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
:root {
  --bg: #eef1f4; --surface: #ffffff; --ink: #15212c; --muted: #586977;
  --line: #d2d9e0; --accent: #a8561f; --accent-soft: #f3e3d6; --good: #2f7a4a;
  --well: #001023; --well-ink: #d9e2ea;
  --cu-f: #c83434; --cu-b: #4d7fc4; --diel: #c9b98a;
  --font-display: "Barlow Semi Condensed", "Arial Narrow", system-ui, sans-serif;
  --font-body: "Barlow", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
  color-scheme: light;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0a131b; --surface: #101c26; --ink: #e2e9ef; --muted: #93a4b2; --line: #22323f;
    --accent: #e3925a; --accent-soft: #2c1d13; --good: #6cc48d; --diel: #8a7c55; color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #0a131b; --surface: #101c26; --ink: #e2e9ef; --muted: #93a4b2; --line: #22323f;
  --accent: #e3925a; --accent-soft: #2c1d13; --good: #6cc48d; --diel: #8a7c55; color-scheme: dark;
}
* { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }
body { margin: 0; background: var(--bg); color: var(--ink); font-family: var(--font-body); font-size: 16px; line-height: 1.55; padding-inline: 16px; padding-block: 0 64px; }
img { max-width: 100%; }
[hidden] { display: none !important; }
.wrap { max-width: 1120px; margin: 0 auto; display: grid; gap: 64px; }
h1,h2,h3 { font-family: var(--font-display); text-wrap: balance; margin: 0; line-height: 1.1; }
h1 { font-size: clamp(2.4rem, 6vw, 3.6rem); font-weight: 700; letter-spacing: .01em; }
h2 { font-size: 1.8rem; font-weight: 600; }
h3 { font-size: 1.15rem; font-weight: 600; }
p { margin: 0; max-width: 68ch; }
a { color: var(--accent); }
code,.mono { font-family: var(--font-mono); font-size: .86em; }
.eyebrow { font-family: var(--font-mono); font-size: .75rem; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }
header { padding-block: 44px 0; display: grid; gap: 14px; }
.lede { font-size: 1.12rem; }
.specs { display: flex; flex-wrap: wrap; gap: 8px 22px; font-family: var(--font-mono); font-size: .85rem; color: var(--muted); font-variant-numeric: tabular-nums; }
.specs b { color: var(--ink); font-weight: 500; }
.status { display: inline-flex; align-items: center; gap: 8px; font-size: .92rem; color: var(--muted); }
.status::before { content: ""; width: 9px; height: 9px; border-radius: 50%; background: var(--accent); flex: none; }
.toc { display: flex; flex-wrap: wrap; gap: 6px 18px; font-size: .92rem; }
section { display: grid; gap: 18px; scroll-margin-top: 16px; }
.sec-head { display: grid; gap: 6px; }
.tabs { display: flex; flex-wrap: wrap; gap: 6px; }
.tab { font: 500 .9rem var(--font-body); color: var(--ink); background: var(--surface); border: 1px solid var(--line); border-radius: 6px; padding: 7px 13px; cursor: pointer; }
.tab:hover { border-color: var(--accent); }
.tab[aria-selected="true"] { background: var(--ink); color: var(--bg); border-color: var(--ink); }
.tab:focus-visible,.zoomable:focus-visible,a:focus-visible,button:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }
.board-tabs { margin-bottom: 2px; }
.bench { display: grid; grid-template-columns: minmax(0,1fr) 310px; gap: 20px; align-items: start; }
.well { background: var(--well); border-radius: 10px; overflow: hidden; position: relative; min-width: 0; display: grid; place-items: center; padding: 10px; }
.well.paper { background: #f5f4f0; }
.well img { display: block; width: 100%; height: auto; }
.zoomable { cursor: zoom-in; }
.hint { position: absolute; right: 10px; bottom: 10px; font: .72rem var(--font-mono); color: var(--well-ink); background: rgba(0,16,35,.72); padding: 3px 8px; border-radius: 4px; pointer-events: none; }
.rail { display: grid; gap: 10px; min-width: 0; }
.rail p { font-size: .95rem; }
.note { font-size: .88rem; color: var(--muted); }
.stack { display: grid; gap: 2px; }
.layer { display: grid; grid-template-columns: 14px minmax(0,1fr) auto; gap: 10px; align-items: center; background: transparent; border: 1px solid transparent; border-radius: 5px; padding: 4px 6px; font: .85rem var(--font-body); color: var(--ink); text-align: left; width: 100%; }
button.layer { cursor: pointer; }
button.layer:hover { border-color: var(--line); background: var(--surface); }
button.layer[aria-pressed="true"] { border-color: var(--accent); background: var(--accent-soft); }
.swatch { width: 14px; border-radius: 2px; }
.layer .t { font-family: var(--font-mono); font-size: .75rem; color: var(--muted); }
.layer.diel { color: var(--muted); }
.layer.diel .swatch { background: var(--diel); opacity: .55; }
.node { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px; display: grid; gap: 6px; align-content: start; min-width: 0; }
.node .ref { font: 500 .75rem var(--font-mono); color: var(--accent); letter-spacing: .05em; }
.node p { font-size: .9rem; color: var(--muted); }
.arrow { display: grid; place-items: center; color: var(--muted); font-family: var(--font-mono); }
.chain-row { display: grid; grid-template-columns: minmax(0,1fr) 28px minmax(0,1fr) 28px minmax(0,1fr) 28px minmax(0,1fr); margin-bottom: 12px; }
.chain-label { font: 500 .75rem var(--font-mono); color: var(--muted); letter-spacing: .08em; text-transform: uppercase; margin: 10px 0 4px; }
.verdict { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; }
.panel { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 18px; display: grid; gap: 12px; align-content: start; min-width: 0; }
.panel h3 { display: flex; align-items: center; gap: 8px; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex: none; }
.dot.done { background: var(--good); }
.dot.open { background: transparent; border: 2px solid var(--accent); }
.panel ul { margin: 0; padding-left: 1.1em; display: grid; gap: 8px; font-size: .95rem; }
.panel li::marker { color: var(--muted); }
.prose { display: grid; gap: 12px; }
.prose p { font-size: 1rem; }
.ways { display: grid; grid-template-columns: repeat(2, minmax(0,1fr)); gap: 14px; }
.way { background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 16px; display: grid; gap: 8px; align-content: start; min-width: 0; }
.way p { font-size: .93rem; }
.tag { font: 500 .7rem var(--font-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
.tbl { overflow-x: auto; }
table { border-collapse: collapse; font-size: .88rem; min-width: 420px; }
th,td { text-align: left; padding: 6px 14px 6px 0; border-bottom: 1px solid var(--line); vertical-align: top; }
th { font: 500 .72rem var(--font-mono); letter-spacing: .08em; text-transform: uppercase; color: var(--muted); }
td.mono { white-space: nowrap; font-variant-numeric: tabular-nums; }
footer { font-size: .85rem; color: var(--muted); border-top: 1px solid var(--line); padding-top: 16px; display: flex; flex-wrap: wrap; gap: 6px 20px; }
.lightbox { position: fixed; inset: 0; background: rgba(0,8,18,.94); z-index: 10; display: grid; grid-template-rows: auto minmax(0,1fr); padding-top: env(safe-area-inset-top,0px); }
.lb-bar { display: flex; justify-content: space-between; align-items: center; gap: 12px; padding: 10px 16px; color: #d9e2ea; font: .85rem var(--font-mono); }
.lb-bar button { font: 500 .85rem var(--font-body); background: #15273a; color: #e6edf3; border: 1px solid #2c4258; border-radius: 6px; padding: 6px 12px; cursor: pointer; }
.lb-scroll { overflow: auto; display: grid; place-items: center; padding: 12px; }
.lb-scroll img { max-width: 100%; max-height: 100%; cursor: zoom-in; }
.lb-scroll.full { place-items: start; }
.lb-scroll.full img { max-width: none; max-height: none; cursor: zoom-out; }
@media (max-width: 860px) {
  .bench { grid-template-columns: minmax(0,1fr); }
  .chain-row { grid-template-columns: minmax(0,1fr); }
  .chain-row .arrow { transform: rotate(90deg); height: 26px; }
  .ways,.verdict { grid-template-columns: minmax(0,1fr); }
}
</style>
</head>
<body>
<div class="wrap">
  <header>
    <span class="eyebrow">Pressure-sensitive mat · thesis baseline and V3</span>
    <h1>PSM Board Viewer</h1>
    <p class="lede">Two generations of the instrumented car-seat pressure mat: a 4×4 VCNL4020 baseline and a modular VCNL4030X01 tile/hub revision. Browse the copper, silkscreen, and full schematics below.</p>
    <div class="specs" id="specs"></div>
    <span class="status" id="status">Schematics, layouts and checks are complete. No board has been fabricated or tested.</span>
    <nav class="toc" aria-label="Sections">
      <a href="#boards">Board views</a><a href="#how">How it works</a><a href="#schematic">Schematics</a><a href="#checks">Checks</a><a href="#explore">Explore</a>
    </nav>
  </header>

  <section id="boards" aria-labelledby="h-boards">
    <div class="sec-head">
      <span class="eyebrow">Layout</span>
      <h2 id="h-boards">The boards</h2>
      <p>Pick a board, then a view. The 3D renders use approximate sensor models; the 2D top/bottom views are composite plots, and the copper/outline views isolate one layer at a time.</p>
    </div>
    <div class="tabs board-tabs" role="tablist" aria-label="Board">
      <button class="tab" role="tab" data-board="v1" aria-selected="true">PSM V1 · thesis baseline</button>
      <button class="tab" role="tab" data-board="tile" aria-selected="false">PSM V3 · sensor tile</button>
      <button class="tab" role="tab" data-board="hub" aria-selected="false">PSM V3 · hub</button>
    </div>
    <div class="tabs" role="tablist" aria-label="Board view">
      <button class="tab" role="tab" data-view="iso" aria-selected="true">3D angled</button>
      <button class="tab" role="tab" data-view="top3d" aria-selected="false">3D top</button>
      <button class="tab" role="tab" data-view="bottom3d" aria-selected="false">3D bottom</button>
      <button class="tab" role="tab" data-view="top" aria-selected="false">Top</button>
      <button class="tab" role="tab" data-view="bottom" aria-selected="false">Bottom</button>
      <button class="tab" role="tab" data-view="fcu" aria-selected="false">Top copper</button>
      <button class="tab" role="tab" data-view="bcu" aria-selected="false">Bottom copper</button>
      <button class="tab" role="tab" data-view="silk" aria-selected="false">Silkscreen</button>
      <button class="tab" role="tab" data-view="outline" aria-selected="false">Outline</button>
    </div>
    <div class="bench">
      <div class="well">
        <img id="board-img" class="zoomable" tabindex="0" alt="PSM board view">
        <span class="hint">click to enlarge</span>
      </div>
      <div class="rail">
        <div class="stack" role="group" aria-label="Board notes">
          <div class="layer"><span class="swatch" style="height:8px;background:var(--cu-f)"></span><span>Top copper</span><span class="t">F.Cu</span></div>
          <div class="layer diel"><span class="swatch" style="height:14px"></span><span>Polyimide / FR-4</span><span class="t">substrate</span></div>
          <div class="layer"><span class="swatch" style="height:8px;background:var(--cu-b)"></span><span>Bottom copper</span><span class="t">B.Cu</span></div>
        </div>
        <h3 id="board-title"></h3>
        <p id="board-cap"></p>
        <p class="note" id="board-note"></p>
        <p class="note">3D sensor models are approximate. Silicone domes, cables, and the car seat are not modeled.</p>
      </div>
    </div>
  </section>

  <section id="how" aria-labelledby="h-how">
    <div class="sec-head">
      <span class="eyebrow">Signal chain</span>
      <h2 id="h-how">How it works</h2>
      <p>The PSM is a passive sensor array: the host selects a mux channel, reads the proximity sensor, and turns the pressure map into occupancy, posture, and respiration signals.</p>
    </div>
    <div class="chain-label">PSM V1 · 16 sensors, two muxes</div>
    <div class="chain-row">
      <div class="node"><span class="ref">HOST</span><h3>Tiva / LaunchPad or Raspberry Pi</h3><p>3V3, GND, SDA, SCL, INT_N, MUX_RST on a 2×5 header.</p></div>
      <div class="arrow" aria-hidden="true">→</div>
      <div class="node"><span class="ref">U17 / U18 · PCA9548A</span><h3>Two 8-channel muxes</h3><p>0x70 and 0x71. One channel per sensor because every VCNL4020 is at 0x13.</p></div>
      <div class="arrow" aria-hidden="true">→</div>
      <div class="node"><span class="ref">U1–U16 · VCNL4020</span><h3>4×4 proximity array</h3><p>IR proximity through the silicone domes; 25.4 mm pitch.</p></div>
      <div class="arrow" aria-hidden="true">→</div>
      <div class="node"><span class="ref">OUTPUT</span><h3>Pressure map</h3><p>Occupancy, posture, movement, and respiration-rate experiments.</p></div>
    </div>
    <div class="chain-label">PSM V3 · 16 sensors, one mux, four tiles</div>
    <div class="chain-row">
      <div class="node"><span class="ref">HOST</span><h3>Raspberry Pi / ESP32 / Tiva</h3><p>Same 2×5 host pinout as V1.</p></div>
      <div class="arrow" aria-hidden="true">→</div>
      <div class="node"><span class="ref">U1 · PCA9548A</span><h3>One hub mux</h3><p>0x70. Channels 0–3 go to four tile ports; channels 4–7 are spare.</p></div>
      <div class="arrow" aria-hidden="true">→</div>
      <div class="node"><span class="ref">4 tiles × 4 VCNL4030X01</span><h3>Addressable tiles</h3><p>Each tile has 0x60/0x51/0x40/0x41, so one mux channel reads four sensors.</p></div>
      <div class="arrow" aria-hidden="true">→</div>
      <div class="node"><span class="ref">OUTPUT</span><h3>Pressure map</h3><p>Modular tiles follow the car-seat contour and can be replaced individually.</p></div>
    </div>
    <div class="prose">
      <p class="note">The boards only implement the pressure modality. The camera, app, and alert pipeline are separate subsystems in the proposal.</p>
    </div>
  </section>

  <section id="schematic" aria-labelledby="h-sch">
    <div class="sec-head">
      <span class="eyebrow">Schematic</span>
      <h2 id="h-sch">The circuit, sheet by sheet</h2>
      <p>Every electrical component is drawn. Test points and mounting holes are PCB-only features. Click an image to read it at full size.</p>
    </div>
    <div class="tabs" role="tablist" aria-label="Schematic">
      <button class="tab" role="tab" data-sheet="v1" aria-selected="true">V1 · 4×4 array</button>
      <button class="tab" role="tab" data-sheet="tile" aria-selected="false">V3 · sensor tile</button>
      <button class="tab" role="tab" data-sheet="hub" aria-selected="false">V3 · hub</button>
    </div>
    <div class="bench">
      <div class="well paper">
        <img id="sch-img" class="zoomable" tabindex="0" alt="PSM schematic">
        <span class="hint">click to enlarge</span>
      </div>
      <div class="rail">
        <h3 id="sch-title"></h3>
        <p id="sch-cap"></p>
        <p class="note"><a id="sch-pdf" href="#">Open the PDF</a></p>
      </div>
    </div>
  </section>

  <section id="checks" aria-labelledby="h-checks">
    <div class="sec-head">
      <span class="eyebrow">Status</span>
      <h2 id="h-checks">Checks and open questions</h2>
      <p>No board has been built. These are the design-file checks that pass, and the things only a fabricated board can answer.</p>
    </div>
    <div class="verdict">
      <div class="panel">
        <h3><span class="dot done" aria-hidden="true"></span>Checked on the design</h3>
        <ul>
          <li><b>ERC:</b> 0 violations on the V1, V3 tile, and V3 hub schematics.</li>
          <li><b>DRC:</b> 0 violations and 0 unconnected items on all three PCBs.</li>
          <li><b>Schematic vs PCB:</b> 0 pad/net mismatches.</li>
          <li><b>Fabrication outputs:</b> Gerbers, drill, position files, BOMs, and PDF/SVG previews are generated.</li>
          <li><b>Libraries:</b> custom VCNL4020/VCNL4030X01 footprints and a shared PSM symbol library are included.</li>
        </ul>
      </div>
      <div class="panel">
        <h3><span class="dot open" aria-hidden="true"></span>Only a real board can answer</h3>
        <ul>
          <li>Does every mux channel and sensor address respond on the first power-up?</li>
          <li>Is the pressure response linear and repeatable after the silicone is bonded?</li>
          <li>Does the flex survive repeated bending and connector insertion?</li>
          <li>Does the tile/hub fit the car-seat contour and harness without changing fit?</li>
          <li>Does the full system meet the proposal's accuracy, latency, and false-alarm targets?</li>
        </ul>
      </div>
    </div>
    <div class="prose">
      <p><b>Not certified.</b> These are research prototypes. They are not medical devices and are not certified to CMVSS 213.1. Do not use them with an infant in a vehicle until the mechanical fit, electrical safety, and sensor performance have been validated.</p>
    </div>
  </section>

  <section id="explore" aria-labelledby="h-ex">
    <div class="sec-head">
      <span class="eyebrow">Source</span>
      <h2 id="h-ex">Explore the design yourself</h2>
    </div>
    <div class="ways">
      <div class="way">
        <span class="tag">Everything</span>
        <h3>GitHub repository</h3>
        <p>The KiCad projects, custom libraries, fabrication outputs, BOMs, and documentation.</p>
        <p><a href="https://github.com/GurshanRiarh/INSTRUMENTED-INFANT-CHILD-CAR-SEAT" target="_blank" rel="noopener">GurshanRiarh/INSTRUMENTED-INFANT-CHILD-CAR-SEAT</a></p>
      </div>
      <div class="way">
        <span class="tag">In the browser</span>
        <h3>KiCanvas</h3>
        <p>Pan and zoom the KiCad boards straight from GitHub.</p>
        <p><a href="https://kicanvas.org/?github=https://github.com/GurshanRiarh/INSTRUMENTED-INFANT-CHILD-CAR-SEAT/blob/main/hardware/psm-v1/psm-v1.kicad_pcb" target="_blank" rel="noopener">V1 board</a> · <a href="https://kicanvas.org/?github=https://github.com/GurshanRiarh/INSTRUMENTED-INFANT-CHILD-CAR-SEAT/blob/main/hardware/psm-v3/tile/psm-v3-tile.kicad_pcb" target="_blank" rel="noopener">V3 tile</a> · <a href="https://kicanvas.org/?github=https://github.com/GurshanRiarh/INSTRUMENTED-INFANT-CHILD-CAR-SEAT/blob/main/hardware/psm-v3/hub/psm-v3-hub.kicad_pcb" target="_blank" rel="noopener">V3 hub</a></p>
      </div>
      <div class="way">
        <span class="tag">Desktop</span>
        <h3>KiCad</h3>
        <p>Open <code>hardware/psm-v1/psm-v1.kicad_pro</code>, <code>hardware/psm-v3/tile/psm-v3-tile.kicad_pro</code>, or <code>hardware/psm-v3/hub/psm-v3-hub.kicad_pro</code> in KiCad 9 or newer.</p>
        <p><a href="https://www.kicad.org/download/" target="_blank" rel="noopener">kicad.org</a></p>
      </div>
      <div class="way">
        <span class="tag">Documents</span>
        <h3>PDFs</h3>
        <p>The full schematics and board fabrication previews.</p>
        <p><a href="docs/psm-v1-schematic.pdf">V1 schematic</a> · <a href="docs/psm-v3-tile-schematic.pdf">V3 tile schematic</a> · <a href="docs/psm-v3-hub-schematic.pdf">V3 hub schematic</a></p>
      </div>
    </div>
  </section>

  <footer>
    <span>PSM V1 / V3</span>
    <span>Designed in KiCad 10.0.7</span>
    <span>Images rendered from the design files, October 2026</span>
  </footer>
</div>

<div class="lightbox" id="lightbox" hidden role="dialog" aria-modal="true" aria-label="Enlarged image">
  <div class="lb-bar"><span id="lb-label"></span><span style="display:flex;gap:8px"><button type="button" id="lb-zoom">Actual size</button><button type="button" id="lb-close">Close</button></span></div>
  <div class="lb-scroll" id="lb-scroll"><img id="lb-img" alt=""></div>
</div>

<script>
const BOARDS = __BOARDS__;
const SCHEMS = __SCHEMS__;
let state = { board: 'v1', view: 'iso', sheet: 'v1' };
const $ = id => document.getElementById(id);
function setTabs(attr, value) {
  document.querySelectorAll('[data-' + attr + ']').forEach(b => b.setAttribute('aria-selected', b.dataset[attr] === value ? 'true' : 'false'));
}
function renderBoard() {
  const b = BOARDS[state.board], v = b.views[state.view];
  $('board-img').src = v.src;
  $('board-img').alt = b.name + ', ' + v.t;
  $('board-img').width = v.w; $('board-img').height = v.h;
  $('board-title').textContent = b.name + ' — ' + v.t;
  $('board-cap').textContent = v.c;
  $('board-note').textContent = b.note;
  $('specs').innerHTML = b.specs.map(s => '<span><b>' + s[0] + '</b> ' + s[1] + '</span>').join('');
  setTabs('board', state.board); setTabs('view', state.view);
}
function renderSchematic() {
  const s = SCHEMS[state.sheet];
  $('sch-img').src = s.src; $('sch-img').alt = s.t;
  $('sch-img').width = s.w; $('sch-img').height = s.h;
  $('sch-title').textContent = s.t; $('sch-cap').textContent = s.c;
  $('sch-pdf').href = s.pdf;
  setTabs('sheet', state.sheet);
}
document.querySelectorAll('[data-board]').forEach(btn => btn.addEventListener('click', () => { state.board = btn.dataset.board; renderBoard(); }));
document.querySelectorAll('[data-view]').forEach(btn => btn.addEventListener('click', () => { state.view = btn.dataset.view; renderBoard(); }));
document.querySelectorAll('[data-sheet]').forEach(btn => btn.addEventListener('click', () => { state.sheet = btn.dataset.sheet; renderSchematic(); }));
renderBoard(); renderSchematic();

const lb = $('lightbox'), lbImg = $('lb-img'), lbScroll = $('lb-scroll'), lbZoom = $('lb-zoom'), lbLabel = $('lb-label');
let lastFocus = null;
function setFull(on) { lbScroll.classList.toggle('full', on); lbZoom.textContent = on ? 'Fit to screen' : 'Actual size'; }
function openLb(img) { lastFocus = img; lbImg.src = img.src; lbImg.alt = img.alt; lbLabel.textContent = img.alt; setFull(false); lb.hidden = false; $('lb-close').focus(); }
function closeLb() { lb.hidden = true; lbImg.removeAttribute('src'); if (lastFocus) lastFocus.focus(); }
document.querySelectorAll('.zoomable').forEach(img => {
  img.addEventListener('click', () => openLb(img));
  img.addEventListener('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); openLb(img); } });
});
lbZoom.addEventListener('click', () => setFull(!lbScroll.classList.contains('full')));
lbImg.addEventListener('click', () => setFull(!lbScroll.classList.contains('full')));
$('lb-close').addEventListener('click', closeLb);
lb.addEventListener('click', e => { if (e.target === lbScroll && !lbScroll.classList.contains('full')) closeLb(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape' && !lb.hidden) closeLb(); });
</script>
</body>
</html>
'''

def main():
    if os.path.isdir(TMP):
        shutil.rmtree(TMP)
    os.makedirs(TMP)
    data, schems = build_data()
    html = HTML.replace('__BOARDS__', json.dumps(data, separators=(',', ':'))).replace('__SCHEMS__', json.dumps(schems, separators=(',', ':')))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    shutil.rmtree(TMP)
    print('wrote', OUT, f'{os.path.getsize(OUT)/1e6:.2f} MB')

if __name__ == '__main__':
    main()
