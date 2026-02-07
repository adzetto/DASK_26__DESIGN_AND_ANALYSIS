"""
Regenerate Twin Towers model with improved bracing pattern.
- Podium: DENSE bracing at every column space
- Tower: Proper DAMA (checkerboard) pattern
- Export to CSV and DXF
"""

import numpy as np
import pandas as pd
import ezdxf
import os
from pathlib import Path

print("=" * 70)
print("REGENERATE TWIN TOWERS MODEL - Improved Bracing")
print("=" * 70)

# ============================================
# GEOMETRY PARAMETERS
# ============================================
BAY_WIDTH = 8.0  # 8m = 80mm in maket

PODIUM_BAYS_X = 5
PODIUM_BAYS_Y = 2
PODIUM_FLOORS = 13

TOWER_BAYS_X = 3  # 3 bays: 7.2 - 1.6 - 7.2
TOWER_BAYS_Y = 2
TOTAL_FLOORS = 26

GROUND_FLOOR_HEIGHT = 9.0
TYPICAL_FLOOR_HEIGHT = 6.0
TOWER_GAP = 8.0

TOWER1_ORIGIN_Y = 0.0
TOWER2_ORIGIN_Y = PODIUM_BAYS_Y * BAY_WIDTH + TOWER_GAP

PODIUM_X_COORDS = np.arange(PODIUM_BAYS_X + 1) * BAY_WIDTH

# Tower column layout: 7.2cm - 1.6cm - 7.2cm = 16cm total
# Centered on podium center (20m): 12 to 28
TOWER_X_COORDS = np.array([12.0, 19.2, 20.8, 28.0])
Y_COORDS_T1 = np.arange(PODIUM_BAYS_Y + 1) * BAY_WIDTH + TOWER1_ORIGIN_Y
Y_COORDS_T2 = np.arange(PODIUM_BAYS_Y + 1) * BAY_WIDTH + TOWER2_ORIGIN_Y

Z_COORDS = np.zeros(TOTAL_FLOORS)
Z_COORDS[0] = 0.0
Z_COORDS[1] = GROUND_FLOOR_HEIGHT
Z_COORDS[2:] = GROUND_FLOOR_HEIGHT + np.arange(1, TOTAL_FLOORS - 1) * TYPICAL_FLOOR_HEIGHT

print(f"Tower 1 Y: {Y_COORDS_T1[0]:.0f} to {Y_COORDS_T1[-1]:.0f}m")
print(f"Tower 2 Y: {Y_COORDS_T2[0]:.0f} to {Y_COORDS_T2[-1]:.0f}m")
print(f"Height: {Z_COORDS[-1]:.0f}m ({TOTAL_FLOORS} floors)")

# ============================================
# NODE GENERATION
# ============================================
def generate_tower_nodes(tower_id, y_coords, x_podium, x_tower, z_coords,
                         podium_floors, total_floors, start_node_id=0):
    nodes = []
    node_lookup = {}
    node_id = start_node_id

    for f in range(podium_floors):
        for x in x_podium:
            for y in y_coords:
                nodes.append({
                    'node_id': node_id, 'x': x, 'y': y, 'z': z_coords[f],
                    'floor': f, 'zone': 'podium', 'tower': tower_id
                })
                node_lookup[(tower_id, f, x, y)] = node_id
                node_id += 1

    for f in range(podium_floors, total_floors):
        for x in x_tower:
            for y in y_coords:
                nodes.append({
                    'node_id': node_id, 'x': x, 'y': y, 'z': z_coords[f],
                    'floor': f, 'zone': 'tower', 'tower': tower_id
                })
                node_lookup[(tower_id, f, x, y)] = node_id
                node_id += 1

    return nodes, node_lookup, node_id

nodes_t1, lookup_t1, next_id = generate_tower_nodes(1, Y_COORDS_T1, PODIUM_X_COORDS, TOWER_X_COORDS, Z_COORDS, PODIUM_FLOORS, TOTAL_FLOORS, 0)
nodes_t2, lookup_t2, next_id = generate_tower_nodes(2, Y_COORDS_T2, PODIUM_X_COORDS, TOWER_X_COORDS, Z_COORDS, PODIUM_FLOORS, TOTAL_FLOORS, next_id)

all_nodes = nodes_t1 + nodes_t2
position_df = pd.DataFrame(all_nodes)
node_lookup = {**lookup_t1, **lookup_t2}

n_nodes = len(position_df)
coords = position_df[['x', 'y', 'z']].values
print(f"Nodes: {n_nodes}")

# ============================================
# ELEMENT GENERATION - IMPROVED BRACING
# ============================================
def generate_tower_elements(tower_id, y_coords, x_podium, x_tower, z_coords,
                            podium_floors, total_floors, node_lookup, start_elem_id=0):
    elements = []
    elem_id = start_elem_id

    def add_element(n1, n2, etype):
        nonlocal elem_id
        if n1 is not None and n2 is not None:
            elements.append({
                'element_id': elem_id, 'node_i': n1, 'node_j': n2,
                'element_type': etype, 'tower': tower_id
            })
            elem_id += 1
            return True
        return False

    def get_node(f, x, y):
        return node_lookup.get((tower_id, f, x, y))

    # BEAMS X
    for f in range(podium_floors):
        for y in y_coords:
            for i in range(len(x_podium) - 1):
                add_element(get_node(f, x_podium[i], y), get_node(f, x_podium[i+1], y), 'beam_x')

    for f in range(podium_floors, total_floors):
        for y in y_coords:
            for i in range(len(x_tower) - 1):
                add_element(get_node(f, x_tower[i], y), get_node(f, x_tower[i+1], y), 'beam_x')

    # BEAMS Y
    for f in range(podium_floors):
        for x in x_podium:
            for i in range(len(y_coords) - 1):
                add_element(get_node(f, x, y_coords[i]), get_node(f, x, y_coords[i+1]), 'beam_y')

    for f in range(podium_floors, total_floors):
        for x in x_tower:
            for i in range(len(y_coords) - 1):
                add_element(get_node(f, x, y_coords[i]), get_node(f, x, y_coords[i+1]), 'beam_y')

    # COLUMNS
    for f in range(podium_floors - 1):
        for x in x_podium:
            for y in y_coords:
                add_element(get_node(f, x, y), get_node(f+1, x, y), 'column')

    for x in x_tower:
        for y in y_coords:
            add_element(get_node(podium_floors-1, x, y), get_node(podium_floors, x, y), 'column')

    for f in range(podium_floors, total_floors - 1):
        for x in x_tower:
            for y in y_coords:
                add_element(get_node(f, x, y), get_node(f+1, x, y), 'column')

    # ============================================
    # GROUND FLOOR BRACING - DENSE (B2 Prevention)
    # Ground floor is 9m (vs 6m typical) - needs extra stiffness
    # ============================================
    # F0 to F1: FULL DENSE bracing on ALL bays, ALL faces
    for y in y_coords:
        for i in range(len(x_podium) - 1):
            x1, x2 = x_podium[i], x_podium[i+1]
            n_bl = get_node(0, x1, y)
            n_br = get_node(0, x2, y)
            n_tl = get_node(1, x1, y)
            n_tr = get_node(1, x2, y)
            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                add_element(n_bl, n_tr, 'brace_xz')
                add_element(n_br, n_tl, 'brace_xz')

    # Ground floor YZ braces (side faces) - DENSE
    for x in x_podium:
        for j in range(len(y_coords) - 1):
            y1, y2 = y_coords[j], y_coords[j+1]
            n_bl = get_node(0, x, y1)
            n_br = get_node(0, x, y2)
            n_tl = get_node(1, x, y1)
            n_tr = get_node(1, x, y2)
            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                add_element(n_bl, n_tr, 'brace_yz')
                add_element(n_br, n_tl, 'brace_yz')

    # ============================================
    # PODIUM BRACES XZ - DAMA PATTERN (F2 and above)
    # ============================================
    for f in range(2, podium_floors - 1, 2):
        f_top = f + 2
        if f_top >= podium_floors:
            f_top = podium_floors - 1
            if f_top <= f:
                continue

        floor_group = f // 2

        for y_idx, y in enumerate(y_coords):
            for i in range(len(x_podium) - 1):
                # DAMA pattern: checkerboard
                if (floor_group + i + y_idx) % 2 != 0:
                    continue

                x1, x2 = x_podium[i], x_podium[i+1]

                n_bl = get_node(f, x1, y)
                n_br = get_node(f, x2, y)
                n_tl = get_node(f_top, x1, y)
                n_tr = get_node(f_top, x2, y)

                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    add_element(n_bl, n_tr, 'brace_xz')
                    add_element(n_br, n_tl, 'brace_xz')

    # ============================================
    # TOWER BRACES XZ - DENSE for stiffness
    # ============================================
    for f in range(podium_floors - 1, total_floors - 1, 2):
        f_top = f + 2
        if f_top >= total_floors:
            break

        floor_group = (f - podium_floors + 1) // 2

        for y_idx, y in enumerate(y_coords):
            # Outer bays (0 and 2) - ALWAYS brace for stiffness
            for i in [0, 2]:
                if i >= len(x_tower) - 1:
                    continue

                x1, x2 = x_tower[i], x_tower[i+1]

                n_bl = get_node(f, x1, y)
                n_br = get_node(f, x2, y)
                n_tl = get_node(f_top, x1, y)
                n_tr = get_node(f_top, x2, y)

                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    add_element(n_bl, n_tr, 'brace_xz')
                    add_element(n_br, n_tl, 'brace_xz')

    # ============================================
    # PODIUM BRACES YZ - Every 2 floors at ends (symmetry)
    # Note: Ground floor YZ already added above
    # ============================================
    for f in range(2, podium_floors - 1, 2):
        f_top = f + 2
        if f_top >= podium_floors:
            f_top = podium_floors - 1
            if f_top <= f:
                continue

        # Both ends for symmetry (A1 prevention)
        for x in [x_podium[0], x_podium[-1]]:
            for j in range(len(y_coords) - 1):
                y1, y2 = y_coords[j], y_coords[j+1]

                n_bl = get_node(f, x, y1)
                n_br = get_node(f, x, y2)
                n_tl = get_node(f_top, x, y1)
                n_tr = get_node(f_top, x, y2)

                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    add_element(n_bl, n_tr, 'brace_yz')
                    add_element(n_br, n_tl, 'brace_yz')

    # ============================================
    # TOWER BRACES YZ - At key levels for symmetry
    # ============================================
    YZ_TOWER_FLOORS = [12, 16, 20, 24]  # Every 4 floors
    for f in YZ_TOWER_FLOORS:
        if f >= total_floors - 2:
            continue
        f_top = f + 2
        if f_top >= total_floors:
            break

        # Both tower ends for symmetry (A1 prevention)
        for x in [x_tower[0], x_tower[-1]]:
            for j in range(len(y_coords) - 1):
                y1, y2 = y_coords[j], y_coords[j+1]

                n_bl = get_node(f, x, y1)
                n_br = get_node(f, x, y2)
                n_tl = get_node(f_top, x, y1)
                n_tr = get_node(f_top, x, y2)

                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    add_element(n_bl, n_tr, 'brace_yz')
                    add_element(n_br, n_tl, 'brace_yz')

    # ============================================
    # CORE WALLS - At key structural levels
    # Balance between stiffness and weight
    # ============================================
    core_x_left = 19.2   # Inner left column
    core_x_right = 20.8  # Inner right column
    core_y_front = y_coords[0]
    core_y_back = y_coords[-1]
    core_y_mid = y_coords[1] if len(y_coords) > 2 else (y_coords[0] + y_coords[-1]) / 2

    # Tower core walls at key levels (every 3 floors for weight savings)
    TOWER_CORE_FLOORS = [12, 15, 18, 21, 24]
    for f in TOWER_CORE_FLOORS:
        if f >= total_floors - 1:
            continue
        f_top = f + 1

        for core_x in [core_x_left, core_x_right]:
            for y1, y2 in [(core_y_front, core_y_mid), (core_y_mid, core_y_back)]:
                n_bl = get_node(f, core_x, y1)
                n_br = get_node(f, core_x, y2)
                n_tl = get_node(f_top, core_x, y1)
                n_tr = get_node(f_top, core_x, y2)
                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    add_element(n_bl, n_tr, 'core_wall')
                    add_element(n_br, n_tl, 'core_wall')

    # Podium core walls at X=16, 24 - only at key levels
    PODIUM_CORE_FLOORS = [0, 3, 6, 9, 12]
    for f in PODIUM_CORE_FLOORS:
        if f >= podium_floors - 1:
            continue
        f_top = f + 1
        for core_x in [16.0, 24.0]:
            for y1, y2 in [(core_y_front, core_y_mid), (core_y_mid, core_y_back)]:
                n_bl = get_node(f, core_x, y1)
                n_br = get_node(f, core_x, y2)
                n_tl = get_node(f_top, core_x, y1)
                n_tr = get_node(f_top, core_x, y2)
                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    add_element(n_bl, n_tr, 'core_wall')
                    add_element(n_br, n_tl, 'core_wall')

    # ============================================
    # SHEAR WALL PANELS (3mm balsa) - MINIMAL SYMMETRIC PLACEMENT
    # Weight-optimized to fit within 17g margin
    # ============================================
    # CRITICAL: All walls must be symmetric about X=20 (structure center)
    # and symmetric front-to-back to avoid torsion (A1)
    #
    # Weight budget: 17g available
    # XZ panel (7.2×6×0.3cm): ~2.07g each
    # YZ panel (8×6×0.3cm): ~2.30g each
    # Target: 8 panels max (2 per tower face = symmetric)

    # ROOF LEVEL XZ PANELS ONLY (F24)
    # This is where the 2.22kg mass is concentrated
    # 4 panels total (2 per tower × front/back = symmetric)
    TOWER_TOP_FLOOR = 24
    if TOWER_TOP_FLOOR < total_floors - 1:
        f = TOWER_TOP_FLOOR
        f_top = f + 1

        # Use LEFT outer bay only (X=12 to 19.2) - symmetric about structure
        # But BOTH front and back for A1 (torsion) prevention
        x1, x2 = x_tower[0], x_tower[1]  # 12.0 to 19.2

        for y in [y_coords[0], y_coords[-1]]:  # Front and back
            n_bl = get_node(f, x1, y)
            n_br = get_node(f, x2, y)
            n_tl = get_node(f_top, x1, y)
            n_tr = get_node(f_top, x2, y)
            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                add_element(n_bl, n_tr, 'shear_wall_xz')
                add_element(n_br, n_tl, 'shear_wall_xz')

        # Also add RIGHT outer bay (X=20.8 to 28) - symmetric about X=20
        x1, x2 = x_tower[2], x_tower[3]  # 20.8 to 28.0

        for y in [y_coords[0], y_coords[-1]]:  # Front and back
            n_bl = get_node(f, x1, y)
            n_br = get_node(f, x2, y)
            n_tl = get_node(f_top, x1, y)
            n_tr = get_node(f_top, x2, y)
            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                add_element(n_bl, n_tr, 'shear_wall_xz')
                add_element(n_br, n_tl, 'shear_wall_xz')

    # Total XZ panels: 8 per tower × 2 towers = 16 panels
    # But we need fewer! Remove one tower or use single bay
    # Actually: 2 bays × 2 faces × 2 towers = 8 panels = 16.6g
    # This just fits! (17g budget)

    # ============================================
    # FLOOR BRACES
    # ============================================
    DIAPHRAGM_FLOORS = [0, 6, 12, 18, 24]

    for f in DIAPHRAGM_FLOORS:
        if f >= total_floors:
            continue

        if f < podium_floors:
            for i in range(len(x_podium) - 1):
                for j in range(len(y_coords) - 1):
                    if (i + j) % 2 != 0:
                        continue
                    x1, x2 = x_podium[i], x_podium[i+1]
                    y1, y2 = y_coords[j], y_coords[j+1]
                    n_bl, n_br = get_node(f, x1, y1), get_node(f, x2, y1)
                    n_tl, n_tr = get_node(f, x1, y2), get_node(f, x2, y2)
                    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                        add_element(n_bl, n_tr, 'brace_floor')
                        add_element(n_br, n_tl, 'brace_floor')
        else:
            for i in range(len(x_tower) - 1):
                for j in range(len(y_coords) - 1):
                    if (i + j) % 2 != 0:
                        continue
                    x1, x2 = x_tower[i], x_tower[i+1]
                    y1, y2 = y_coords[j], y_coords[j+1]
                    n_bl, n_br = get_node(f, x1, y1), get_node(f, x2, y1)
                    n_tl, n_tr = get_node(f, x1, y2), get_node(f, x2, y2)
                    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                        add_element(n_bl, n_tr, 'brace_floor')
                        add_element(n_br, n_tl, 'brace_floor')

    # SPACE BRACES - podium to tower transition
    f_pod_top = podium_floors - 1
    f_tow_bot = podium_floors
    # Tower X: [12.0, 19.2, 20.8, 28.0]
    for x_pod, x_tow in [(0.0, 12.0), (40.0, 28.0)]:
        for y in y_coords:
            n_pod = get_node(f_pod_top, x_pod, y)
            for y_tow in y_coords:
                n_tow = get_node(f_tow_bot, x_tow, y_tow)
                add_element(n_pod, n_tow, 'brace_space')

    return elements, elem_id

# Generate tower elements
elements_t1, next_elem_id = generate_tower_elements(1, Y_COORDS_T1, PODIUM_X_COORDS, TOWER_X_COORDS, Z_COORDS, PODIUM_FLOORS, TOTAL_FLOORS, node_lookup, 0)
elements_t2, next_elem_id = generate_tower_elements(2, Y_COORDS_T2, PODIUM_X_COORDS, TOWER_X_COORDS, Z_COORDS, PODIUM_FLOORS, TOTAL_FLOORS, node_lookup, next_elem_id)

print(f"Tower 1: {len(elements_t1)} elements")
print(f"Tower 2: {len(elements_t2)} elements")

# ============================================
# BRIDGE GENERATION - COUPLED SHEAR WALL
# ============================================
# Bridge dimensions: 8m x 8m x floor_height
BRIDGE_FLOORS_SINGLE = [(5, 6), (11, 12), (17, 18)]
BRIDGE_FLOORS_DOUBLE = (23, 25)

# Bridge X coordinates: ALWAYS 8m width (16 to 24)
BRIDGE_X_LEFT = 16.0
BRIDGE_X_RIGHT = 24.0

Y_T1_BACK = Y_COORDS_T1[-1]   # 16.0
Y_T2_FRONT = Y_COORDS_T2[0]   # 24.0
Y_BRIDGE_MID = (Y_T1_BACK + Y_T2_FRONT) / 2  # 20.0

bridge_elements = []
bridge_nodes = []
bridge_node_lookup = {}
bridge_node_id = n_nodes
elem_id = next_elem_id

# For tower floors, we need to add bridge connection nodes at X=16, X=24
# These are not at column locations but on the tower face
tower_bridge_floors = set()
for fb, ft in BRIDGE_FLOORS_SINGLE:
    if fb >= PODIUM_FLOORS:
        tower_bridge_floors.add(fb)
    if ft >= PODIUM_FLOORS:
        tower_bridge_floors.add(ft)
for f in BRIDGE_FLOORS_DOUBLE:
    if f >= PODIUM_FLOORS:
        tower_bridge_floors.add(f)

# Add tower face nodes for bridge connections
tower_bridge_nodes = []
for f in tower_bridge_floors:
    z = Z_COORDS[f]
    # Tower 1 back face (Y = Y_T1_BACK = 16)
    for x in [BRIDGE_X_LEFT, BRIDGE_X_RIGHT]:
        tower_bridge_nodes.append({
            'node_id': bridge_node_id, 'x': x, 'y': Y_T1_BACK, 'z': z,
            'floor': f, 'zone': 'tower_bridge_face', 'tower': 1
        })
        node_lookup[(1, f, x, Y_T1_BACK)] = bridge_node_id
        bridge_node_id += 1
    # Tower 2 front face (Y = Y_T2_FRONT = 24)
    for x in [BRIDGE_X_LEFT, BRIDGE_X_RIGHT]:
        tower_bridge_nodes.append({
            'node_id': bridge_node_id, 'x': x, 'y': Y_T2_FRONT, 'z': z,
            'floor': f, 'zone': 'tower_bridge_face', 'tower': 2
        })
        node_lookup[(2, f, x, Y_T2_FRONT)] = bridge_node_id
        bridge_node_id += 1

print(f"Tower bridge face nodes added: {len(tower_bridge_nodes)}")

def add_bridge_node(floor_idx, x, y):
    global bridge_node_id
    z = Z_COORDS[floor_idx]
    key = ('bridge', floor_idx, x, y)
    if key not in bridge_node_lookup:
        bridge_nodes.append({
            'node_id': bridge_node_id, 'x': x, 'y': y, 'z': z,
            'floor': floor_idx, 'zone': 'bridge', 'tower': 'bridge'
        })
        bridge_node_lookup[key] = bridge_node_id
        bridge_node_id += 1
    return bridge_node_lookup[key]

def get_bridge_node(floor_idx, x, y):
    return bridge_node_lookup.get(('bridge', floor_idx, x, y))

def get_t1_node(f, x, y):
    return node_lookup.get((1, f, x, y))

def get_t2_node(f, x, y):
    return node_lookup.get((2, f, x, y))

# Create bridge mid-span nodes (in the gap between towers)
# All bridges use X = 16 and 24 (8m width)
for floor_bot, floor_top in BRIDGE_FLOORS_SINGLE:
    for f in [floor_bot, floor_top]:
        add_bridge_node(f, BRIDGE_X_LEFT, Y_BRIDGE_MID)
        add_bridge_node(f, BRIDGE_X_RIGHT, Y_BRIDGE_MID)

for f in BRIDGE_FLOORS_DOUBLE:
    add_bridge_node(f, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    add_bridge_node(f, BRIDGE_X_RIGHT, Y_BRIDGE_MID)

def create_box_bridge(floor_bot, floor_top, start_id):
    """
    Create box bridge with dimensions:
    - Width (X): 8m (BRIDGE_X_LEFT=16 to BRIDGE_X_RIGHT=24)
    - Length (Y): 8m (tower gap)
    - Height (Z): floor_top - floor_bot
    """
    elements = []
    current_id = start_id

    # All bridges use same X coordinates (8m width)
    nodes = {}
    # Bottom floor nodes
    nodes['bot_t1_left'] = get_t1_node(floor_bot, BRIDGE_X_LEFT, Y_T1_BACK)
    nodes['bot_t1_right'] = get_t1_node(floor_bot, BRIDGE_X_RIGHT, Y_T1_BACK)
    nodes['bot_t2_left'] = get_t2_node(floor_bot, BRIDGE_X_LEFT, Y_T2_FRONT)
    nodes['bot_t2_right'] = get_t2_node(floor_bot, BRIDGE_X_RIGHT, Y_T2_FRONT)
    nodes['bot_mid_left'] = get_bridge_node(floor_bot, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    nodes['bot_mid_right'] = get_bridge_node(floor_bot, BRIDGE_X_RIGHT, Y_BRIDGE_MID)

    # Top floor nodes
    nodes['top_t1_left'] = get_t1_node(floor_top, BRIDGE_X_LEFT, Y_T1_BACK)
    nodes['top_t1_right'] = get_t1_node(floor_top, BRIDGE_X_RIGHT, Y_T1_BACK)
    nodes['top_t2_left'] = get_t2_node(floor_top, BRIDGE_X_LEFT, Y_T2_FRONT)
    nodes['top_t2_right'] = get_t2_node(floor_top, BRIDGE_X_RIGHT, Y_T2_FRONT)
    nodes['top_mid_left'] = get_bridge_node(floor_top, BRIDGE_X_LEFT, Y_BRIDGE_MID)
    nodes['top_mid_right'] = get_bridge_node(floor_top, BRIDGE_X_RIGHT, Y_BRIDGE_MID)

    if any(v is None for v in nodes.values()):
        print(f"  WARNING: Bridge F{floor_bot}-F{floor_top} skipped - missing nodes")
        for k, v in nodes.items():
            if v is None:
                print(f"    Missing: {k}")
        return elements, start_id

    def add_bridge_elem(n1, n2, etype, conn='pin'):
        nonlocal current_id
        elements.append({
            'element_id': current_id, 'node_i': nodes[n1], 'node_j': nodes[n2],
            'element_type': etype, 'tower': 'bridge', 'connection': conn
        })
        current_id += 1

    # Bottom beams
    add_bridge_elem('bot_t1_left', 'bot_t1_right', 'bridge_beam')
    add_bridge_elem('bot_t2_left', 'bot_t2_right', 'bridge_beam')
    add_bridge_elem('bot_mid_left', 'bot_mid_right', 'bridge_beam', 'rigid')
    for side in ['left', 'right']:
        add_bridge_elem(f'bot_t1_{side}', f'bot_mid_{side}', 'bridge_beam')
        add_bridge_elem(f'bot_mid_{side}', f'bot_t2_{side}', 'bridge_beam')

    # Top beams
    add_bridge_elem('top_t1_left', 'top_t1_right', 'bridge_beam')
    add_bridge_elem('top_t2_left', 'top_t2_right', 'bridge_beam')
    add_bridge_elem('top_mid_left', 'top_mid_right', 'bridge_beam', 'rigid')
    for side in ['left', 'right']:
        add_bridge_elem(f'top_t1_{side}', f'top_mid_{side}', 'bridge_beam')
        add_bridge_elem(f'top_mid_{side}', f'top_t2_{side}', 'bridge_beam')

    # Columns
    for pos in ['t1_left', 't1_right', 't2_left', 't2_right', 'mid_left', 'mid_right']:
        conn = 'rigid' if 'mid' in pos else 'pin'
        add_bridge_elem(f'bot_{pos}', f'top_{pos}', 'bridge_column', conn)

    # Braces
    add_bridge_elem('bot_t1_left', 'bot_mid_right', 'bridge_brace_bot')
    add_bridge_elem('bot_t1_right', 'bot_mid_left', 'bridge_brace_bot')
    add_bridge_elem('bot_mid_left', 'bot_t2_right', 'bridge_brace_bot')
    add_bridge_elem('bot_mid_right', 'bot_t2_left', 'bridge_brace_bot')

    add_bridge_elem('top_t1_left', 'top_mid_right', 'bridge_brace_top')
    add_bridge_elem('top_t1_right', 'top_mid_left', 'bridge_brace_top')
    add_bridge_elem('top_mid_left', 'top_t2_right', 'bridge_brace_top')
    add_bridge_elem('top_mid_right', 'top_t2_left', 'bridge_brace_top')

    # Side trusses
    for side in ['left', 'right']:
        add_bridge_elem(f'bot_t1_{side}', f'top_mid_{side}', 'bridge_truss_side')
        add_bridge_elem(f'top_t1_{side}', f'bot_mid_{side}', 'bridge_truss_side')
        add_bridge_elem(f'bot_mid_{side}', f'top_t2_{side}', 'bridge_truss_side')
        add_bridge_elem(f'top_mid_{side}', f'bot_t2_{side}', 'bridge_truss_side')

    # Face braces (XZ plane - minor)
    add_bridge_elem('bot_t1_left', 'top_t1_right', 'bridge_brace_face')
    add_bridge_elem('bot_t1_right', 'top_t1_left', 'bridge_brace_face')
    add_bridge_elem('bot_t2_left', 'top_t2_right', 'bridge_brace_face')
    add_bridge_elem('bot_t2_right', 'top_t2_left', 'bridge_brace_face')

    # ============================================
    # COUPLED SHEAR WALL BRACING (YZ plane)
    # These provide Y-direction resistance
    # ============================================
    # Left side YZ braces (X = BRIDGE_X_LEFT)
    add_bridge_elem('bot_t1_left', 'top_mid_left', 'bridge_shear_yz', 'rigid')
    add_bridge_elem('top_t1_left', 'bot_mid_left', 'bridge_shear_yz', 'rigid')
    add_bridge_elem('bot_mid_left', 'top_t2_left', 'bridge_shear_yz', 'rigid')
    add_bridge_elem('top_mid_left', 'bot_t2_left', 'bridge_shear_yz', 'rigid')

    # Right side YZ braces (X = BRIDGE_X_RIGHT)
    add_bridge_elem('bot_t1_right', 'top_mid_right', 'bridge_shear_yz', 'rigid')
    add_bridge_elem('top_t1_right', 'bot_mid_right', 'bridge_shear_yz', 'rigid')
    add_bridge_elem('bot_mid_right', 'top_t2_right', 'bridge_shear_yz', 'rigid')
    add_bridge_elem('top_mid_right', 'bot_t2_right', 'bridge_shear_yz', 'rigid')

    return elements, current_id

# Create bridges
for floor_bot, floor_top in BRIDGE_FLOORS_SINGLE:
    new_elems, elem_id = create_box_bridge(floor_bot, floor_top, elem_id)
    bridge_elements.extend(new_elems)
new_elems, elem_id = create_box_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1], elem_id)
bridge_elements.extend(new_elems)

print(f"Bridge elements: {len(bridge_elements)}")
print(f"Bridge mid-span nodes: {len(bridge_nodes)}")

# ============================================
# COMBINE ALL DATA
# ============================================
# Combine tower bridge face nodes + bridge mid-span nodes
all_bridge_nodes = tower_bridge_nodes + bridge_nodes
print(f"Total bridge-related nodes: {len(all_bridge_nodes)}")

if all_bridge_nodes:
    bridge_nodes_df = pd.DataFrame(all_bridge_nodes)
    position_df = pd.concat([position_df, bridge_nodes_df], ignore_index=True)
    n_total_nodes = n_nodes + len(all_bridge_nodes)

    new_coords = np.zeros((n_total_nodes, 3))
    new_coords[:n_nodes] = coords
    # Add all bridge-related nodes (tower face nodes + mid-span nodes)
    for bn in all_bridge_nodes:
        new_coords[bn['node_id']] = [bn['x'], bn['y'], bn['z']]
    coords = new_coords
else:
    n_total_nodes = n_nodes

all_elements = elements_t1 + elements_t2 + bridge_elements

# Calculate lengths
for elem in all_elements:
    n1, n2 = elem['node_i'], elem['node_j']
    c1, c2 = coords[n1], coords[n2]
    length = np.sqrt(np.sum((c2 - c1) ** 2))
    elem['length'] = round(length, 4)
    if 'connection' not in elem:
        elem['connection'] = 'rigid'

connectivity_df = pd.DataFrame(all_elements)

print(f"\nTotal nodes: {n_total_nodes}")
print(f"Total elements: {len(connectivity_df)}")
print(f"\nElements by type:")
print(connectivity_df['element_type'].value_counts().to_string())

# ============================================
# WEIGHT ANALYSIS
# ============================================
# Different cross-sections:
# - Frame elements (6mm × 6mm): 36 mm² area
# - Shear wall panels (3mm thick): panel area based on geometry

BALSA_AREA_6MM = 36  # mm² for 6mm × 6mm stick
PANEL_THICKNESS = 3  # mm for shear wall panels
WEIGHT_LIMIT = 1.40
DENSITY = 160  # kg/m³

# Separate frame elements from panel elements
frame_types = ['column', 'beam_x', 'beam_y', 'brace_xz', 'brace_yz', 'brace_floor',
               'brace_space', 'core_wall', 'bridge_beam', 'bridge_column',
               'bridge_brace_top', 'bridge_brace_bot', 'bridge_truss_side',
               'bridge_brace_face', 'bridge_shear_yz']
panel_types = ['shear_wall_xz', 'shear_wall_yz']

# Frame element weight (6mm × 6mm sticks)
frame_df = connectivity_df[connectivity_df['element_type'].isin(frame_types)]
frame_length_mm = frame_df['length'].sum() * 10  # Convert from model units to mm
weight_frame = frame_length_mm * BALSA_AREA_6MM * DENSITY / 1e9  # kg

# Panel element weight (3mm thick panels)
# For panels, the diagonals represent the panel - convert to actual panel area
# Each panel has 2 diagonals; panel area = height × width × thickness
panel_df = connectivity_df[connectivity_df['element_type'].isin(panel_types)]
weight_panels = 0

if len(panel_df) > 0:
    # Group by floor to calculate panel areas
    # Each pair of diagonals = 1 panel
    n_panels_xz = len(panel_df[panel_df['element_type'] == 'shear_wall_xz']) // 2
    n_panels_yz = len(panel_df[panel_df['element_type'] == 'shear_wall_yz']) // 2

    # Estimate panel dimensions from element data
    # XZ panels: span one bay width (7.2cm or 8cm) × one floor height (6cm)
    # YZ panels: span one bay width (8cm) × one floor height (6cm)

    # Calculate typical panel dimensions
    typical_floor_height = 6.0  # cm (model units)
    bay_width_outer = 7.2  # cm for tower outer bay
    bay_width_inner = 8.0  # cm for standard bay

    # XZ panels (outer bays: 7.2cm wide)
    panel_area_xz = typical_floor_height * bay_width_outer * PANEL_THICKNESS / 10  # cm³
    weight_panels_xz = n_panels_xz * panel_area_xz * DENSITY / 1e6  # kg

    # YZ panels (standard bays: 8cm wide)
    panel_area_yz = typical_floor_height * bay_width_inner * PANEL_THICKNESS / 10  # cm³
    weight_panels_yz = n_panels_yz * panel_area_yz * DENSITY / 1e6  # kg

    weight_panels = weight_panels_xz + weight_panels_yz
    print(f"\nShear Wall Panels:")
    print(f"  XZ panels: {n_panels_xz} × ({typical_floor_height}×{bay_width_outer}×{PANEL_THICKNESS/10}) cm³ = {weight_panels_xz*1000:.1f} g")
    print(f"  YZ panels: {n_panels_yz} × ({typical_floor_height}×{bay_width_inner}×{PANEL_THICKNESS/10}) cm³ = {weight_panels_yz*1000:.1f} g")

total_weight = weight_frame + weight_panels

print(f"\nWEIGHT SUMMARY:")
print(f"  Frame elements (6mm×6mm): {weight_frame:.3f} kg ({frame_length_mm:,.0f} mm)")
print(f"  Panel elements (3mm):     {weight_panels:.3f} kg")
print(f"  --------------------------------")
print(f"  TOTAL:                    {total_weight:.3f} kg")
print(f"  Limit:                    {WEIGHT_LIMIT} kg")
print(f"  Margin:                   {(WEIGHT_LIMIT - total_weight)*1000:.0f} g")
print(f"  Status: {'✓ OK' if total_weight <= WEIGHT_LIMIT else '✗ OVER LIMIT!'}")

# ============================================
# SAVE DATA
# ============================================
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

position_df.to_csv(DATA_DIR / 'twin_position_matrix.csv', index=False)
connectivity_df.to_csv(DATA_DIR / 'twin_connectivity_matrix.csv', index=False)

adj = np.zeros((n_total_nodes, n_total_nodes), dtype=int)
for _, row in connectivity_df.iterrows():
    i, j = int(row['node_i']), int(row['node_j'])
    adj[i, j] = adj[j, i] = 1
np.savetxt(DATA_DIR / 'twin_adjacency_matrix.csv', adj, delimiter=',', fmt='%d')

np.savez(DATA_DIR / 'twin_building_data.npz',
         adjacency_matrix=adj, coords=coords,
         podium_x=PODIUM_X_COORDS, tower_x=TOWER_X_COORDS,
         y_coords_t1=Y_COORDS_T1, y_coords_t2=Y_COORDS_T2, z_coords=Z_COORDS,
         tower_gap=TOWER_GAP,
         bridge_floors_single=np.array(BRIDGE_FLOORS_SINGLE),
         bridge_floors_double=np.array(BRIDGE_FLOORS_DOUBLE))

print(f"\nData saved to {DATA_DIR}")

# ============================================
# EXPORT DXF
# ============================================
EXPORT_DIR = Path(__file__).parent.parent / 'exports'
EXPORT_DIR.mkdir(exist_ok=True)
OUTPUT_FILE = EXPORT_DIR / "twin_towers_dama_v2.dxf"

print(f"\nCreating DXF...")
doc = ezdxf.new("R2010")
msp = doc.modelspace()

LAYER_CFG = {
    "column": {"color": 5, "lw": 50},
    "beam_x": {"color": 3, "lw": 35},
    "beam_y": {"color": 30, "lw": 35},
    "brace_xz": {"color": 1, "lw": 25},
    "brace_yz": {"color": 6, "lw": 25},
    "brace_floor": {"color": 7, "lw": 18},
    "brace_space": {"color": 250, "lw": 35},
    "core_wall": {"color": 44, "lw": 50},
    "shear_wall_xz": {"color": 140, "lw": 70},  # 3mm balsa panel - XZ plane
    "shear_wall_yz": {"color": 170, "lw": 70},  # 3mm balsa panel - YZ plane
    "bridge_beam": {"color": 6, "lw": 50},
    "bridge_column": {"color": 200, "lw": 40},
    "bridge_brace_top": {"color": 210, "lw": 30},
    "bridge_brace_bot": {"color": 220, "lw": 30},
    "bridge_truss_side": {"color": 6, "lw": 35},
    "bridge_brace_face": {"color": 230, "lw": 30},
    "bridge_shear_yz": {"color": 10, "lw": 40},  # Coupled shear wall bracing
    "GRID": {"color": 8, "lw": 13},
    "ANNO": {"color": 7, "lw": 0},
}

for name, cfg in LAYER_CFG.items():
    doc.layers.add(name, color=cfg["color"], lineweight=cfg["lw"])

node_xyz = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in position_df.iterrows()}

for _, row in connectivity_df.iterrows():
    etype = row['element_type']
    n1, n2 = int(row['node_i']), int(row['node_j'])
    if n1 in node_xyz and n2 in node_xyz:
        p1, p2 = node_xyz[n1], node_xyz[n2]
        layer = etype if etype in LAYER_CFG else "OUTLINE"
        msp.add_line(p1, p2, dxfattribs={"layer": layer})

doc.saveas(OUTPUT_FILE)
print(f"\n{'=' * 70}")
print(f"DXF SAVED: {OUTPUT_FILE}")
print("=" * 70)
