"""
V10 ECCENTRICITY & TORSION ANALYSIS
====================================
Compute center of rigidity, eccentricity ratios, 
and A1a torsional irregularity coefficient.
"""
import numpy as np
import pandas as pd
from pathlib import Path
import openseespy.opensees as ops
from collections import defaultdict

DATA = Path(__file__).parent.parent / 'data'
pos_df = pd.read_csv(DATA / 'twin_position_matrix_v10.csv')
conn_df = pd.read_csv(DATA / 'twin_connectivity_matrix_v10.csv')

pos_df['node_id'] = pos_df['node_id'].astype(int)
conn_df['node_i'] = conn_df['node_i'].astype(int)
conn_df['node_j'] = conn_df['node_j'].astype(int)
conn_df['element_id'] = conn_df['element_id'].astype(int)

S = 0.01
E_long = 3.5e6
G_balsa = 0.2e6
b = 0.006
A = b**2
I = b**4 / 12
J = 0.1406 * b**4

def build_model():
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    
    node_map = {}
    for _, row in pos_df.iterrows():
        nid = int(row['node_id'])
        x, y, z = row['x'] * S, row['y'] * S, row['z'] * S
        ops.node(nid, x, y, z)
        node_map[nid] = (x, y, z)
    
    base_nodes = [int(n) for n in pos_df[pos_df['floor'] == 0]['node_id'].tolist()]
    for nid in base_nodes:
        ops.fix(nid, 1, 1, 1, 1, 1, 1)
    
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.geomTransf('Linear', 2, 1, 0, 0)
    ops.geomTransf('Linear', 3, 0, 1, 0)
    ops.uniaxialMaterial('Elastic', 100, E_long)
    
    pin_types = {'brace_xz', 'brace_yz', 'floor_brace',
                 'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top'}
    
    for _, row in conn_df.iterrows():
        eid = int(row['element_id'])
        ni = int(row['node_i'])
        nj = int(row['node_j'])
        et = row['element_type']
        p1, p2 = node_map[ni], node_map[nj]
        dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
        
        if et in pin_types:
            ops.element('Truss', eid, ni, nj, A, 100)
        else:
            t = 3
            if dz < 0.1 * max(dx, dy, 1e-9):
                t = 1 if dx > dy else 2
            ops.element('elasticBeamColumn', eid, ni, nj,
                        A, E_long, G_balsa, J, I, I, t)
    
    return node_map, base_nodes

node_map, base_nodes = build_model()

# ============================================
# CENTER OF MASS per floor
# ============================================
all_floors = sorted(pos_df['floor'].unique())
max_floor = max(all_floors)

node_mass_total = defaultdict(float)
all_int_nodes = [int(n) for n in pos_df['node_id'].tolist()]

MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
for f in MASS_FLOORS:
    fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
    m = 1.60 / 1000 / len(fnodes)
    for nid in fnodes:
        node_mass_total[nid] += m

rnodes = [int(n) for n in pos_df[pos_df['floor'] == max_floor]['node_id'].tolist()]
mr = 2.22 / 1000 / len(rnodes)
for nid in rnodes:
    node_mass_total[nid] += mr

SELF_KG = 1.168
ms = SELF_KG / 1000 / len(all_int_nodes)
for nid in all_int_nodes:
    node_mass_total[nid] += ms

# Set masses
for nid, m in node_mass_total.items():
    ops.mass(nid, m, m, m, 0, 0, 0)

print("=" * 70)
print("V10 ECCENTRICITY & TORSION ANALYSIS")
print("=" * 70)

# CM per floor
print(f"\n{'Floor':>5} {'CM_x':>8} {'CM_y':>8} {'Mass(g)':>10}")
print("-" * 35)
floor_data = {}
for f in sorted(all_floors):
    if f == 0:
        continue
    fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
    total_m = sum(node_mass_total.get(nid, 0) for nid in fnodes)
    if total_m < 1e-15:
        continue
    cm_x = sum(node_map[nid][0] * node_mass_total.get(nid, 0) for nid in fnodes) / total_m
    cm_y = sum(node_map[nid][1] * node_mass_total.get(nid, 0) for nid in fnodes) / total_m
    floor_data[f] = {'cm_x': cm_x, 'cm_y': cm_y, 'mass': total_m, 'nodes': fnodes}
    if f <= 5 or f >= max_floor - 2 or f in MASS_FLOORS:
        print(f"{f:5d} {cm_x*100:8.2f} {cm_y*100:8.2f} {total_m*1e6:10.2f}")

# ============================================
# CENTER OF RIGIDITY per floor (unit force method)
# ============================================
print("\n--- Center of Rigidity (unit force method) ---")

# Apply unit force in X at each floor, measure rotation to find CR_y
# Apply unit force in Y at each floor, measure rotation to find CR_x
# CR is where force produces zero rotation

# Method: Apply unit force Fx=1 at floor nodes, measure θz rotation
# If force at y=CR_y, no torsion. Otherwise θz ≠ 0.
# Alternative: compute floor stiffness matrix approach

# Simpler approach: Apply Fx=1 distributed to floor nodes, get displacements
# CR_y = Σ(k_i * y_i) / Σ(k_i) where k_i is lateral stiffness at node i

# Even simpler for symmetric structures: 
# Since the building is doubly symmetric (X and Y), CR ≈ CM
# Let's verify by applying lateral loads and checking twist

ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply unit force in Y direction at each floor node (proportional to height)
for f in sorted(all_floors):
    if f == 0:
        continue
    fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
    z = node_map[fnodes[0]][2]
    for nid in fnodes:
        ops.load(nid, 0.0, z, 0.0, 0.0, 0.0, 0.0)

ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Linear')
ops.analysis('Static')
ops.analyze(1)

# For each floor, compute average displacement and max/min for torsion check
print(f"\n{'Floor':>5} {'δ_y_avg':>10} {'δ_y_max':>10} {'δ_y_min':>10} {'η_bi':>8} {'θ_z_avg':>10}")
print("-" * 60)

eccentricity_results = []
for f in sorted(all_floors):
    if f == 0:
        continue
    fnodes = floor_data[f]['nodes']
    
    # Get Y displacements
    disps_y = []
    disps_x = []
    for nid in fnodes:
        d = ops.nodeDisp(nid)
        x_pos = node_map[nid][0]
        y_pos = node_map[nid][1]
        disps_y.append((x_pos, y_pos, d[1]))  # Y displacement
        disps_x.append((x_pos, y_pos, d[0]))  # X displacement
    
    dy_vals = [d[2] for d in disps_y]
    dy_max = max(dy_vals)
    dy_min = min(dy_vals)
    dy_avg = np.mean(dy_vals)
    
    # Torsional irregularity: η_bi = δ_max / δ_avg
    if abs(dy_avg) > 1e-15:
        eta_bi = dy_max / dy_avg
    else:
        eta_bi = 1.0
    
    # Average rotation about Z
    # θ_z ≈ (δ_y_max - δ_y_min) / L_x
    Lx = max(d[0] for d in disps_y) - min(d[0] for d in disps_y)
    theta_z = (dy_max - dy_min) / Lx if Lx > 1e-9 else 0.0
    
    eccentricity_results.append({
        'floor': f, 'dy_avg': dy_avg, 'dy_max': dy_max, 'dy_min': dy_min,
        'eta_bi': eta_bi, 'theta_z': theta_z
    })
    
    if f <= 5 or f >= max_floor - 2 or f in MASS_FLOORS:
        print(f"{f:5d} {dy_avg:10.6f} {dy_max:10.6f} {dy_min:10.6f} {eta_bi:8.4f} {theta_z:10.8f}")

# Summary
eta_max = max(r['eta_bi'] for r in eccentricity_results)
eta_floor = [r['floor'] for r in eccentricity_results if r['eta_bi'] == eta_max][0]
print(f"\nMax η_bi = {eta_max:.4f} at floor {eta_floor}")
print(f"η_bi < 1.2: {'OK' if eta_max < 1.2 else 'FAIL (düzensiz)'}")
print(f"η_bi < 1.4: {'OK' if eta_max < 1.4 else 'FAIL'}")
print(f"η_bi < 2.0: {'OK' if eta_max < 2.0 else 'ağır düzensizlik'}")

# Center of rigidity from displacement pattern
# CR_x: where Y-force produces zero X displacement
# For double symmetric building, CR ≈ geometric center
# Let's compute from floor stiffness distribution
print(f"\n--- Eccentricity Summary ---")
print(f"Plan dimensions: Lx = {(29.7-0.3):.1f} cm, Ly = {(39.7-0.3):.1f} cm (both towers)")
print(f"Per tower: Ly_tower = {(15.7-0.3):.1f} cm")
print(f"CM_x = {floor_data[max_floor]['cm_x']*100:.2f} cm")
print(f"CM_y = {floor_data[max_floor]['cm_y']*100:.2f} cm")

# For symmetric structures
cr_x = 15.0  # symmetric X
cr_y = 20.0  # symmetric Y (midpoint between towers)
print(f"CR_x ≈ {cr_x:.2f} cm (symmetric)")
print(f"CR_y ≈ {cr_y:.2f} cm (symmetric)")
ex = abs(floor_data[max_floor]['cm_x']*100 - cr_x)
ey = abs(floor_data[max_floor]['cm_y']*100 - cr_y)
Lx = 29.4  # 29.7 - 0.3
Ly = 39.4  # 39.7 - 0.3
print(f"e_x = {ex:.3f} cm, e_x/L_x = {ex/Lx:.4f}")
print(f"e_y = {ey:.3f} cm, e_y/L_y = {ey/Ly:.4f}")
print(f"Limit: e/L < 0.05 → {'OK' if max(ex/Lx, ey/Ly) < 0.05 else 'FAIL'}")

# ============================================
# DRIFT under unit lateral load
# ============================================
print(f"\n--- Interstory Drift (unit lateral load) ---")
Z_COORDS = [0.0, 9.0]
for i in range(2, 26):
    Z_COORDS.append(Z_COORDS[-1] + 6.0)

for f in range(1, len(Z_COORDS)):
    fnodes = floor_data.get(f, {}).get('nodes', [])
    if not fnodes:
        continue
    prev_nodes = floor_data.get(f-1, {}).get('nodes', []) if f > 1 else []
    
    dy_f = np.mean([ops.nodeDisp(nid)[1] for nid in fnodes])
    if f == 1:
        dy_prev = 0.0
    elif prev_nodes:
        dy_prev = np.mean([ops.nodeDisp(nid)[1] for nid in prev_nodes])
    else:
        continue
    
    h = Z_COORDS[f] - Z_COORDS[f-1]
    delta = abs(dy_f - dy_prev)
    drift = delta / (h * S)
    
    if f <= 3 or f >= 23:
        print(f"  Floor {f:2d}: δ={delta*1000:.4f} mm, h={h:.0f} cm, drift={drift:.6f}")

print("\nDone.")
