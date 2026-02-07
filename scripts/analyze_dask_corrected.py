"""
CORRECTED MODAL ANALYSIS
========================
Refined analysis with realistic Balsa properties and connectivity.

Corrections:
1. Material: Balsa is Anisotropic. 
   - E_parallel = 3.5 GPa (Columns/Beams)
   - G_modulus = 0.2 GPa (Realistic Shear for Balsa)
2. Connectivity:
   - Braces are modeled as 'Truss' (Pinned) elements, not rigid frames.
   - This prevents artificial frame-action stiffness.
3. Panels:
   - Modeled as Equivalent Struts.
   - Effective width reduced to 0.4 * Width (Validation heuristic) to account for shear lag.

Units: m, kN, tonne, s
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import openseespy.opensees as ops

# Setup
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'

print("=" * 70)
print("CORRECTED DASK MODAL ANALYSIS")
print("=" * 70)

# 1. LOAD DATA
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except FileNotFoundError:
    print("Error: Data files not found.")
    sys.exit(1)

# 2. REALISTIC MATERIAL PARAMETERS
MAKET_SCALE = 0.01

# Stiffness
E_long = 3.5e6    # 3.5 GPa (Grain Parallel - Columns)
E_trans = 0.5e6   # 0.5 GPa (Grain Perpendicular - some beams?)
G_balsa = 0.2e6   # 0.2 GPa (Shear Modulus - Low!)

# Sections
b_frame = 0.006
A_frame = b_frame**2
I_frame = b_frame**4 / 12
J_frame = 0.1406 * b_frame**4

# Panel Equivalent Strut
# Panel 3.4cm x 6cm x 3mm
# Diagonal Length L_d = sqrt(3.4^2 + 6^2) = 6.9cm
# Equivalent width w_eq. Common rule: w_eq ~ 0.25 to 0.5 * Diagonal
# Let's use w_eq = 1.7cm (half of 3.4cm width, approx 0.25*Ld)
t_panel = 0.003
w_panel_eq = 0.017 # Reduced from 0.034 to account for realistic shear field
A_panel = t_panel * w_panel_eq

# 3. OPENSEES MODEL
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

# Transformations
ops.geomTransf('Linear', 1, 0, 1, 0) # X-beams
ops.geomTransf('Linear', 2, 1, 0, 0) # Y-beams
ops.geomTransf('Linear', 3, 0, 1, 0) # Vertical

# Elements
truss_mat_tag = 100
ops.uniaxialMaterial('Elastic', truss_mat_tag, E_long) # Truss takes E_long

# Element Categories
pin_types = ['brace_xz', 'brace_yz', 'floor_brace', 'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top']
panel_types = ['shear_wall_xz', 'shear_wall_yz']

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']
    
    p1 = node_map[ni]
    p2 = node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
    
    # --- MODELING LOGIC ---
    
    # 1. PANELS & BRACES -> TRUSS ELEMENTS (Pinned)
    # This removes moment transfer at nodes, making the model more realistic (flexible)
    if etype in pin_types:
        # Standard Braces
        ops.element('Truss', eid, ni, nj, A_frame, truss_mat_tag)
        
    elif etype in panel_types:
        # Shear Wall Panels (Equivalent Strut)
        # Use A_panel (Reduced)
        ops.element('Truss', eid, ni, nj, A_panel, truss_mat_tag)
        
    else:
        # 2. FRAMES (Columns, Beams) -> ElasticBeamColumn
        transf = 3
        if dz < 0.1 * max(dx, dy):
            transf = 1 if dx > dy else 2
        
        # Use G_balsa (Low shear stiffness)
        ops.element('elasticBeamColumn', eid, ni, nj, A_frame, E_long, G_balsa, J_frame, I_frame, I_frame, transf)

# 4. MASSES
total_mass = 0
# Floor Plates
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PLATE = 1.60 / 1000
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

# Self Weight
SELF_KG = 1.4
nodes_all = pos_df['node_id'].tolist()
m_self = (SELF_KG/1000) / len(nodes_all)
for nid in nodes_all:
    ops.mass(int(nid), m_self, m_self, m_self, 0, 0, 0)
total_mass += SELF_KG/1000

print(f"Total Mass: {total_mass:.4f} tonne")

# 5. EIGENVALUE ANALYSIS & PARTICIPATION
num_modes = 8
try:
    vals = ops.eigen(num_modes)
    periods = [2*np.pi/np.sqrt(v) for v in vals]
except:
    print("Eigen Analysis Failed")
    sys.exit(1)

print(f"\n{'MODE':<4} | {'PERIOD (s)':<10} | {'FREQ (Hz)':<10} | {'PARTICIPATION %':<25} | {'TYPE'}")
print("-" * 80)

# Calculate Center of Mass
sum_mx, sum_my = 0, 0
for nid in nodes_all:
    x, y, z = node_map[nid]
    m_node = ops.nodeMass(nid, 1)
    sum_mx += m_node * x
    sum_my += m_node * y
cm_x = sum_mx / total_mass
cm_y = sum_my / total_mass

for mode_idx in range(num_modes):
    mode = mode_idx + 1
    T = periods[mode_idx]
    freq = 1.0/T
    
    # Modal Participation
    part_x, part_y, part_rz = 0.0, 0.0, 0.0
    gen_mass = 0.0
    
    for nid in nodes_all:
        x, y, z = node_map[nid]
        m = ops.nodeMass(nid, 1)
        if m <= 1e-9: continue
        
        phi = ops.nodeEigenvector(nid, mode) # ux, uy, uz, rx, ry, rz
        ux, uy = phi[0], phi[1]
        
        gen_mass += m * (ux**2 + uy**2 + phi[2]**2) # Simplified
        
        part_x += m * ux
        part_y += m * uy
        
        # Torsion
        r_x = -(y - cm_y)
        r_y = (x - cm_x)
        part_rz += m * (ux * r_x + uy * r_y)

    ratio_x = (part_x**2 / gen_mass) / total_mass * 100
    ratio_y = (part_y**2 / gen_mass) / total_mass * 100
    
    # Classification
    mtype = "Local/Coupled"
    if ratio_x > 40: mtype = "Global Sway X"
    elif ratio_y > 40: mtype = "Global Sway Y"
    elif ratio_x > 10 and ratio_y > 10: mtype = "Diagonal Sway"
    elif ratio_x < 5 and ratio_y < 5: mtype = "Torsion / Anti-Symm"

    print(f"{mode:<4} | {T:<10.4f} | {freq:<10.2f} | X:{ratio_x:.1f}%  Y:{ratio_y:.1f}%        | {mtype}")

print("-" * 80)
print("Analysis Note:")
print("- If periods are still < 0.06s, the structure is naturally very stiff.")
print("- Truss elements used for braces (Pin connections).")
print("- Reduced Shear Modulus used for Balsa.")
