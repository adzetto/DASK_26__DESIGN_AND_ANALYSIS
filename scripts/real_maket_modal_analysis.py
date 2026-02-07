"""
REAL MAKET MODAL ANALYSIS
=========================
Performs eigenvalue analysis on the V7 Twin Towers model
interpreting dimensions and masses as the PHYSICAL MAKET.

Parameters:
- Height: 153 cm (1.53 m)
- Width: 30 cm (0.30 m)
- Depth: 16 cm (0.16 m)
- Material: Balsa (E = 3.5 GPa)
- Mass: DASK Competition Masses + Self Weight
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import json

# Setup paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
RESULTS_DIR = SCRIPT_DIR.parent / 'results' / 'data'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("REAL MAKET PHYSICAL ANALYSIS (1:1 Scale Simulation)")
print("=" * 70)

# ============================================
# 1. PHYSICAL CONSTANTS
# ============================================
# Maket Dimensions
MAKET_SCALE = 0.01  # Data is in cm, convert to m (153 units -> 1.53m)

# Material: Balsa Wood (High Density assumption for stiffness)
E_GPa = 3.5
E_kPa = E_GPa * 1e6  # 3,500,000 kPa (kN/m²)
NU = 0.3
G_kPa = E_kPa / (2 * (1 + NU))

# Section Properties
# 1. Frames (6x6mm sticks)
b_frame = 0.006  # m
A_frame = b_frame ** 2
I_frame = (b_frame ** 4) / 12
J_frame = 0.1406 * (b_frame ** 4)

# 2. Shear Wall Panels (3mm balsa in 3.4cm bays)
# Modeled as equivalent X-braces (2 diagonals per panel)
# Width = 3.4cm = 0.034m
t_panel = 0.003  # m
w_panel = 0.034  # m (3.4cm width)
A_panel = t_panel * w_panel
I_panel = (w_panel * t_panel**3) / 12  # Weak axis bending
J_panel = 0.1406 * t_panel**4          # Torsion (approx)

print(f"PHYSICAL PARAMETERS:")
print(f"  Height:       1.53 m")
print(f"  Material E:   {E_GPa} GPa")
print(f"  Frame Sect:   6x6 mm")
print(f"  Panel Sect:   3x12 mm (in 1.2cm Core Gaps)")

# ============================================
# 2. LOAD MODEL DATA
# ============================================
print("\nLoading V7 Model Data...")
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except FileNotFoundError:
    print("Error: Model data not found. Please run regenerate_twin_model_final.py first.")
    sys.exit(1)

print(f"  Nodes:    {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# Verify Height
max_z = pos_df['z'].max() * MAKET_SCALE
if abs(max_z - 1.53) > 0.01:
    print(f"  WARNING: Model height is {max_z:.2f}m, expected 1.53m")
else:
    print(f"  Geometry Check: Height = {max_z:.2f}m [OK]")

# ============================================
# 3. BUILD OPENSEES MODEL
# ============================================
try:
    import openseespy.opensees as ops
except ImportError:
    print("Error: OpenSeesPy library not found.")
    sys.exit(1)

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create Nodes
node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x = row['x'] * MAKET_SCALE
    y = row['y'] * MAKET_SCALE
    z = row['z'] * MAKET_SCALE
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

# Fix Base (Floor 0)
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].tolist()
for nid in base_nodes:
    ops.fix(int(nid), 1, 1, 1, 1, 1, 1)

# Transformations
ops.geomTransf('Linear', 1, 0, 1, 0)  # X-beams
ops.geomTransf('Linear', 2, 1, 0, 0)  # Y-beams
ops.geomTransf('Linear', 3, 0, 1, 0)  # Columns/Verticals

# Create Elements
shear_types = ['shear_wall_xz', 'shear_wall_yz']
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']
    
    # Determine transformation
    p1 = node_map[ni]
    p2 = node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
    
    transf = 3 # Default vertical
    if dz < 0.1 * max(dx, dy): # Horizontal
        transf = 1 if dx > dy else 2
        
    # Determine Section
    if etype in shear_types:
        A, I, J = A_panel, I_panel, J_panel
    else:
        A, I, J = A_frame, I_frame, J_frame
        
    ops.element('elasticBeamColumn', eid, ni, nj, A, E_kPa, G_kPa, J, I, I, transf)

# ============================================
# 4. APPLY MASSES (DASK RULES)
# ============================================
# 1.6 kg plates at floors 3, 6, 9, 12, 15, 18, 21, 24
# 2.22 kg plate at Roof (Floor 25/Top) - Note: Script usually treats Top as 25 or 26
# Let's verify top floor index
TOP_FLOOR = pos_df['floor'].max()
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]

MASS_PLATE_KG = 1.60
MASS_ROOF_KG = 2.22

total_added_mass = 0

print("\nAdding Masses:")
for f in MASS_FLOORS:
    nodes = pos_df[pos_df['floor'] == f]['node_id'].tolist()
    if not nodes: continue
    mass_per_node = (MASS_PLATE_KG / 1000) / len(nodes) # tonnes
    for nid in nodes:
        ops.mass(int(nid), mass_per_node, mass_per_node, mass_per_node, 0,0,0)
    total_added_mass += MASS_PLATE_KG

# Roof Mass
roof_nodes = pos_df[pos_df['floor'] == TOP_FLOOR]['node_id'].tolist()
if roof_nodes:
    mass_per_node = (MASS_ROOF_KG / 1000) / len(roof_nodes)
    for nid in roof_nodes:
        ops.mass(int(nid), mass_per_node, mass_per_node, mass_per_node, 0,0,0)
    total_added_mass += MASS_ROOF_KG

# Self Weight Estimation (1.3 kg distributed)
# We add this roughly to all nodes to be accurate
SELF_WEIGHT_KG = 1.32
nodes_all = pos_df['node_id'].tolist()
mass_self = (SELF_WEIGHT_KG / 1000) / len(nodes_all)
for nid in nodes_all:
    ops.mass(int(nid), mass_self, mass_self, mass_self, 0,0,0)

total_mass = total_added_mass + SELF_WEIGHT_KG
print(f"  Added Plate Mass: {total_added_mass:.2f} kg")
print(f"  Self Weight:      {SELF_WEIGHT_KG:.2f} kg")
print(f"  TOTAL MASS:       {total_mass:.2f} kg")

# ============================================
# 5. EIGENVALUE ANALYSIS
# ============================================
print("\nCalculating Modes...")
try:
    # 3 modes
    vals = ops.eigen(3)
    periods = [2 * np.pi / np.sqrt(v) for v in vals]
    T1 = periods[0]
except:
    print("Eigenvalue solver failed!")
    sys.exit(1)

print("-" * 40)
print(f"  MODE 1 PERIOD (T1):  {T1:.4f} s")
print(f"  MODE 1 FREQUENCY:    {1/T1:.2f} Hz")
print("-" * 40)

# ============================================
# 6. SPECTRUM CHECK (ASCENDING vs PLATEAU)
# ============================================
TA = 0.061  # seconds
TB = 0.303  # seconds

print("\nSPECTRUM ANALYSIS RESULT:")
print(f"  Target (Ascending):  T < {TA:.3f} s")
print(f"  Current Model:       T = {T1:.3f} s")

if T1 <= TA:
    print("\n  ✅ RESULT: ASCENDING REGION (STIFF)")
    print("  The model is extremely stiff.")
else:
    print("\n  ❌ RESULT: NOT ASCENDING REGION")
    if T1 <= TB:
        print("  Status: PLATEAU REGION (Maximum Acceleration)")
    else:
        print("  Status: DESCENDING REGION (Lower Acceleration)")
    
    ratio = T1 / TA
    stiff_req = ratio ** 2
    print(f"\n  To reach Ascending region:")
    print(f"  - Period must decrease by {ratio:.1f}x")
    print(f"  - Stiffness must increase by {stiff_req:.1f}x")
    print("  (This is likely physically impossible with Balsa at this weight limit)")

print("=" * 70)
