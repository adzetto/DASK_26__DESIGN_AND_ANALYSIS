"""
V10 MODAL ANALYSIS
==================
OpenSees modal analysis for the V10 twin tower model.
Changes from corrected analysis:
- Reads twin_position_matrix_v10.csv and twin_connectivity_matrix_v10.csv
- No shear_wall panels -- all braces are stick elements (Truss)
- Self weight updated to V10 weight (1.506 kg)

Units: m, kN, tonne, s
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

try:
    import openseespy.opensees as ops
except ImportError:
    print("ERROR: openseespy not installed. Install with: pip install openseespy")
    sys.exit(1)

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'

print("=" * 70)
print("V10 MODAL ANALYSIS")
print("=" * 70)

# 1. LOAD V10 DATA
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix_v10.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix_v10.csv')
print(f"Nodes: {len(pos_df)}, Elements: {len(conn_df)}")

# 2. MATERIAL PROPERTIES
MAKET_SCALE = 0.01  # cm -> m

E_long = 3.5e6    # kPa (3.5 GPa longitudinal)
G_balsa = 0.2e6   # kPa (0.2 GPa shear)

b_frame = 0.006   # 6mm
A_frame = b_frame ** 2                  # 3.6e-5 m^2
I_frame = b_frame ** 4 / 12            # 1.08e-10 m^4
J_frame = 0.1406 * b_frame ** 4        # torsion constant

# 3. BUILD MODEL
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x = row['x'] * MAKET_SCALE
    y = row['y'] * MAKET_SCALE
    z = row['z'] * MAKET_SCALE
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

# Fix base
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].tolist()
for nid in base_nodes:
    ops.fix(int(nid), 1, 1, 1, 1, 1, 1)
print(f"Fixed base nodes: {len(base_nodes)}")

# Geometric transformations
ops.geomTransf('Linear', 1, 0, 1, 0)  # X-beams
ops.geomTransf('Linear', 2, 1, 0, 0)  # Y-beams
ops.geomTransf('Linear', 3, 0, 1, 0)  # Vertical (columns)

# Truss material
truss_mat = 100
ops.uniaxialMaterial('Elastic', truss_mat, E_long)

# Pin (truss) element types
pin_types = {'brace_xz', 'brace_yz', 'floor_brace',
             'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top'}

n_frame = 0
n_truss = 0
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']

    p1, p2 = node_map[ni], node_map[nj]
    dx = abs(p1[0] - p2[0])
    dy = abs(p1[1] - p2[1])
    dz = abs(p1[2] - p2[2])

    if etype in pin_types:
        ops.element('Truss', eid, ni, nj, A_frame, truss_mat)
        n_truss += 1
    else:
        # Frame element
        transf = 3  # vertical default
        if dz < 0.1 * max(dx, dy, 1e-9):
            transf = 1 if dx > dy else 2
        ops.element('elasticBeamColumn', eid, ni, nj,
                    A_frame, E_long, G_balsa, J_frame, I_frame, I_frame, transf)
        n_frame += 1

print(f"Frame elements: {n_frame}, Truss elements: {n_truss}")

# 4. MASSES
total_mass = 0.0

# Floor plates
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PLATE = 1.60 / 1000  # tonne

for f in MASS_FLOORS:
    fnodes = pos_df[pos_df['floor'] == f]['node_id'].tolist()
    if fnodes:
        m = MASS_PLATE / len(fnodes)
        for nid in fnodes:
            ops.mass(int(nid), m, m, m, 0, 0, 0)
        total_mass += MASS_PLATE

# Roof plate
top_floor = int(pos_df['floor'].max())
roof_nodes = pos_df[pos_df['floor'] == top_floor]['node_id'].tolist()
MASS_ROOF = 2.22 / 1000  # tonne
if roof_nodes:
    m = MASS_ROOF / len(roof_nodes)
    for nid in roof_nodes:
        ops.mass(int(nid), m, m, m, 0, 0, 0)
    total_mass += MASS_ROOF

# Self weight (V10 = 1.506 kg)
SELF_KG = 1.506
all_nodes = pos_df['node_id'].tolist()
m_self = (SELF_KG / 1000) / len(all_nodes)
for nid in all_nodes:
    ops.mass(int(nid), m_self, m_self, m_self, 0, 0, 0)
total_mass += SELF_KG / 1000

print(f"Total mass: {total_mass * 1000:.2f} kg = {total_mass:.4f} tonne")

# 5. EIGENVALUE ANALYSIS
num_modes = 20
print(f"\nRunning eigenvalue analysis ({num_modes} modes)...")

try:
    eigenvalues = ops.eigen(num_modes)
    periods = [2 * np.pi / np.sqrt(v) for v in eigenvalues]
except Exception as e:
    print(f"Eigenvalue analysis failed: {e}")
    sys.exit(1)

# Center of mass
sum_mx, sum_my = 0.0, 0.0
for nid in all_nodes:
    x, y, z = node_map[nid]
    m_node = ops.nodeMass(nid, 1)
    sum_mx += m_node * x
    sum_my += m_node * y
cm_x = sum_mx / total_mass
cm_y = sum_my / total_mass
print(f"Center of mass: ({cm_x*100:.1f}, {cm_y*100:.1f}) cm")

# 6. RESULTS
print(f"\n{'='*80}")
print(f"{'MODE':<5} {'PERIOD (s)':<12} {'FREQ (Hz)':<12} {'X %':<8} {'Y %':<8} {'TYPE'}")
print(f"{'='*80}")

results = []
for mode_idx in range(num_modes):
    mode = mode_idx + 1
    T = periods[mode_idx]
    freq = 1.0 / T

    part_x, part_y, part_rz = 0.0, 0.0, 0.0
    gen_mass = 0.0

    for nid in all_nodes:
        x, y, z = node_map[nid]
        m = ops.nodeMass(nid, 1)
        if m <= 1e-12:
            continue

        phi = ops.nodeEigenvector(nid, mode)
        ux, uy, uz = phi[0], phi[1], phi[2]

        gen_mass += m * (ux**2 + uy**2 + uz**2)
        part_x += m * ux
        part_y += m * uy

        r_x = -(y - cm_y)
        r_y = (x - cm_x)
        part_rz += m * (ux * r_x + uy * r_y)

    if gen_mass > 1e-15:
        ratio_x = (part_x**2 / gen_mass) / total_mass * 100
        ratio_y = (part_y**2 / gen_mass) / total_mass * 100
    else:
        ratio_x, ratio_y = 0, 0

    mtype = "Local/Coupled"
    if ratio_x > 40:
        mtype = "Global Sway X"
    elif ratio_y > 40:
        mtype = "Global Sway Y"
    elif ratio_x > 10 and ratio_y > 10:
        mtype = "Diagonal Sway"
    elif ratio_x < 5 and ratio_y < 5:
        mtype = "Torsion / Anti-Symm"

    print(f"{mode:<5} {T:<12.4f} {freq:<12.2f} {ratio_x:<8.1f} {ratio_y:<8.1f} {mtype}")
    results.append({'mode': mode, 'T': T, 'freq': freq, 'X%': ratio_x, 'Y%': ratio_y, 'type': mtype})

print(f"{'='*80}")
print(f"\nT1 = {results[0]['T']:.4f} s  (V9 was 0.200 s)")
if len(results) > 1:
    print(f"T2 = {results[1]['T']:.4f} s")
if len(results) > 2:
    print(f"T3 = {results[2]['T']:.4f} s")

# Save results
results_df = pd.DataFrame(results)
results_df.to_csv(DATA_DIR / 'modal_results_v10.csv', index=False)
print(f"\nResults saved: data/modal_results_v10.csv")
