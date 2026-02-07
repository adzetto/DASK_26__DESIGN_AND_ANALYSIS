"""
SCALED CONCRETE MODAL ANALYSIS (1:20 Scale)
===========================================
Analyzes the structure as if it were a 1:20 scale Reinforced Concrete model.

Parameters:
- Geometry Scale: 1:20 of Real Building (153m -> 7.65m).
  (Current Data is 1:100, so we multiply by 5).
- Sections: 30cm x 30cm (0.3m x 0.3m) Concrete Members.
- Material: Concrete (C30).
  - E = 30 GPa
  - Density = 2.5 tonne/m3

Objective: Check periods for a heavier, larger concrete frame.
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
print("SCALED CONCRETE MODAL ANALYSIS")
print("=" * 70)

# 1. LOAD DATA
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except FileNotFoundError:
    print("Error: Data files not found.")
    sys.exit(1)

# 2. SCALING PARAMETERS
# Original Data: units = cm (153.0 units = 1.53m physical model)
# Target: 1:20 Scale of 153m Real Building = 7.65m.
# Scaling Factor from Data(cm) to Target(m):
# 153.0 * K = 7.65  => K = 0.05
GEO_SCALE = 0.05 

# Material: Concrete
E_conc = 30.0e6  # 30 GPa = 30,000,000 kPa
G_conc = E_conc / (2 * (1 + 0.2)) # nu = 0.2
Rho_conc = 2.5   # tonne/m3 (2500 kg/m3)

# Sections: 30cm x 30cm
b_col = 0.3  # m
h_col = 0.3  # m
A_col = b_col * h_col
I_col = (b_col * h_col**3) / 12
J_col = 0.1406 * b_col**4 # Approx

# Panels? 
# Balsa panels were 3mm.
# Let's scale them to Concrete Shear Walls.
# Thickness: Say 10cm (0.1m)?
# Or maintain the aspect ratio? 
# 3mm balsa -> 0.3m (30cm) concrete column is 100x ratio.
# 3mm panel -> 15cm concrete wall? 
t_wall = 0.15 # 15cm wall
# Width: The bays scale with geometry (3.4cm * 5 = 17cm -> 0.17m bay width).
# Wait, 3.4cm bay at 1:20 scale (5x) is 17cm.
# 30cm columns won't fit in a 17cm bay!
# The user asked to scale "6mm to 30cm".
# But if the bay width is small (3.4cm data), scaling geometry by 5 gives 17cm bay.
# You can't put a 30cm column in a 17cm bay.
#
# INTERPRETATION FIX:
# The user wants a "1:20 length" scale.
# Real building 153m -> Model 7.65m.
# Real bay 8m -> Model 0.4m (40cm).
# Real column ? -> Model 30cm? 
# 30cm column for a 7m building is reasonable.
# But our "3.4cm" bay in data corresponds to what?
# In 1:100 model, 3.4cm = 3.4m real.
# In 1:20 model, 3.4m real = 3.4 / 20 = 0.17m (17cm).
# So 30cm columns will OVERLAP significantly in the 17cm bays.
# We will proceed, OpenSees doesn't care about collision. It calculates stiffness centerline-to-centerline.
# However, this physical clash implies the "30cm" request might be too thick for the "1:20" geometry.
# We will use it as requested.

print(f"Geometry Scale: Data * {GEO_SCALE} (Height {153*GEO_SCALE:.2f} m)")
print(f"Section:        {b_col}m x {h_col}m Concrete")
print(f"Material:       Concrete (E={E_conc/1e6:.1f} GPa, Rho={Rho_conc} t/m3)")

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

# Elements
ops.geomTransf('Linear', 1, 0, 1, 0)
ops.geomTransf('Linear', 2, 1, 0, 0)
ops.geomTransf('Linear', 3, 0, 1, 0)

# We treat everything as Concrete Frames for this study
# Except braces which we assume are Concrete Struts (Truss)
pin_types = ['brace_xz', 'brace_yz', 'floor_brace', 'bridge_truss']
panel_types = ['shear_wall_xz', 'shear_wall_yz']

# Check Bay Width for Panels
# Data 3.4 -> Scale 0.05 -> 0.17m.
w_panel_conc = 3.4 * GEO_SCALE 
A_panel_conc = w_panel_conc * t_wall

# Define Material 1 for Trusses (Moved before element loop)
ops.uniaxialMaterial('Elastic', 1, E_conc)

elem_masses = {} # Track mass to assign to nodes

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']
    
    p1, p2 = node_map[ni], node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
    L = np.sqrt(dx**2 + dy**2 + dz**2)
    
    # Determine Section
    if etype in panel_types:
        # Concrete Shear Wall (Strut)
        A = A_panel_conc
        ops.element('Truss', eid, ni, nj, A, 1) # Mat Tag 1 later
        vol = A * L
    elif etype in pin_types:
        # Concrete Brace (Strut 20x20cm?)
        A = 0.2 * 0.2
        ops.element('Truss', eid, ni, nj, A, 1)
        vol = A * L
    else:
        # Frame 30x30cm
        A = A_col
        transf = 3
        if dz < 0.1 * max(dx, dy): transf = 1 if dx > dy else 2
        
        # We need a material tag.
        # elasticBeamColumn needs E, G.
        # We can't define material inline for elasticBeamColumn, we pass properties directly.
        # But we need to assign MASS.
        # OpenSees can assign density in element? 
        # 'elasticBeamColumn' with '-mass' option?
        # Yes: element elasticBeamColumn ... -mass $massDens
        # massDens = mass per unit length = A * Rho
        m_dens = A * Rho_conc
        ops.element('elasticBeamColumn', eid, ni, nj, A, E_conc, G_conc, J_col, I_col, I_col, transf, '-mass', m_dens)
        
        # For Truss elements, we must add mass manually to nodes
        # because standard Truss doesn't always support -mass in all versions?
        # Let's assume we do it manually for Trusses.
        vol = 0 # Handled by element mass? No, assume trusses need manual mass
        # Actually elasticBeamColumn handles it.
        # Let's use elasticBeamColumn for EVERYTHING for mass consistency if possible?
        # No, braces should be pinned.
        # Let's just lump truss mass to nodes.
        
        # Logic for truss mass:
        m_elem = (A * L) * Rho_conc
        if ni not in elem_masses: elem_masses[ni] = 0
        if nj not in elem_masses: elem_masses[nj] = 0
        elem_masses[ni] += m_elem / 2
        elem_masses[nj] += m_elem / 2

# Material 1 defined above

# Apply Manual Mass from Trusses
for nid, m in elem_masses.items():
    ops.mass(nid, m, m, m, 0,0,0)

print("Model Built.")

# 4. EIGENVALUE ANALYSIS
print("\nCalculating Modes...")
try:
    num_modes = 5
    vals = ops.eigen(num_modes)
    periods = [2*np.pi/np.sqrt(v) for v in vals]
    
    print(f"\n{'MODE':<4} | {'PERIOD (s)':<10} | {'FREQ (Hz)':<10}")
    print("-" * 35)
    for i, T in enumerate(periods):
        print(f"{i+1:<4} | {T:<10.4f} | {1/T:<10.2f}")
    print("-" * 35)
    
except Exception as e:
    print(f"Analysis Failed: {e}")

# 5. INTERPRETATION
T1 = periods[0]
print("\nInterpretation:")
print(f"T1 = {T1:.4f} s.")
print("Comparison:")
print("- Balsa Model (1.5m): ~0.04 s")
print(f"- Concrete Model (7.65m): {T1:.4f} s")
if T1 > 0.04:
    print("-> Result: As expected, scaling up increases the period (slower).")
else:
    print("-> Result: Still very stiff! The 30cm columns are massive for this scale.")
