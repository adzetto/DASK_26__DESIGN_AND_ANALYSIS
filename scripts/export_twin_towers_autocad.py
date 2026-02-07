"""
Export DASK 2026 Twin Towers structural model to AutoCAD DXF.
  - 3D model in modelspace
  - 2D projection views: Top, Bottom, Front, Back, Left, Right
  - Separate views for Podium and Tower sections

Reads: twin_building_data.npz, twin_position_matrix.csv, twin_connectivity_matrix.csv
"""

import numpy as np
import pandas as pd
import ezdxf
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
EXPORT_DIR = SCRIPT_DIR.parent / 'exports'
EXPORT_DIR.mkdir(exist_ok=True)

OUTPUT_FILE = EXPORT_DIR / "twin_towers_all_views.dxf"

# ---------------------------------------------------------------------------
# ACI colors and layer configuration
# ---------------------------------------------------------------------------
LAYER_CFG = {
    # Tower elements
    "column":           {"color": 5,  "lw": 50},   # blue
    "beam_x":           {"color": 3,  "lw": 35},   # green
    "beam_y":           {"color": 30, "lw": 35},   # orange
    "brace_xz":         {"color": 1,  "lw": 25},   # red
    "brace_yz":         {"color": 6,  "lw": 25},   # magenta
    "brace_floor":      {"color": 7,  "lw": 18},   # white
    "brace_space":      {"color": 250, "lw": 35},  # dark gray
    "brace_corner":     {"color": 4,   "lw": 35},  # cyan
    "core_wall":        {"color": 44,  "lw": 50},  # brown

    # Bridge elements
    "bridge_beam":      {"color": 6,   "lw": 50},  # magenta
    "bridge_column":    {"color": 200, "lw": 40},  # dark magenta
    "bridge_brace_top": {"color": 210, "lw": 30},  # hotpink
    "bridge_brace_bot": {"color": 220, "lw": 30},  # deeppink
    "bridge_truss_side":{"color": 6,   "lw": 35},  # fuchsia
    "bridge_brace_face":{"color": 230, "lw": 30},  # mediumvioletred
    "bridge_shear_yz":  {"color": 10,  "lw": 40},  # coupled shear wall

    # Utility layers
    "NODES":            {"color": 7,  "lw": 0},
    "GRID":             {"color": 8,  "lw": 13},
    "ANNO":             {"color": 7,  "lw": 0},
    "OUTLINE":          {"color": 9,  "lw": 25},

    # 2D view layers
    "VIEW_FRONT":       {"color": 5,  "lw": 25},
    "VIEW_BACK":        {"color": 5,  "lw": 25},
    "VIEW_LEFT":        {"color": 30, "lw": 25},
    "VIEW_RIGHT":       {"color": 30, "lw": 25},
    "VIEW_TOP":         {"color": 3,  "lw": 25},
    "VIEW_BOTTOM":      {"color": 3,  "lw": 25},
    "VIEW_BRACE":       {"color": 1,  "lw": 18},
    "VIEW_BRIDGE":      {"color": 6,  "lw": 35},
    "VIEW_TITLE":       {"color": 7,  "lw": 0},
    "VIEW_BORDER":      {"color": 8,  "lw": 25},
}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
print("=" * 70)
print("TWIN TOWERS AUTOCAD EXPORT - ALL VIEWS")
print("=" * 70)

print("\nLoading data...")
npz_path = DATA_DIR / 'twin_building_data.npz'
if not npz_path.exists():
    print(f"ERROR: {npz_path} not found!")
    exit(1)

npz = np.load(npz_path)
coords = npz['coords']
podium_x = npz['podium_x']
tower_x = npz['tower_x']
y_coords_t1 = npz['y_coords_t1']
y_coords_t2 = npz['y_coords_t2']
z_coords = npz['z_coords']
tower_gap = float(npz['tower_gap'])

pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')

print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# Geometry
max_x = float(podium_x[-1])
max_y_t1 = float(y_coords_t1[-1])
max_y_t2 = float(y_coords_t2[-1])
total_h = float(z_coords[-1])
n_floors = len(z_coords)

# Podium/Tower floor split
PODIUM_FLOORS = 13  # floors 0-12
PODIUM_HEIGHT = float(z_coords[PODIUM_FLOORS - 1])  # Z at floor 12

print(f"\nGeometry:")
print(f"  X extent: 0 to {max_x:.0f}m")
print(f"  Y extent: 0 to {max_y_t2:.0f}m")
print(f"  Total height: {total_h:.0f}m ({n_floors} floors)")
print(f"  Podium height: {PODIUM_HEIGHT:.0f}m ({PODIUM_FLOORS} floors)")

# node_id -> (x,y,z)
node_xyz = {}
for _, r in pos_df.iterrows():
    node_xyz[int(r["node_id"])] = (r["x"], r["y"], r["z"])

# ---------------------------------------------------------------------------
# Create DXF
# ---------------------------------------------------------------------------
print("\nCreating DXF document...")
doc = ezdxf.new("R2010")
msp = doc.modelspace()

# Add layers
for name, cfg in LAYER_CFG.items():
    doc.layers.add(name, color=cfg["color"], lineweight=cfg["lw"])

# ===== PART 1: 3D MODEL =====
MODEL_3D_OFFSET = (-300, 0, 0)  # Move 3D model to the left

print("\n  Adding 3D structural elements...")
element_count = {}
for _, row in conn_df.iterrows():
    etype = row["element_type"]
    n1 = int(row["node_i"])
    n2 = int(row["node_j"])

    if n1 not in node_xyz or n2 not in node_xyz:
        continue

    p1_orig = node_xyz[n1]
    p2_orig = node_xyz[n2]
    p1 = (p1_orig[0] + MODEL_3D_OFFSET[0], p1_orig[1], p1_orig[2])
    p2 = (p2_orig[0] + MODEL_3D_OFFSET[0], p2_orig[1], p2_orig[2])

    layer = etype if etype in LAYER_CFG else "OUTLINE"
    msp.add_line(p1, p2, dxfattribs={"layer": layer})
    element_count[etype] = element_count.get(etype, 0) + 1

print("  Element counts:")
for etype, count in sorted(element_count.items()):
    print(f"    {etype}: {count}")

# ===== PART 2: 2D VIEWS =====
print("\n  Creating 2D views...")

# View layout parameters
VIEW_GAP = 30  # Gap between views
TITLE_HEIGHT = 3.0

def get_view_layer(etype):
    """Get appropriate layer for element type in 2D views"""
    if 'bridge' in etype:
        return "VIEW_BRIDGE"
    elif 'brace' in etype:
        return "VIEW_BRACE"
    else:
        return None  # Use default

def filter_by_floor_range(df, min_floor, max_floor):
    """Filter elements where both nodes are within floor range"""
    mask = []
    for _, row in df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            mask.append(False)
            continue

        z1, z2 = node_xyz[n1][2], node_xyz[n2][2]

        # Get floor indices
        f1 = np.argmin(np.abs(z_coords - z1))
        f2 = np.argmin(np.abs(z_coords - z2))

        # Check if both nodes are in floor range
        in_range = (min_floor <= f1 <= max_floor) and (min_floor <= f2 <= max_floor)
        mask.append(in_range)

    return df[mask]

def filter_by_y(df, y_values, tolerance=1.0):
    """Filter elements at specific Y values (for front/back views)"""
    mask = []
    for _, row in df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            mask.append(False)
            continue

        y1, y2 = node_xyz[n1][1], node_xyz[n2][1]
        at_face_1 = any(abs(y1 - y) < tolerance for y in y_values)
        at_face_2 = any(abs(y2 - y) < tolerance for y in y_values)
        same_y = abs(y1 - y2) < tolerance

        mask.append((at_face_1 and at_face_2) or (same_y and at_face_1))

    return df[mask]

def filter_by_x(df, x_values, tolerance=1.0):
    """Filter elements at specific X values (for left/right views)"""
    mask = []
    for _, row in df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            mask.append(False)
            continue

        x1, x2 = node_xyz[n1][0], node_xyz[n2][0]
        at_face_1 = any(abs(x1 - x) < tolerance for x in x_values)
        at_face_2 = any(abs(x2 - x) < tolerance for x in x_values)
        same_x = abs(x1 - x2) < tolerance

        mask.append((at_face_1 and at_face_2) or (same_x and at_face_1))

    return df[mask]

def filter_by_z(df, z_value, tolerance=1.0):
    """Filter elements at specific Z value (for top/bottom plan views)"""
    mask = []
    for _, row in df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            mask.append(False)
            continue

        z1, z2 = node_xyz[n1][2], node_xyz[n2][2]
        at_level = abs(z1 - z_value) < tolerance and abs(z2 - z_value) < tolerance
        mask.append(at_level)

    return df[mask]

def draw_elevation_xz(elements, offset_x, offset_y, default_layer, title, scale=1.0):
    """Draw elevation in XZ plane (front/back view)"""
    count = 0
    for _, row in elements.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            continue

        p1, p2 = node_xyz[n1], node_xyz[n2]
        x1 = p1[0] * scale + offset_x
        z1 = p1[2] * scale + offset_y
        x2 = p2[0] * scale + offset_x
        z2 = p2[2] * scale + offset_y

        etype = row['element_type']
        layer = get_view_layer(etype) or default_layer
        msp.add_line((x1, z1, 0), (x2, z2, 0), dxfattribs={"layer": layer})
        count += 1

    # Title
    msp.add_text(title, height=TITLE_HEIGHT,
                 dxfattribs={"layer": "VIEW_TITLE", "insert": (offset_x, offset_y - 8, 0)})
    return count

def draw_elevation_yz(elements, offset_x, offset_y, default_layer, title, scale=1.0):
    """Draw elevation in YZ plane (left/right view)"""
    count = 0
    for _, row in elements.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            continue

        p1, p2 = node_xyz[n1], node_xyz[n2]
        y1 = p1[1] * scale + offset_x
        z1 = p1[2] * scale + offset_y
        y2 = p2[1] * scale + offset_x
        z2 = p2[2] * scale + offset_y

        etype = row['element_type']
        layer = get_view_layer(etype) or default_layer
        msp.add_line((y1, z1, 0), (y2, z2, 0), dxfattribs={"layer": layer})
        count += 1

    msp.add_text(title, height=TITLE_HEIGHT,
                 dxfattribs={"layer": "VIEW_TITLE", "insert": (offset_x, offset_y - 8, 0)})
    return count

def draw_plan_xy(elements, offset_x, offset_y, default_layer, title, scale=1.0):
    """Draw plan in XY plane (top/bottom view)"""
    count = 0
    for _, row in elements.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            continue

        p1, p2 = node_xyz[n1], node_xyz[n2]
        x1 = p1[0] * scale + offset_x
        y1 = p1[1] * scale + offset_y
        x2 = p2[0] * scale + offset_x
        y2 = p2[1] * scale + offset_y

        etype = row['element_type']
        layer = get_view_layer(etype) or default_layer
        msp.add_line((x1, y1, 0), (x2, y2, 0), dxfattribs={"layer": layer})
        count += 1

    msp.add_text(title, height=TITLE_HEIGHT,
                 dxfattribs={"layer": "VIEW_TITLE", "insert": (offset_x, offset_y - 8, 0)})
    return count

def draw_view_border(x, y, width, height, title):
    """Draw border around a view"""
    msp.add_lwpolyline(
        [(x, y), (x + width, y), (x + width, y + height), (x, y + height), (x, y)],
        dxfattribs={"layer": "VIEW_BORDER"}
    )

# ---------------------------------------------------------------------------
# VIEW LAYOUT - Arranged in a grid
# ---------------------------------------------------------------------------
# Row 1: FRONT views (Full, Podium, Tower)
# Row 2: BACK views (Full, Podium, Tower)
# Row 3: LEFT views (Full, Podium, Tower)
# Row 4: RIGHT views (Full, Podium, Tower)
# Row 5: TOP (roof plan) and BOTTOM (ground plan)

ROW_HEIGHT = total_h + VIEW_GAP + 20
COL_WIDTH = max_x + VIEW_GAP + 20
BASE_X = 0
BASE_Y = -150

# Y values for front/back faces
FRONT_Y = [float(y_coords_t1[0]), float(y_coords_t2[0])]  # Y=0, Y=24
BACK_Y = [float(y_coords_t1[-1]), float(y_coords_t2[-1])]  # Y=16, Y=40

# X values for left/right faces
LEFT_X = [0.0]  # X=0
RIGHT_X = [float(podium_x[-1])]  # X=40

print("\n  --- FRONT ELEVATION VIEWS ---")
# Full front
front_full = filter_by_y(conn_df, FRONT_Y)
cnt = draw_elevation_xz(front_full, BASE_X, BASE_Y, "VIEW_FRONT",
                        f"FRONT ELEVATION - FULL (Y=0,24)")
print(f"    Full: {cnt} elements")

# Podium front
front_podium = filter_by_y(filter_by_floor_range(conn_df, 0, PODIUM_FLOORS-1), FRONT_Y)
cnt = draw_elevation_xz(front_podium, BASE_X + COL_WIDTH, BASE_Y, "VIEW_FRONT",
                        f"FRONT - PODIUM (F0-F{PODIUM_FLOORS-1})")
print(f"    Podium: {cnt} elements")

# Tower front
front_tower = filter_by_y(filter_by_floor_range(conn_df, PODIUM_FLOORS-1, n_floors-1), FRONT_Y)
cnt = draw_elevation_xz(front_tower, BASE_X + COL_WIDTH * 2, BASE_Y, "VIEW_FRONT",
                        f"FRONT - TOWER (F{PODIUM_FLOORS-1}-F{n_floors-1})")
print(f"    Tower: {cnt} elements")

print("\n  --- BACK ELEVATION VIEWS ---")
# Full back
back_full = filter_by_y(conn_df, BACK_Y)
cnt = draw_elevation_xz(back_full, BASE_X, BASE_Y - ROW_HEIGHT, "VIEW_BACK",
                        f"BACK ELEVATION - FULL (Y=16,40)")
print(f"    Full: {cnt} elements")

# Podium back
back_podium = filter_by_y(filter_by_floor_range(conn_df, 0, PODIUM_FLOORS-1), BACK_Y)
cnt = draw_elevation_xz(back_podium, BASE_X + COL_WIDTH, BASE_Y - ROW_HEIGHT, "VIEW_BACK",
                        f"BACK - PODIUM (F0-F{PODIUM_FLOORS-1})")
print(f"    Podium: {cnt} elements")

# Tower back
back_tower = filter_by_y(filter_by_floor_range(conn_df, PODIUM_FLOORS-1, n_floors-1), BACK_Y)
cnt = draw_elevation_xz(back_tower, BASE_X + COL_WIDTH * 2, BASE_Y - ROW_HEIGHT, "VIEW_BACK",
                        f"BACK - TOWER (F{PODIUM_FLOORS-1}-F{n_floors-1})")
print(f"    Tower: {cnt} elements")

print("\n  --- LEFT ELEVATION VIEWS ---")
# Full left
left_full = filter_by_x(conn_df, LEFT_X)
cnt = draw_elevation_yz(left_full, BASE_X, BASE_Y - ROW_HEIGHT * 2, "VIEW_LEFT",
                        f"LEFT ELEVATION - FULL (X=0)")
print(f"    Full: {cnt} elements")

# Podium left
left_podium = filter_by_x(filter_by_floor_range(conn_df, 0, PODIUM_FLOORS-1), LEFT_X)
cnt = draw_elevation_yz(left_podium, BASE_X + COL_WIDTH, BASE_Y - ROW_HEIGHT * 2, "VIEW_LEFT",
                        f"LEFT - PODIUM (F0-F{PODIUM_FLOORS-1})")
print(f"    Podium: {cnt} elements")

# Tower left (X=12 for tower - new layout)
left_tower = filter_by_x(filter_by_floor_range(conn_df, PODIUM_FLOORS-1, n_floors-1), [12.0])
cnt = draw_elevation_yz(left_tower, BASE_X + COL_WIDTH * 2, BASE_Y - ROW_HEIGHT * 2, "VIEW_LEFT",
                        f"LEFT - TOWER (X=12, F{PODIUM_FLOORS-1}+)")
print(f"    Tower: {cnt} elements")

print("\n  --- RIGHT ELEVATION VIEWS ---")
# Full right
right_full = filter_by_x(conn_df, RIGHT_X)
cnt = draw_elevation_yz(right_full, BASE_X, BASE_Y - ROW_HEIGHT * 3, "VIEW_RIGHT",
                        f"RIGHT ELEVATION - FULL (X=40)")
print(f"    Full: {cnt} elements")

# Podium right
right_podium = filter_by_x(filter_by_floor_range(conn_df, 0, PODIUM_FLOORS-1), RIGHT_X)
cnt = draw_elevation_yz(right_podium, BASE_X + COL_WIDTH, BASE_Y - ROW_HEIGHT * 3, "VIEW_RIGHT",
                        f"RIGHT - PODIUM (F0-F{PODIUM_FLOORS-1})")
print(f"    Podium: {cnt} elements")

# Tower right (X=28 for tower - new layout)
right_tower = filter_by_x(filter_by_floor_range(conn_df, PODIUM_FLOORS-1, n_floors-1), [28.0])
cnt = draw_elevation_yz(right_tower, BASE_X + COL_WIDTH * 2, BASE_Y - ROW_HEIGHT * 3, "VIEW_RIGHT",
                        f"RIGHT - TOWER (X=28, F{PODIUM_FLOORS-1}+)")
print(f"    Tower: {cnt} elements")

print("\n  --- PLAN VIEWS ---")
# Bottom plan (Floor 0)
z_floor0 = float(z_coords[0])
bottom_plan = filter_by_z(conn_df, z_floor0, tolerance=1.0)
# Include floor beams for plan
floor0_beams = conn_df[
    (conn_df['element_type'].isin(['beam_x', 'beam_y', 'brace_floor'])) &
    (conn_df.apply(lambda r: abs(node_xyz.get(int(r['node_i']), (0,0,999))[2] - z_floor0) < 1.0
                   if int(r['node_i']) in node_xyz else False, axis=1))
]
cnt = draw_plan_xy(floor0_beams, BASE_X, BASE_Y - ROW_HEIGHT * 4, "VIEW_BOTTOM",
                   f"BOTTOM PLAN - FLOOR 0 (Z={z_floor0:.0f}m)")
print(f"    Bottom (F0): {cnt} elements")

# Top plan (Floor 25 / roof)
z_roof = float(z_coords[-1])
roof_beams = conn_df[
    (conn_df['element_type'].isin(['beam_x', 'beam_y', 'brace_floor'])) &
    (conn_df.apply(lambda r: abs(node_xyz.get(int(r['node_i']), (0,0,-999))[2] - z_roof) < 1.0
                   if int(r['node_i']) in node_xyz else False, axis=1))
]
cnt = draw_plan_xy(roof_beams, BASE_X + COL_WIDTH, BASE_Y - ROW_HEIGHT * 4, "VIEW_TOP",
                   f"TOP PLAN - ROOF F{n_floors-1} (Z={z_roof:.0f}m)")
print(f"    Top (Roof): {cnt} elements")

# Podium top (Floor 12)
z_podium_top = float(z_coords[PODIUM_FLOORS - 1])
podium_top_beams = conn_df[
    (conn_df['element_type'].isin(['beam_x', 'beam_y', 'brace_floor'])) &
    (conn_df.apply(lambda r: abs(node_xyz.get(int(r['node_i']), (0,0,-999))[2] - z_podium_top) < 1.0
                   if int(r['node_i']) in node_xyz else False, axis=1))
]
cnt = draw_plan_xy(podium_top_beams, BASE_X + COL_WIDTH * 2, BASE_Y - ROW_HEIGHT * 4, "VIEW_TOP",
                   f"PODIUM TOP PLAN - F{PODIUM_FLOORS-1} (Z={z_podium_top:.0f}m)")
print(f"    Podium top (F12): {cnt} elements")

# Bridge plan
print("\n  --- BRIDGE VIEWS ---")
bridge_elems = conn_df[conn_df['tower'] == 'bridge']
cnt = draw_elevation_xz(bridge_elems, BASE_X, BASE_Y - ROW_HEIGHT * 5, "VIEW_BRIDGE",
                        f"BRIDGE ELEMENTS - XZ VIEW")
print(f"    Bridge XZ: {cnt} elements")

cnt = draw_elevation_yz(bridge_elems, BASE_X + COL_WIDTH, BASE_Y - ROW_HEIGHT * 5, "VIEW_BRIDGE",
                        f"BRIDGE ELEMENTS - YZ VIEW")
print(f"    Bridge YZ: {cnt} elements")

# ---------------------------------------------------------------------------
# Save DXF
# ---------------------------------------------------------------------------
doc.saveas(OUTPUT_FILE)
print(f"\n{'=' * 70}")
print(f"DXF SAVED: {OUTPUT_FILE}")
print("=" * 70)
print(f"""
VIEW LAYOUT:
  Row 1: FRONT elevations (Full, Podium, Tower)
  Row 2: BACK elevations (Full, Podium, Tower)
  Row 3: LEFT elevations (Full, Podium, Tower)
  Row 4: RIGHT elevations (Full, Podium, Tower)
  Row 5: PLAN views (Ground F0, Roof, Podium top F12)
  Row 6: BRIDGE views (XZ, YZ)

  3D MODEL is offset to X=-300 for clarity

In AutoCAD:
  - ZOOM EXTENTS to see all views
  - Use layer controls to show/hide element types
  - 3DORBIT for 3D model view
""")
