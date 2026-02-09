"""
EXPORT MODEL V10 TO AUTOCAD DXF — MEGA BRACE VERSION
=====================================================
Creates DXF files:
  1. twin_towers_v10_autocad.dxf  — Full 3D wireframe + annotations
  2. twin_towers_v10_plan.dxf     — Ground floor XY plan
  3. twin_towers_v10_front.dxf    — Front elevation (XZ, y-min face)
  4. twin_towers_v10_side.dxf     — Side elevation (YZ, x-min face) — shows mega braces
"""

import numpy as np
import pandas as pd
import ezdxf
from ezdxf import colors
from pathlib import Path

print("=" * 70)
print("EXPORTING MODEL V10 (MEGA BRACE) TO AUTOCAD DXF")
print("=" * 70)

# ── data ────────────────────────────────────────────────────────────
DATA_DIR    = Path(__file__).parent.parent / 'data'
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

pos_df  = pd.read_csv(DATA_DIR / 'twin_position_matrix_v10.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix_v10.csv')

print(f"Nodes:    {len(pos_df)}")
print(f"Elements: {len(conn_df)}")

# coordinate lookup  {node_id: (x, y, z)}
coords = {}
for _, r in pos_df.iterrows():
    coords[int(r['node_id'])] = (r['x'], r['y'], r['z'])

# ── layer colours (ACI) ────────────────────────────────────────────
LAYER_COLORS = {
    'column':        4,   # Cyan
    'beam_x':        3,   # Green
    'beam_y':        2,   # Yellow
    'brace_xz':      6,   # Magenta
    'brace_yz':      1,   # Red
    'floor_brace':   5,   # Blue
    'bridge_beam':  30,   # Orange
    'bridge_column':30,
    'bridge_truss': 40,
    'bridge_rigid': 50,
}

# ═══════════════════════════════════════════════════════════════════
# 1)  FULL 3-D MODEL
# ═══════════════════════════════════════════════════════════════════
print("\n— Creating 3-D model DXF —")
doc3d = ezdxf.new('R2010', setup=True)
msp3d = doc3d.modelspace()

for lname, col in LAYER_COLORS.items():
    doc3d.layers.add(lname, color=col)
doc3d.layers.add('annotations', color=7)
doc3d.layers.add('dimensions',  color=4)
doc3d.layers.add('floor_levels', color=3)

elem_counts = {}
for _, row in conn_df.iterrows():
    n1, n2 = int(row['node_i']), int(row['node_j'])
    etype  = row['element_type']
    if n1 not in coords or n2 not in coords:
        continue
    layer = etype if etype in LAYER_COLORS else 'column'
    msp3d.add_line(coords[n1], coords[n2], dxfattribs={'layer': layer})
    elem_counts[etype] = elem_counts.get(etype, 0) + 1

# floor annotations
floor_z = sorted(pos_df['z'].unique())
max_x = pos_df['x'].max()
max_y = pos_df['y'].max()
for i, z in enumerate(floor_z):
    label = "GROUND" if i == 0 else ("ROOF" if i == len(floor_z)-1 else f"F{i}")
    label += f" z={z:.0f}"
    msp3d.add_text(label, dxfattribs={
        'layer': 'floor_levels', 'height': 1.2,
        'insert': (max_x + 4, max_y / 2, z)
    })

# title
title = [
    "DASK 2026 — TWIN TOWERS V10",
    "Mega Brace (Diamond) — YZ System",
    f"Elements: {len(conn_df)}, Nodes: {len(pos_df)}",
    f"Height: {pos_df['z'].max():.0f} cm  |  Scale 1:50",
    "Date: 2026-02-09",
]
ty = -8
for line in title:
    msp3d.add_text(line, dxfattribs={
        'layer': 'annotations', 'height': 2.0, 'insert': (0, ty, 0)})
    ty -= 3.5

f3d = EXPORTS_DIR / 'twin_towers_v10_autocad.dxf'
doc3d.saveas(f3d)
print(f"  Saved: {f3d.name}")
for et, c in sorted(elem_counts.items()):
    print(f"    {et:<20}: {c}")


# ═══════════════════════════════════════════════════════════════════
# helper: create a 2-D projection DXF
# ═══════════════════════════════════════════════════════════════════
def make_2d_dxf(out_path, proj_fn, filter_fn, title_str, node_markers=False):
    """
    proj_fn(p) -> (u, v)          : 3-D→2-D projection
    filter_fn(p1, p2, etype) -> bool : which elements to include
    """
    doc = ezdxf.new('R2010', setup=True)
    msp = doc.modelspace()
    for lname, col in LAYER_COLORS.items():
        doc.layers.add(lname, color=col)
    doc.layers.add('annotations', color=7)
    doc.layers.add('nodes', color=1)

    drawn = 0
    for _, row in conn_df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        etype  = row['element_type']
        if n1 not in coords or n2 not in coords:
            continue
        p1, p2 = coords[n1], coords[n2]
        if not filter_fn(p1, p2, etype):
            continue
        layer = etype if etype in LAYER_COLORS else 'column'
        msp.add_line(proj_fn(p1), proj_fn(p2), dxfattribs={'layer': layer})
        drawn += 1

    if node_markers:
        ground_nodes = pos_df[pos_df['z'] == 0]
        for _, r in ground_nodes.iterrows():
            pt = proj_fn((r['x'], r['y'], r['z']))
            msp.add_circle(pt, radius=0.3, dxfattribs={'layer': 'nodes'})

    # title
    msp.add_text(title_str, dxfattribs={
        'layer': 'annotations', 'height': 2.0, 'insert': (0, -6, 0)})

    doc.saveas(out_path)
    print(f"  Saved: {out_path.name}  ({drawn} elements)")


# ═══════════════════════════════════════════════════════════════════
# 2)  PLAN VIEW  (XY at z=0)
# ═══════════════════════════════════════════════════════════════════
print("\n— Creating plan view (XY) —")
make_2d_dxf(
    EXPORTS_DIR / 'twin_towers_v10_plan.dxf',
    proj_fn   = lambda p: (p[0], p[1]),
    filter_fn = lambda p1, p2, et: (abs(p1[2]) < 0.5 or abs(p2[2]) < 0.5)
                                   and et in ('column','beam_x','beam_y','floor_brace',
                                              'bridge_beam','bridge_column'),
    title_str = "V10 — Ground Floor Plan (XY)",
    node_markers = True,
)


# ═══════════════════════════════════════════════════════════════════
# 3)  FRONT ELEVATION  (XZ, front face y = y_min per tower)
# ═══════════════════════════════════════════════════════════════════
print("\n— Creating front elevation (XZ) —")

y_fronts = {pos_df['y'].min(), 24.3}   # Tower 1 front, Tower 2 front
y_tol = 0.5

def filter_front(p1, p2, et):
    # columns are always on the face if both nodes share the same y
    if et == 'column':
        return any(abs(p1[1] - yf) < y_tol for yf in y_fronts)
    # beams / braces on XZ face
    if et in ('beam_x', 'brace_xz'):
        return (any(abs(p1[1] - yf) < y_tol for yf in y_fronts) and
                any(abs(p2[1] - yf) < y_tol for yf in y_fronts))
    # bridges
    if 'bridge' in et:
        return True
    return False

make_2d_dxf(
    EXPORTS_DIR / 'twin_towers_v10_front.dxf',
    proj_fn   = lambda p: (p[0], p[2]),
    filter_fn = filter_front,
    title_str = "V10 — Front Elevation (XZ, y_min)",
)


# ═══════════════════════════════════════════════════════════════════
# 4)  SIDE ELEVATION  (YZ, left face x = 0.3)  — MEGA BRACE view
# ═══════════════════════════════════════════════════════════════════
print("\n— Creating side elevation (YZ) — shows mega braces —")

x_side = 0.3   # left-most column line
x_tol  = 0.5

def filter_side(p1, p2, et):
    on_face_1 = abs(p1[0] - x_side) < x_tol
    on_face_2 = abs(p2[0] - x_side) < x_tol
    if et == 'column':
        return on_face_1
    if et in ('beam_y', 'brace_yz'):
        return on_face_1 and on_face_2
    # show bridges that cross between towers (project Y,Z)
    if 'bridge' in et:
        return True
    return False

make_2d_dxf(
    EXPORTS_DIR / 'twin_towers_v10_side.dxf',
    proj_fn   = lambda p: (p[1], p[2]),
    filter_fn = filter_side,
    title_str = "V10 — Side Elevation (YZ, x=0.3) — Mega Brace",
)


# ═══════════════════════════════════════════════════════════════════
print("\n" + "=" * 70)
print("AUTOCAD EXPORT COMPLETE —  4 DXF files")
print("=" * 70)
print(f"\n  1. {f3d.name:<40} Full 3-D wireframe")
print(f"  2. twin_towers_v10_plan.dxf{'':<13} Ground floor plan")
print(f"  3. twin_towers_v10_front.dxf{'':<12} Front elevation XZ")
print(f"  4. twin_towers_v10_side.dxf{'':<13} Side elevation YZ (mega brace)")
print(f"\nLayer colour key:")
for lname, col in LAYER_COLORS.items():
    print(f"  {lname:<20}: ACI {col}")
