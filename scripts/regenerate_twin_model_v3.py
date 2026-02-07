#!/usr/bin/env python3
"""
TWIN TOWERS MODEL V3 - TBDY2018 & DASK Compliant (Weight Optimized)
====================================================================
Reduced weight version with:
- Perimeter frame + Core structure
- Simplified interior grid
- Bracing only at key floors

Layout:
- Base X: 36cm (7-7-3.4-1.2-3.4-7-7)
- Base Y: 40cm (two towers + gap)
- Tower Y: 16cm each (4-3.4-1.2-3.4-4)
"""

import numpy as np
import pandas as pd
from pathlib import Path
import ezdxf

print("=" * 70)
print("TWIN TOWERS MODEL V3 - Weight Optimized")
print("=" * 70)

# ============================================
# GEOMETRY PARAMETERS
# ============================================
# Podium X: 7-7-3.4-1.2-3.4-7-7 = 36m (FULL GRID)
PODIUM_X_COORDS = np.array([0.0, 7.0, 14.0, 17.4, 18.6, 22.0, 29.0, 36.0])
PODIUM_X_BAYS = [7.0, 7.0, 3.4, 1.2, 3.4, 7.0, 7.0]

# Tower X: Central columns only (column continuity from podium)
TOWER_X_COORDS = np.array([7.0, 14.0, 17.4, 18.6, 22.0, 29.0])

# Tower Y: 4-3.4-1.2-3.4-4 = 16m (FULL GRID)
Y_BAYS_T1 = np.array([0.0, 4.0, 7.4, 8.6, 12.0, 16.0])
Y_BAYS_T2 = np.array([24.0, 28.0, 31.4, 32.6, 36.0, 40.0])

TOWER_GAP = 8.0

print(f"Podium X: {PODIUM_X_COORDS} (6 positions)")
print(f"Tower X: {TOWER_X_COORDS} (4 positions)")
print(f"Tower 1 Y: {Y_BAYS_T1}")
print(f"Tower 2 Y: {Y_BAYS_T2}")

# Floor heights
FLOOR_HEIGHT_GROUND = 9.0
FLOOR_HEIGHT_NORMAL = 6.0
TOTAL_FLOORS = 26
PODIUM_FLOORS = 13

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

# Generate nodes
for tower_num, y_coords in [(1, Y_BAYS_T1), (2, Y_BAYS_T2)]:
    for floor in range(TOTAL_FLOORS):
        x_coords = PODIUM_X_COORDS if floor < PODIUM_FLOORS else TOWER_X_COORDS
        zone = 'podium' if floor < PODIUM_FLOORS else 'tower'

        for x in x_coords:
            for y in y_coords:
                add_node(tower_num, floor, x, y, zone)

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
    return elem_id - 1

def get_node(tower, floor, x, y):
    return node_lookup.get((tower, floor, x, y))

# Key bracing floors (every 2 floors for better lateral resistance)
BRACING_FLOORS = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24]

for tower_num, y_coords in [(1, Y_BAYS_T1), (2, Y_BAYS_T2)]:
    tower_str = f'tower{tower_num}'

    for floor in range(TOTAL_FLOORS):
        is_podium = floor < PODIUM_FLOORS
        x_coords = PODIUM_X_COORDS if is_podium else TOWER_X_COORDS

        # COLUMNS
        if floor < TOTAL_FLOORS - 1:
            next_x_coords = PODIUM_X_COORDS if floor + 1 < PODIUM_FLOORS else TOWER_X_COORDS
            for x in x_coords:
                if x in next_x_coords:
                    for y in y_coords:
                        n1 = get_node(tower_num, floor, x, y)
                        n2 = get_node(tower_num, floor + 1, x, y)
                        add_element(n1, n2, 'column', tower_str)

        # BEAMS - X direction (perimeter + core)
        for i in range(len(x_coords) - 1):
            for y in [y_coords[0], y_coords[-1]]:  # Only perimeter
                n1 = get_node(tower_num, floor, x_coords[i], y)
                n2 = get_node(tower_num, floor, x_coords[i+1], y)
                add_element(n1, n2, 'beam_x', tower_str)
            # Core beams (middle Y)
            for y in y_coords[1:-1]:
                n1 = get_node(tower_num, floor, x_coords[i], y)
                n2 = get_node(tower_num, floor, x_coords[i+1], y)
                add_element(n1, n2, 'beam_x', tower_str)

        # BEAMS - Y direction (perimeter + core)
        for j in range(len(y_coords) - 1):
            for x in [x_coords[0], x_coords[-1]]:  # Only perimeter
                n1 = get_node(tower_num, floor, x, y_coords[j])
                n2 = get_node(tower_num, floor, x, y_coords[j+1])
                add_element(n1, n2, 'beam_y', tower_str)
            # Core beams (middle X: 17.4 and 18.6)
            for x in x_coords:
                if 17.0 < x < 19.0:  # Core X
                    n1 = get_node(tower_num, floor, x, y_coords[j])
                    n2 = get_node(tower_num, floor, x, y_coords[j+1])
                    add_element(n1, n2, 'beam_y', tower_str)

        # BRACING (only at key floors)
        if floor < TOTAL_FLOORS - 1 and floor in BRACING_FLOORS:
            next_x_coords = PODIUM_X_COORDS if floor + 1 < PODIUM_FLOORS else TOWER_X_COORDS

            # =====================================================
            # FRONT/BACK FACES - DAMA (Checkerboard) PATTERN
            # Bay'ler ve katlar arasında zıt fazda bracing
            # 1.2cm core bay'de brace YOK
            # =====================================================
            for y in [y_coords[0], y_coords[-1]]:
                for bay_idx in range(len(x_coords) - 1):
                    x_left = x_coords[bay_idx]
                    x_right = x_coords[bay_idx + 1]
                    bay_width = x_right - x_left

                    # Skip 1.2m narrow core bay (17.4-18.6)
                    if bay_width < 2.0:
                        continue

                    # Check if both columns continue to next floor
                    if x_left not in next_x_coords or x_right not in next_x_coords:
                        continue

                    # DAMA pattern: alternating based on bay_idx + floor
                    # Even sum = diagonal going right-up
                    # Odd sum = diagonal going left-up
                    dama_phase = (bay_idx + floor) % 2

                    n_bot_left = get_node(tower_num, floor, x_left, y)
                    n_bot_right = get_node(tower_num, floor, x_right, y)
                    n_top_left = get_node(tower_num, floor + 1, x_left, y)
                    n_top_right = get_node(tower_num, floor + 1, x_right, y)

                    if dama_phase == 0:
                        # Diagonal: bottom-left to top-right
                        add_element(n_bot_left, n_top_right, 'brace_dama', tower_str, 'pin')
                    else:
                        # Diagonal: bottom-right to top-left
                        add_element(n_bot_right, n_top_left, 'brace_dama', tower_str, 'pin')

            # Side faces - X bracing (edge X, ALL Y bays except core)
            for x in [x_coords[0], x_coords[-1]]:
                if x in next_x_coords:
                    # All Y bays except narrow core (1.2m)
                    for j in range(len(y_coords) - 1):
                        bay_width = y_coords[j+1] - y_coords[j]
                        if bay_width < 2.0:  # Skip 1.2m core bay
                            continue
                        n1 = get_node(tower_num, floor, x, y_coords[j])
                        n2 = get_node(tower_num, floor + 1, x, y_coords[j+1])
                        n3 = get_node(tower_num, floor, x, y_coords[j+1])
                        n4 = get_node(tower_num, floor + 1, x, y_coords[j])
                        add_element(n1, n2, 'brace_x', tower_str, 'pin')
                        add_element(n3, n4, 'brace_x', tower_str, 'pin')

            # Core walls (X-direction: 17.4-18.6)
            if 17.4 in x_coords and 18.6 in x_coords:
                for y in [y_coords[0], y_coords[-1]]:
                    n1 = get_node(tower_num, floor, 17.4, y)
                    n2 = get_node(tower_num, floor + 1, 18.6, y)
                    add_element(n1, n2, 'core_wall', tower_str)
                    n1 = get_node(tower_num, floor, 18.6, y)
                    n2 = get_node(tower_num, floor + 1, 17.4, y)
                    add_element(n1, n2, 'core_wall', tower_str)

            # Core walls (Y-direction: middle Y bay)
            y_mid_idx = len(y_coords) // 2 - 1
            if y_mid_idx >= 0 and y_mid_idx < len(y_coords) - 1:
                for x in [x_coords[0], x_coords[-1]]:
                    if x in next_x_coords:
                        n1 = get_node(tower_num, floor, x, y_coords[y_mid_idx])
                        n2 = get_node(tower_num, floor + 1, x, y_coords[y_mid_idx + 1])
                        add_element(n1, n2, 'core_wall', tower_str)
                        n1 = get_node(tower_num, floor, x, y_coords[y_mid_idx + 1])
                        n2 = get_node(tower_num, floor + 1, x, y_coords[y_mid_idx])
                        add_element(n1, n2, 'core_wall', tower_str)

# Transfer bracing at podium top (X=0→7 and X=36→29)
for tower_num, y_coords in [(1, Y_BAYS_T1), (2, Y_BAYS_T2)]:
    tower_str = f'tower{tower_num}'
    for x_pod, x_tow in [(0.0, 7.0), (36.0, 29.0)]:
        for y in y_coords:
            n_pod = get_node(tower_num, PODIUM_FLOORS - 1, x_pod, y)
            n_tow = get_node(tower_num, PODIUM_FLOORS, x_tow, y)
            if n_pod and n_tow:
                add_element(n_pod, n_tow, 'brace_transfer', tower_str, 'pin')

print(f"Tower elements: {len(elements)}")

# ============================================
# BRIDGES
# ============================================
BRIDGE_X_LEFT = 14.0
BRIDGE_X_RIGHT = 22.0
BRIDGE_FLOORS_SINGLE = [(5, 6), (11, 12), (17, 18)]
BRIDGE_FLOORS_DOUBLE = (23, 25)

Y_T1_BACK = Y_BAYS_T1[-1]
Y_T2_FRONT = Y_BAYS_T2[0]
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

# Create bridge nodes
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
    if n1 is None or n2 is None:
        return
    bridge_elements.append({
        'element_id': elem_id, 'node_i': n1, 'node_j': n2,
        'element_type': etype, 'tower': 'bridge', 'connection': conn
    })
    elem_id += 1

def create_bridge(floor_bot, floor_top, is_rigid_top=False):
    """
    Create bridge structure.
    is_rigid_top: If True, adds extra bracing for maximum rigidity (top bridge with 3mm balsa cover)
    """
    # Tower nodes
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

    nodes_check = [t1_bot_l, t1_bot_r, t1_top_l, t1_top_r,
                   t2_bot_l, t2_bot_r, t2_top_l, t2_top_r,
                   mid_bot_l, mid_bot_r, mid_top_l, mid_top_r]
    if any(n is None for n in nodes_check):
        print(f"  WARNING: Bridge F{floor_bot}-F{floor_top} missing nodes")
        return

    bridge_type = 'bridge_rigid' if is_rigid_top else 'bridge'

    # Bottom beams
    add_bridge_elem(t1_bot_l, t1_bot_r, 'bridge_beam')
    add_bridge_elem(t1_bot_l, mid_bot_l, 'bridge_beam')
    add_bridge_elem(t1_bot_r, mid_bot_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, mid_bot_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, t2_bot_l, 'bridge_beam')
    add_bridge_elem(mid_bot_r, t2_bot_r, 'bridge_beam')
    add_bridge_elem(t2_bot_l, t2_bot_r, 'bridge_beam')

    # Top beams
    add_bridge_elem(t1_top_l, t1_top_r, 'bridge_beam')
    add_bridge_elem(t1_top_l, mid_top_l, 'bridge_beam')
    add_bridge_elem(t1_top_r, mid_top_r, 'bridge_beam')
    add_bridge_elem(mid_top_l, mid_top_r, 'bridge_beam')
    add_bridge_elem(mid_top_l, t2_top_l, 'bridge_beam')
    add_bridge_elem(mid_top_r, t2_top_r, 'bridge_beam')
    add_bridge_elem(t2_top_l, t2_top_r, 'bridge_beam')

    # Columns
    add_bridge_elem(mid_bot_l, mid_top_l, 'bridge_column')
    add_bridge_elem(mid_bot_r, mid_top_r, 'bridge_column')

    # Coupled shear wall (YZ)
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_l, t1_top_l, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_shear_yz')
    add_bridge_elem(t2_bot_l, mid_top_l, 'bridge_shear_yz')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_r, t1_top_r, 'bridge_shear_yz')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_shear_yz')
    add_bridge_elem(t2_bot_r, mid_top_r, 'bridge_shear_yz')

    # Truss
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_truss')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_truss')

    # =========================================================
    # EXTRA RIGID BRACING FOR TOP BRIDGE (3mm balsa sheet cover)
    # =========================================================
    if is_rigid_top:
        print(f"  Adding RIGID bracing to top bridge F{floor_bot}-F{floor_top}...")

        # BOTTOM PLANE - Full X-bracing (for 3mm balsa sheet)
        # T1 section
        add_bridge_elem(t1_bot_l, mid_bot_r, 'bridge_rigid_bot')
        add_bridge_elem(t1_bot_r, mid_bot_l, 'bridge_rigid_bot')
        # Mid section
        add_bridge_elem(mid_bot_l, t2_bot_r, 'bridge_rigid_bot')
        add_bridge_elem(mid_bot_r, t2_bot_l, 'bridge_rigid_bot')
        # Full diagonal
        add_bridge_elem(t1_bot_l, t2_bot_r, 'bridge_rigid_bot')
        add_bridge_elem(t1_bot_r, t2_bot_l, 'bridge_rigid_bot')

        # TOP PLANE - Full X-bracing (for 3mm balsa sheet)
        # T1 section
        add_bridge_elem(t1_top_l, mid_top_r, 'bridge_rigid_top')
        add_bridge_elem(t1_top_r, mid_top_l, 'bridge_rigid_top')
        # Mid section
        add_bridge_elem(mid_top_l, t2_top_r, 'bridge_rigid_top')
        add_bridge_elem(mid_top_r, t2_top_l, 'bridge_rigid_top')
        # Full diagonal
        add_bridge_elem(t1_top_l, t2_top_r, 'bridge_rigid_top')
        add_bridge_elem(t1_top_r, t2_top_l, 'bridge_rigid_top')

        # SIDE FACES (XZ) - Extra X-bracing
        # Left side (X = BRIDGE_X_LEFT)
        add_bridge_elem(t1_bot_l, t2_top_l, 'bridge_rigid_xz')
        add_bridge_elem(t2_bot_l, t1_top_l, 'bridge_rigid_xz')
        # Right side (X = BRIDGE_X_RIGHT)
        add_bridge_elem(t1_bot_r, t2_top_r, 'bridge_rigid_xz')
        add_bridge_elem(t2_bot_r, t1_top_r, 'bridge_rigid_xz')

        # FRONT/BACK FACES (YZ at tower faces) - Extra X-bracing
        # T1 face
        add_bridge_elem(t1_bot_l, t1_top_r, 'bridge_rigid_yz')
        add_bridge_elem(t1_bot_r, t1_top_l, 'bridge_rigid_yz')
        # T2 face
        add_bridge_elem(t2_bot_l, t2_top_r, 'bridge_rigid_yz')
        add_bridge_elem(t2_bot_r, t2_top_l, 'bridge_rigid_yz')

        # 3D SPACE DIAGONALS (corner to corner)
        add_bridge_elem(t1_bot_l, t2_top_r, 'bridge_rigid_3d')
        add_bridge_elem(t1_bot_r, t2_top_l, 'bridge_rigid_3d')
        add_bridge_elem(t2_bot_l, t1_top_r, 'bridge_rigid_3d')
        add_bridge_elem(t2_bot_r, t1_top_l, 'bridge_rigid_3d')

print("\nCreating bridges...")
for fb, ft in BRIDGE_FLOORS_SINGLE:
    create_bridge(fb, ft, is_rigid_top=False)
# TOP BRIDGE (F23-F25) - Extra rigid for 3mm balsa sheet cover
create_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1], is_rigid_top=True)

print(f"Bridge elements: {len(bridge_elements)}")
print(f"Bridge nodes: {len(bridge_nodes)}")

# ============================================
# COMBINE DATA
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

for elem in all_elements:
    n1, n2 = elem['node_i'], elem['node_j']
    c1, c2 = coords[n1], coords[n2]
    elem['length'] = round(np.sqrt(np.sum((c2 - c1) ** 2)), 4)

connectivity_df = pd.DataFrame(all_elements)

print(f"\nTotal nodes: {n_total}")
print(f"Total elements: {len(connectivity_df)}")
print("\nElements by type:")
print(connectivity_df['element_type'].value_counts().to_string())

# Weight analysis
total_length_mm = connectivity_df['length'].sum() * 10
WEIGHT_LIMIT = 1.40
weight = total_length_mm * 36 * 160 / 1e9

print(f"\nTotal length: {total_length_mm:,.0f} mm")
print(f"Weight (ρ=160): {weight:.3f} kg")
print(f"Limit: {WEIGHT_LIMIT} kg")
print(f"Margin: {(WEIGHT_LIMIT - weight)*1000:.0f}g")
print(f"Status: {'✓ OK' if weight <= WEIGHT_LIMIT else '✗ OVER'}")

# Save data
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

position_df.to_csv(DATA_DIR / 'twin_position_matrix.csv', index=False)
connectivity_df.to_csv(DATA_DIR / 'twin_connectivity_matrix.csv', index=False)

adj = np.zeros((n_total, n_total), dtype=int)
for _, row in connectivity_df.iterrows():
    i, j = int(row['node_i']), int(row['node_j'])
    adj[i, j] = adj[j, i] = 1
np.savetxt(DATA_DIR / 'twin_adjacency_matrix.csv', adj, delimiter=',', fmt='%d')

np.savez(DATA_DIR / 'twin_building_data.npz',
         adjacency_matrix=adj, coords=coords,
         podium_x=PODIUM_X_COORDS, tower_x=TOWER_X_COORDS,
         y_coords_t1=Y_BAYS_T1, y_coords_t2=Y_BAYS_T2, z_coords=Z_COORDS,
         tower_gap=TOWER_GAP,
         bridge_floors_single=np.array(BRIDGE_FLOORS_SINGLE),
         bridge_floors_double=np.array(BRIDGE_FLOORS_DOUBLE))

print(f"\nData saved to {DATA_DIR}")

# Create DXF
print("\nCreating DXF...")
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

doc = ezdxf.new('R2010')
msp = doc.modelspace()

LAYER_COLORS = {
    'column': 7, 'beam_x': 3, 'beam_y': 4,
    'brace_dama': 1, 'brace_x': 1, 'brace_transfer': 6,
    'core_wall': 5,
    'bridge_beam': 2, 'bridge_column': 2,
    'bridge_shear_yz': 1, 'bridge_truss': 6,
    # Rigid top bridge elements
    'bridge_rigid_bot': 5, 'bridge_rigid_top': 5,
    'bridge_rigid_xz': 6, 'bridge_rigid_yz': 6,
    'bridge_rigid_3d': 1
}

for etype in connectivity_df['element_type'].unique():
    color = LAYER_COLORS.get(etype, 7)
    doc.layers.new(name=etype, dxfattribs={'color': color})

for _, elem in connectivity_df.iterrows():
    n1, n2 = int(elem['node_i']), int(elem['node_j'])
    p1 = tuple(coords[n1])
    p2 = tuple(coords[n2])
    msp.add_line(p1, p2, dxfattribs={'layer': elem['element_type']})

dxf_path = EXPORTS_DIR / 'twin_towers_v3.dxf'
doc.saveas(dxf_path)

print(f"\n{'='*70}")
print(f"DXF SAVED: {dxf_path}")
print(f"{'='*70}")
