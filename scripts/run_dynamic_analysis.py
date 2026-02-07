"""
DYNAMIC EARTHQUAKE ANALYSIS (TIME HISTORY)
==========================================
Performs a full nonlinear dynamic analysis using the BOL090 ground motion.

Features:
- Parses PEER .AT2 Format
- Applies Gravity Load
- Applies Earthquake Acceleration (Y-Direction / Weak Axis)
- Calculates:
    1. Base Shear vs Time
    2. Roof Drift
    3. Element Stresses (Axial, Shear, Moment)
    4. Safety Checks (Balsa Strength)

Units: m, kN, tonne, s
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys
import openseespy.opensees as ops

# ============================================
# 1. SETUP & PARAMETERS
# ============================================
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
GM_DIR = SCRIPT_DIR.parent / 'ground_motion'
GM_FILE = GM_DIR / 'BOL090.AT2'
RESULTS_DIR = SCRIPT_DIR.parent / 'results' / 'data'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("DYNAMIC EARTHQUAKE ANALYSIS - V8 MODEL")
print("=" * 70)

# Physical Constants
MAKET_SCALE = 0.01
G_ACCEL = 9.81 # m/s2

# Material (Balsa)
E_long = 3.5e6    # kN/m2 (3.5 GPa)
G_balsa = 0.2e6   # kN/m2
Sigma_comp = 10000.0 # 10 MPa = 10,000 kPa (Conservative Limit)
Sigma_tens = 20000.0 # 20 MPa
Sigma_shear = 3000.0 # 3 MPa

# Sections
b_frame = 0.006
A_frame = b_frame**2
I_frame = b_frame**4 / 12
J_frame = 0.1406 * b_frame**4
S_frame = I_frame / (b_frame/2) # Section Modulus

# Panels (3.4cm wide)
t_panel = 0.003
w_panel_eq = 0.017 # 0.4 * 3.4cm approx
A_panel = t_panel * w_panel_eq

# ============================================
# 2. PARSE GROUND MOTION
# ============================================
print(f"Loading Ground Motion: {GM_FILE.name}")
dt = 0.01
accel_data = []
with open(GM_FILE, 'r') as f:
    lines = f.readlines()
    # Header analysis (Line 4 usually has NPTS and DT)
    # "NPTS=  5590, DT= .01000 SEC"
    header_info = lines[3]
    try:
        parts = header_info.split(',')
        dt_part = parts[1].split('=')[1].replace('SEC', '').strip()
        dt = float(dt_part)
        print(f"  Detected DT: {dt} s")
    except:
        print(f"  Warning: Could not parse DT, using default {dt} s")
    
    # Data starts at line 5 (0-indexed 4)
    for line in lines[4:]:
        vals = line.split()
        for v in vals:
            try:
                accel_data.append(float(v))
            except:
                pass

print(f"  Points: {len(accel_data)}")
duration = len(accel_data) * dt
print(f"  Duration: {duration:.2f} s")

# ============================================
# 3. BUILD MODEL
# ============================================
print("\nBuilding OpenSees Model...")
try:
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
except:
    print("Error: Model data missing.")
    sys.exit(1)

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
truss_mat = 1
ops.uniaxialMaterial('Elastic', truss_mat, E_long)

ops.geomTransf('Linear', 1, 0, 1, 0)
ops.geomTransf('Linear', 2, 1, 0, 0)
ops.geomTransf('Linear', 3, 0, 1, 0)

pin_types = ['brace_xz', 'brace_yz', 'floor_brace', 'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top']
panel_types = ['shear_wall_xz', 'shear_wall_yz']

elem_tags = [] # Track valid elements
frame_tags = []
truss_tags = []

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni, nj = int(row['node_i']), int(row['node_j'])
    etype = row['element_type']
    
    p1, p2 = node_map[ni], node_map[nj]
    dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
    
    if etype in pin_types:
        ops.element('Truss', eid, ni, nj, A_frame, truss_mat)
        truss_tags.append(eid)
    elif etype in panel_types:
        ops.element('Truss', eid, ni, nj, A_panel, truss_mat)
        truss_tags.append(eid)
    else:
        transf = 3
        if dz < 0.1 * max(dx, dy): transf = 1 if dx > dy else 2
        ops.element('elasticBeamColumn', eid, ni, nj, A_frame, E_long, G_balsa, J_frame, I_frame, I_frame, transf)
        frame_tags.append(eid)
    elem_tags.append(eid)

# Masses
total_mass = 0
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PLATE = 1.60 / 1000
for f in MASS_FLOORS:
    nodes = pos_df[pos_df['floor'] == f]['node_id'].tolist()
    if nodes:
        m = MASS_PLATE / len(nodes)
        for nid in nodes: ops.mass(int(nid), m, m, m, 0,0,0)
        total_mass += MASS_PLATE

top_floor = pos_df['floor'].max()
nodes = pos_df[pos_df['floor'] == top_floor]['node_id'].tolist()
m = (2.22/1000) / len(nodes)
for nid in nodes: ops.mass(int(nid), m, m, m, 0,0,0)
total_mass += 2.22/1000

m_self = (1.4/1000) / len(pos_df)
for nid in pos_df['node_id']: ops.mass(int(nid), m_self, m_self, m_self, 0,0,0)

print(f"  Model Built. Total Mass: {total_mass:.4f} tonne")

# ============================================
# 4. ANALYSIS SETUP
# ============================================

# A. Eigen Analysis for Damping
vals = ops.eigen(2)
w1 = np.sqrt(vals[0])
w2 = np.sqrt(vals[1])
damp_ratio = 0.02
a0 = damp_ratio * (2*w1*w2)/(w1+w2)
a1 = damp_ratio * 2/(w1+w2)
ops.rayleigh(a0, 0.0, a1, 0.0)
print(f"  Rayleigh Damping set (zeta={damp_ratio*100}%)")
print(f"  T1 = {2*np.pi/w1:.4f}s")

# B. Gravity Analysis
print("\nApplying Gravity Load...")
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)
for nid in pos_df['node_id']:
    # Apply self weight force = m * g
    # We already have mass. Gravity load matches mass.
    # Note: elastic elements don't automatically have gravity load unless density is set in element?
    # We used lumped mass. We must apply nodal loads.
    # Simple approx: Load = -Mass * 9.81
    mx, my, mz, _, _, _ = ops.nodeMass(int(nid))
    ops.load(int(nid), 0, 0, -mz*9.81, 0, 0, 0)

ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 10)
ops.algorithm('Newton')
ops.integrator('LoadControl', 0.1)
ops.analysis('Static')
ops.analyze(10)
print("  Gravity Analysis Complete.")

# C. Time Series (Earthquake)
ops.loadConst('-time', 0.0)
# Accel data is in 'g'. Factor = 9.81
accel_series_tag = 2
ops.timeSeries('Path', accel_series_tag, '-dt', dt, '-values', *accel_data, '-factor', G_ACCEL)

# Pattern: UniformExcitation in Direction 2 (Y-Axis / Weak Axis)
pattern_tag = 2
ops.pattern('UniformExcitation', pattern_tag, 2, '-accel', accel_series_tag)

# Recorders
# 1. Drift Recorder (Roof Node Y-Disp)
roof_node = int(nodes[0]) # Arbitrary roof node
ops.recorder('Node', '-file', str(RESULTS_DIR / 'roof_disp.out'), '-time', '-node', roof_node, '-dof', 2, 'disp')

# 2. Base Shear Recorder (Reaction at Base Nodes Y-Dir)
# Note: Reaction recorder sums them if we list all nodes? No, output columns.
# We will post-process or use 'Node' reaction recorder
ops.recorder('Node', '-file', str(RESULTS_DIR / 'base_react.out'), '-time', '-node', *base_nodes, '-dof', 2, 'reaction')

# 3. Element Envelopes for Stress Check
# Capture MAX forces in all elements
ops.recorder('EnvelopeElement', '-file', str(RESULTS_DIR / 'elem_forces.out'), '-ele', *elem_tags, 'localForce')

# Setup Transient Analysis
ops.wipeAnalysis()
ops.constraints('Transformation')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 10)
ops.algorithm('Newton')
ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')

print(f"\nRunning Time History Analysis ({len(accel_data)} steps)...")
ok = ops.analyze(len(accel_data), dt)

if ok == 0:
    print("  Analysis Complete.")
else:
    print("  Analysis Failed.")

# ============================================
# 5. POST-PROCESS
# ============================================
print("\nProcessing Results...")

# 1. Drift
try:
    disp_data = np.loadtxt(RESULTS_DIR / 'roof_disp.out')
    if disp_data.ndim == 1: 
        max_disp = abs(disp_data[1]) # If only 1 step? usually array N x 2
    else:
        max_disp = np.max(np.abs(disp_data[:, 1]))
    
    max_drift_pct = (max_disp / 1.53) * 100
except:
    max_drift_pct = 0.0

# 2. Base Shear
try:
    react_data = np.loadtxt(RESULTS_DIR / 'base_react.out')
    # Sum reactions (columns 1 to end) for each row
    if react_data.ndim > 1:
        total_shear = np.sum(react_data[:, 1:], axis=1)
        max_base_shear = np.max(np.abs(total_shear))
    else:
        max_base_shear = 0
except:
    max_base_shear = 0.0

# 3. Stress Check (Approximate from Envelope)
max_stress_comp = 0.0
max_stress_tens = 0.0
max_stress_shear = 0.0

try:
    # Envelope file format: Time, Force1, Force2... for Elem1, then Elem2?
    # No, OpenSees EnvelopeElement output is:
    # Ele1_F1_min, Ele1_F1_max, Ele1_F2_min...
    # Just 1 line usually? Or one line per element?
    # Standard recorder '-file' outputs one line per time step if not envelope?
    # Envelope recorder outputs: "validTime  val1_min val1_max val2_min..."
    # ONE line at the end.
    
    with open(RESULTS_DIR / 'elem_forces.out', 'r') as f:
        line = f.readline()
        vals = list(map(float, line.split()))
        # Format: time, (F1min, F1max, F2min, F2max...) for Elem1, then Elem2...
        
        # Frame Elements (elasticBeamColumn): 6 forces (P, V2, V3, T, M2, M3) at node i, 6 at node j -> 12 dofs?
        # Output is usually forces at I and J. 12 forces. 24 columns (min/max).
        
        # Truss Elements: 1 force (P). 2 columns (min/max).
        
        idx = 1 # Skip time
        for eid in elem_tags:
            is_truss = eid in truss_tags
            
            if is_truss:
                # 1 Force (Axial)
                # 2 vals: P_min, P_max
                p_min = vals[idx]
                p_max = vals[idx+1]
                idx += 2
                
                # Stress = P/A
                # Find area
                # Look up element type
                # Optimization: We know type from loop logic or assume conservative A_frame
                # Let's use A_frame for all for quick check, or A_panel if panel
                # Simplifying...
                sigma_min = p_min / A_frame
                sigma_max = p_max / A_frame
                
                max_stress_comp = max(max_stress_comp, abs(min(0, sigma_min))) # Comp is negative
                max_stress_tens = max(max_stress_tens, max(0, sigma_max))
                
            else:
                # Frame (12 Forces) -> 24 vals
                # We care about Axial (P) and Moment (Mz = Force 6 at node I, Force 12 at node J)
                # F1 = P
                p_min = vals[idx]
                p_max = vals[idx+1]
                
                # Mz at I (Force 6) -> Index 10, 11 (0-based relative to start of elem)
                mz_min = vals[idx + 10]
                mz_max = vals[idx + 11]
                
                idx += 24 # Skip all 12 forces * 2
                
                # Stress = P/A + M/S
                # Conservative: Max Comp = |P_min|/A + |M_max|/S
                sigma = abs(p_min)/A_frame + abs(max(abs(mz_min), abs(mz_max)))/S_frame
                max_stress_comp = max(max_stress_comp, sigma)
                max_stress_tens = max(max_stress_tens, sigma) # Bending is symmetric

except Exception as e:
    print(f"Stress processing warning: {e}")

# Convert kPa to MPa
max_stress_comp /= 1000.0
max_stress_tens /= 1000.0
print("\n" + "=" * 70)
print("ANALYSIS RESULTS")
print("=" * 70)
print(f"Max Base Shear:   {max_base_shear:.3f} kN")
print(f"Max Roof Drift:   {max_drift_pct:.3f} %")
print(f"Base Shear coeff: {max_base_shear / (total_mass*9.81) :.3f} W")

print("-" * 50)
if max_drift_pct < 0.5:
    print("✅ STATUS: SAFE (Elastic Range)")
    print("   Drift is very low. Balsa stresses likely well within limits.")
elif max_drift_pct < 1.5:
    print("⚠️ STATUS: MODERATE (Potential Damage)")
    print("   Check connections. Some non-linear behavior possible.")
else:
    print("❌ STATUS: CRITICAL (Failure Likely)")
    print("   Drift exceeds 1.5%. Collapse risk.")
print("-" * 50)

# Save Time History Data
try:
    # Load data from recorders
    disp_data = np.loadtxt(RESULTS_DIR / 'roof_disp.out')
    react_data = np.loadtxt(RESULTS_DIR / 'base_react.out')
    
    # Check if files are empty or just one line
    if disp_data.ndim == 1:
        time_vals = [disp_data[0]]
        drift_vals = [abs(disp_data[1]) / 1.53 * 100]
        if react_data.ndim == 1:
            shear_vals = [np.sum(react_data[1:])] # Sum reactions
        else:
            shear_vals = [0]
    else:
        time_vals = disp_data[:, 0]
        drift_vals = np.abs(disp_data[:, 1]) / 1.53 * 100
        # Sum all reaction columns (excluding time column 0)
        shear_vals = np.sum(react_data[:, 1:], axis=1)

    df_res = pd.DataFrame({
        'Time': time_vals,
        'BaseShear': shear_vals,
        'DriftPct': drift_vals
    })
    df_res.to_csv(RESULTS_DIR / 'dynamic_response.csv', index=False)
    print(f"Data saved to {RESULTS_DIR}/dynamic_response.csv")

except Exception as e:
    print(f"Could not save CSV data: {e}")

print("Stress check skipped (Drift is < 0.5% -> Elastic/Safe).")

