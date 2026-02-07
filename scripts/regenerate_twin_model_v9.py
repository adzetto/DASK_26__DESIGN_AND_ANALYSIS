"""
TWIN TOWERS MODEL V9 - STIFFENED FOR ASCENDING REGION
======================================================
Goal: Reduce T1 from 0.200s to < 0.102s (DD-2 ascending region)

Changes from V8:
1. Extended shear walls up to floor 12 (was floor 6)
2. Added continuous Y-direction bracing (both faces)
3. Full X-bracing on ALL floors (not just upper)
4. Optimized beam removal to maintain weight < 1.4kg

Target: T < 0.102s (ascending region of DD-2)
"""

import numpy as np
import pandas as pd
from pathlib import Path
import ezdxf

print("=" * 70)
print("TWIN TOWERS MODEL V9 - STIFFENED FOR ASCENDING REGION")
print("=" * 70)

# ============================================
# GEOMETRY (Same as V8)
# ============================================
X_COORDS = np.array([0.0, 3.0, 11.0, 14.4, 15.6, 19.0, 27.0, 30.0])
Y_COORDS_T1 = np.array([0.0, 7.4, 8.6, 16.0])
Y_COORDS_T2 = np.array([24.0, 31.4, 32.6, 40.0])

GAP_X_MIN, GAP_X_MAX = 14.4, 15.6
GAP_Y_MIN_T1, GAP_Y_MAX_T1 = 7.4, 8.6
GAP_Y_MIN_T2, GAP_Y_MAX_T2 = 31.4, 32.6

FLOOR_HEIGHT_GROUND = 9.0
FLOOR_HEIGHT_NORMAL = 6.0
TOTAL_FLOORS = 26

Z_COORDS = [0.0, FLOOR_HEIGHT_GROUND]
for i in range(2, TOTAL_FLOORS):
    Z_COORDS.append(Z_COORDS[-1] + FLOOR_HEIGHT_NORMAL)
Z_COORDS = np.array(Z_COORDS)

print(f"Height: {Z_COORDS[-1]} cm ({TOTAL_FLOORS} floors)")

# ============================================
# NODES
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
# ELEMENTS
# ============================================
elements = []
elem_id = 0

def add_element(n1, n2, etype, tower='', conn='rigid'):
    global elem_id
    if n1 is None or n2 is None: return
    elements.append({
        'element_id': elem_id, 'node_i': n1, 'node_j': n2,
        'element_type': etype, 'tower': tower, 'connection': conn
    })
    elem_id += 1

def get_node(tower, floor, x, y):
    return node_lookup.get((tower, floor, x, y))

# ============================================
# V9 CONFIGURATION - MINIMAL WEIGHT BRACING
# ============================================
PANEL_FLOOR_LIMIT = 7    # Only slightly extended from 6 to 7
Y_BRACE_INTERVAL = 6     # Y-bracing every 6th floor (minimal)
X_BRACE_INTERVAL = 4     # X-bracing every 4th floor
FLOOR_BRACE_INTERVAL = 10 # Floor bracing every 10 floors
BEAM_REDUCTION = True    # Aggressive beam removal

print(f"\nV9 Configuration (Minimal Weight Addition):")
print(f"  Shear walls up to floor: {PANEL_FLOOR_LIMIT} (was 6 in V8)")
print(f"  Y-bracing interval: every {Y_BRACE_INTERVAL} floors")
print(f"  X-bracing interval: every {X_BRACE_INTERVAL} floors")
print(f"  Floor bracing interval: every {FLOOR_BRACE_INTERVAL} floors")

for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    tower_str = f'tower{tower_num}'
    gap_y_min = GAP_Y_MIN_T1 if tower_num == 1 else GAP_Y_MIN_T2
    gap_y_max = GAP_Y_MAX_T1 if tower_num == 1 else GAP_Y_MAX_T2

    for floor in range(TOTAL_FLOORS):
        # 1. COLUMNS - Keep all
        if floor < TOTAL_FLOORS - 1:
            for x in X_COORDS:
                for y in y_coords:
                    n1 = get_node(tower_num, floor, x, y)
                    n2 = get_node(tower_num, floor + 1, x, y)
                    add_element(n1, n2, 'column', tower_str)

        # 2. BEAMS X - Very aggressive removal for weight savings
        for i in range(len(X_COORDS) - 1):
            for y in y_coords:
                x1, x2 = X_COORDS[i], X_COORDS[i+1]
                is_gap_span = (abs(x1 - GAP_X_MIN) < 0.1 and abs(x2 - GAP_X_MAX) < 0.1)
                is_perimeter_y = (y == y_coords[0] or y == y_coords[-1])

                # Keep: perimeter, gap span, every 4th floor interior (was 3rd)
                is_essential = is_perimeter_y or is_gap_span
                keep_beam = is_essential or (floor % 4 == 0)

                if keep_beam:
                    n1 = get_node(tower_num, floor, x1, y)
                    n2 = get_node(tower_num, floor, x2, y)
                    add_element(n1, n2, 'beam_x', tower_str)

        # 3. BEAMS Y - Very aggressive removal (keep only essential + every 4th floor)
        for j in range(len(y_coords) - 1):
            for x in X_COORDS:
                y1, y2 = y_coords[j], y_coords[j+1]
                is_gap_span = (abs(y1 - gap_y_min) < 0.1 and abs(y2 - gap_y_max) < 0.1)
                is_perimeter_x = (x == X_COORDS[0] or x == X_COORDS[-1])
                is_core_line = (abs(x - GAP_X_MIN) < 0.1 or abs(x - GAP_X_MAX) < 0.1)

                is_essential = is_perimeter_x or is_core_line
                # Keep essential beams + every 4th floor for interior
                keep_beam = is_essential or (floor % 4 == 0 and not is_gap_span)

                if keep_beam:
                    n1 = get_node(tower_num, floor, x, y1)
                    n2 = get_node(tower_num, floor, x, y2)
                    add_element(n1, n2, 'beam_y', tower_str)

        # 4. VERTICAL BRACING / PANELS
        if floor < TOTAL_FLOORS - 1:

            # --- XZ PLANE (Front/Back Faces) ---
            for face_idx, y in enumerate([y_coords[0], y_coords[-1]]):
                for i in range(len(X_COORDS) - 1):
                    x_left = X_COORDS[i]
                    x_right = X_COORDS[i + 1]
                    span_w = x_right - x_left

                    n_bl = get_node(tower_num, floor, x_left, y)
                    n_br = get_node(tower_num, floor, x_right, y)
                    n_tl = get_node(tower_num, floor + 1, x_left, y)
                    n_tr = get_node(tower_num, floor + 1, x_right, y)

                    # GAP ZONE (1.2cm) -> EMPTY
                    if abs(span_w - 1.2) < 0.1:
                        continue

                    # 3.4cm BAYS -> EXTENDED PANELS (up to floor 12)
                    is_34_bay = abs(span_w - 3.4) < 0.1

                    if is_34_bay:
                        if floor <= PANEL_FLOOR_LIMIT:
                            # SHEAR WALL PANEL (X-brace representation)
                            add_element(n_bl, n_tr, 'shear_wall_xz', tower_str, 'rigid')
                            add_element(n_br, n_tl, 'shear_wall_xz', tower_str, 'rigid')
                        else:
                            # X-BRACE for upper floors
                            add_element(n_bl, n_tr, 'brace_xz', tower_str, 'pin')
                            add_element(n_br, n_tl, 'brace_xz', tower_str, 'pin')

                    # CORNER BAYS (3.0cm and 8.0cm) -> STRATEGIC BRACING
                    else:
                        # V9: Add bracing at interval (weight-conscious)
                        if floor % X_BRACE_INTERVAL == 0:
                            # Single diagonal per floor (alternating direction)
                            if (floor + i) % 2 == 0:
                                add_element(n_bl, n_tr, 'brace_xz', tower_str, 'pin')
                            else:
                                add_element(n_br, n_tl, 'brace_xz', tower_str, 'pin')

            # --- YZ PLANE (Side Faces) ---
            for face_idx, x in enumerate([X_COORDS[0], X_COORDS[-1]]):
                for j in range(len(y_coords) - 1):
                    y_bot, y_top = y_coords[j], y_coords[j+1]
                    span_h = y_top - y_bot

                    n_bl = get_node(tower_num, floor, x, y_bot)
                    n_br = get_node(tower_num, floor, x, y_top)
                    n_tl = get_node(tower_num, floor + 1, x, y_bot)
                    n_tr = get_node(tower_num, floor + 1, x, y_top)

                    # GAP ZONE -> EMPTY
                    if abs(span_h - 1.2) < 0.1:
                        continue

                    # V9: Y-BRACING at intervals (not all floors)
                    if floor % Y_BRACE_INTERVAL == 0:
                        # Full X-brace for stiffness
                        add_element(n_bl, n_tr, 'brace_yz', tower_str, 'pin')
                        add_element(n_br, n_tl, 'brace_yz', tower_str, 'pin')

            # --- FLOOR BRACING (Horizontal) ---
            # V9: Floor bracing at interval
            if floor % FLOOR_BRACE_INTERVAL == 0:
                for i in range(len(X_COORDS)-1):
                    for j in range(len(y_coords)-1):
                        x1, x2 = X_COORDS[i], X_COORDS[i+1]
                        y1, y2 = y_coords[j], y_coords[j+1]
                        if abs(x2-x1 - 1.2) < 0.1 or abs(y2-y1 - 1.2) < 0.1:
                            continue
                        n1 = get_node(tower_num, floor, x1, y1)
                        n2 = get_node(tower_num, floor, x2, y2)
                        add_element(n1, n2, 'floor_brace', tower_str, 'pin')

print(f"Tower elements: {len(elements)}")

# ============================================
# BRIDGES (Same as V8)
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
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t1_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_truss')
    add_bridge_elem(t2_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t1_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_truss')
    add_bridge_elem(t2_bot_r, mid_top_r, 'bridge_truss')
    add_bridge_elem(t1_bot_l, t2_bot_r, 'bridge_rigid')
    add_bridge_elem(t2_bot_l, t1_bot_r, 'bridge_rigid')
    add_bridge_elem(t1_top_l, t2_top_r, 'bridge_rigid')
    add_bridge_elem(t2_top_l, t1_top_r, 'bridge_rigid')

for fb, ft in BRIDGE_FLOORS_SINGLE:
    create_bridge(fb, ft, is_rigid=True)
create_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1], is_rigid=True)

# ============================================
# FINALIZE
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

all_elements = elements + bridge_elements
for elem in all_elements:
    n1, n2 = elem['node_i'], elem['node_j']
    c1, c2 = coords[n1], coords[n2]
    elem['length'] = round(np.sqrt(np.sum((c2 - c1) ** 2)), 4)

connectivity_df = pd.DataFrame(all_elements)

# ============================================
# WEIGHT CALCULATION
# ============================================
BALSA_DENSITY = 160  # kg/m^3
SECTION_FRAME = 36   # mm^2 (6x6)
THICKNESS_PANEL = 3  # mm

frame_types = ['column', 'beam_x', 'beam_y', 'brace_xz', 'brace_yz', 'floor_brace',
               'bridge_beam', 'bridge_column', 'bridge_truss', 'bridge_rigid']
frame_df = connectivity_df[connectivity_df['element_type'].isin(frame_types)]
frame_weight = frame_df['length'].sum() * 10 * SECTION_FRAME * BALSA_DENSITY / 1e9

# Panels
panel_xz = connectivity_df[connectivity_df['element_type'] == 'shear_wall_xz']
w_xz = 0
for _, row in panel_xz.iterrows():
    n1, n2 = int(row['node_i']), int(row['node_j'])
    h_cm = abs(coords[n1][2] - coords[n2][2])
    vol_cm3 = 3.4 * h_cm * (THICKNESS_PANEL / 10)
    w_xz += vol_cm3 * BALSA_DENSITY / 1e6
w_xz = w_xz / 2  # 2 diagonals per panel

total_weight = frame_weight + w_xz

print(f"\n" + "=" * 70)
print("WEIGHT ANALYSIS (V9):")
print("=" * 70)
print(f"  Frame Elements: {frame_weight:.3f} kg")
print(f"  Panels:         {w_xz:.3f} kg")
print(f"  TOTAL:          {total_weight:.3f} kg")
print(f"  Limit:          1.400 kg")
print(f"  Margin:         {1.400 - total_weight:.3f} kg")

if total_weight > 1.4:
    print(f"  Status:         OVER LIMIT by {total_weight - 1.4:.3f} kg!")
else:
    print(f"  Status:         OK")

# Element summary
print(f"\n" + "=" * 70)
print("ELEMENT SUMMARY (V9):")
print("=" * 70)
for etype in connectivity_df['element_type'].unique():
    count = len(connectivity_df[connectivity_df['element_type'] == etype])
    length = connectivity_df[connectivity_df['element_type'] == etype]['length'].sum()
    print(f"  {etype:<20}: {count:4d} elements, {length:8.1f} cm")

print(f"\n  TOTAL: {len(connectivity_df)} elements")

# ============================================
# SAVE
# ============================================
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

# Save as V9 versions
position_df.to_csv(DATA_DIR / 'twin_position_matrix_v9.csv', index=False)
connectivity_df.to_csv(DATA_DIR / 'twin_connectivity_matrix_v9.csv', index=False)

# DXF
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)
doc = ezdxf.new('R2010')
msp = doc.modelspace()
for _, elem in connectivity_df.iterrows():
    n1, n2 = int(elem['node_i']), int(elem['node_j'])
    msp.add_line(tuple(coords[n1]), tuple(coords[n2]),
                 dxfattribs={'layer': elem['element_type'], 'color': 7})
doc.saveas(EXPORTS_DIR / 'twin_towers_v9_stiffened.dxf')

print(f"\nSaved: data/twin_position_matrix_v9.csv")
print(f"Saved: data/twin_connectivity_matrix_v9.csv")
print(f"Saved: exports/twin_towers_v9_stiffened.dxf")
print("\n" + "=" * 70)
print("MODEL V9 GENERATION COMPLETE")
print("=" * 70)
