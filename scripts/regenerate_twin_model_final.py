"""
TWIN TOWERS MODEL V7 - FINAL
============================
- Geometry: Based on V6 Light (30x16cm, No Podium)
- Shear Walls: 3mm Balsa Panels at Core Zones (Replaces X-braces)
- Weight Optimization: Target 1.4kg
"""

import numpy as np
import pandas as pd
from pathlib import Path
import ezdxf

print("=" * 70)
print("TWIN TOWERS MODEL V7 - SHEAR WALLS")
print("=" * 70)

# ============================================
# GEOMETRY - Custom grid with 1.2cm core zone
# ============================================
# X Layout: 3-8-3.4-1.2-3.4-8-3 = 30cm (7 bays)
X_COORDS = np.array([0.0, 3.0, 11.0, 14.4, 15.6, 19.0, 27.0, 30.0])

# Y Layout per tower: 7.4-1.2-7.4 = 16cm (3 bays) - OPTIMIZED FOR WEIGHT
Y_COORDS_T1 = np.array([0.0, 7.4, 8.6, 16.0])
Y_COORDS_T2 = np.array([24.0, 31.4, 32.6, 40.0])

TOWER_GAP = 8.0
TOWER_WIDTH = 30.0
TOWER_DEPTH = 16.0
CORE_GAP = 1.2  # cm

print(f"Tower: {TOWER_WIDTH} x {TOWER_DEPTH} cm")

# Floor heights
FLOOR_HEIGHT_GROUND = 9.0
FLOOR_HEIGHT_NORMAL = 6.0
TOTAL_FLOORS = 26  # 153 cm

Z_COORDS = [0.0, FLOOR_HEIGHT_GROUND]
for i in range(2, TOTAL_FLOORS):
    Z_COORDS.append(Z_COORDS[-1] + FLOOR_HEIGHT_NORMAL)
Z_COORDS = np.array(Z_COORDS)

print(f"Height: {Z_COORDS[-1]}m ({TOTAL_FLOORS} floors)")

# ============================================
# NODE GENERATION
# ============================================
nodes = []
node_id = 0
node_lookup = {}

def add_node(tower, floor, x, y):
    global node_id
    z = Z_COORDS[floor]
    key = (tower, floor, x, y)
    if key not in node_lookup:
        nodes.append({
            'node_id': node_id, 'x': x, 'y': y, 'z': z,
            'floor': floor, 'zone': 'tower', 'tower': tower
        })
        node_lookup[key] = node_id
        node_id += 1
    return node_lookup[key]

for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    for floor in range(TOTAL_FLOORS):
        for x in X_COORDS:
            for y in y_coords:
                add_node(tower_num, floor, x, y)

n_nodes = len(nodes)
print(f"Nodes: {n_nodes}")

position_df = pd.DataFrame(nodes)
coords = np.zeros((n_nodes, 3))
for node in nodes:
    coords[node['node_id']] = [node['x'], node['y'], node['z']]

# ============================================
# ELEMENT GENERATION
# ============================================
elements = []
elem_id = 0

def add_element(n1, n2, etype, tower='', conn='rigid'):
    global elem_id
    if n1 is None or n2 is None:
        return None
    elements.append({
        'element_id': elem_id, 'node_i': n1, 'node_j': n2,
        'element_type': etype, 'tower': tower, 'connection': conn
    })
    elem_id += 1

def get_node(tower, floor, x, y):
    return node_lookup.get((tower, floor, x, y))

# ============================================
# MAIN STRUCTURAL ELEMENTS
# ============================================
CORNER_BRACE_FLOORS_XZ = [0, 6, 12, 18, 24]
CORNER_BRACE_FLOORS_YZ = [0, 8, 16, 24]
FLOOR_BRACE_FLOORS = [0, 12, 24]

for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    tower_str = f'tower{tower_num}'

    for floor in range(TOTAL_FLOORS):
        # COLUMNS
        if floor < TOTAL_FLOORS - 1:
            for x in X_COORDS:
                for y in y_coords:
                    n1 = get_node(tower_num, floor, x, y)
                    n2 = get_node(tower_num, floor + 1, x, y)
                    add_element(n1, n2, 'column', tower_str)

        # BEAMS
        # Optimization: Alternating Internal Beams
        # Keep Perimeter and Core beams on all floors.
        # Alternate others: Beam X on Even, Beam Y on Odd (or vice versa).
        
        is_perimeter_y_t1 = (y_coords[0] == 0) # Just checks relative
        
        for i in range(len(X_COORDS) - 1):
            for y in y_coords:
                # BEAM X
                # Check if essential (Perimeter or Core)
                is_perimeter_y = (y == y_coords[0] or y == y_coords[-1])
                # Core X lines are 14.4 and 15.6. But Beam X is BETWEEN X lines.
                # Core gap is between 14.4 and 15.6 (index 3).
                x1, x2 = X_COORDS[i], X_COORDS[i+1]
                is_core_x_span = (abs(x1 - 14.4) < 0.1 and abs(x2 - 15.6) < 0.1)
                
                is_essential = is_perimeter_y or is_core_x_span
                
                if is_essential or (floor % 2 == 0):
                     n1 = get_node(tower_num, floor, x1, y)
                     n2 = get_node(tower_num, floor, x2, y)
                     add_element(n1, n2, 'beam_x', tower_str)

        for j in range(len(y_coords) - 1):
            for x in X_COORDS:
                # BEAM Y
                is_perimeter_x = (x == X_COORDS[0] or x == X_COORDS[-1])
                is_core_x_line = (abs(x - 14.4) < 0.1 or abs(x - 15.6) < 0.1)
                
                is_essential = is_perimeter_x or is_core_x_line
                
                if is_essential or (floor % 2 != 0):
                    n1 = get_node(tower_num, floor, x, y_coords[j])
                    n2 = get_node(tower_num, floor, x, y_coords[j+1])
                    add_element(n1, n2, 'beam_y', tower_str)

        # BRACING & PANELS
        if floor < TOTAL_FLOORS - 1:
            # -------------------------------------------------
            # XZ PLANE
            # -------------------------------------------------
            for face_idx, y in enumerate([y_coords[0], y_coords[-1]]):
                for i in range(len(X_COORDS) - 1):
                    x_left = X_COORDS[i]
                    x_right = X_COORDS[i + 1]
                    panel_width = x_right - x_left

                    n_bl = get_node(tower_num, floor, x_left, y)
                    n_br = get_node(tower_num, floor, x_right, y)
                    n_tl = get_node(tower_num, floor + 1, x_left, y)
                    n_tr = get_node(tower_num, floor + 1, x_right, y)

                    # Core zone check (1.2cm)
                    is_core = abs(panel_width - CORE_GAP) < 0.1
                    
                    if is_core:
                        # REPLACED BRACE WITH PANEL (shear_wall_xz)
                        # Modeled as two diagonals for connectivity, but weight will be calculated as PANEL
                        add_element(n_bl, n_tr, 'shear_wall_xz', tower_str, 'rigid')
                        add_element(n_br, n_tl, 'shear_wall_xz', tower_str, 'rigid')
                    elif floor in CORNER_BRACE_FLOORS_XZ and (i == 0 or i == len(X_COORDS) - 2):
                        # Corner braces (pins)
                        if (floor + i + face_idx) % 2 == 0:
                            add_element(n_bl, n_tr, 'brace_xz', tower_str, 'pin')
                        else:
                            add_element(n_br, n_tl, 'brace_xz', tower_str, 'pin')

            # -------------------------------------------------
            # YZ PLANE
            # -------------------------------------------------
            for face_idx, x in enumerate([X_COORDS[0], X_COORDS[-1]]):
                for j in range(len(y_coords) - 1):
                    y_bot = y_coords[j]
                    y_top = y_coords[j + 1]
                    panel_height = y_top - y_bot

                    n_bl = get_node(tower_num, floor, x, y_bot)
                    n_br = get_node(tower_num, floor, x, y_top)
                    n_tl = get_node(tower_num, floor + 1, x, y_bot)
                    n_tr = get_node(tower_num, floor + 1, x, y_top)

                    is_core = abs(panel_height - CORE_GAP) < 0.1
                    
                    if is_core:
                        # REPLACED BRACE WITH PANEL (shear_wall_yz)
                        add_element(n_bl, n_tr, 'shear_wall_yz', tower_str, 'rigid')
                        add_element(n_br, n_tl, 'shear_wall_yz', tower_str, 'rigid')
                    elif floor in CORNER_BRACE_FLOORS_YZ and (j == 0 or j == len(y_coords) - 2):
                        if (floor + j + face_idx) % 2 == 0:
                            add_element(n_bl, n_tr, 'brace_yz', tower_str, 'pin')
                        else:
                            add_element(n_br, n_tl, 'brace_yz', tower_str, 'pin')

            # -------------------------------------------------
            # FLOOR DIAPHRAGM
            # -------------------------------------------------
            if floor in FLOOR_BRACE_FLOORS:
                for i in range(len(X_COORDS) - 1):
                    for j in range(len(y_coords) - 1):
                        x_l, x_r = X_COORDS[i], X_COORDS[i+1]
                        y_b, y_t = y_coords[j], y_coords[j+1]
                        n1 = get_node(tower_num, floor, x_l, y_b)
                        n2 = get_node(tower_num, floor, x_r, y_t)
                        n3 = get_node(tower_num, floor, x_r, y_b)
                        n4 = get_node(tower_num, floor, x_l, y_t)
                        if (i + j) % 2 == 0:
                            add_element(n1, n2, 'floor_brace', tower_str, 'pin')
                        else:
                            add_element(n3, n4, 'floor_brace', tower_str, 'pin')

print(f"Tower elements: {len(elements)}")

# ============================================
# BRIDGES
# ============================================
BRIDGE_X_LEFT = 11.0
BRIDGE_X_RIGHT = 19.0
BRIDGE_FLOORS_SINGLE = [(5, 6), (11, 12), (17, 18)]
BRIDGE_FLOORS_DOUBLE = (23, 25)

Y_T1_BACK = Y_COORDS_T1[-1]
Y_T2_FRONT = Y_COORDS_T2[0]
Y_BRIDGE_MID = (Y_T1_BACK + Y_T2_FRONT) / 2

bridge_nodes = []
bridge_node_lookup = {}
bridge_node_id = n_nodes

def add_bridge_node(floor, x, y):
    global bridge_node_id
    z = Z_COORDS[floor]
    key = ('bridge', floor, x, y)
    if key not in bridge_node_lookup:
        bridge_nodes.append({
            'node_id': bridge_node_id, 'x': x, 'y': y, 'z': z,
            'floor': floor, 'zone': 'bridge', 'tower': 'bridge'
        })
        bridge_node_lookup[key] = bridge_node_id
        bridge_node_id += 1
    return bridge_node_lookup[key]

def get_bridge_node(floor, x, y):
    return bridge_node_lookup.get(('bridge', floor, x, y))

all_bridge_floors = set()
for fb, ft in BRIDGE_FLOORS_SINGLE:
    all_bridge_floors.update([fb, ft])
all_bridge_floors.update([BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1]])

for f in all_bridge_floors:
    for x in [BRIDGE_X_LEFT, BRIDGE_X_RIGHT]:
        add_bridge_node(f, x, Y_BRIDGE_MID)

bridge_elements = []
def add_bridge_elem(n1, n2, etype, conn='rigid'):
    global elem_id
    if n1 is None or n2 is None: return
    bridge_elements.append({
        'element_id': elem_id, 'node_i': n1, 'node_j': n2,
        'element_type': etype, 'tower': 'bridge', 'connection': conn
    })
    elem_id += 1

def create_bridge(floor_bot, floor_top, is_rigid=False):
    t1_bot_l = get_node(1, floor_bot, BRIDGE_X_LEFT, Y_T1_BACK)
    t1_bot_r = get_node(1, floor_bot, BRIDGE_X_RIGHT, Y_T1_BACK)
    t1_top_l = get_node(1, floor_top, BRIDGE_X_LEFT, Y_T1_BACK)
    t1_top_r = get_node(1, floor_top, BRIDGE_X_RIGHT, Y_T1_BACK)
    t2_bot_l = get_node(2, floor_bot, BRIDGE_X_LEFT, Y_T2_FRONT)
    t2_bot_r = get_node(2, floor_bot, BRIDGE_X_RIGHT, Y_T2_FRONT)
    t2_top_l = get_node(2, floor_top, BRIDGE_X_LEFT, Y_T2_FRONT)
    t2_top_r = get_node(2, floor_top, BRIDGE_X_RIGHT, Y_T2_FRONT)
    mid_bot_l = get_bridge_node(floor_bot, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    mid_bot_r = get_bridge_node(floor_bot, BRIDGE_X_RIGHT, Y_BRIDGE_MID)
    mid_top_l = get_bridge_node(floor_top, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    mid_top_r = get_bridge_node(floor_top, BRIDGE_X_RIGHT, Y_BRIDGE_MID)

    # Simplified Bridge Structure
    add_bridge_elem(t1_bot_l, mid_bot_l, 'bridge_beam')
    add_bridge_elem(t1_bot_r, mid_bot_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, mid_bot_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, t2_bot_l, 'bridge_beam')
    add_bridge_elem(mid_bot_r, t2_bot_r, 'bridge_beam')
    add_bridge_elem(t1_top_l, mid_top_l, 'bridge_beam')
    add_bridge_elem(t1_top_r, mid_top_r, 'bridge_beam')
    add_bridge_elem(mid_top_l, mid_top_r, 'bridge_beam')
    add_bridge_elem(mid_top_l, t2_top_l, 'bridge_beam')
    add_bridge_elem(mid_top_r, t2_top_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, mid_top_l, 'bridge_column')
    add_bridge_elem(mid_bot_r, mid_top_r, 'bridge_column')
    
    # Trusses
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t1_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_truss')
    add_bridge_elem(t2_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t1_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_truss')
    add_bridge_elem(t2_bot_r, mid_top_r, 'bridge_truss')

    if is_rigid:
        add_bridge_elem(t1_bot_l, t2_top_l, 'bridge_rigid')
        add_bridge_elem(t2_bot_l, t1_top_l, 'bridge_rigid')
        add_bridge_elem(t1_bot_r, t2_top_r, 'bridge_rigid')
        add_bridge_elem(t2_bot_r, t1_top_r, 'bridge_rigid')

print("\nCreating bridges...")
for fb, ft in BRIDGE_FLOORS_SINGLE:
    create_bridge(fb, ft, is_rigid=False)
create_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1], is_rigid=True)

# ============================================
# COMBINE DATA & WEIGHT
# ============================================
if bridge_nodes:
    bridge_nodes_df = pd.DataFrame(bridge_nodes)
    position_df = pd.concat([position_df, bridge_nodes_df], ignore_index=True)
    n_total = n_nodes + len(bridge_nodes)
    new_coords = np.zeros((n_total, 3))
    new_coords[:n_nodes] = coords
    for bn in bridge_nodes:
        new_coords[bn['node_id']] = [bn['x'], bn['y'], bn['z']]
    coords = new_coords
else:
    n_total = n_nodes

all_elements = elements + bridge_elements

# Calculate Lengths
for elem in all_elements:
    n1, n2 = elem['node_i'], elem['node_j']
    c1, c2 = coords[n1], coords[n2]
    elem['length'] = round(np.sqrt(np.sum((c2 - c1) ** 2)), 4)

connectivity_df = pd.DataFrame(all_elements)
print(f"\nElements by type:")
print(connectivity_df['element_type'].value_counts().to_string())

# ------------------------------------------------------------------
# WEIGHT CALCULATION
# ------------------------------------------------------------------
BALSA_DENSITY = 160  # kg/m³
SECTION_FRAME = 36   # mm² (6x6mm)
THICKNESS_PANEL = 3  # mm

# 1. Frame Elements (sticks)
frame_types = ['column', 'beam_x', 'beam_y', 'brace_xz', 'brace_yz', 'floor_brace',
               'bridge_beam', 'bridge_column', 'bridge_truss', 'bridge_rigid']
frame_df = connectivity_df[connectivity_df['element_type'].isin(frame_types)]
frame_weight = frame_df['length'].sum() * 10 * SECTION_FRAME * BALSA_DENSITY / 1e9

# 2. Panel Elements (Shear Walls)
# The DataFrame has 2 diagonals per panel.
# We calculate area based on the actual geometry, not the diagonal length.
panel_xz = connectivity_df[connectivity_df['element_type'] == 'shear_wall_xz']
panel_yz = connectivity_df[connectivity_df['element_type'] == 'shear_wall_yz']

# Count unique panels (each has 2 diagonal elements)
n_panels_xz = len(panel_xz) // 2
n_panels_yz = len(panel_yz) // 2

# Dimensions:
# Core gap = 1.2 cm
# Floor heights = 9cm (G) or 6cm (Typ)
# For simplicity, assume average or sum up exact areas?
# Most are 6cm high. One is 9cm.
# Let's be precise: group by floor height
panel_xz_weight = 0
panel_yz_weight = 0

# Helper to calc panel weight
def calc_panel_weight(df_panels, width_cm):
    w = 0
    # Group by floor to check height
    # But checking each element is easier.
    # Since we have 2 elements per panel, we can just sum areas of all elements and divide by 2?
    # No, area = width * height. Diagonal length doesn't directly give area easily without z.
    # Let's iterate.
    seen_pairs = set()
    for _, row in df_panels.iterrows():
        # Identify unique panel by sorted node pair? No, diagonals are different.
        # Identify by (floor, tower, x_left/right, y...)
        # Simplified:
        # Just use average height (weighted by count).
        # Better: Most floors are 6cm. Floor 0 is 9cm.
        # Check node Z difference.
        n1, n2 = int(row['node_i']), int(row['node_j'])
        h = abs(coords[n1][2] - coords[n2][2]) # cm (model units)
        # Volume = Width(m) * Height(m) * Thickness(m)
        # width_cm is in cm -> /100
        # h is in cm -> /100
        # THICKNESS is in mm -> /1000
        vol = (width_cm / 100) * (h / 100) * (THICKNESS_PANEL / 1000)
        w += vol * BALSA_DENSITY
    return w / 2 # Divide by 2 because 2 diagonals per panel

panel_xz_weight = calc_panel_weight(panel_xz, CORE_GAP)
panel_yz_weight = calc_panel_weight(panel_yz, CORE_GAP)

total_weight = frame_weight + panel_xz_weight + panel_yz_weight

print(f"\nWEIGHT ANALYSIS:")
print(f"  Frame Elements: {frame_weight:.3f} kg")
print(f"  Panels XZ:      {panel_xz_weight:.3f} kg ({n_panels_xz} panels)")
print(f"  Panels YZ:      {panel_yz_weight:.3f} kg ({n_panels_yz} panels)")
print(f"  TOTAL:          {total_weight:.3f} kg")
print(f"  Limit:          1.400 kg")
print(f"  Status:         {'✓ OK' if total_weight <= 1.4 else '✗ OVER LIMIT'}")

# ============================================
# SAVE & EXPORT
# ============================================
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)
position_df.to_csv(DATA_DIR / 'twin_position_matrix.csv', index=False)
connectivity_df.to_csv(DATA_DIR / 'twin_connectivity_matrix.csv', index=False)
np.savez(DATA_DIR / 'twin_building_data.npz',
         coords=coords, x_coords=X_COORDS, y_coords_t1=Y_COORDS_T1, y_coords_t2=Y_COORDS_T2, z_coords=Z_COORDS)

# DXF
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
doc = ezdxf.new('R2010')
msp = doc.modelspace()
LAYER_COLORS = {
    'column': 7, 'beam_x': 3, 'beam_y': 4,
    'brace_xz': 1, 'brace_yz': 1,
    'shear_wall_xz': 130, 'shear_wall_yz': 130, # Cyan/Greenish for panels
    'floor_brace': 6,
    'bridge_beam': 2, 'bridge_column': 2,
    'bridge_truss': 6, 'bridge_rigid': 5
}
for etype in connectivity_df['element_type'].unique():
    color = LAYER_COLORS.get(etype, 7)
    doc.layers.new(name=etype, dxfattribs={'color': color})

for _, elem in connectivity_df.iterrows():
    n1, n2 = int(elem['node_i']), int(elem['node_j'])
    p1 = tuple(coords[n1])
    p2 = tuple(coords[n2])
    msp.add_line(p1, p2, dxfattribs={'layer': elem['element_type']})

    # Add solid hatch for panels?
    # For now just lines. The user can see the layer color.

dxf_path = EXPORTS_DIR / 'twin_towers_v7_panels.dxf'
doc.saveas(dxf_path)
print(f"DXF Saved: {dxf_path}")
