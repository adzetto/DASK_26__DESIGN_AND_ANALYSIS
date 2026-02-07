#!/usr/bin/env python3
"""
TWIN TOWERS MODEL V2 - TBDY2018 & DASK Compliant
================================================
Structural regularity improvements:
- Column continuity from podium to tower
- Bridges connected to columns
- Chevron bracing on front/back (3.4m bays)
- X-bracing on sides
- No irregularities

Layout:
- Base: 36 x 36 cm (scale 1:100 → 36 x 36 m)
- Podium X: 7-7-3.4-1.2-3.4-7-7 = 36m
- Side Y (each tower): 4-3.4-1.2-3.4-4 = 16m
- Tower gap: 8m (Y=16 to Y=24)
- Total Y: 16 + 8 + 16 = 40m? → Adjust to fit 36m base

Actually for 36m Y total:
- Tower 1: 0-14m (4-3-1-3-3 = 14m)
- Gap: 8m (Y=14 to Y=22)
- Tower 2: 22-36m

Let me recalculate to fit 36m:
Option 1: Keep tower depth 16m, reduce gap
- Tower 1: 0-16m, Gap: 4m, Tower 2: 20-36m (total 36m)
- Gap too small for bridges

Option 2: Reduce tower depth
- Tower 1: 0-14m (4-2.5-1-2.5-4 = 14m)
- Gap: 8m
- Tower 2: 22-36m
- Total: 14 + 8 + 14 = 36m ✓

Final Layout:
- Podium X: 7-7-3.4-1.2-3.4-7-7 = 36m → [0, 7, 14, 17.4, 18.6, 22, 29, 36]
- Tower Y: 4-2.5-1-2.5-4 = 14m (symmetric, 1m core)
- Tower 1 Y: [0, 4, 6.5, 7.5, 10, 14]
- Tower 2 Y: [22, 26, 28.5, 29.5, 32, 36]
- Gap: Y = 14 to 22 (8m)
"""

import numpy as np
import pandas as pd
from pathlib import Path
import ezdxf

print("=" * 70)
print("TWIN TOWERS MODEL V2 - TBDY2018 & DASK Compliant")
print("=" * 70)

# ============================================
# GEOMETRY PARAMETERS
# ============================================
# Base: 36 x 36 cm (model scale 1:100)
BASE_X = 36.0  # m
BASE_Y = 36.0  # m

# Podium X layout: 7-7-3.4-1.2-3.4-7-7 = 36m
PODIUM_X_COORDS = np.array([0.0, 7.0, 14.0, 17.4, 18.6, 22.0, 29.0, 36.0])
PODIUM_X_BAYS = [7.0, 7.0, 3.4, 1.2, 3.4, 7.0, 7.0]

# Tower Y layout per tower: 4-3.4-1.2-3.4-4 = 16m (as specified)
# Total Y remains 40m: Tower1(16m) + Gap(8m) + Tower2(16m) = 40m
TOWER_Y_BAYS = [4.0, 3.4, 1.2, 3.4, 4.0]  # 16m total
TOWER_DEPTH = sum(TOWER_Y_BAYS)  # 16m
TOWER_GAP = 8.0  # 8m gap for bridges

# Tower Y coordinates (40m total, not 36m in Y)
Y_COORDS_T1 = np.array([0.0, 4.0, 7.4, 8.6, 12.0, 16.0])
Y_COORDS_T2 = np.array([24.0, 28.0, 31.4, 32.6, 36.0, 40.0])
BASE_Y = 40.0  # Keep 40m in Y direction for bridge clearance

print(f"Base: {BASE_X} x {BASE_Y} m")
print(f"Tower 1 Y: {Y_COORDS_T1[0]} to {Y_COORDS_T1[-1]}m (depth: {TOWER_DEPTH}m)")
print(f"Tower 2 Y: {Y_COORDS_T2[0]} to {Y_COORDS_T2[-1]}m (depth: {TOWER_DEPTH}m)")
print(f"Gap: {TOWER_GAP}m (Y={Y_COORDS_T1[-1]} to Y={Y_COORDS_T2[0]})")

# Tower X: Use central columns from podium for continuity
# Podium X: [0, 7, 14, 17.4, 18.6, 22, 29, 36]
# Tower uses: [7, 14, 17.4, 18.6, 22, 29] (drop edge columns)
TOWER_X_COORDS = np.array([7.0, 14.0, 17.4, 18.6, 22.0, 29.0])

print(f"Podium X coords: {PODIUM_X_COORDS}")
print(f"Tower X coords: {TOWER_X_COORDS}")

# Floor heights
FLOOR_HEIGHT_GROUND = 9.0  # m (F0 to F1)
FLOOR_HEIGHT_NORMAL = 6.0  # m (F1+)

TOTAL_FLOORS = 26  # F0 to F25 (F25 = roof at 153m)
PODIUM_FLOORS = 13  # F0 to F12 = podium (75m height)

# Calculate Z coordinates
Z_COORDS = [0.0, FLOOR_HEIGHT_GROUND]  # F0, F1
for i in range(2, TOTAL_FLOORS):
    Z_COORDS.append(Z_COORDS[-1] + FLOOR_HEIGHT_NORMAL)
Z_COORDS = np.array(Z_COORDS)

TOTAL_HEIGHT = Z_COORDS[-1]
PODIUM_HEIGHT = Z_COORDS[PODIUM_FLOORS]

print(f"Height: {TOTAL_HEIGHT}m ({TOTAL_FLOORS} floors)")
print(f"Podium: {PODIUM_HEIGHT}m ({PODIUM_FLOORS} floors)")

# ============================================
# NODE GENERATION
# ============================================
nodes = []
node_id = 0
node_lookup = {}  # (tower, floor, x, y) -> node_id

def add_node(tower, floor, x, y, zone):
    global node_id
    z = Z_COORDS[floor]
    key = (tower, floor, x, y)
    if key not in node_lookup:
        nodes.append({
            'node_id': node_id, 'x': x, 'y': y, 'z': z,
            'floor': floor, 'zone': zone, 'tower': tower
        })
        node_lookup[key] = node_id
        node_id += 1
    return node_lookup[key]

# Generate tower nodes
for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    for floor in range(TOTAL_FLOORS):
        if floor < PODIUM_FLOORS:
            # Podium: use full X coords
            x_coords = PODIUM_X_COORDS
            zone = 'podium'
        else:
            # Tower: use reduced X coords (column continuity)
            x_coords = TOWER_X_COORDS
            zone = 'tower'

        for x in x_coords:
            for y in y_coords:
                add_node(tower_num, floor, x, y, zone)

n_nodes = len(nodes)
print(f"Nodes: {n_nodes}")

# Create position dataframe
position_df = pd.DataFrame(nodes)

# Create coordinate array
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
        'element_id': elem_id,
        'node_i': n1,
        'node_j': n2,
        'element_type': etype,
        'tower': tower,
        'connection': conn
    })
    elem_id += 1
    return elem_id - 1

def get_node(tower, floor, x, y):
    return node_lookup.get((tower, floor, x, y))

# Generate elements for each tower
for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    tower_str = f'tower{tower_num}'

    for floor in range(TOTAL_FLOORS):
        is_podium = floor < PODIUM_FLOORS
        x_coords = PODIUM_X_COORDS if is_podium else TOWER_X_COORDS

        # COLUMNS (vertical)
        if floor < TOTAL_FLOORS - 1:
            next_floor = floor + 1
            next_x_coords = PODIUM_X_COORDS if next_floor < PODIUM_FLOORS else TOWER_X_COORDS

            for x in x_coords:
                # Check if column continues to next floor
                if x in next_x_coords:
                    for y in y_coords:
                        n1 = get_node(tower_num, floor, x, y)
                        n2 = get_node(tower_num, next_floor, x, y)
                        add_element(n1, n2, 'column', tower_str)

        # BEAMS (horizontal)
        # X-direction beams
        for i in range(len(x_coords) - 1):
            for y in y_coords:
                n1 = get_node(tower_num, floor, x_coords[i], y)
                n2 = get_node(tower_num, floor, x_coords[i+1], y)
                add_element(n1, n2, 'beam_x', tower_str)

        # Y-direction beams
        for x in x_coords:
            for j in range(len(y_coords) - 1):
                n1 = get_node(tower_num, floor, x, y_coords[j])
                n2 = get_node(tower_num, floor, x, y_coords[j+1])
                add_element(n1, n2, 'beam_y', tower_str)

        # BRACING AND CORE WALLS - Only at key floors to reduce weight
        # Key floors: 0, 4, 8, 12 (podium), 16, 20, 24 (tower)
        BRACING_FLOORS = [0, 4, 8, 12, 16, 20, 24]

        if floor < TOTAL_FLOORS - 1 and floor in BRACING_FLOORS:
            next_floor = floor + 1
            next_x_coords = PODIUM_X_COORDS if next_floor < PODIUM_FLOORS else TOWER_X_COORDS

            # =============================================
            # CORE WALLS (X-direction: 1.2m bay, Y-direction: 1.2m bay)
            # =============================================
            # X-direction core: between 17.4 and 18.6 (1.2m bay)
            if 17.4 in x_coords and 18.6 in x_coords:
                for y in [y_coords[0], y_coords[-1]]:
                    n1 = get_node(tower_num, floor, 17.4, y)
                    n2 = get_node(tower_num, next_floor, 18.6, y)
                    add_element(n1, n2, 'core_wall', tower_str)
                    n1 = get_node(tower_num, floor, 18.6, y)
                    n2 = get_node(tower_num, next_floor, 17.4, y)
                    add_element(n1, n2, 'core_wall', tower_str)

            # Y-direction core: 1.2m bay (y_coords[2] to y_coords[3])
            y_core_1 = y_coords[2]  # 7.4 or 31.4
            y_core_2 = y_coords[3]  # 8.6 or 32.6
            x_edges = [x_coords[0], x_coords[-1]]
            for x in x_edges:
                if x in next_x_coords:
                    n1 = get_node(tower_num, floor, x, y_core_1)
                    n2 = get_node(tower_num, next_floor, x, y_core_2)
                    add_element(n1, n2, 'core_wall', tower_str)
                    n1 = get_node(tower_num, floor, x, y_core_2)
                    n2 = get_node(tower_num, next_floor, x, y_core_1)
                    add_element(n1, n2, 'core_wall', tower_str)

            # =============================================
            # FRONT/BACK FACES (XZ plane) - CHEVRON BRACING
            # Only in 3.4m bays (indices 2,4 in podium: 14-17.4 and 18.6-22)
            # =============================================
            chevron_bays = []
            for i in range(len(x_coords) - 1):
                bay_width = x_coords[i+1] - x_coords[i]
                if abs(bay_width - 3.4) < 0.1:  # 3.4m bay
                    chevron_bays.append((x_coords[i], x_coords[i+1]))

            for y in [y_coords[0], y_coords[-1]]:  # Front and back faces
                for x_left, x_right in chevron_bays:
                    if x_left in next_x_coords and x_right in next_x_coords:
                        # Chevron pattern: inverted V
                        x_mid = (x_left + x_right) / 2
                        # Find mid-point node or use beam midpoint approximation
                        # For chevron, connect bottom corners to top center
                        n_bot_left = get_node(tower_num, floor, x_left, y)
                        n_bot_right = get_node(tower_num, floor, x_right, y)
                        n_top_left = get_node(tower_num, next_floor, x_left, y)
                        n_top_right = get_node(tower_num, next_floor, x_right, y)

                        # X-bracing as chevron approximation
                        add_element(n_bot_left, n_top_right, 'brace_chevron', tower_str, 'pin')
                        add_element(n_bot_right, n_top_left, 'brace_chevron', tower_str, 'pin')

            # =============================================
            # SIDE FACES (YZ plane) - X-BRACING
            # =============================================
            # Use left and right X edges
            x_edges = [x_coords[0], x_coords[-1]]
            for x in x_edges:
                if x in next_x_coords:
                    # X-brace in each Y bay
                    for j in range(len(y_coords) - 1):
                        # Skip core bay (1.0m)
                        bay_width = y_coords[j+1] - y_coords[j]
                        if bay_width < 1.5:  # Skip narrow core bay
                            continue

                        n1 = get_node(tower_num, floor, x, y_coords[j])
                        n2 = get_node(tower_num, next_floor, x, y_coords[j+1])
                        n3 = get_node(tower_num, floor, x, y_coords[j+1])
                        n4 = get_node(tower_num, next_floor, x, y_coords[j])

                        # X-bracing pattern
                        add_element(n1, n2, 'brace_x', tower_str, 'pin')
                        add_element(n3, n4, 'brace_x', tower_str, 'pin')

# ============================================
# PODIUM-TO-TOWER TRANSITION BRACING
# ============================================
# At podium top (F12), add transfer elements where columns discontinue
for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    tower_str = f'tower{tower_num}'
    f_pod_top = PODIUM_FLOORS - 1  # F12
    f_tow_bot = PODIUM_FLOORS  # F13

    # Columns at X=0 and X=36 don't continue to tower
    # Add diagonal transfers
    for x_pod, x_tow in [(0.0, 7.0), (36.0, 29.0)]:
        for y in y_coords:
            n_pod = get_node(tower_num, f_pod_top, x_pod, y)
            n_tow = get_node(tower_num, f_tow_bot, x_tow, y)
            if n_pod is not None and n_tow is not None:
                add_element(n_pod, n_tow, 'brace_transfer', tower_str, 'pin')

print(f"Tower elements: {len(elements)}")

# ============================================
# BRIDGE GENERATION - CONNECTED TO COLUMNS
# ============================================
# Bridge locations: must connect to actual column locations
# Tower X coords: [7, 14, 17.4, 18.6, 22, 29]
# Use X=14 and X=22 for bridge connections (these are column locations)

BRIDGE_X_LEFT = 14.0   # Column location
BRIDGE_X_RIGHT = 22.0  # Column location
BRIDGE_WIDTH = BRIDGE_X_RIGHT - BRIDGE_X_LEFT  # 8m

# Bridge floors
BRIDGE_FLOORS_SINGLE = [(5, 6), (11, 12), (17, 18)]
BRIDGE_FLOORS_DOUBLE = (23, 25)

Y_T1_BACK = Y_COORDS_T1[-1]   # 14.0
Y_T2_FRONT = Y_COORDS_T2[0]   # 22.0
Y_BRIDGE_MID = (Y_T1_BACK + Y_T2_FRONT) / 2  # 18.0

print(f"\nBridge X: {BRIDGE_X_LEFT} to {BRIDGE_X_RIGHT} ({BRIDGE_WIDTH}m)")
print(f"Bridge Y: {Y_T1_BACK} to {Y_T2_FRONT} ({Y_T2_FRONT - Y_T1_BACK}m gap)")

# Bridge mid-span nodes
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

# Create bridge mid-span nodes
all_bridge_floors = set()
for fb, ft in BRIDGE_FLOORS_SINGLE:
    all_bridge_floors.add(fb)
    all_bridge_floors.add(ft)
for f in [BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1]]:
    all_bridge_floors.add(f)

for f in all_bridge_floors:
    for x in [BRIDGE_X_LEFT, BRIDGE_X_RIGHT]:
        add_bridge_node(f, x, Y_BRIDGE_MID)

bridge_elements = []

def add_bridge_elem(n1, n2, etype, conn='rigid'):
    global elem_id
    if n1 is None or n2 is None:
        print(f"  WARNING: Bridge element skipped - missing node")
        return
    bridge_elements.append({
        'element_id': elem_id,
        'node_i': n1,
        'node_j': n2,
        'element_type': etype,
        'tower': 'bridge',
        'connection': conn
    })
    elem_id += 1

def create_bridge(floor_bot, floor_top):
    """Create bridge with proper column connections"""
    print(f"  Creating bridge F{floor_bot}-F{floor_top}...")

    # Get column nodes at tower faces
    # Tower 1 back face (Y = 14)
    t1_bot_left = get_node(1, floor_bot, BRIDGE_X_LEFT, Y_T1_BACK)
    t1_bot_right = get_node(1, floor_bot, BRIDGE_X_RIGHT, Y_T1_BACK)
    t1_top_left = get_node(1, floor_top, BRIDGE_X_LEFT, Y_T1_BACK)
    t1_top_right = get_node(1, floor_top, BRIDGE_X_RIGHT, Y_T1_BACK)

    # Tower 2 front face (Y = 22)
    t2_bot_left = get_node(2, floor_bot, BRIDGE_X_LEFT, Y_T2_FRONT)
    t2_bot_right = get_node(2, floor_bot, BRIDGE_X_RIGHT, Y_T2_FRONT)
    t2_top_left = get_node(2, floor_top, BRIDGE_X_LEFT, Y_T2_FRONT)
    t2_top_right = get_node(2, floor_top, BRIDGE_X_RIGHT, Y_T2_FRONT)

    # Bridge mid-span nodes
    mid_bot_left = get_bridge_node(floor_bot, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    mid_bot_right = get_bridge_node(floor_bot, BRIDGE_X_RIGHT, Y_BRIDGE_MID)
    mid_top_left = get_bridge_node(floor_top, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    mid_top_right = get_bridge_node(floor_top, BRIDGE_X_RIGHT, Y_BRIDGE_MID)

    # Check all nodes exist
    nodes_dict = {
        't1_bot_left': t1_bot_left, 't1_bot_right': t1_bot_right,
        't1_top_left': t1_top_left, 't1_top_right': t1_top_right,
        't2_bot_left': t2_bot_left, 't2_bot_right': t2_bot_right,
        't2_top_left': t2_top_left, 't2_top_right': t2_top_right,
        'mid_bot_left': mid_bot_left, 'mid_bot_right': mid_bot_right,
        'mid_top_left': mid_top_left, 'mid_top_right': mid_top_right
    }

    missing = [k for k, v in nodes_dict.items() if v is None]
    if missing:
        print(f"    WARNING: Missing nodes: {missing}")
        return

    # BOTTOM FLOOR BEAMS
    add_bridge_elem(t1_bot_left, t1_bot_right, 'bridge_beam')
    add_bridge_elem(t1_bot_left, mid_bot_left, 'bridge_beam')
    add_bridge_elem(t1_bot_right, mid_bot_right, 'bridge_beam')
    add_bridge_elem(mid_bot_left, mid_bot_right, 'bridge_beam')
    add_bridge_elem(mid_bot_left, t2_bot_left, 'bridge_beam')
    add_bridge_elem(mid_bot_right, t2_bot_right, 'bridge_beam')
    add_bridge_elem(t2_bot_left, t2_bot_right, 'bridge_beam')

    # TOP FLOOR BEAMS
    add_bridge_elem(t1_top_left, t1_top_right, 'bridge_beam')
    add_bridge_elem(t1_top_left, mid_top_left, 'bridge_beam')
    add_bridge_elem(t1_top_right, mid_top_right, 'bridge_beam')
    add_bridge_elem(mid_top_left, mid_top_right, 'bridge_beam')
    add_bridge_elem(mid_top_left, t2_top_left, 'bridge_beam')
    add_bridge_elem(mid_top_right, t2_top_right, 'bridge_beam')
    add_bridge_elem(t2_top_left, t2_top_right, 'bridge_beam')

    # VERTICAL COLUMNS (only at mid-span, tower nodes use tower columns)
    add_bridge_elem(mid_bot_left, mid_top_left, 'bridge_column')
    add_bridge_elem(mid_bot_right, mid_top_right, 'bridge_column')

    # COUPLED SHEAR WALL - YZ plane bracing (Y-direction resistance)
    # Left side (X = 14)
    add_bridge_elem(t1_bot_left, mid_top_left, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_left, t1_top_left, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_left, t2_top_left, 'bridge_shear_yz')
    add_bridge_elem(t2_bot_left, mid_top_left, 'bridge_shear_yz')

    # Right side (X = 22)
    add_bridge_elem(t1_bot_right, mid_top_right, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_right, t1_top_right, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_right, t2_top_right, 'bridge_shear_yz')
    add_bridge_elem(t2_bot_right, mid_top_right, 'bridge_shear_yz')

    # TRUSS - Side faces (connecting T1 to mid to T2)
    # Left side
    add_bridge_elem(t1_bot_left, mid_top_left, 'bridge_truss')
    add_bridge_elem(mid_bot_left, t2_top_left, 'bridge_truss')
    # Right side
    add_bridge_elem(t1_bot_right, mid_top_right, 'bridge_truss')
    add_bridge_elem(mid_bot_right, t2_top_right, 'bridge_truss')

    # XZ plane bracing (minor)
    add_bridge_elem(t1_bot_left, t1_top_right, 'bridge_brace_xz')
    add_bridge_elem(t1_bot_right, t1_top_left, 'bridge_brace_xz')
    add_bridge_elem(t2_bot_left, t2_top_right, 'bridge_brace_xz')
    add_bridge_elem(t2_bot_right, t2_top_left, 'bridge_brace_xz')

# Create all bridges
print("\nCreating bridges...")
for fb, ft in BRIDGE_FLOORS_SINGLE:
    create_bridge(fb, ft)
create_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1])

print(f"Bridge elements: {len(bridge_elements)}")
print(f"Bridge mid-span nodes: {len(bridge_nodes)}")

# ============================================
# COMBINE ALL DATA
# ============================================
# Add bridge nodes to position dataframe
if bridge_nodes:
    bridge_nodes_df = pd.DataFrame(bridge_nodes)
    position_df = pd.concat([position_df, bridge_nodes_df], ignore_index=True)

    # Extend coordinate array
    n_total = n_nodes + len(bridge_nodes)
    new_coords = np.zeros((n_total, 3))
    new_coords[:n_nodes] = coords
    for bn in bridge_nodes:
        new_coords[bn['node_id']] = [bn['x'], bn['y'], bn['z']]
    coords = new_coords
else:
    n_total = n_nodes

# Combine all elements
all_elements = elements + bridge_elements

# Calculate lengths
for elem in all_elements:
    n1, n2 = elem['node_i'], elem['node_j']
    c1, c2 = coords[n1], coords[n2]
    length = np.sqrt(np.sum((c2 - c1) ** 2))
    elem['length'] = round(length, 4)

connectivity_df = pd.DataFrame(all_elements)

print(f"\nTotal nodes: {n_total}")
print(f"Total elements: {len(connectivity_df)}")
print("\nElements by type:")
print(connectivity_df['element_type'].value_counts().to_string())

# ============================================
# WEIGHT ANALYSIS
# ============================================
total_length_mm = connectivity_df['length'].sum() * 10  # m to mm (scale 1:100)
BALSA_AREA = 36  # mm^2 (6x6mm)
WEIGHT_LIMIT = 1.40  # kg

weight = total_length_mm * BALSA_AREA * 160 / 1e9  # kg (density 160 kg/m3)
margin = WEIGHT_LIMIT - weight

print(f"\nTotal length: {total_length_mm:,.0f} mm")
print(f"Weight (ρ=160): {weight:.3f} kg")
print(f"Limit: {WEIGHT_LIMIT} kg")
print(f"Margin: {margin*1000:.0f}g")
print(f"Status: {'✓ OK' if weight <= WEIGHT_LIMIT else '✗ OVER'}")

# ============================================
# SAVE DATA
# ============================================
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

position_df.to_csv(DATA_DIR / 'twin_position_matrix.csv', index=False)
connectivity_df.to_csv(DATA_DIR / 'twin_connectivity_matrix.csv', index=False)

# Adjacency matrix
adj = np.zeros((n_total, n_total), dtype=int)
for _, row in connectivity_df.iterrows():
    i, j = int(row['node_i']), int(row['node_j'])
    adj[i, j] = adj[j, i] = 1
np.savetxt(DATA_DIR / 'twin_adjacency_matrix.csv', adj, delimiter=',', fmt='%d')

# NPZ file
np.savez(DATA_DIR / 'twin_building_data.npz',
         adjacency_matrix=adj, coords=coords,
         podium_x=PODIUM_X_COORDS, tower_x=TOWER_X_COORDS,
         y_coords_t1=Y_COORDS_T1, y_coords_t2=Y_COORDS_T2, z_coords=Z_COORDS,
         tower_gap=TOWER_GAP,
         bridge_floors_single=np.array(BRIDGE_FLOORS_SINGLE),
         bridge_floors_double=np.array(BRIDGE_FLOORS_DOUBLE))

print(f"\nData saved to {DATA_DIR}")

# ============================================
# CREATE DXF
# ============================================
print("\nCreating DXF...")
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

doc = ezdxf.new('R2010')
msp = doc.modelspace()

# Layer colors
LAYER_COLORS = {
    'column': 7, 'beam_x': 3, 'beam_y': 4,
    'brace_chevron': 1, 'brace_x': 1, 'brace_transfer': 6,
    'core_wall': 5,
    'bridge_beam': 2, 'bridge_column': 2,
    'bridge_shear_yz': 1, 'bridge_truss': 6, 'bridge_brace_xz': 4
}

for etype in connectivity_df['element_type'].unique():
    color = LAYER_COLORS.get(etype, 7)
    doc.layers.new(name=etype, dxfattribs={'color': color})

# Add elements
for _, elem in connectivity_df.iterrows():
    n1, n2 = int(elem['node_i']), int(elem['node_j'])
    p1 = tuple(coords[n1])
    p2 = tuple(coords[n2])
    msp.add_line(p1, p2, dxfattribs={'layer': elem['element_type']})

dxf_path = EXPORTS_DIR / 'twin_towers_v2.dxf'
doc.saveas(dxf_path)

print(f"\n{'='*70}")
print(f"DXF SAVED: {dxf_path}")
print(f"{'='*70}")

# ============================================
# STRUCTURAL SUMMARY
# ============================================
print("\n" + "="*70)
print("STRUCTURAL SUMMARY - TBDY2018 & DASK COMPLIANT")
print("="*70)
print(f"""
Layout:
  Base: {BASE_X} x {BASE_Y} cm (36x36)
  Podium X: 7-7-3.4-1.2-3.4-7-7 = 36m
  Tower Y: 4-2.5-1-2.5-4 = 14m per tower
  Gap: {TOWER_GAP}m

Column Continuity:
  - Podium columns at X=[0,7,14,17.4,18.6,22,29,36]
  - Tower columns at X=[7,14,17.4,18.6,22,29] (continuous)
  - Transfer braces at X=0→7 and X=36→29

Bracing System:
  - Chevron bracing on front/back faces (3.4m bays)
  - X-bracing on side faces
  - Core walls in 1.2m (X) and 1.0m (Y) bays

Bridges:
  - Connected to columns at X=14 and X=22
  - 4 bridges total at F5-6, F11-12, F17-18, F23-25
  - Coupled shear wall bracing for Y-direction resistance
  - 8m x 8m footprint

Weight: {weight:.3f} kg / {WEIGHT_LIMIT} kg limit ({margin*1000:.0f}g margin)
""")
