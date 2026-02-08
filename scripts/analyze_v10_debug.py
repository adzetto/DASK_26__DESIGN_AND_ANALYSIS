"""
V10 MODAL ANALYSIS - DEBUG VERSION
"""
import numpy as np
import pandas as pd
from pathlib import Path
import sys
import openseespy.opensees as ops

DATA = Path(__file__).parent.parent / 'data'
pos_df = pd.read_csv(DATA / 'twin_position_matrix_v10.csv')
conn_df = pd.read_csv(DATA / 'twin_connectivity_matrix_v10.csv')

# Ensure integer node IDs
pos_df['node_id'] = pos_df['node_id'].astype(int)
conn_df['node_i'] = conn_df['node_i'].astype(int)
conn_df['node_j'] = conn_df['node_j'].astype(int)
conn_df['element_id'] = conn_df['element_id'].astype(int)

S = 0.01  # cm -> m
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

# Fix base
base_nodes = [int(n) for n in pos_df[pos_df['floor'] == 0]['node_id'].tolist()]
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)
print(f"Nodes: {len(pos_df)}, Base fixed: {len(base_nodes)}")

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

# Mass
total_mass = 0.0
all_int_nodes = [int(n) for n in pos_df['node_id'].tolist()]

# Floor plates
for f in [3, 6, 9, 12, 15, 18, 21, 24]:
    fnodes = [int(n) for n in pos_df[pos_df['floor'] == f]['node_id'].tolist()]
    m = 1.60 / 1000 / len(fnodes)
    for nid in fnodes:
        ops.mass(nid, m, m, m, 0, 0, 0)
    total_mass += 1.60 / 1000

# Roof
tf = int(pos_df['floor'].max())
rnodes = [int(n) for n in pos_df[pos_df['floor'] == tf]['node_id'].tolist()]
mr = 2.22 / 1000 / len(rnodes)
for nid in rnodes:
    ops.mass(nid, mr, mr, mr, 0, 0, 0)
total_mass += 2.22 / 1000

# Self weight
ms = 1.506 / 1000 / len(all_int_nodes)
for nid in all_int_nodes:
    ops.mass(nid, ms, ms, ms, 0, 0, 0)
total_mass += 1.506 / 1000

print(f"Total mass: {total_mass*1000:.2f} kg")

# DEBUG: Check mass on a few nodes
for test_nid in [0, 1, 64, 128, 192]:
    m_test = ops.nodeMass(test_nid, 1)
    x, y, z = node_map[test_nid]
    print(f"  Node {test_nid}: mass={m_test:.6e}, pos=({x*100:.1f},{y*100:.1f},{z*100:.1f}) cm")

# DEBUG: Center of mass
smx, smy, smz, sm_total = 0, 0, 0, 0
for nid in all_int_nodes:
    x, y, z = node_map[nid]
    m = ops.nodeMass(nid, 1)
    smx += m * x
    smy += m * y
    smz += m * z
    sm_total += m
print(f"\nMass from nodeMass sum: {sm_total*1000:.2f} kg (expected: {total_mass*1000:.2f})")
if sm_total > 0:
    cmx = smx / sm_total
    cmy = smy / sm_total
    cmz = smz / sm_total
    print(f"Center of mass: ({cmx*100:.1f}, {cmy*100:.1f}, {cmz*100:.1f}) cm")

# Eigen
num_modes = 12
print(f"\nEigen analysis ({num_modes} modes)...")
try:
    vals = ops.eigen(num_modes)
except Exception as e:
    print(f"FAILED: {e}")
    sys.exit(1)

periods = [2*np.pi/np.sqrt(v) for v in vals]

# Free (non-base) nodes only for participation
free_nodes = [int(n) for n in pos_df[pos_df['floor'] > 0]['node_id'].tolist()]
print(f"Free nodes: {len(free_nodes)}")

print(f"\n{'Mode':<5} {'T(s)':<10} {'f(Hz)':<10} {'X%':<8} {'Y%':<8} {'Type'}")
print("-" * 55)

for mi in range(num_modes):
    mode = mi + 1
    T = periods[mi]
    f = 1.0 / T

    px, py = 0.0, 0.0
    gm = 0.0
    max_ux, max_uy = 0.0, 0.0

    for nid in free_nodes:
        m = ops.nodeMass(nid, 1)
        if m < 1e-15:
            continue
        phi = ops.nodeEigenvector(nid, mode)
        ux, uy, uz = phi[0], phi[1], phi[2]
        gm += m * (ux**2 + uy**2 + uz**2)
        px += m * ux
        py += m * uy
        if abs(ux) > max_ux: max_ux = abs(ux)
        if abs(uy) > max_uy: max_uy = abs(uy)

    if gm > 1e-15:
        rx = (px**2 / gm) / total_mass * 100
        ry = (py**2 / gm) / total_mass * 100
    else:
        rx, ry = 0, 0

    mt = 'Local'
    if rx > 40: mt = 'Sway X'
    elif ry > 40: mt = 'Sway Y'
    elif rx > 10 and ry > 10: mt = 'Diagonal'
    elif rx < 5 and ry < 5: mt = 'Tors/Local'

    extra = ""
    if mi < 5:
        extra = f"  max_ux={max_ux:.3e} max_uy={max_uy:.3e}"
    print(f"{mode:<5} {T:<10.4f} {f:<10.2f} {rx:<8.1f} {ry:<8.1f} {mt}{extra}")

print("-" * 55)
print(f"T1={periods[0]:.4f}s  T2={periods[1]:.4f}s  T3={periods[2]:.4f}s")
