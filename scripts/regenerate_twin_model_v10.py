"""
TWIN TOWERS MODEL V10
=====================
Changes from V9:
1. No shear wall panels - all braces are stick X-braces
2. Inner 3.4cm bays: X-cross (both diags) floors 0-11 (up to 2nd bridge)
3. No braces on corner 3.0cm bays (X=0-3, 27-30)
4. 8.0cm bays: X-cross every 3 floors
5. YZ braces: X-cross every 3 floors on side faces 
6. Weight limit: 2.000 kg
"""

import numpy as np
import pandas as pd
from pathlib import Path
import ezdxf

print("=" * 70)
print("TWIN TOWERS MODEL V10")
print("=" * 70)

# ============================================
# GEOMETRY  (all coordinates = column CENTERS)
# Column section 6×6 mm → half-width 0.3 cm
# X spacings c-t-c: 2.7, 8.3, 3.7, 3.7, 8.3, 2.7 (total 29.4)
# Y spacings c-t-c per tower: 7.7, 7.7 (total 15.4)
# Remaining 0.6 cm = column overhangs at edges
# ============================================
X_COORDS = np.array([0.3, 3.0, 11.3, 15.0, 18.7, 27.0, 29.7])  # 7 columns
Y_COORDS_T1 = np.array([0.3, 8.0, 15.7])   # 3 columns per tower
Y_COORDS_T2 = np.array([24.3, 32.0, 39.7])

FLOOR_HEIGHT_GROUND = 9.0
FLOOR_HEIGHT_NORMAL = 6.0
TOTAL_FLOORS = 26

Z_COORDS = [0.0, FLOOR_HEIGHT_GROUND]
for i in range(2, TOTAL_FLOORS):
    Z_COORDS.append(Z_COORDS[-1] + FLOOR_HEIGHT_NORMAL)
Z_COORDS = np.array(Z_COORDS)

print(f"Height: {Z_COORDS[-1]} cm ({TOTAL_FLOORS} floors)")

# ============================================
# V10 CONFIGURATION
# ============================================
INNER_BRACE_LIMIT = 13      # Inner 3.7cm X-cross up to floor 13
XZ_BRACE_INTERVAL = 3       # 8.3cm bays: X-cross every 3 floors
YZ_BRACE_INTERVAL = 3       # YZ X-cross every 3 floors
FLOOR_BRACE_INTERVAL = 10   # Floor bracing every 10 floors
BEAM_KEEP_INTERVAL = 4      # Keep interior beams every 4th floor

print(f"\nV10 Configuration:")
print(f"  Inner 3.7cm braces: floors 0-{INNER_BRACE_LIMIT-1} (X-cross)")
print(f"  Outer 8.3cm braces: every {XZ_BRACE_INTERVAL} floors (X-cross)")
print(f"  Corner 2.7cm bays: NO braces")
print(f"  YZ braces: every {YZ_BRACE_INTERVAL} floors (X-cross, checkerboard)")
print(f"  Floor bracing: every {FLOOR_BRACE_INTERVAL} floors")

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

# Build brace groups: first 4 floors per-floor, then 3-floor groups
PERFLOOR_BRACE_LIMIT = 4  # First 4 floors: brace every floor
brace_groups_3 = []
for f in range(min(PERFLOOR_BRACE_LIMIT, TOTAL_FLOORS - 1)):
    brace_groups_3.append((f, f + 1))
f = PERFLOOR_BRACE_LIMIT
while f < TOTAL_FLOORS - 1:
    f_top = min(f + XZ_BRACE_INTERVAL, TOTAL_FLOORS - 1)
    brace_groups_3.append((f, f_top))
    f = f_top

print(f"\nBrace groups (3-floor): {brace_groups_3}")

for tower_num, y_coords in [(1, Y_COORDS_T1), (2, Y_COORDS_T2)]:
    tower_str = f'tower{tower_num}'

    for floor in range(TOTAL_FLOORS):
        # 1. COLUMNS
        if floor < TOTAL_FLOORS - 1:
            for x in X_COORDS:
                for y in y_coords:
                    n1 = get_node(tower_num, floor, x, y)
                    n2 = get_node(tower_num, floor + 1, x, y)
                    add_element(n1, n2, 'column', tower_str)

        # 2. BEAMS X
        for i in range(len(X_COORDS) - 1):
            for y in y_coords:
                x1, x2 = X_COORDS[i], X_COORDS[i+1]
                is_perimeter_y = (y == y_coords[0] or y == y_coords[-1])
                keep_beam = is_perimeter_y or (floor % BEAM_KEEP_INTERVAL == 0)
                if keep_beam:
                    n1 = get_node(tower_num, floor, x1, y)
                    n2 = get_node(tower_num, floor, x2, y)
                    add_element(n1, n2, 'beam_x', tower_str)

        # 3. BEAMS Y
        for j in range(len(y_coords) - 1):
            for x in X_COORDS:
                y1, y2 = y_coords[j], y_coords[j+1]
                is_perimeter_x = (x == X_COORDS[0] or x == X_COORDS[-1])
                keep_beam = is_perimeter_x or (floor % BEAM_KEEP_INTERVAL == 0)
                if keep_beam:
                    n1 = get_node(tower_num, floor, x, y1)
                    n2 = get_node(tower_num, floor, x, y2)
                    add_element(n1, n2, 'beam_y', tower_str)

        # 4. XZ BRACES (Front/Back faces) - per floor for inner, multi-floor for outer
        if floor < TOTAL_FLOORS - 1:
            for y in [y_coords[0], y_coords[-1]]:
                for i in range(len(X_COORDS) - 1):
                    x_left = X_COORDS[i]
                    x_right = X_COORDS[i + 1]
                    span_w = x_right - x_left

                    # 3.7cm INNER BAYS -> X-cross per floor, bottom + top 2 floors
                    if abs(span_w - 3.7) < 0.15:
                        if floor < INNER_BRACE_LIMIT or floor >= TOTAL_FLOORS - 3:
                            n_bl = get_node(tower_num, floor, x_left, y)
                            n_br = get_node(tower_num, floor, x_right, y)
                            n_tl = get_node(tower_num, floor + 1, x_left, y)
                            n_tr = get_node(tower_num, floor + 1, x_right, y)
                            add_element(n_bl, n_tr, 'brace_xz', tower_str, 'pin')
                            add_element(n_br, n_tl, 'brace_xz', tower_str, 'pin')

                    # 2.7cm CORNER BAYS -> NO BRACES
                    elif abs(span_w - 2.7) < 0.15:
                        pass

                    # 8.3cm BAYS -> handled in multi-floor groups below
                    else:
                        pass

    # 8.0cm bay X-cross braces: 3-floor span groups
    for fb, ft in brace_groups_3:
        for y in [y_coords[0], y_coords[-1]]:
            for i in range(len(X_COORDS) - 1):
                span_w = X_COORDS[i+1] - X_COORDS[i]
                if abs(span_w - 8.3) < 0.15:
                    n_bl = get_node(tower_num, fb, X_COORDS[i], y)
                    n_br = get_node(tower_num, fb, X_COORDS[i+1], y)
                    n_tl = get_node(tower_num, ft, X_COORDS[i], y)
                    n_tr = get_node(tower_num, ft, X_COORDS[i+1], y)
                    add_element(n_bl, n_tr, 'brace_xz', tower_str, 'pin')
                    add_element(n_br, n_tl, 'brace_xz', tower_str, 'pin')

    # YZ braces: 3-floor span MIRRORED CHECKERBOARD on side faces
    # Tower 1: odd groups → right bay, even groups → left bay
    # Tower 2: odd groups → left bay, even groups → right bay
    # First and last groups: FULL (both bays)
    n_groups = len(brace_groups_3)
    for gi, (fb, ft) in enumerate(brace_groups_3):
        is_full = (gi == 0 or gi == n_groups - 1)  # bottom & top = full
        for x in [X_COORDS[0], X_COORDS[-1]]:
            active_bays = []
            for j in range(len(y_coords) - 1):
                y_bot, y_top = y_coords[j], y_coords[j+1]
                active_bays.append((j, y_bot, y_top))
            for bi, (j, y_bot, y_top) in enumerate(active_bays):
                if is_full:
                    place = True
                else:
                    # Tower 1: place if (gi+bi) even; Tower 2: place if (gi+bi) odd
                    if tower_num == 1:
                        place = (gi + bi) % 2 == 0
                    else:
                        place = (gi + bi) % 2 == 1
                if not place:
                    continue
                n_bl = get_node(tower_num, fb, x, y_bot)
                n_br = get_node(tower_num, fb, x, y_top)
                n_tl = get_node(tower_num, ft, x, y_bot)
                n_tr = get_node(tower_num, ft, x, y_top)
                add_element(n_bl, n_tr, 'brace_yz', tower_str, 'pin')
                add_element(n_br, n_tl, 'brace_yz', tower_str, 'pin')

    # FLOOR BRACES
    for floor in range(TOTAL_FLOORS):
        if floor % FLOOR_BRACE_INTERVAL != 0:
            continue
        for i in range(len(X_COORDS)-1):
            for j in range(len(y_coords)-1):
                x1, x2 = X_COORDS[i], X_COORDS[i+1]
                y1, y2 = y_coords[j], y_coords[j+1]
                if abs(x2-x1 - 0.6) < 0.15 or abs(y2-y1 - 0.6) < 0.15:
                    continue
                n1 = get_node(tower_num, floor, x1, y1)
                n2 = get_node(tower_num, floor, x2, y2)
                add_element(n1, n2, 'floor_brace', tower_str, 'pin')

print(f"Tower elements: {len(elements)}")

# ============================================
# BRIDGES (Same as V9)
# ============================================
BRIDGE_X_LEFT = 11.3
BRIDGE_X_RIGHT = 18.7
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

def create_bridge(floor_bot, floor_top):
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

    # Beams (10)
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
    # Columns (2)
    add_bridge_elem(mid_bot_l, mid_top_l, 'bridge_column')
    add_bridge_elem(mid_bot_r, mid_top_r, 'bridge_column')
    # Truss (8)
    add_bridge_elem(t1_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t1_top_l, 'bridge_truss')
    add_bridge_elem(mid_bot_l, t2_top_l, 'bridge_truss')
    add_bridge_elem(t2_bot_l, mid_top_l, 'bridge_truss')
    add_bridge_elem(t1_bot_r, mid_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t1_top_r, 'bridge_truss')
    add_bridge_elem(mid_bot_r, t2_top_r, 'bridge_truss')
    add_bridge_elem(t2_bot_r, mid_top_r, 'bridge_truss')
    # Rigid (4)
    add_bridge_elem(t1_bot_l, t2_bot_r, 'bridge_rigid')
    add_bridge_elem(t2_bot_l, t1_bot_r, 'bridge_rigid')
    add_bridge_elem(t1_top_l, t2_top_r, 'bridge_rigid')
    add_bridge_elem(t2_top_l, t1_top_r, 'bridge_rigid')

for fb, ft in BRIDGE_FLOORS_SINGLE:
    create_bridge(fb, ft)
create_bridge(BRIDGE_FLOORS_DOUBLE[0], BRIDGE_FLOORS_DOUBLE[1])

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

total_length = connectivity_df['length'].sum()
frame_weight = total_length * 10 * SECTION_FRAME * BALSA_DENSITY / 1e9

print(f"\n{'='*70}")
print("WEIGHT ANALYSIS (V10):")
print(f"{'='*70}")
print(f"  Total length:   {total_length:.1f} cm")
print(f"  Frame weight:   {frame_weight:.4f} kg")
print(f"  Limit:          2.000 kg")
print(f"  Margin:         {2.000 - frame_weight:.4f} kg")
if frame_weight > 2.0:
    print(f"  Status:         OVER LIMIT!")
else:
    print(f"  Status:         OK")

# Element summary
print(f"\n{'='*70}")
print("ELEMENT SUMMARY (V10):")
print(f"{'='*70}")
for etype in sorted(connectivity_df['element_type'].unique()):
    sub = connectivity_df[connectivity_df['element_type'] == etype]
    print(f"  {etype:<20}: {len(sub):4d} elements, {sub['length'].sum():8.1f} cm")
print(f"\n  TOTAL: {len(connectivity_df)} elements, {len(position_df)} nodes")

# ============================================
# SAVE
# ============================================
DATA_DIR = Path(__file__).parent.parent / 'data'
DATA_DIR.mkdir(exist_ok=True)

position_df.to_csv(DATA_DIR / 'twin_position_matrix_v10.csv', index=False)
connectivity_df.to_csv(DATA_DIR / 'twin_connectivity_matrix_v10.csv', index=False)

# DXF with colors
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'
EXPORTS_DIR.mkdir(exist_ok=True)

LAYER_COLORS = {
    'column': 4, 'beam_x': 3, 'beam_y': 2,
    'brace_xz': 6, 'brace_yz': 1, 'floor_brace': 5,
    'bridge_beam': 30, 'bridge_column': 30,
    'bridge_truss': 40, 'bridge_rigid': 50,
}

doc = ezdxf.new('R2010')
msp = doc.modelspace()
for layer_name, color in LAYER_COLORS.items():
    doc.layers.add(layer_name, color=color)

for _, elem in connectivity_df.iterrows():
    n1, n2 = int(elem['node_i']), int(elem['node_j'])
    etype = elem['element_type']
    color = LAYER_COLORS.get(etype, 7)
    msp.add_line(tuple(coords[n1]), tuple(coords[n2]),
                 dxfattribs={'layer': etype, 'color': color})
try:
    doc.saveas(EXPORTS_DIR / 'twin_towers_v10.dxf')
except PermissionError:
    print("  WARNING: DXF file locked (close AutoCAD and retry)")

# ============================================
# SKETCHUP RUBY SCRIPT EXPORT
# ============================================
SKETCHUP_COLORS = {
    'column':       [0, 200, 200],
    'beam_x':       [0, 200, 0],
    'beam_y':       [220, 160, 0],
    'brace_xz':     [200, 0, 200],
    'brace_yz':     [220, 40, 40],
    'floor_brace':  [160, 0, 160],
    'bridge_beam':  [220, 160, 0],
    'bridge_column':[220, 160, 0],
    'bridge_truss': [180, 120, 0],
    'bridge_rigid': [120, 120, 120],
}

skp_path = EXPORTS_DIR / 'twin_towers_v10.rb'
with open(skp_path, 'w') as f:
    f.write("# SketchUp Ruby Script - DASK Twin Towers V10\n")
    f.write("# Open SketchUp > Window > Ruby Console > load this file\n")
    f.write("# Units: mm (SketchUp default)\n\n")
    f.write("model = Sketchup.active_model\n")
    f.write("model.start_operation('DASK V10', true)\n")
    f.write("ents = model.active_entities\n\n")

    # Create groups per element type
    etypes_used = sorted(connectivity_df['element_type'].unique())
    for etype in etypes_used:
        rgb = SKETCHUP_COLORS.get(etype, [180, 180, 180])
        sub = connectivity_df[connectivity_df['element_type'] == etype]
        f.write(f"# --- {etype} ({len(sub)} elements) ---\n")
        f.write(f"grp_{etype} = ents.add_group\n")
        f.write(f"grp_{etype}.name = '{etype}'\n")
        f.write(f"ge = grp_{etype}.entities\n")
        for _, elem in sub.iterrows():
            n1, n2 = int(elem['node_i']), int(elem['node_j'])
            # coords in cm -> convert to mm for SketchUp
            x1, y1, z1 = coords[n1] * 10
            x2, y2, z2 = coords[n2] * 10
            f.write(f"ge.add_line([{x1:.1f},{y1:.1f},{z1:.1f}],[{x2:.1f},{y2:.1f},{z2:.1f}])\n")
        f.write(f"mat = model.materials.add('{etype}')\n")
        f.write(f"mat.color = [{rgb[0]},{rgb[1]},{rgb[2]}]\n")
        f.write(f"grp_{etype}.material = mat\n\n")

    f.write("model.commit_operation\n")
    f.write("Sketchup.active_model.active_view.zoom_extents\n")
    f.write("puts 'DASK V10 model loaded successfully!'\n")

print(f"\nSaved: data/twin_position_matrix_v10.csv")
print(f"Saved: data/twin_connectivity_matrix_v10.csv")
print(f"Saved: exports/twin_towers_v10.dxf")
print(f"Saved: exports/twin_towers_v10.rb (SketchUp)")
print(f"\n{'='*70}")
print("MODEL V10 GENERATION COMPLETE")
print(f"{'='*70}")
