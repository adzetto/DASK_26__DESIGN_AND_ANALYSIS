#!/usr/bin/env python3
"""
TWIN TOWERS MODEL V5 - RIGID DESIGN
====================================
Maximum stiffness design with:
- Continuous shear walls on ALL faces
- Dense bracing on EVERY floor
- Full core system
- Maximum lateral resistance

Target: Minimize period, maximize stiffness
"""

import numpy as np
import pandas as pd
from pathlib import Path
import ezdxf

print("=" * 70)
print("TWIN TOWERS MODEL V5 - MAXIMUM RIGIDITY")
print("=" * 70)

# ============================================
# GEOMETRY - Custom grid with 1.2cm core zone
# ============================================
# X Layout: 3-8-3.4-1.2-3.4-8-3 = 30cm (7 bays)
X_COORDS = np.array([0.0, 3.0, 11.0, 14.4, 15.6, 19.0, 27.0, 30.0])

# Y Layout per tower: 4-3.4-1.2-3.4-4 = 16cm (5 bays)
Y_COORDS_T1 = np.array([0.0, 4.0, 7.4, 8.6, 12.0, 16.0])
Y_COORDS_T2 = np.array([24.0, 28.0, 31.4, 32.6, 36.0, 40.0])

TOWER_GAP = 8.0
TOWER_WIDTH = 30.0
TOWER_DEPTH = 16.0

print(f"Tower: {TOWER_WIDTH} x {TOWER_DEPTH} cm")
print(f"X bays: {len(X_COORDS)-1} bays = 30cm")
print(f"Y bays: {len(Y_COORDS_T1)-1} bays = 16cm per tower")

# Floor heights
FLOOR_HEIGHT_GROUND = 9.0
FLOOR_HEIGHT_NORMAL = 6.0
TOTAL_FLOORS = 27

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

for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    tower_str = f'tower{tower_num}'

    for floor in range(TOTAL_FLOORS):
        # =====================================================
        # COLUMNS - All grid intersections
        # =====================================================
        if floor < TOTAL_FLOORS - 1:
            for x in X_COORDS:
                for y in y_coords:
                    n1 = get_node(tower_num, floor, x, y)
                    n2 = get_node(tower_num, floor + 1, x, y)
                    add_element(n1, n2, 'column', tower_str)

        # =====================================================
        # BEAMS - Full grid (required for structural stability)
        # =====================================================
        # X-direction beams - full grid
        for i in range(len(X_COORDS) - 1):
            for y in y_coords:
                n1 = get_node(tower_num, floor, X_COORDS[i], y)
                n2 = get_node(tower_num, floor, X_COORDS[i+1], y)
                add_element(n1, n2, 'beam_x', tower_str)

        # Y-direction beams - full grid
        for j in range(len(y_coords) - 1):
            for x in X_COORDS:
                n1 = get_node(tower_num, floor, x, y_coords[j])
                n2 = get_node(tower_num, floor, x, y_coords[j+1])
                add_element(n1, n2, 'beam_y', tower_str)

        # =====================================================
        # SHEAR WALLS & BRACING - Chevron + Mega-brace design
        # Front/Back: DAMA + Chevron pattern
        # Sides: Multi-story mega-braces
        # =====================================================
        if floor < TOTAL_FLOORS - 1:

            # -------------------------------------------------
            # FRONT/BACK FACES (XZ plane) - DAMA + Chevron
            # Core zone: Shear wall plate
            # Others: Chevron (V-brace) with DAMA pattern
            # -------------------------------------------------
            for face_idx, y in enumerate([y_coords[0], y_coords[-1]]):
                for i in range(len(X_COORDS) - 1):
                    x_left = X_COORDS[i]
                    x_right = X_COORDS[i + 1]
                    x_mid = (x_left + x_right) / 2
                    panel_width = x_right - x_left

                    n_bl = get_node(tower_num, floor, x_left, y)
                    n_br = get_node(tower_num, floor, x_right, y)
                    n_tl = get_node(tower_num, floor + 1, x_left, y)
                    n_tr = get_node(tower_num, floor + 1, x_right, y)

                    # Core zone (1.2cm panels): Shear wall plate
                    is_core = abs(panel_width - 1.2) < 0.1
                    
                    if is_core:
                        add_element(n_bl, n_tr, 'shear_wall_xz', tower_str, 'pin')
                        add_element(n_br, n_tl, 'shear_wall_xz', tower_str, 'pin')
                    else:
                        # DAMA pattern with chevron
                        # Chevron: alternating V and inverted-V
                        if (floor + i + face_idx) % 2 == 0:
                            # Single diagonal (weight saving)
                            add_element(n_bl, n_tr, 'brace_xz', tower_str, 'pin')
                        else:
                            add_element(n_br, n_tl, 'brace_xz', tower_str, 'pin')

            # -------------------------------------------------
            # SIDE FACES (YZ plane) - Mega-braces (multi-story)
            # Only add braces at specific floor intervals
            # -------------------------------------------------
            mega_brace_floors = [0, 4, 8, 12, 16, 20, 24]  # Every 4 floors
            
            for face_idx, x in enumerate([X_COORDS[0], X_COORDS[-1]]):
                for j in range(len(y_coords) - 1):
                    y_bot = y_coords[j]
                    y_top = y_coords[j + 1]
                    panel_height = y_top - y_bot

                    n_bl = get_node(tower_num, floor, x, y_bot)
                    n_br = get_node(tower_num, floor, x, y_top)
                    n_tl = get_node(tower_num, floor + 1, x, y_bot)
                    n_tr = get_node(tower_num, floor + 1, x, y_top)

                    # Core zone (1.2cm panels): Shear wall plate
                    is_core = abs(panel_height - 1.2) < 0.1
                    
                    if is_core:
                        add_element(n_bl, n_tr, 'shear_wall_yz', tower_str, 'pin')
                        add_element(n_br, n_tl, 'shear_wall_yz', tower_str, 'pin')
                    elif floor in mega_brace_floors:
                        # Mega-brace at interval floors - full X
                        add_element(n_bl, n_tr, 'brace_yz', tower_str, 'pin')
                        add_element(n_br, n_tl, 'brace_yz', tower_str, 'pin')
                    else:
                        # Skip bracing on intermediate floors (weight saving)
                        pass

            # -------------------------------------------------
            # INTERIOR CORE WALLS at 1.2cm zone only
            # Reduced for weight optimization
            # -------------------------------------------------
            # Only at core X lines (14.4 and 15.6)
            core_x_lines = [14.4, 15.6]
            for cx in core_x_lines:
                if cx in X_COORDS:
                    for j in range(len(y_coords) - 1):
                        # Only corner Y panels for core
                        if j == 0 or j == len(y_coords) - 2:
                            n_bl = get_node(tower_num, floor, cx, y_coords[j])
                            n_br = get_node(tower_num, floor, cx, y_coords[j+1])
                            n_tl = get_node(tower_num, floor + 1, cx, y_coords[j])
                            n_tr = get_node(tower_num, floor + 1, cx, y_coords[j+1])
                            if n_bl and n_br and n_tl and n_tr:
                                add_element(n_bl, n_tr, 'core_wall_yz', tower_str, 'pin')
                                add_element(n_br, n_tl, 'core_wall_yz', tower_str, 'pin')
            
            # Core Y lines - reduced coverage
            core_y_values = [7.4, 8.6] if tower_num == 1 else [31.4, 32.6]
            for cy in core_y_values:
                if cy in y_coords:
                    # Only corner X panels
                    for i in [0, len(X_COORDS) - 2]:
                        n_bl = get_node(tower_num, floor, X_COORDS[i], cy)
                        n_br = get_node(tower_num, floor, X_COORDS[i+1], cy)
                        n_tl = get_node(tower_num, floor + 1, X_COORDS[i], cy)
                        n_tr = get_node(tower_num, floor + 1, X_COORDS[i+1], cy)
                        if n_bl and n_br and n_tl and n_tr:
                            add_element(n_bl, n_tr, 'core_wall_xz', tower_str, 'pin')
                            add_element(n_br, n_tl, 'core_wall_xz', tower_str, 'pin')

            # -------------------------------------------------
            # FLOOR DIAPHRAGM X-BRACING (XY plane) - DAMA pattern
            # Alternating single diagonal for weight optimization
            # -------------------------------------------------
            for i in range(len(X_COORDS) - 1):
                for j in range(len(y_coords) - 1):
                    x_l, x_r = X_COORDS[i], X_COORDS[i+1]
                    y_b, y_t = y_coords[j], y_coords[j+1]
                    
                    n1 = get_node(tower_num, floor, x_l, y_b)
                    n2 = get_node(tower_num, floor, x_r, y_t)
                    n3 = get_node(tower_num, floor, x_r, y_b)
                    n4 = get_node(tower_num, floor, x_l, y_t)
                    
                    # DAMA pattern: single diagonal alternating
                    if (floor + i + j) % 2 == 0:
                        add_element(n1, n2, 'floor_brace', tower_str, 'pin')
                    else:
                        add_element(n3, n4, 'floor_brace', tower_str, 'pin')

print(f"Tower elements: {len(elements)}")

# ============================================
# BRIDGES - Rigid connections
# ============================================
# Updated X coords to match new grid (11 and 19 are on grid)
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
    if n1 is None or n2 is None:
        return
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

    all_nodes = [t1_bot_l, t1_bot_r, t1_top_l, t1_top_r,
                 t2_bot_l, t2_bot_r, t2_top_l, t2_top_r,
                 mid_bot_l, mid_bot_r, mid_top_l, mid_top_r]
    if any(n is None for n in all_nodes):
        print(f"  WARNING: Bridge F{floor_bot}-F{floor_top} missing nodes")
        return

    # Beams
    add_bridge_elem(t1_bot_l, t1_bot_r, 'bridge_beam')
    add_bridge_elem(t1_bot_l, mid_bot_l, 'bridge_beam')
    add_bridge_elem(t1_bot_r, mid_bot_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, mid_bot_r, 'bridge_beam')
    add_bridge_elem(mid_bot_l, t2_bot_l, 'bridge_beam')
    add_bridge_elem(mid_bot_r, t2_bot_r, 'bridge_beam')
    add_bridge_elem(t2_bot_l, t2_bot_r, 'bridge_beam')

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

    # Shear bracing (YZ) - Coupled wall action
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_shear')
    add_bridge_elem(mid_bot_l, t1_top_l, 'bridge_shear')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_shear')
    add_bridge_elem(t2_bot_l, mid_top_l, 'bridge_shear')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_shear')
    add_bridge_elem(mid_bot_r, t1_top_r, 'bridge_shear')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_shear')
    add_bridge_elem(t2_bot_r, mid_top_r, 'bridge_shear')

    # Truss diagonals
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_truss')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_truss')

    # Extra rigid for top bridge
    if is_rigid:
        # Bottom X-bracing
        add_bridge_elem(t1_bot_l, mid_bot_r, 'bridge_rigid')
        add_bridge_elem(t1_bot_r, mid_bot_l, 'bridge_rigid')
        add_bridge_elem(mid_bot_l, t2_bot_r, 'bridge_rigid')
        add_bridge_elem(mid_bot_r, t2_bot_l, 'bridge_rigid')
        add_bridge_elem(t1_bot_l, t2_bot_r, 'bridge_rigid')
        add_bridge_elem(t1_bot_r, t2_bot_l, 'bridge_rigid')

        # Top X-bracing
        add_bridge_elem(t1_top_l, mid_top_r, 'bridge_rigid')
        add_bridge_elem(t1_top_r, mid_top_l, 'bridge_rigid')
        add_bridge_elem(mid_top_l, t2_top_r, 'bridge_rigid')
        add_bridge_elem(mid_top_r, t2_top_l, 'bridge_rigid')
        add_bridge_elem(t1_top_l, t2_top_r, 'bridge_rigid')
        add_bridge_elem(t1_top_r, t2_top_l, 'bridge_rigid')

        # Side X-bracing
        add_bridge_elem(t1_bot_l, t2_top_l, 'bridge_rigid')
        add_bridge_elem(t2_bot_l, t1_top_l, 'bridge_rigid')
        add_bridge_elem(t1_bot_r, t2_top_r, 'bridge_rigid')
        add_bridge_elem(t2_bot_r, t1_top_r, 'bridge_rigid')

        # Face X-bracing
        add_bridge_elem(t1_bot_l, t1_top_r, 'bridge_rigid')
        add_bridge_elem(t1_bot_r, t1_top_l, 'bridge_rigid')
        add_bridge_elem(t2_bot_l, t2_top_r, 'bridge_rigid')
        add_bridge_elem(t2_bot_r, t2_top_l, 'bridge_rigid')

        # 3D diagonals
        add_bridge_elem(t1_bot_l, t2_top_r, 'bridge_rigid')
        add_bridge_elem(t1_bot_r, t2_top_l, 'bridge_rigid')
        add_bridge_elem(t2_bot_l, t1_top_r, 'bridge_rigid')
        add_bridge_elem(t2_bot_r, t1_top_l, 'bridge_rigid')

print("\nCreating bridges...")
for fb, ft in BRIDGE_FLOORS_SINGLE:
    create_bridge(fb, ft, is_rigid=False)
create_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1], is_rigid=True)

print(f"Bridge elements: {len(bridge_elements)}")

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

# Weight
total_length_mm = connectivity_df['length'].sum() * 10
weight = total_length_mm * 36 * 160 / 1e9

print(f"\nTotal length: {total_length_mm:,.0f} mm")
print(f"Weight (ρ=160): {weight:.3f} kg")

# Count shear wall elements
shear_elements = connectivity_df[connectivity_df['element_type'].str.contains('shear|wall|core', case=False)]
print(f"\nShear wall/core elements: {len(shear_elements)}")

# Save
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
         x_coords=X_COORDS, podium_x=X_COORDS, tower_x=X_COORDS,
         y_coords_t1=Y_COORDS_T1, y_coords_t2=Y_COORDS_T2, z_coords=Z_COORDS,
         tower_gap=TOWER_GAP,
         bridge_floors_single=np.array(BRIDGE_FLOORS_SINGLE),
         bridge_floors_double=np.array(BRIDGE_FLOORS_DOUBLE))

print(f"\nData saved to {DATA_DIR}")

# DXF
print("\nCreating DXF...")
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

doc = ezdxf.new('R2010')
msp = doc.modelspace()

LAYER_COLORS = {
    'column': 7, 'beam_x': 3, 'beam_y': 4,
    'shear_wall_xz': 1, 'shear_wall_yz': 1,
    'core_wall_xz': 5, 'core_wall_yz': 5,
    'floor_brace': 6,
    'bridge_beam': 2, 'bridge_column': 2, 'bridge_shear': 1,
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

dxf_path = EXPORTS_DIR / 'twin_towers_v5_rigid.dxf'
doc.saveas(dxf_path)

print(f"\n{'='*70}")
print(f"DXF SAVED: {dxf_path}")
print(f"{'='*70}")

print(f"""
RIGID DESIGN SUMMARY
====================
- Shear walls on ALL faces (front, back, left, right)
- Interior core walls at X=10, 15, 20
- Interior walls at all Y lines
- Floor diaphragm bracing every 4 floors
- Full X-bracing pattern throughout

Total shear wall elements: {len(shear_elements)}
This should significantly INCREASE stiffness and DECREASE period.
""")
