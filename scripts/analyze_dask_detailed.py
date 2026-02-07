"""
DETAILED MODAL ANALYSIS (Modes 1-8)
===================================
Performs eigenvalue analysis and computes Modal Participating Mass Ratios
to identify critical directions (X, Y, Rotation) for each mode.

Units: m, kN, tonne, s
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

# Setup
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'

print("=" * 70)
print("DETAILED DASK MODAL ANALYSIS (Modes 1-8)")
print("=" * 70)

# 1. LOAD DATA
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except FileNotFoundError:
    print("Error: Data files not found.")
    sys.exit(1)

# 2. PHYSICAL PARAMETERS
MAKET_SCALE = 0.01
E_kPa = 3.5e6 # 3.5 GPa
G_kPa = E_kPa / 2.6

# Sections
b_frame = 0.006
A_frame = b_frame**2
I_frame = b_frame**4 / 12
J_frame = 0.1406 * b_frame**4

# Panels (3.4cm wide)
t_panel = 0.003
w_panel = 0.034
A_panel = t_panel * w_panel
I_panel = (w_panel * t_panel**3) / 12
J_panel = 0.1406 * t_panel**4

# 3. OPENSEES MODEL
import openseespy.opensees as ops
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Nodes
node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x']*MAKET_SCALE, row['y']*MAKET_SCALE, row['z']*MAKET_SCALE
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

# Fix Base
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].tolist()
for nid in base_nodes:
    ops.fix(int(nid), 1, 1, 1, 1, 1, 1)

# Elements
ops.geomTransf('Linear', 1, 0, 1, 0) # X-beams
ops.geomTransf('Linear', 2, 1, 0, 0) # Y-beams
ops.geomTransf('Linear', 3, 0, 1, 0) # Vertical

shear_types = ['shear_wall_xz', 'shear_wall_yz']

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']
    
    p1 = node_map[ni]
    p2 = node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
    
    transf = 3
    if dz < 0.1 * max(dx, dy):
        transf = 1 if dx > dy else 2
        
    if etype in shear_types:
        A, I, J = A_panel, I_panel, J_panel
    else:
        A, I, J = A_frame, I_frame, J_frame
        
    ops.element('elasticBeamColumn', eid, ni, nj, A, E_kPa, G_kPa, J, I, I, transf)

# 4. MASSES
total_mass = 0
# Floor Plates
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PLATE = 1.60 / 1000 # tonne
for f in MASS_FLOORS:
    nodes = pos_df[pos_df['floor'] == f]['node_id'].tolist()
    if nodes:
        m = MASS_PLATE / len(nodes)
        for nid in nodes:
            ops.mass(int(nid), m, m, m, 0, 0, 0)
        total_mass += MASS_PLATE

# Roof Plate
top_floor = pos_df['floor'].max()
nodes = pos_df[pos_df['floor'] == top_floor]['node_id'].tolist()
MASS_ROOF = 2.22 / 1000
if nodes:
    m = MASS_ROOF / len(nodes)
    for nid in nodes:
        ops.mass(int(nid), m, m, m, 0, 0, 0)
    total_mass += MASS_ROOF

# Self Weight (Approx 1.4kg distributed)
SELF_KG = 1.4
nodes_all = pos_df['node_id'].tolist()
m_self = (SELF_KG/1000) / len(nodes_all)
for nid in nodes_all:
    ops.mass(int(nid), m_self, m_self, m_self, 0, 0, 0)
total_mass += SELF_KG/1000

print(f"Total Mass: {total_mass:.4f} tonne")

# 5. EIGENVALUE ANALYSIS (8 MODES)
num_modes = 8
vals = ops.eigen(num_modes)
periods = [2*np.pi/np.sqrt(v) for v in vals]

# 6. MODAL PARTICIPATION
# Calculate participation factors manually
# Gamma_i = (phi_i^T * M * r) / (phi_i^T * M * phi_i)
# We need M * phi_i first.
# OpenSees 'nodeEigenvector' gives phi_i at a node.
# Mass is diagonal.

print(f"\n{'MODE':<4} | {'PERIOD (s)':<10} | {'FREQ (Hz)':<10} | {'CRITICAL DIRECTION':<20} | {'DETAILS'}")
print("-" * 75)

for mode_idx in range(num_modes):
    mode = mode_idx + 1
    T = periods[mode_idx]
    freq = 1.0/T
    
    # Calculate participation vectors
    L_x, L_y, L_rz = 0.0, 0.0, 0.0
    M_eff = 0.0 # Generalized mass term (denominator)
    
    # Iterate all nodes to sum up
    # Note: Rotational mass is 0 in our lumped model, so only translational M contributes to Generalized Mass
    # but we check X, Y translations.
    
    # Center of Mass approx for Rz calculation?
    # Let's assume (15cm, 20cm) roughly center? 
    # Better: Sum (m * x), Sum (m * y) / Total M
    # But for participation, we need rigid body vector 'r'.
    # r_x = [1, 0, 0...] at all nodes
    # r_y = [0, 1, 0...] at all nodes
    # r_rz = [-y, x, 0...] relative to Center of Rigidity/Mass
    
    # Center of Mass Calculation
    sum_mx, sum_my = 0, 0
    for nid in nodes_all:
        x, y, z = node_map[nid]
        # Get mass at node (nodeMass returns list of 6)
        m_node = ops.nodeMass(nid, 1) # x-mass
        sum_mx += m_node * x
        sum_my += m_node * y
    
    cm_x = sum_mx / total_mass
    cm_y = sum_my / total_mass
    
    gen_mass_denom = 0.0
    
    part_x = 0.0
    part_y = 0.0
    part_rz = 0.0
    
    for nid in nodes_all:
        x, y, z = node_map[nid]
        m = ops.nodeMass(nid, 1)
        if m <= 1e-9: continue
        
        # Eigenvector
        phi = ops.nodeEigenvector(nid, mode) # [ux, uy, uz, rx, ry, rz]
        ux, uy, rz = phi[0], phi[1], phi[5]
        
        # Denominator: phi^T * M * phi
        gen_mass_denom += m * (ux**2 + uy**2 + phi[2]**2)
        
        # Numerators: phi^T * M * r
        part_x += m * ux * 1.0
        part_y += m * uy * 1.0
        
        # Torsion r = (-y, x) relative to CM
        r_rot_x = -(y - cm_y)
        r_rot_y = (x - cm_x)
        part_rz += m * (ux * r_rot_x + uy * r_rot_y) # Simplified Rz participation
        
    # Effective Modal Mass ratios
    # M_eff_i = L_i^2 / M_gen
    ratio_x = (part_x**2 / gen_mass_denom) / total_mass * 100
    ratio_y = (part_y**2 / gen_mass_denom) / total_mass * 100
    # Rotation mass unit is different (moment of inertia), but relative magnitude helps
    # Normalize Rz by a characteristic dimension to compare? Or just look at raw magnitude?
    # Standard practice: Effective Inertia. Let's just look at X vs Y vs Mixed.
    
    direction = "MIXED/TORSION"
    if ratio_x > 50: direction = "X-TRANSLATION"
    elif ratio_y > 50: direction = "Y-TRANSLATION"
    elif ratio_x > 20 and ratio_y > 20: direction = "DIAGONAL/MIXED"
    
    # Check for pure torsion (low translation)
    if ratio_x < 5 and ratio_y < 5:
        direction = "PURE TORSION (Rz)"

    print(f"{mode:<4} | {T:<10.4f} | {freq:<10.2f} | {direction:<20} | Ux:{ratio_x:.1f}% Uy:{ratio_y:.1f}%")

print("-" * 75)
print("ANALYSIS COMPLETE")
