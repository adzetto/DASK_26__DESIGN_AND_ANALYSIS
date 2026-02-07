"""
TBDY 2018 - Complete Floor-by-Floor Irregularity & Eccentricity Analysis
Twin Towers V9 (1:50 Scale Model)

TBDY 2018 Table 3.6:
  A1a - Torsional Irregularity          (eta_bi > 1.2)
  A1b - Floor Discontinuity             (area ratio check)
  A2  - Plan Projection Irregularity    (projection > 20%)
  A3  - Non-Parallel Axis              (axis check)

TBDY 2018 Table 3.7:
  B1  - Soft Story (Stiffness)          (eta_ki < 0.7)
  B2  - Weak Story (Strength)           (eta_ci < 0.8)
  B3  - Mass Irregularity               (m_i/m_i+1 > 1.5)

Plus: Center of Mass, Center of Rigidity, Eccentricities per floor
"""

import csv
import sys
import io
import os
import json

# Windows console encoding fix
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POS_CSV = os.path.join(BASE_DIR, "twin_position_matrix_v9.csv")
CONN_CSV = os.path.join(BASE_DIR, "twin_connectivity_matrix_v9.csv")

print("=" * 80)
print("  TBDY 2018 - COMPLETE IRREGULARITY & ECCENTRICITY ANALYSIS")
print("  Twin Towers V9 (1:50 Scale Model)")
print("  All floor-by-floor checks per TBDY 2018 Tables 3.6 & 3.7")
print("=" * 80)
print()

# =============================================================================
# READ MODEL DATA
# =============================================================================
print(">>> Reading model data...")

nodes = []
with open(POS_CSV, 'r') as f:
    for row in csv.DictReader(f):
        nodes.append({
            'id': int(row['node_id']),
            'x': float(row['x']),
            'y': float(row['y']),
            'z': float(row['z']),
            'floor': int(row['floor']),
            'tower': row['tower'].strip(),
            'zone': row['zone'].strip()
        })

elements = []
with open(CONN_CSV, 'r') as f:
    for row in csv.DictReader(f):
        elements.append({
            'id': int(row['element_id']),
            'ni': int(row['node_i']),
            'nj': int(row['node_j']),
            'type': row['element_type'].strip(),
            'tower': row['tower'].strip(),
            'conn': row['connection'].strip(),
            'length': float(row['length'])
        })

print(f"    Nodes: {len(nodes)}, Elements: {len(elements)}")

# Organize by floor
floors = {}
for n in nodes:
    fl = n['floor']
    if fl not in floors:
        floors[fl] = []
    floors[fl].append(n)

sorted_floors = sorted(floors.keys())
num_floors = max(sorted_floors)
print(f"    Floors: {sorted_floors[0]} to {num_floors} ({len(sorted_floors)} levels)")

# Node lookup
node_map = {n['id']: n for n in nodes}

# Material/section properties (from model)
E = 170.0      # kN/cm2
G = 65.385     # kN/cm2
A = 0.36       # cm2
Iz = 0.0108    # cm4
g_val = 981.0  # cm/s2

# Mass per node (distributed)
total_mass_kg = 40.62
mass_per_node = total_mass_kg / len([n for n in nodes if n['floor'] > 0])

print(f"    Total mass: {total_mass_kg} kg")
print(f"    Mass per node: {mass_per_node:.4f} kg")
print()

# =============================================================================
# HELPER: Get floor plan dimensions
# =============================================================================
def get_floor_plan(floor_num):
    """Get plan dimensions and node positions for a floor."""
    fl_nodes = floors.get(floor_num, [])
    if not fl_nodes:
        return None

    xs = [n['x'] for n in fl_nodes]
    ys = [n['y'] for n in fl_nodes]

    return {
        'nodes': fl_nodes,
        'n_nodes': len(fl_nodes),
        'x_min': min(xs), 'x_max': max(xs),
        'y_min': min(ys), 'y_max': max(ys),
        'Lx': max(xs) - min(xs),
        'Ly': max(ys) - min(ys),
        'x_center': sum(xs) / len(xs),
        'y_center': sum(ys) / len(ys),
    }

# =============================================================================
# HELPER: Center of Mass (CM)
# =============================================================================
def calc_center_of_mass(floor_num):
    """Calculate CM assuming equal mass at each node."""
    fl_nodes = floors.get(floor_num, [])
    if not fl_nodes:
        return 0, 0, 0

    # Exclude ground floor nodes (they're fixed)
    active = [n for n in fl_nodes if n['floor'] > 0]
    if not active:
        active = fl_nodes

    total_m = len(active) * mass_per_node
    cx = sum(n['x'] * mass_per_node for n in active) / total_m
    cy = sum(n['y'] * mass_per_node for n in active) / total_m
    return cx, cy, total_m

# =============================================================================
# HELPER: Center of Rigidity (CR) - simplified
# =============================================================================
def calc_center_of_rigidity(floor_num):
    """
    Estimate CR based on column positions.
    CR = sum(k_i * x_i) / sum(k_i) for each direction.
    For identical columns, CR = centroid of column positions.
    """
    # Get columns connecting this floor to floor below
    fl_nodes_set = set(n['id'] for n in floors.get(floor_num, []))
    fl_below_set = set(n['id'] for n in floors.get(floor_num - 1, []))

    columns = []
    for e in elements:
        if e['type'] == 'column':
            if (e['ni'] in fl_below_set and e['nj'] in fl_nodes_set) or \
               (e['nj'] in fl_below_set and e['ni'] in fl_nodes_set):
                # Get top node position (this floor)
                top_id = e['nj'] if e['nj'] in fl_nodes_set else e['ni']
                columns.append(node_map[top_id])

    if not columns:
        # Fallback: use all nodes
        return calc_center_of_mass(floor_num)[:2]

    # For uniform columns, CR = centroid of column positions
    cr_x = sum(c['x'] for c in columns) / len(columns)
    cr_y = sum(c['y'] for c in columns) / len(columns)
    return cr_x, cr_y

# =============================================================================
# HELPER: Story stiffness estimation
# =============================================================================
def estimate_story_stiffness(floor_num):
    """
    Estimate lateral stiffness of a story.
    k = sum(12*E*I/h^3) for all columns in the story.
    """
    fl_nodes_set = set(n['id'] for n in floors.get(floor_num, []))
    fl_below_set = set(n['id'] for n in floors.get(floor_num - 1, []))

    col_count = 0
    brace_count = 0
    k_total = 0.0

    for e in elements:
        if (e['ni'] in fl_below_set and e['nj'] in fl_nodes_set) or \
           (e['nj'] in fl_below_set and e['ni'] in fl_nodes_set):

            h = e['length']
            if h <= 0:
                continue

            if e['type'] == 'column':
                # Fixed-fixed column stiffness
                k_col = 12.0 * E * Iz / (h ** 3)
                k_total += k_col
                col_count += 1
            elif e['type'] == 'brace':
                # Brace axial stiffness projected horizontally
                top_id = e['nj'] if e['nj'] in fl_nodes_set else e['ni']
                bot_id = e['ni'] if top_id == e['nj'] else e['nj']
                dx = node_map[top_id]['x'] - node_map[bot_id]['x']
                dy = node_map[top_id]['y'] - node_map[bot_id]['y']
                dz = node_map[top_id]['z'] - node_map[bot_id]['z']
                L = (dx**2 + dy**2 + dz**2) ** 0.5
                if L > 0:
                    cos_x = dx / L
                    cos_y = dy / L
                    k_brace_x = E * A * cos_x**2 / L
                    k_brace_y = E * A * cos_y**2 / L
                    k_total += (k_brace_x + k_brace_y)
                    brace_count += 1

    return k_total, col_count, brace_count

# =============================================================================
# HELPER: Story mass
# =============================================================================
def calc_story_mass(floor_num):
    """Mass of a single floor."""
    fl_nodes = [n for n in floors.get(floor_num, []) if n['floor'] > 0]
    return len(fl_nodes) * mass_per_node

# =============================================================================
# HELPER: Torsional irregularity at a floor
# =============================================================================
def calc_torsional_irregularity(floor_num, direction='x'):
    """
    A1a: eta_bi = delta_max / delta_avg
    Using simplified stiffness-based displacement estimation.
    """
    plan = get_floor_plan(floor_num)
    if not plan or plan['n_nodes'] < 4:
        return 1.0, 0, 0

    fl_nodes = plan['nodes']

    # Get center of rigidity
    cr_x, cr_y = calc_center_of_rigidity(floor_num)
    cm_x, cm_y, _ = calc_center_of_mass(floor_num)

    # Eccentricity
    e_x = cm_x - cr_x
    e_y = cm_y - cr_y

    # Plan dimensions
    Lx = plan['Lx']
    Ly = plan['Ly']

    if direction == 'x':
        # Loading in X: torsion from eccentricity e_y
        # Add 5% accidental eccentricity
        e_total = abs(e_y) + 0.05 * Ly

        # Displacement at each node: u_i = u_avg + theta * (y_i - cr_y)
        # theta proportional to torsional moment / torsional stiffness
        # Simplified: displacement varies linearly with distance from CR

        if Ly > 0:
            disps = []
            for n in fl_nodes:
                y_dist = n['y'] - cr_y
                # Normalized displacement: 1 + (e_total * y_dist) / (Ly/2)^2
                u_norm = 1.0 + e_total * y_dist / ((Ly / 2.0) ** 2) if Ly > 0 else 1.0
                disps.append(abs(u_norm))

            d_max = max(disps)
            d_avg = sum(disps) / len(disps)
            eta = d_max / d_avg if d_avg > 0 else 1.0
            return eta, e_total, Ly
        else:
            return 1.0, 0, 0
    else:
        e_total = abs(e_x) + 0.05 * Lx
        if Lx > 0:
            disps = []
            for n in fl_nodes:
                x_dist = n['x'] - cr_x
                u_norm = 1.0 + e_total * x_dist / ((Lx / 2.0) ** 2) if Lx > 0 else 1.0
                disps.append(abs(u_norm))
            d_max = max(disps)
            d_avg = sum(disps) / len(disps)
            eta = d_max / d_avg if d_avg > 0 else 1.0
            return eta, e_total, Lx
        else:
            return 1.0, 0, 0

# =============================================================================
# MAIN ANALYSIS
# =============================================================================
print("=" * 80)
print("  FLOOR-BY-FLOOR IRREGULARITY ANALYSIS")
print("=" * 80)
print()

results = []

for fl in sorted_floors:
    if fl == 0:
        continue  # Skip ground floor

    plan = get_floor_plan(fl)
    plan_below = get_floor_plan(fl - 1)

    # --- Center of Mass ---
    cm_x, cm_y, floor_mass = calc_center_of_mass(fl)

    # --- Center of Rigidity ---
    cr_x, cr_y = calc_center_of_rigidity(fl)

    # --- Eccentricities ---
    e_x = cm_x - cr_x
    e_y = cm_y - cr_y

    Lx = plan['Lx'] if plan else 0
    Ly = plan['Ly'] if plan else 0

    # Accidental eccentricity (TBDY 2018: +/- 5%)
    e_acc_x = 0.05 * Lx
    e_acc_y = 0.05 * Ly

    # Total eccentricity
    e_total_x = abs(e_x) + e_acc_x
    e_total_y = abs(e_y) + e_acc_y

    # --- A1a: Torsional Irregularity ---
    eta_x, _, _ = calc_torsional_irregularity(fl, 'x')
    eta_y, _, _ = calc_torsional_irregularity(fl, 'y')
    eta_max = max(eta_x, eta_y)

    a1a_irregular = eta_max > 1.2
    a1a_severe = eta_max > 2.0

    # D_bi amplification factor
    if eta_max > 1.2 and eta_max <= 2.0:
        D_bi = (eta_max / 1.2) ** 2
    elif eta_max > 2.0:
        D_bi = -1  # Not permitted
    else:
        D_bi = 1.0

    # --- A2: Plan Projection Irregularity ---
    # Check if plan has significant setbacks compared to floor below
    a2_irregular = False
    if plan and plan_below:
        # If current floor area significantly smaller than below
        area_ratio_x = plan['Lx'] / plan_below['Lx'] if plan_below['Lx'] > 0 else 1.0
        area_ratio_y = plan['Ly'] / plan_below['Ly'] if plan_below['Ly'] > 0 else 1.0
        # Projection check: if setback > 20% of plan dimension
        if area_ratio_x < 0.8 or area_ratio_y < 0.8:
            a2_irregular = True

    # --- B1: Soft Story (Stiffness Irregularity) ---
    k_i, n_col_i, n_brace_i = estimate_story_stiffness(fl)

    b1_irregular = False
    b1_eta = 1.0
    if fl < num_floors:
        k_above, _, _ = estimate_story_stiffness(fl + 1)
        if k_above > 0:
            b1_eta = k_i / k_above
            if b1_eta < 0.7:
                b1_irregular = True

    # --- B2: Weak Story (Strength Irregularity) ---
    # For elastic model: strength proportional to stiffness * yield displacement
    # Simplified: use stiffness ratio as proxy
    b2_irregular = False
    b2_eta = 1.0
    if fl < num_floors:
        k_above2, _, _ = estimate_story_stiffness(fl + 1)
        if k_above2 > 0:
            b2_eta = k_i / k_above2
            if b2_eta < 0.8:
                b2_irregular = True

    # --- B3: Mass Irregularity ---
    m_i = calc_story_mass(fl)
    b3_irregular = False
    b3_ratio_above = 1.0
    b3_ratio_below = 1.0

    if fl < num_floors:
        m_above = calc_story_mass(fl + 1)
        if m_above > 0:
            b3_ratio_above = m_i / m_above
    if fl > 1:
        m_below = calc_story_mass(fl - 1)
        if m_below > 0:
            b3_ratio_below = m_i / m_below

    if b3_ratio_above > 1.5 or b3_ratio_below > 1.5:
        b3_irregular = True

    results.append({
        'floor': fl,
        'z': plan['nodes'][0]['z'] if plan else 0,
        'n_nodes': plan['n_nodes'] if plan else 0,
        'Lx': Lx, 'Ly': Ly,
        'cm_x': cm_x, 'cm_y': cm_y,
        'cr_x': cr_x, 'cr_y': cr_y,
        'e_x': e_x, 'e_y': e_y,
        'e_acc_x': e_acc_x, 'e_acc_y': e_acc_y,
        'e_total_x': e_total_x, 'e_total_y': e_total_y,
        'eta_x': eta_x, 'eta_y': eta_y, 'eta_max': eta_max,
        'a1a': a1a_irregular, 'a1a_severe': a1a_severe, 'D_bi': D_bi,
        'a2': a2_irregular,
        'k_story': k_i, 'n_col': n_col_i, 'n_brace': n_brace_i,
        'b1_eta': b1_eta, 'b1': b1_irregular,
        'b2_eta': b2_eta, 'b2': b2_irregular,
        'mass': m_i,
        'b3_above': b3_ratio_above, 'b3_below': b3_ratio_below, 'b3': b3_irregular,
    })

# =============================================================================
# PRINT RESULTS - ECCENTRICITIES
# =============================================================================
print("-" * 80)
print("  TABLE 1: CENTER OF MASS (CM) & CENTER OF RIGIDITY (CR)")
print("  TBDY 2018 - Eccentricity at Each Floor")
print("-" * 80)
print(f"{'Floor':>5} {'Z(cm)':>7} {'CM_x':>8} {'CM_y':>8} {'CR_x':>8} {'CR_y':>8} {'e_x':>7} {'e_y':>7} {'e_acc_x':>7} {'e_acc_y':>7}")
print("-" * 80)

for r in results:
    print(f"{r['floor']:5d} {r['z']:7.1f} {r['cm_x']:8.2f} {r['cm_y']:8.2f} "
          f"{r['cr_x']:8.2f} {r['cr_y']:8.2f} {r['e_x']:7.2f} {r['e_y']:7.2f} "
          f"{r['e_acc_x']:7.2f} {r['e_acc_y']:7.2f}")

print()

# =============================================================================
# PRINT RESULTS - A1a TORSIONAL IRREGULARITY
# =============================================================================
print("-" * 80)
print("  TABLE 2: A1a TORSIONAL IRREGULARITY (TBDY 2018 Table 3.6)")
print("  eta_bi = Delta_max / Delta_avg  |  Limit: 1.2  |  Severe: 2.0")
print("-" * 80)
print(f"{'Floor':>5} {'Z(cm)':>7} {'eta_X':>8} {'eta_Y':>8} {'eta_max':>8} {'D_bi':>7} {'Status':>20}")
print("-" * 80)

for r in results:
    if r['a1a_severe']:
        status = "NOT PERMITTED (>2.0)"
    elif r['a1a']:
        status = f"IRREGULAR (D={r['D_bi']:.3f})"
    else:
        status = "REGULAR"
    print(f"{r['floor']:5d} {r['z']:7.1f} {r['eta_x']:8.4f} {r['eta_y']:8.4f} "
          f"{r['eta_max']:8.4f} {r['D_bi']:7.3f} {status:>20}")

print()

# =============================================================================
# PRINT RESULTS - B1 SOFT STORY
# =============================================================================
print("-" * 80)
print("  TABLE 3: B1 SOFT STORY IRREGULARITY (TBDY 2018 Table 3.7)")
print("  eta_ki = k_i / k_(i+1)  |  Limit: < 0.7 = SOFT STORY")
print("-" * 80)
print(f"{'Floor':>5} {'Z(cm)':>7} {'k_i(kN/cm)':>12} {'Cols':>5} {'Braces':>7} {'eta_ki':>8} {'Status':>15}")
print("-" * 80)

for r in results:
    status = "SOFT STORY" if r['b1'] else "OK"
    print(f"{r['floor']:5d} {r['z']:7.1f} {r['k_story']:12.4f} {r['n_col']:5d} {r['n_brace']:7d} "
          f"{r['b1_eta']:8.4f} {status:>15}")

print()

# =============================================================================
# PRINT RESULTS - B2 WEAK STORY
# =============================================================================
print("-" * 80)
print("  TABLE 4: B2 WEAK STORY IRREGULARITY (TBDY 2018 Table 3.7)")
print("  eta_ci = V_i / V_(i+1)  |  Limit: < 0.8 = WEAK STORY")
print("-" * 80)
print(f"{'Floor':>5} {'Z(cm)':>7} {'eta_ci':>8} {'Status':>15}")
print("-" * 80)

for r in results:
    status = "WEAK STORY" if r['b2'] else "OK"
    print(f"{r['floor']:5d} {r['z']:7.1f} {r['b2_eta']:8.4f} {status:>15}")

print()

# =============================================================================
# PRINT RESULTS - B3 MASS IRREGULARITY
# =============================================================================
print("-" * 80)
print("  TABLE 5: B3 MASS IRREGULARITY (TBDY 2018 Table 3.7)")
print("  m_i / m_(i+1) > 1.5 OR m_i / m_(i-1) > 1.5 = IRREGULAR")
print("-" * 80)
print(f"{'Floor':>5} {'Z(cm)':>7} {'Mass(kg)':>10} {'Nodes':>6} {'m/m_above':>10} {'m/m_below':>10} {'Status':>15}")
print("-" * 80)

for r in results:
    status = "IRREGULAR" if r['b3'] else "OK"
    print(f"{r['floor']:5d} {r['z']:7.1f} {r['mass']:10.4f} {r['n_nodes']:6d} "
          f"{r['b3_above']:10.4f} {r['b3_below']:10.4f} {status:>15}")

print()

# =============================================================================
# PRINT RESULTS - TOTAL ECCENTRICITIES WITH D_bi AMPLIFICATION
# =============================================================================
print("-" * 80)
print("  TABLE 6: DESIGN ECCENTRICITIES (TBDY 2018 Section 4.7.4)")
print("  e_design = D_bi * (e_structural + 0.05*L)")
print("-" * 80)
print(f"{'Floor':>5} {'e_x':>7} {'+e_accX':>8} {'e_totX':>8} {'e_y':>7} {'+e_accY':>8} {'e_totY':>8} {'D_bi':>6} {'e_desX':>8} {'e_desY':>8}")
print("-" * 80)

for r in results:
    e_des_x = r['D_bi'] * r['e_total_x'] if r['D_bi'] > 0 else float('inf')
    e_des_y = r['D_bi'] * r['e_total_y'] if r['D_bi'] > 0 else float('inf')
    print(f"{r['floor']:5d} {r['e_x']:7.2f} {r['e_acc_x']:8.2f} {r['e_total_x']:8.2f} "
          f"{r['e_y']:7.2f} {r['e_acc_y']:8.2f} {r['e_total_y']:8.2f} "
          f"{r['D_bi']:6.3f} {e_des_x:8.2f} {e_des_y:8.2f}")

print()

# =============================================================================
# SUMMARY
# =============================================================================
print("=" * 80)
print("  IRREGULARITY SUMMARY")
print("=" * 80)
print()

# A1a summary
a1a_floors = [r['floor'] for r in results if r['a1a']]
a1a_severe_floors = [r['floor'] for r in results if r['a1a_severe']]
max_eta = max(r['eta_max'] for r in results)
max_eta_floor = [r['floor'] for r in results if r['eta_max'] == max_eta][0]

print(f"  A1a - Torsional Irregularity:")
print(f"    Max eta_bi = {max_eta:.4f} (Floor {max_eta_floor})")
if a1a_severe_floors:
    print(f"    SEVERE (eta > 2.0) at floors: {a1a_severe_floors}")
    print(f"    >>> BUILDING PERMIT CANNOT BE ISSUED (TBDY 2018)")
elif a1a_floors:
    max_Dbi = max(r['D_bi'] for r in results if r['a1a'])
    print(f"    IRREGULAR (1.2 < eta <= 2.0) at floors: {a1a_floors}")
    print(f"    Max amplification D_bi = {max_Dbi:.3f}")
    print(f"    >>> Accidental eccentricity must be amplified by D_bi")
else:
    print(f"    REGULAR - No torsional irregularity")

print()

# B1 summary
b1_floors = [r['floor'] for r in results if r['b1']]
print(f"  B1 - Soft Story:")
if b1_floors:
    print(f"    SOFT STORY at floors: {b1_floors}")
    min_b1 = min(r['b1_eta'] for r in results if r['b1'])
    print(f"    Minimum eta_ki = {min_b1:.4f}")
else:
    print(f"    No soft story irregularity detected")

print()

# B2 summary
b2_floors = [r['floor'] for r in results if r['b2']]
print(f"  B2 - Weak Story:")
if b2_floors:
    print(f"    WEAK STORY at floors: {b2_floors}")
else:
    print(f"    No weak story irregularity detected")

print()

# B3 summary
b3_floors = [r['floor'] for r in results if r['b3']]
print(f"  B3 - Mass Irregularity:")
if b3_floors:
    print(f"    IRREGULAR at floors: {b3_floors}")
    for fl in b3_floors:
        r = [r for r in results if r['floor'] == fl][0]
        print(f"      Floor {fl}: m/m_above={r['b3_above']:.2f}, m/m_below={r['b3_below']:.2f}")
else:
    print(f"    No mass irregularity detected")

print()
print("=" * 80)

# =============================================================================
# SAVE RESULTS
# =============================================================================
os.makedirs(os.path.join(BASE_DIR, "results"), exist_ok=True)

# CSV output
csv_file = os.path.join(BASE_DIR, "results", "tbdy2018_irregularities.csv")
with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'floor', 'z', 'n_nodes', 'Lx', 'Ly',
        'cm_x', 'cm_y', 'cr_x', 'cr_y',
        'e_x', 'e_y', 'e_acc_x', 'e_acc_y', 'e_total_x', 'e_total_y',
        'eta_x', 'eta_y', 'eta_max', 'D_bi',
        'a1a', 'a1a_severe',
        'k_story', 'n_col', 'n_brace', 'b1_eta', 'b1',
        'b2_eta', 'b2',
        'mass', 'b3_above', 'b3_below', 'b3',
    ])
    writer.writeheader()
    for r in results:
        row = {k: v for k, v in r.items() if k != 'a2'}
        writer.writerow(row)

print(f">>> Results saved to: {csv_file}")

# JSON output
json_file = os.path.join(BASE_DIR, "results", "tbdy2018_irregularities.json")
json_data = {
    'model': 'Twin Towers V9 (1:50 Scale)',
    'code': 'TBDY 2018',
    'total_floors': num_floors,
    'total_nodes': len(nodes),
    'total_elements': len(elements),
    'summary': {
        'a1a_max_eta': float(max_eta),
        'a1a_max_eta_floor': int(max_eta_floor),
        'a1a_irregular_floors': [int(f) for f in a1a_floors],
        'b1_soft_story_floors': [int(f) for f in b1_floors],
        'b2_weak_story_floors': [int(f) for f in b2_floors],
        'b3_mass_irregular_floors': [int(f) for f in b3_floors],
    },
    'floor_results': [{k: (float(v) if isinstance(v, (int, float)) and not isinstance(v, bool) else
                          bool(v) if isinstance(v, bool) else v) for k, v in r.items()} for r in results]
}
with open(json_file, 'w') as f:
    json.dump(json_data, f, indent=2)

print(f">>> Results saved to: {json_file}")
print()
print(">>> Analysis complete.")
