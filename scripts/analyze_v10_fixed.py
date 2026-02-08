"""
V10 MODAL ANALYSIS - FIXED MASS ACCUMULATION
=============================================
Bug fix: ops.mass() replaces (doesn't add) on repeated calls.
Must accumulate all mass per node, then call ops.mass() once.

Units: m, kN, tonne, s
"""
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import openseespy.opensees as ops
from collections import defaultdict

DATA = Path(__file__).parent.parent / 'data'
pos_df = pd.read_csv(DATA / 'twin_position_matrix_v10.csv')
conn_df = pd.read_csv(DATA / 'twin_connectivity_matrix_v10.csv')

pos_df['node_id'] = pos_df['node_id'].astype(int)
conn_df['node_i'] = conn_df['node_i'].astype(int)
conn_df['node_j'] = conn_df['node_j'].astype(int)
conn_df['element_id'] = conn_df['element_id'].astype(int)

print("=" * 70)
print("V10 MODAL ANALYSIS (FIXED)")
print("=" * 70)

S = 0.01
E_long = 3.5e6    # kPa
G_balsa = 0.2e6   # kPa
b = 0.006
A = b**2
I = b**4 / 12
J = 0.1406 * b**4

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

print(f"Nodes: {len(pos_df)}, Elements: {len(conn_df)}, Base fixed: {len(base_nodes)}")

ops.geomTransf('Linear', 1, 0, 1, 0)
ops.geomTransf('Linear', 2, 1, 0, 0)
ops.geomTransf('Linear', 3, 0, 1, 0)
ops.uniaxialMaterial('Elastic', 100, E_long)

pin_types = {'brace_xz', 'brace_yz', 'floor_brace',
             'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top'}

n_frame, n_truss = 0, 0
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    et = row['element_type']
    p1, p2 = node_map[ni], node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])

    if et in pin_types:
        ops.element('Truss', eid, ni, nj, A, 100)
        n_truss += 1
    else:
        t = 3
        if dz < 0.1 * max(dx, dy, 1e-9):
            t = 1 if dx > dy else 2
        ops.element('elasticBeamColumn', eid, ni, nj,
                    A, E_long, G_balsa, J, I, I, t)
        n_frame += 1

print(f"Frame: {n_frame}, Truss: {n_truss}")

# ============================================
# MASS: Accumulate first, then set ONCE
# ============================================
node_mass = defaultdict(float)
all_int_nodes = [int(n) for n in pos_df['node_id'].tolist()]

# Floor plates: 1.60 kg each at floors 3,6,...,24
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
total_plate_mass = 0.0
for f in MASS_FLOORS:
    fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
    m = 1.60 / 1000 / len(fnodes)
    for nid in fnodes:
        node_mass[nid] += m
    total_plate_mass += 1.60 / 1000

# Roof plate: 2.22 kg
tf = int(pos_df['floor'].max())
rnodes = [int(n) for n in pos_df[pos_df['floor'] == tf]['node_id'].tolist()]
mr = 2.22 / 1000 / len(rnodes)
for nid in rnodes:
    node_mass[nid] += mr
total_roof_mass = 2.22 / 1000

# Self weight: distributed to all nodes
SELF_KG = 1.149
ms = SELF_KG / 1000 / len(all_int_nodes)
for nid in all_int_nodes:
    node_mass[nid] += ms

total_mass = total_plate_mass + total_roof_mass + SELF_KG / 1000

# Now set mass ONCE per node
for nid, m in node_mass.items():
    ops.mass(nid, m, m, m, 0, 0, 0)

print(f"\nMass breakdown:")
print(f"  Floor plates: {total_plate_mass*1000:.2f} kg ({len(MASS_FLOORS)} floors × 1.60 kg)")
print(f"  Roof plate:   {total_roof_mass*1000:.2f} kg")
print(f"  Self weight:  {SELF_KG:.3f} kg")
print(f"  TOTAL:        {total_mass*1000:.2f} kg = {total_mass:.4f} tonne")

# Verify
sm_check = sum(ops.nodeMass(nid, 1) for nid in all_int_nodes)
print(f"  Verify sum:   {sm_check*1000:.2f} kg")

# Center of mass
smx, smy, smz = 0, 0, 0
for nid in all_int_nodes:
    x, y, z = node_map[nid]
    m = ops.nodeMass(nid, 1)
    smx += m*x; smy += m*y; smz += m*z
cmx = smx/sm_check; cmy = smy/sm_check; cmz = smz/sm_check
print(f"  CM: ({cmx*100:.1f}, {cmy*100:.1f}, {cmz*100:.1f}) cm")

# ============================================
# EIGENVALUE ANALYSIS
# ============================================
num_modes = 12
print(f"\nRunning eigenvalue analysis ({num_modes} modes)...")

try:
    vals = ops.eigen(num_modes)
    periods = [2*np.pi/np.sqrt(v) for v in vals]
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)

free_nodes = [int(n) for n in pos_df[pos_df['floor'] > 0]['node_id'].tolist()]

print(f"\n{'='*80}")
print(f"{'Mode':<5} {'T (s)':<12} {'f (Hz)':<12} {'X %':<8} {'Y %':<8} {'Type'}")
print(f"{'='*80}")

results = []
for mi in range(num_modes):
    mode = mi + 1
    T = periods[mi]
    freq = 1.0 / T

    px, py = 0.0, 0.0
    gm = 0.0

    for nid in free_nodes:
        m = ops.nodeMass(nid, 1)
        if m < 1e-15: continue
        phi = ops.nodeEigenvector(nid, mode)
        ux, uy, uz = phi[0], phi[1], phi[2]
        gm += m * (ux**2 + uy**2 + uz**2)
        px += m * ux
        py += m * uy

    if gm > 1e-15:
        rx = (px**2 / gm) / total_mass * 100
        ry = (py**2 / gm) / total_mass * 100
    else:
        rx, ry = 0, 0

    mt = 'Local/Coupled'
    if rx > 40: mt = 'SWAY X'
    elif ry > 40: mt = 'SWAY Y'
    elif rx > 10 and ry > 10: mt = 'Diagonal'
    elif rx > 10: mt = 'Sway X (moderate)'
    elif ry > 10: mt = 'Sway Y (moderate)'
    elif rx < 5 and ry < 5: mt = 'Torsion/Local'

    print(f"{mode:<5} {T:<12.4f} {freq:<12.2f} {rx:<8.1f} {ry:<8.1f} {mt}")
    results.append({'mode': mode, 'T': T, 'freq': freq, 'X%': rx, 'Y%': ry, 'type': mt})

print(f"{'='*80}")
print(f"\n*** T1 = {results[0]['T']:.4f} s  (V9 was 0.200 s) ***")
if len(results) > 1: print(f"*** T2 = {results[1]['T']:.4f} s ***")
if len(results) > 2: print(f"*** T3 = {results[2]['T']:.4f} s ***")

# Save
pd.DataFrame(results).to_csv(DATA / 'modal_results_v10.csv', index=False)
print(f"\nResults saved: data/modal_results_v10.csv")
