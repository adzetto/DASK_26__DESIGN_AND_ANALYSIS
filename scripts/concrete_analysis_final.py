"""
FINAL CONCRETE ANALYSIS (1:50 Scale Geometry, Steel Braces)
===========================================================
- Vertical Scale: 6cm Model -> 3.0m Real (Factor 50).
- Height: 153cm Model -> 76.5m Real.
- Sections: 30cm x 30cm Concrete Columns/Beams.
- Braces: Steel (E=200 GPa).
- Damping: 5% Rayleigh.

Objective: Final Period and Drift Check.
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
print("FINAL CONCRETE ANALYSIS (1:50 Scale)")
print("=" * 70)

# 1. LOAD DATA
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except:
    print("Error: Data files not found.")
    sys.exit(1)

# 2. SCALING PARAMETERS
# 6cm (0.06m) -> 3.0m
# Scale Factor = 3.0 / 0.06 = 50.0
GEO_SCALE = 50.0 # From Model Meters (units=m in CSV? No, units=model units).
# CSV data X is roughly 0 to 30.
# If "30" means 30cm, then unit is cm.
# 6 units (cm) -> 3.0m.
# Scale = 3.0 / 6 = 0.5 (meters per unit).
# Let's verify CSV unit.
# X coords: 0, 3, 11... 30.
# If unit is cm, width is 30cm.
# Height 153cm.
# Target: 6cm -> 3m. Scale = 300cm/6cm = 50.
# Target Height = 153 * 50 = 7650cm = 76.5m.
# Target Width = 30 * 50 = 1500cm = 15m.
# Coordinate Multiplier from CSV (which is in cm? No, CSV "x" is 0..30).
# So Multiplier K: x_real = x_csv * K.
# K = 0.5? No.
# If x_csv = 6, x_real = 3.0.
# K = 3.0 / 6 = 0.5.
# So scaling factor from CSV to Real Meters is 0.5.
SCALE_FACTOR = 0.5 

print(f"Scale Factor: 1 unit (cm) = {SCALE_FACTOR} m")
print(f"Real Height:  {153 * SCALE_FACTOR:.2f} m (25 Stories)")
print(f"Real Width:   {30 * SCALE_FACTOR:.2f} m")

# Materials
E_conc = 30.0e6  # 30 GPa
G_conc = E_conc/2.4
Rho_conc = 2.5   # t/m3

E_steel = 200.0e6 # 200 GPa
Rho_steel = 7.85  # t/m3

# Sections
# Cols/Beams: 30cm x 30cm
b_col = 0.3
A_col = b_col**2
I_col = b_col**4 / 12
J_col = 0.14 * b_col**4

# Braces: Steel
# Assume reasonable size for 25 story building bracing
# Tube 200x200x10mm? Area ~ 76cm2 = 0.0076 m2
A_brace = 0.0076 

# Panels: Concrete Shear Walls
# Thickness 20cm?
t_wall = 0.20
# Width: 3.4 unit bay * 0.5 scale = 1.7m wide.
w_wall = 3.4 * SCALE_FACTOR
A_wall = t_wall * w_wall

# 3. BUILD MODEL
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Nodes
node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x']*SCALE_FACTOR, row['y']*SCALE_FACTOR, row['z']*SCALE_FACTOR
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

# Fix Base
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].tolist()
for nid in base_nodes: ops.fix(int(nid), 1, 1, 1, 1, 1, 1)

# Transformation
ops.geomTransf('Linear', 1, 0, 1, 0)
ops.geomTransf('Linear', 2, 1, 0, 0)
ops.geomTransf('Linear', 3, 0, 1, 0)

# Elements
pin_types = ['brace_xz', 'brace_yz', 'floor_brace', 'bridge_truss']
panel_types = ['shear_wall_xz', 'shear_wall_yz']

# Materials (Defined before usage)
ops.uniaxialMaterial('Elastic', 1, E_conc)
ops.uniaxialMaterial('Elastic', 2, E_steel)

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
        ops.element('Truss', eid, ni, nj, A_wall, 1) # Mat 1 (Conc)
        m = A_wall * L * Rho_conc
    elif etype in pin_types:
        # Steel Brace (Truss)
        ops.element('Truss', eid, ni, nj, A_brace, 2) # Mat 2 (Steel)
        m = A_brace * L * Rho_steel
    else:
        # Frame (Concrete)
        transf = 3
        if dz < 0.1 * max(dx, dy): transf = 1 if dx > dy else 2
        m_dens = A_col * Rho_conc
        ops.element('elasticBeamColumn', eid, ni, nj, A_col, E_conc, G_conc, J_col, I_col, I_col, transf, '-mass', m_dens)
        m = 0
        
    if m > 0:
        if ni not in elem_masses: elem_masses[ni] = 0
        if nj not in elem_masses: elem_masses[nj] = 0
        elem_masses[ni] += m/2
        elem_masses[nj] += m/2

# Materials defined above

# Apply Truss Masses
for nid, m in elem_masses.items():
    ops.mass(nid, m, m, m, 0,0,0)

# Floor Loads (Live Load + Slab)
# Assume 500 kg/m2 (5 kN/m2) distributed on floors
# Area per node approx: 3m x 3m = 9m2 -> 45 kN mass ~ 4.5 tonne
# Simplified: Add mass to all floor nodes
nodes_all = pos_df['node_id'].tolist()
M_FLOOR_NODE = 4.5 # Tonnes per node (Rough Estimate for slab)
for nid in nodes_all:
    ops.mass(int(nid), M_FLOOR_NODE, M_FLOOR_NODE, M_FLOOR_NODE, 0,0,0)

print(f"Added Slab Mass: {M_FLOOR_NODE} t/node")

# 4. EIGENVALUE ANALYSIS
try:
    vals = ops.eigen(5)
    periods = [2*np.pi/np.sqrt(v) for v in vals]
    print("\nFINAL MODAL RESULTS:")
    print(f"{'MODE':<4} | {'PERIOD (s)':<10} | {'FREQ (Hz)':<10}")
    print("-" * 35)
    for i, p in enumerate(periods):
        print(f"{i+1:<4} | {p:<10.4f} | {1/p:<10.2f}")
        
    T1 = periods[0]
    print("-" * 35)
    print(f"Fundamental Period: {T1:.3f} s")
    
    # Interpretation
    # For a 76m (25 story) building, typical T ~ 0.1 * N = 2.5s.
    # If T << 2.5s, it's very stiff.
    
    if T1 < 1.0:
        print("Status: EXTREMELY STIFF (Shear Wall Dominant)")
    elif T1 < 2.5:
        print("Status: NORMAL STIFFNESS (Frame-Wall)")
    else:
        print("Status: FLEXIBLE (Frame)")

except Exception as e:
    print(f"Error: {e}")
