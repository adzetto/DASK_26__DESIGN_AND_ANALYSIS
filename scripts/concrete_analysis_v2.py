"""
CONCRETE MODEL ANALYSIS V2
==========================
- Geometry Scale: 1:20 of Prototype (153m -> 7.65m).
- Sections: 30cm x 30cm Concrete.
- Mass: Self-weight + Scaled Point Masses (15kg -> ~1.9 tonnes).
- Damping: 5% Rayleigh.

Objective: detailed modal analysis with 'realistic' concrete parameters.
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
print("CONCRETE MODEL ANALYSIS V2 (1:20 Scale)")
print("=" * 70)

# 1. LOAD DATA
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except FileNotFoundError:
    print("Error: Data files not found.")
    sys.exit(1)

# 2. SCALING PARAMETERS
# ---------------------
# Length Scale: 1:20 relative to 153m real building.
# Data is 1:100 (153 units = 1.53m).
# Target is 7.65m.
# Factor K: 153.0 * K = 7.65 => K = 0.05
GEO_SCALE = 0.05 

# Mass Scaling (Volume): S_L^3
# Balsa Model Scale (1:100) vs Concrete Model (1:20)
# Ratio = 5.
# Mass Scale = 5^3 = 125.
MASS_SCALE = 125.0

# Material: Concrete C30
E_conc = 30.0e6  # 30 GPa = 30,000,000 kPa
G_conc = E_conc / (2 * (1 + 0.2)) # nu = 0.2
Rho_conc = 2.5   # tonne/m3

# Sections: 30cm x 30cm
b_col = 0.3  # m
h_col = 0.3  # m
A_col = b_col * h_col
I_col = (b_col * h_col**3) / 12
J_col = 0.1406 * b_col**4

# Panels (Walls): Scaled to 15cm thick Concrete
t_wall = 0.15 # 15cm
# Width scales with geometry (3.4cm * 0.05 -> 0.0017m?? NO)
# Data units are cm.
# 3.4 (data) * 0.05 (scale) = 0.17 m = 17cm.
w_panel_conc = 3.4 * GEO_SCALE # 0.17 m
A_panel_conc = t_wall * w_panel_conc

print(f"Geometry Height: {153*GEO_SCALE:.2f} m")
print(f"Column Section:  {b_col}m x {h_col}m")
print(f"Wall Section:    {t_wall}m thick x {w_panel_conc:.2f}m wide")
print(f"Point Mass Scale: x{MASS_SCALE}")

# 3. OPENSEES MODEL
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Nodes
node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x']*GEO_SCALE, row['y']*GEO_SCALE, row['z']*GEO_SCALE
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

# Fix Base
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].tolist()
for nid in base_nodes:
    ops.fix(int(nid), 1, 1, 1, 1, 1, 1)

# Transformation
ops.geomTransf('Linear', 1, 0, 1, 0)
ops.geomTransf('Linear', 2, 1, 0, 0)
ops.geomTransf('Linear', 3, 0, 1, 0)

# Material
ops.uniaxialMaterial('Elastic', 1, E_conc)

# Elements
pin_types = ['brace_xz', 'brace_yz', 'floor_brace', 'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top']
panel_types = ['shear_wall_xz', 'shear_wall_yz']

elem_masses = {}

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']
    
    p1, p2 = node_map[ni], node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
    L = np.sqrt(dx**2 + dy**2 + dz**2)
    
    if etype in panel_types:
        # Concrete Wall (Truss)
        ops.element('Truss', eid, ni, nj, A_panel_conc, 1)
        m = A_panel_conc * L * Rho_conc
    elif etype in pin_types:
        # Concrete Brace (Truss 20x20cm)
        A_brace = 0.2*0.2
        ops.element('Truss', eid, ni, nj, A_brace, 1)
        m = A_brace * L * Rho_conc
    else:
        # Frame 30x30cm
        transf = 3
        if dz < 0.1 * max(dx, dy): transf = 1 if dx > dy else 2
        # Use elasticBeamColumn with mass density
        m_dens = A_col * Rho_conc
        ops.element('elasticBeamColumn', eid, ni, nj, A_col, E_conc, G_conc, J_col, I_col, I_col, transf, '-mass', m_dens)
        m = 0 # Handled by element

    if m > 0:
        if ni not in elem_masses: elem_masses[ni] = 0
        if nj not in elem_masses: elem_masses[nj] = 0
        elem_masses[ni] += m/2
        elem_masses[nj] += m/2

# Apply Truss Masses
for nid, m in elem_masses.items():
    ops.mass(nid, m, m, m, 0,0,0)

# 4. APPLY POINT MASSES (Scaled)
# Balsa: 1.6kg plates. Scaled x125 => 200 kg = 0.2 tonne
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
M_PLATE = 1.60 / 1000 * MASS_SCALE
for f in MASS_FLOORS:
    nodes = pos_df[pos_df['floor'] == f]['node_id'].tolist()
    if nodes:
        m_node = M_PLATE / len(nodes)
        for nid in nodes:
            ops.mass(int(nid), m_node, m_node, m_node, 0,0,0)

# Roof Mass
top_floor = pos_df['floor'].max()
nodes = pos_df[pos_df['floor'] == top_floor]['node_id'].tolist()
M_ROOF = 2.22 / 1000 * MASS_SCALE
if nodes:
    m_node = M_ROOF / len(nodes)
    for nid in nodes:
        ops.mass(int(nid), m_node, m_node, m_node, 0,0,0)

print(f"Added Mass per Plate: {M_PLATE*1000:.1f} kg ({M_PLATE:.3f} t)")
print(f"Added Mass Roof:      {M_ROOF*1000:.1f} kg ({M_ROOF:.3f} t)")

# 5. EIGENVALUE ANALYSIS
try:
    vals = ops.eigen(5)
    periods = [2*np.pi/np.sqrt(v) for v in vals]
    freqs = [1/p for p in periods]
    
    print("\nMODAL RESULTS:")
    print(f"{'MODE':<4} | {'PERIOD (s)':<10} | {'FREQ (Hz)':<10}")
    print("-" * 35)
    for i, p in enumerate(periods):
        print(f"{i+1:<4} | {p:<10.4f} | {freqs[i]:<10.2f}")
    
    # 6. RAYLEIGH DAMPING (5%)
    # Calculate Alpha/Beta for 5% damping at Mode 1 and Mode 3
    w1 = 2*np.pi/periods[0]
    w3 = 2*np.pi/periods[2]
    zeta = 0.05
    
    # [ 1/2w1  w1/2 ] [ a0 ] = [ zeta ]
    # [ 1/2w3  w3/2 ] [ a1 ]   [ zeta ]
    # Determinant = (w3/4w1 - w1/4w3)
    
    det = (w3**2 - w1**2) / (4*w1*w3)
    # This is standard formula solving...
    # Or simpler:
    a0 = zeta * 2 * w1 * w3 / (w1 + w3)
    a1 = zeta * 2 / (w1 + w3)
    
    print("\nRAYLEIGH DAMPING PARAMETERS (5%):")
    print(f"AlphaM (Mass prop):      {a0:.4f}")
    print(f"BetaK (Stiffness prop):  {a1:.6f}")
    print("These coefficients should be used in dynamic analysis.")

except Exception as e:
    print(f"Analysis Failed: {e}")
