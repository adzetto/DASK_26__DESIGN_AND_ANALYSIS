"""
Export building structural model to AutoCAD DXF.
  - 3D model in modelspace
  - 2D projection views: Top, Front, Back, Left, Right
    arranged on one drawing sheet
Reads: position_matrix.csv, connectivity_matrix.csv, building_data.npz
"""

import numpy as np
import pandas as pd
import ezdxf
import os

# ---------------------------------------------------------------------------
DATA_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(DATA_DIR, "building_3d.dxf")

# ACI colours
LAYER_CFG = {
    "column":           {"color": 5,  "lw": 50},   # blue
    "beam_x":           {"color": 3,  "lw": 35},   # green
    "beam_y":           {"color": 30, "lw": 35},   # orange
    "brace_xz":         {"color": 1,  "lw": 25},   # red
    "brace_yz":         {"color": 6,  "lw": 25},   # magenta
    "brace_floor":      {"color": 7,  "lw": 18},   # white - floor slab braces
    "brace_space":      {"color": 250, "lw": 35},  # dark gray - 3D space frame braces
    "chevron":          {"color": 6,   "lw": 35},  # magenta
    "core_wall":        {"color": 44,  "lw": 50},  # brown - central core shear walls
    "NODES":            {"color": 7,  "lw": 0},
    "GRID":             {"color": 8,  "lw": 13},
    "ANNO":             {"color": 7,  "lw": 0},
    "OUTLINE":          {"color": 9,  "lw": 25},
    # 2D view layers
    "VIEW_TOP":             {"color": 3, "lw": 25},
    "VIEW_FRONT":           {"color": 5, "lw": 25},
    "VIEW_BACK":            {"color": 5, "lw": 25},
    "VIEW_LEFT":            {"color": 30, "lw": 25},
    "VIEW_RIGHT":           {"color": 30, "lw": 25},
    "VIEW_BRACE_XZ":        {"color": 1, "lw": 18},
    "VIEW_BRACE_YZ":        {"color": 1, "lw": 18},
    "VIEW_BRACE_FLOOR":     {"color": 7, "lw": 13},
    "VIEW_BRACE_SPACE":     {"color": 250, "lw": 25},
    "VIEW_CHEVRON":         {"color": 6,   "lw": 25},
    "VIEW_TITLE":           {"color": 7, "lw": 0},
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("Loading data ...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, "position_matrix.csv"))
conn_df = pd.read_csv(os.path.join(DATA_DIR, "connectivity_matrix.csv"))
npz = np.load(os.path.join(DATA_DIR, "building_data.npz"))

podium_x = npz["podium_x"]
tower_x  = npz["tower_x"]
y_coords = npz["y_coords"]
z_coords = npz["z_coords"]

max_x = float(podium_x[-1])       # 40
max_y = float(y_coords[-1])       # 16
total_h = float(z_coords[-1])     # 153
n_floors = len(z_coords)
# Detect podium floor count from coords
podium_floors = 0
for i, z in enumerate(z_coords):
    if i > 0:
        # check which x coords exist at this floor
        floor_nodes = pos_df[pos_df['floor'] == i]
        if 0.0 in floor_nodes['x'].values:
            podium_floors = i + 1
        else:
            break
    else:
        podium_floors = 1
podium_top_z = float(z_coords[podium_floors - 1])
tx0 = float(tower_x[0])
tx1 = float(tower_x[-1])

print(f"  Nodes: {len(pos_df)}, Elements: {len(conn_df)}")
print(f"  Floors: {n_floors}, Podium: {podium_floors}, Height: {total_h:.0f}m")

# node_id -> (x,y,z)
node_xyz = {}
for _, r in pos_df.iterrows():
    node_xyz[int(r["node_id"])] = (r["x"], r["y"], r["z"])

# ---------------------------------------------------------------------------
# Create DXF
# ---------------------------------------------------------------------------
print("Creating DXF ...")
doc = ezdxf.new("R2010")
msp = doc.modelspace()

for name, cfg in LAYER_CFG.items():
    doc.layers.add(name, color=cfg["color"], lineweight=cfg["lw"])

# ===== PART 1 : 3D MODEL =====
# Offset 3D model to the left so it doesn't overlap with 2D views
MODEL_3D_X_OFFSET = -150  # Move 3D model to the left

print("  3D structural elements ...")
for _, row in conn_df.iterrows():
    p1_orig = node_xyz[int(row["node_i"])]
    p2_orig = node_xyz[int(row["node_j"])]
    p1 = (p1_orig[0] + MODEL_3D_X_OFFSET, p1_orig[1], p1_orig[2])
    p2 = (p2_orig[0] + MODEL_3D_X_OFFSET, p2_orig[1], p2_orig[2])
    msp.add_line(p1, p2, dxfattribs={"layer": row["element_type"]})

# Nodes
for nid, xyz in node_xyz.items():
    msp.add_point((xyz[0] + MODEL_3D_X_OFFSET, xyz[1], xyz[2]), dxfattribs={"layer": "NODES"})

# Grid at z=0
all_x = sorted(set(podium_x.tolist() + tower_x.tolist()))
for x in all_x:
    msp.add_line((x + MODEL_3D_X_OFFSET, 0, 0), (x + MODEL_3D_X_OFFSET, max_y, 0), dxfattribs={"layer": "GRID"})
for y in y_coords:
    msp.add_line((0 + MODEL_3D_X_OFFSET, y, 0), (max_x + MODEL_3D_X_OFFSET, y, 0), dxfattribs={"layer": "GRID"})

# Floor annotations
for i, z in enumerate(z_coords):
    msp.add_text(f"FL {i} (z={z:.0f}m)", height=1.0,
                 dxfattribs={"layer": "ANNO", "insert": (-10 + MODEL_3D_X_OFFSET, -3, z)})

# Outline boxes
def box_wire(x0, y0, z0, x1, y1, z1, layer):
    b = [(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)]
    t = [(x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1)]
    for i in range(4):
        msp.add_line(b[i], b[(i+1)%4], dxfattribs={"layer": layer})
        msp.add_line(t[i], t[(i+1)%4], dxfattribs={"layer": layer})
        msp.add_line(b[i], t[i], dxfattribs={"layer": layer})

box_wire(0 + MODEL_3D_X_OFFSET, 0, 0, max_x + MODEL_3D_X_OFFSET, max_y, podium_top_z, "OUTLINE")
box_wire(tx0 + MODEL_3D_X_OFFSET, 0, podium_top_z, tx1 + MODEL_3D_X_OFFSET, max_y, total_h, "OUTLINE")

# ===== PART 2 : 2D PROJECTION VIEWS =====
# Layout:
#
#              TOP VIEW
#        LEFT  FRONT  RIGHT  BACK
#
# We place them below the 3D model, offset in Z=0 plane
# Using negative Y region so they don't overlap 3D.

GAP = 30          # gap between views
BASE_Y = -50      # start Y for 2D views row
TOP_BASE_Y = BASE_Y + total_h + GAP  # top view above elevations

print("  2D projection views ...")

# Helper: collect elements on a face
def get_face_elements(conn, pos, axis, value, etypes):
    """Get elements where both nodes have pos[axis]==value and element_type in etypes."""
    face_nodes = set(pos[pos[axis] == value]['node_id'])
    mask = (conn['node_i'].isin(face_nodes) &
            conn['node_j'].isin(face_nodes) &
            conn['element_type'].isin(etypes))
    return conn[mask]

def get_edge_face_elements(conn, pos, axis, values_by_zone, etypes):
    """Get elements on an edge face that spans podium+tower with different axis values."""
    node_ids = set()
    for zone, val in values_by_zone:
        nodes = pos[(pos['zone'] == zone) & (pos[axis] == val)]
        node_ids.update(nodes['node_id'])
    mask = (conn['node_i'].isin(node_ids) &
            conn['node_j'].isin(node_ids) &
            conn['element_type'].isin(etypes))
    return conn[mask]

def draw_2d_view(elements, pos, h_axis, v_axis, offset_x, offset_y,
                 layer_map, title):
    """Draw a 2D projected view at (offset_x, offset_y) in XY plane (z=0)."""
    for _, row in elements.iterrows():
        n1 = pos[pos['node_id'] == row['node_i']].iloc[0]
        n2 = pos[pos['node_id'] == row['node_j']].iloc[0]
        etype = row['element_type']

        x1 = float(n1[h_axis]) + offset_x
        y1 = float(n1[v_axis]) + offset_y
        x2 = float(n2[h_axis]) + offset_x
        y2 = float(n2[v_axis]) + offset_y

        layer = layer_map.get(etype, "0")

        msp.add_line((x1, y1, 0), (x2, y2, 0), dxfattribs={"layer": layer})

    # Title
    msp.add_text(title, height=2.5,
                 dxfattribs={"layer": "VIEW_TITLE",
                             "insert": (offset_x, offset_y - 8, 0)})


# --- TOP VIEW (Plan at z=0) ---
# Show floor 0 plan: beams and floor braces in XY plane
top_ox = 0
top_oy = TOP_BASE_Y
floor0_nodes = set(pos_df[pos_df['floor'] == 0]['node_id'])
floor0_elems = conn_df[
    (conn_df['node_i'].isin(floor0_nodes)) &
    (conn_df['node_j'].isin(floor0_nodes)) &
    (conn_df['element_type'].isin(['beam_x', 'beam_y', 'brace_floor']))
]
# Draw frame elements
for _, row in floor0_elems.iterrows():
    n1 = pos_df[pos_df['node_id'] == row['node_i']].iloc[0]
    n2 = pos_df[pos_df['node_id'] == row['node_j']].iloc[0]
    etype = row['element_type']
    x1 = float(n1['x']) + top_ox
    y1 = float(n1['y']) + top_oy
    x2 = float(n2['x']) + top_ox
    y2 = float(n2['y']) + top_oy
    if etype == 'brace_floor':
        layer = "VIEW_BRACE_FLOOR"
    else:
        layer = "VIEW_TOP"
    msp.add_line((x1, y1, 0), (x2, y2, 0), dxfattribs={"layer": layer})
msp.add_text("TOP VIEW (Plan - Floor 0)", height=2.5,
             dxfattribs={"layer": "VIEW_TITLE",
                         "insert": (top_ox, top_oy - 8, 0)})

# Also draw tower outline on top view
msp.add_line((tx0+top_ox, 0+top_oy, 0), (tx1+top_ox, 0+top_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_line((tx1+top_ox, 0+top_oy, 0), (tx1+top_ox, max_y+top_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_line((tx1+top_ox, max_y+top_oy, 0), (tx0+top_ox, max_y+top_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_line((tx0+top_ox, max_y+top_oy, 0), (tx0+top_ox, 0+top_oy, 0),
             dxfattribs={"layer": "OUTLINE"})

# --- TRANSITION FLOOR PLAN (Podium top - shows space braces) ---
trans_floor = podium_floors - 1
trans_ox = max_x + GAP
trans_oy = TOP_BASE_Y
trans_floor_nodes = set(pos_df[pos_df['floor'] == trans_floor]['node_id'])
trans_elems = conn_df[
    (conn_df['node_i'].isin(trans_floor_nodes)) &
    (conn_df['node_j'].isin(trans_floor_nodes)) &
    (conn_df['element_type'].isin(['beam_x', 'beam_y', 'brace_floor', 'brace_space']))
]
# Draw elements
for _, row in trans_elems.iterrows():
    n1 = pos_df[pos_df['node_id'] == row['node_i']].iloc[0]
    n2 = pos_df[pos_df['node_id'] == row['node_j']].iloc[0]
    etype = row['element_type']
    x1 = float(n1['x']) + trans_ox
    y1 = float(n1['y']) + trans_oy
    x2 = float(n2['x']) + trans_ox
    y2 = float(n2['y']) + trans_oy
    if etype == 'brace_floor':
        layer = "VIEW_BRACE_FLOOR"
    elif etype == 'brace_space':
        layer = "VIEW_BRACE_SPACE"
    else:
        layer = "VIEW_TOP"
    msp.add_line((x1, y1, 0), (x2, y2, 0), dxfattribs={"layer": layer})
# Tower outline
msp.add_line((tx0+trans_ox, 0+trans_oy, 0), (tx1+trans_ox, 0+trans_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_line((tx1+trans_ox, 0+trans_oy, 0), (tx1+trans_ox, max_y+trans_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_line((tx1+trans_ox, max_y+trans_oy, 0), (tx0+trans_ox, max_y+trans_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_line((tx0+trans_ox, max_y+trans_oy, 0), (tx0+trans_ox, 0+trans_oy, 0),
             dxfattribs={"layer": "OUTLINE"})
msp.add_text(f"TRANSITION FLOOR PLAN (Floor {trans_floor})", height=2.5,
             dxfattribs={"layer": "VIEW_TITLE",
                         "insert": (trans_ox, trans_oy - 8, 0)})

# --- FRONT ELEVATION (Y=0, show X vs Z) ---
front_ox = 0
front_oy = BASE_Y
front_elems = get_face_elements(conn_df, pos_df, 'y', 0.0,
                                ['column', 'beam_x', 'brace_xz', 'chevron'])
front_layers = {
    'column': 'VIEW_FRONT', 'beam_x': 'VIEW_FRONT',
    'brace_xz': 'VIEW_BRACE_XZ', 'chevron': 'VIEW_CHEVRON'
}
draw_2d_view(front_elems, pos_df, 'x', 'z', front_ox, front_oy,
             front_layers, "FRONT ELEVATION (Y=0)")

# --- BACK ELEVATION (Y=16, show X vs Z, mirrored) ---
back_ox = max_x + GAP + max_y + GAP + max_y + GAP
back_oy = BASE_Y
back_elems = get_face_elements(conn_df, pos_df, 'y', max_y,
                               ['column', 'beam_x', 'brace_xz', 'chevron'])
# Mirror X for back view: x_draw = max_x - x
for _, row in back_elems.iterrows():
    n1 = pos_df[pos_df['node_id'] == row['node_i']].iloc[0]
    n2 = pos_df[pos_df['node_id'] == row['node_j']].iloc[0]
    etype = row['element_type']
    x1 = max_x - float(n1['x']) + back_ox
    y1 = float(n1['z']) + back_oy
    x2 = max_x - float(n2['x']) + back_ox
    y2 = float(n2['z']) + back_oy
    
    layer = "VIEW_BACK"
    if etype == "brace_xz": layer = "VIEW_BRACE_XZ"
    elif etype == "chevron": layer = "VIEW_CHEVRON"
    
    msp.add_line((x1, y1, 0), (x2, y2, 0), dxfattribs={"layer": layer})
msp.add_text("BACK ELEVATION (Y=16m)", height=2.5,
             dxfattribs={"layer": "VIEW_TITLE",
                         "insert": (back_ox, back_oy - 8, 0)})

# --- LEFT ELEVATION (X=0 podium / X=8 tower, show Y vs Z) ---
left_ox = -(max_y + GAP)
left_oy = BASE_Y
left_elems = get_edge_face_elements(conn_df, pos_df, 'x',
                                    [('podium', 0.0), ('tower', tx0)],
                                    ['column', 'beam_y', 'brace_yz'])
left_layers = {'column': 'VIEW_LEFT', 'beam_y': 'VIEW_LEFT', 'brace_yz': 'VIEW_BRACE_YZ'}
draw_2d_view(left_elems, pos_df, 'y', 'z', left_ox, left_oy,
             left_layers, "LEFT ELEVATION")

# --- RIGHT ELEVATION (X=40 podium / X=32 tower, show Y vs Z, mirrored) ---
right_ox = max_x + GAP
right_oy = BASE_Y
right_elems = get_edge_face_elements(conn_df, pos_df, 'x',
                                     [('podium', max_x), ('tower', tx1)],
                                     ['column', 'beam_y', 'brace_yz'])
# Mirror Y for right view: y_draw = max_y - y
for _, row in right_elems.iterrows():
    n1 = pos_df[pos_df['node_id'] == row['node_i']].iloc[0]
    n2 = pos_df[pos_df['node_id'] == row['node_j']].iloc[0]
    etype = row['element_type']
    x1 = max_y - float(n1['y']) + right_ox
    y1 = float(n1['z']) + right_oy
    x2 = max_y - float(n2['y']) + right_ox
    y2 = float(n2['z']) + right_oy
    layer = "VIEW_BRACE_YZ" if etype == "brace_yz" else "VIEW_RIGHT"
    msp.add_line((x1, y1, 0), (x2, y2, 0), dxfattribs={"layer": layer})
msp.add_text("RIGHT ELEVATION", height=2.5,
             dxfattribs={"layer": "VIEW_TITLE",
                         "insert": (right_ox, right_oy - 8, 0)})

# ---------------------------------------------------------------------------
doc.saveas(OUTPUT_FILE)
print(f"\nDXF saved: {OUTPUT_FILE}")
print("Open in AutoCAD -> ZOOM EXTENTS to see all views.")
print("Use 3DORBIT for the 3D model, or switch to Top view for the 2D projections.")
