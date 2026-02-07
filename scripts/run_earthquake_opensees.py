"""
OpenSeesPy Earthquake Analysis Script
- Replicates SAP2000 analysis for verification
- Uses same model data from CSV/NPZ files
- Applies DASK 2025 competition masses
"""

import os
import sys
import numpy as np
import pandas as pd
import openseespy.opensees as ops
import time
import re

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Use paths from config
DATA_DIR = config.DATA_DIR
RESULTS_DATA_DIR = config.RESULTS_DATA_DIR
AT2_FILE = config.EARTHQUAKE_FILE

# Material and section properties from config
BALSA_E = config.BALSA_E
BALSA_DENSITY = config.BALSA_DENSITY
BALSA_NU = config.BALSA_NU
BALSA_G = config.BALSA_G
FRAME_SIZE = config.FRAME_SIZE
WALL_THICK = config.WALL_THICK

# Frame section properties (6x6 mm)
FRAME_A = FRAME_SIZE ** 2                          # mm²
FRAME_I = (FRAME_SIZE ** 4) / 12                   # mm⁴
FRAME_J = 0.1406 * FRAME_SIZE ** 4                 # Torsional constant for square

# DASK Mass configuration
MASS_FLOORS_1_60 = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_FLOOR_ROOF = 25
MASS_1_60_KG = 1.60
MASS_ROOF_KG = 2.22

# ---------------------------------------------------------------------------
# Parse AT2 file
# ---------------------------------------------------------------------------
def parse_at2(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header_line = lines[3]
    npts_match = re.search(r'NPTS\s*=\s*(\d+)', header_line)
    dt_match = re.search(r'DT\s*=\s*([.\d]+)', header_line)
    npts = int(npts_match.group(1)) if npts_match else None
    dt = float(dt_match.group(1)) if dt_match else None
    acc_values = []
    for line in lines[4:]:
        for val in line.split():
            try:
                acc_values.append(float(val))
            except:
                continue
    return np.arange(npts) * dt, np.array(acc_values[:npts]), dt, npts

# ---------------------------------------------------------------------------
# Main Script
# ---------------------------------------------------------------------------
print("=" * 70)
print("OPENSEESPY EARTHQUAKE ANALYSIS")
print("=" * 70)

# Load earthquake data
print(f"\nLoading: {AT2_FILE}")
time_arr, acc_g, dt, npts = parse_at2(AT2_FILE)
pga = np.max(np.abs(acc_g))
print(f"  Duration: {time_arr[-1]:.1f}s, PGA: {pga:.4f}g")

# Load model data
print("\nLoading model data...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, "position_matrix.csv"))
conn_df = pd.read_csv(os.path.join(DATA_DIR, "connectivity_matrix.csv"))

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")

# Convert to mm
pos_df['x_mm'] = pos_df['x'] * 1000
pos_df['y_mm'] = pos_df['y'] * 1000
pos_df['z_mm'] = pos_df['z'] * 1000

max_z = pos_df['z'].max()
top_nodes = pos_df[pos_df['z'] == max_z]['node_id'].tolist()
print(f"  Top nodes at Z={max_z}m: {len(top_nodes)} nodes")

# ---------------------------------------------------------------------------
# Initialize OpenSees Model
# ---------------------------------------------------------------------------
print("\n--- BUILDING OPENSEES MODEL ---")
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create coordinate transformations for 3D frames
# vecxz defines the local xz plane (must NOT be parallel to element axis)
ops.geomTransf('Linear', 1, 0, 1, 0)   # For vertical elements (Z-axis), vecxz = Y
ops.geomTransf('Linear', 2, 0, 0, 1)   # For Y-direction elements, vecxz = Z
ops.geomTransf('Linear', 3, 0, 1, 0)   # For X-direction elements, vecxz = Y

# ---------------------------------------------------------------------------
# Create Nodes
# ---------------------------------------------------------------------------
print(f"Creating {n_nodes} nodes...")
node_coords = {}

for idx, row in pos_df.iterrows():
    nid = int(row['node_id']) + 1  # OpenSees node IDs start from 1
    x, y, z = float(row['x_mm']), float(row['y_mm']), float(row['z_mm'])
    node_coords[int(row['node_id'])] = (x, y, z)
    ops.node(nid, x, y, z)

# ---------------------------------------------------------------------------
# Apply Boundary Conditions (Fixed Base)
# ---------------------------------------------------------------------------
base_z = pos_df['z_mm'].min()
count_fix = 0
for idx, row in pos_df.iterrows():
    if abs(row['z_mm'] - base_z) < 1.0:
        nid = int(row['node_id']) + 1
        ops.fix(nid, 1, 1, 1, 1, 1, 1)
        count_fix += 1
print(f"Fixed {count_fix} base nodes.")

# ---------------------------------------------------------------------------
# Create Material
# ---------------------------------------------------------------------------
# Elastic material for frames
mat_tag = 1
# Note: OpenSees uses consistent units - we use N, mm, kg
# E in N/mm² (MPa), density in kg/mm³
ops.uniaxialMaterial('Elastic', mat_tag, BALSA_E)

# ---------------------------------------------------------------------------
# Create Elements
# ---------------------------------------------------------------------------
print("Creating elements...")

frame_count = 0
shell_count = 0

# Helper to find node by coord
def find_node_id(tx, ty, tz):
    for nid, (nx, ny, nz) in node_coords.items():
        if abs(nx-tx) < 1.0 and abs(ny-ty) < 1.0 and abs(nz-tz) < 1.0:
            return nid
    return None

# Track created shell panels
created_panels = set()

for idx, row in conn_df.iterrows():
    etype = row['element_type']

    if 'node_id_i' in row:
        n1, n2 = int(row['node_id_i']), int(row['node_id_j'])
    else:
        n1, n2 = int(row['node_i']), int(row['node_j'])

    elem_id = int(row['element_id']) + 1  # OpenSees element IDs start from 1

    # Get coordinates
    p1 = node_coords[n1]
    p2 = node_coords[n2]

    # Determine transformation based on element orientation
    dz = abs(p2[2] - p1[2])
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    # Choose transformation based on element direction
    # vecxz must not be parallel to element axis
    if dz > max(dx, dy):  # Vertical element (along Z)
        transf_tag = 1  # vecxz = Y for vertical elements
    elif dx > dy:  # Element primarily along X
        transf_tag = 3  # vecxz = Y for X-direction elements
    else:  # Element primarily along Y
        transf_tag = 2  # vecxz = Z for Y-direction elements

    if etype == 'core_wall':
        # For shell elements, we need 4 corner nodes
        # Sort by Z to get bottom and top
        if p1[2] > p2[2]:
            p1, p2 = p2, p1
            n1, n2 = n2, n1

        x1, y1, z1 = p1
        x2, y2, z2 = p2

        n3 = None
        n4 = None

        if abs(y1 - y2) < 1.0:  # Planar in XZ
            n3 = find_node_id(x2, y1, z1)
            n4 = find_node_id(x1, y2, z2)
        elif abs(x1 - x2) < 1.0:  # Planar in YZ
            n3 = find_node_id(x1, y2, z1)
            n4 = find_node_id(x2, y1, z2)

        if n3 is not None and n4 is not None:
            panel_key = tuple(sorted([n1, n2, n3, n4]))

            if panel_key not in created_panels:
                # Create shell section
                sec_tag = 1000 + shell_count
                # ShellMITC4 requires nDMaterial, use ElasticIsotropic
                if shell_count == 0:
                    ops.nDMaterial('ElasticIsotropic', 100, BALSA_E, BALSA_NU)
                    ops.section('PlateFiber', 200, 100, WALL_THICK)

                try:
                    # Shell element (node order: counter-clockwise)
                    ops.element('ShellMITC4', elem_id,
                               n1 + 1, n3 + 1, n2 + 1, n4 + 1, 200)
                    created_panels.add(panel_key)
                    shell_count += 1
                except Exception as e:
                    # Fall back to frame element
                    try:
                        ops.element('elasticBeamColumn', elem_id,
                                   n1 + 1, n2 + 1,
                                   FRAME_A, BALSA_E, BALSA_G, FRAME_J, FRAME_I, FRAME_I,
                                   transf_tag)
                        frame_count += 1
                    except:
                        pass
        else:
            # Create as frame element (diagonal brace)
            try:
                ops.element('elasticBeamColumn', elem_id,
                           n1 + 1, n2 + 1,
                           FRAME_A, BALSA_E, BALSA_G, FRAME_J, FRAME_I, FRAME_I,
                           transf_tag)
                frame_count += 1
            except:
                pass
    else:
        # Regular frame element
        try:
            ops.element('elasticBeamColumn', elem_id,
                       n1 + 1, n2 + 1,
                       FRAME_A, BALSA_E, BALSA_G, FRAME_J, FRAME_I, FRAME_I,
                       transf_tag)
            frame_count += 1
        except Exception as e:
            if frame_count < 5:
                print(f"  Frame error: {e}")

print(f"Created {frame_count} frames, {shell_count} shell panels")

# ---------------------------------------------------------------------------
# Add Masses (DASK Specification)
# ---------------------------------------------------------------------------
print("\n--- ADDING MASS (DASK SPECS) ---")

# Count nodes per floor
floor_nodes = {}
for idx, row in pos_df.iterrows():
    floor = int(row['floor'])
    if floor not in floor_nodes:
        floor_nodes[floor] = []
    floor_nodes[floor].append(int(row['node_id']))

mass_count = 0
total_mass_kg = 0.0

# Apply 1.60 kg to floors 3, 6, 9, 12, 15, 18, 21, 24
# UNIT CONVERSION: With N (force), mm (length), s (time):
# Mass unit = N·s²/mm = kg·(m/s²)·s²/mm = kg·m/mm = 1000 kg
# So mass in model units = kg / 1000 = kg * 1e-3
# Or equivalently, use tonnes (1 tonne = 1000 kg = 1 N·s²/mm)
MASS_CONVERSION = 1e-3  # kg to N·s²/mm (or tonnes)

for floor in MASS_FLOORS_1_60:
    if floor in floor_nodes:
        n_nodes_floor = len(floor_nodes[floor])
        mass_per_node_kg = MASS_1_60_KG / n_nodes_floor
        mass_value = mass_per_node_kg * MASS_CONVERSION  # Convert to consistent units

        for node_id in floor_nodes[floor]:
            ops.mass(node_id + 1, mass_value, mass_value, 0.0, 0.0, 0.0, 0.0)
            mass_count += 1

        total_mass_kg += MASS_1_60_KG
        print(f"  Floor {floor}: {MASS_1_60_KG} kg distributed to {n_nodes_floor} nodes ({mass_per_node_kg*1000:.1f} g/node)")

# Apply 2.22 kg to roof (floor 25)
if MASS_FLOOR_ROOF in floor_nodes:
    n_nodes_floor = len(floor_nodes[MASS_FLOOR_ROOF])
    mass_per_node_kg = MASS_ROOF_KG / n_nodes_floor
    mass_value = mass_per_node_kg * MASS_CONVERSION  # Convert to consistent units

    for node_id in floor_nodes[MASS_FLOOR_ROOF]:
        ops.mass(node_id + 1, mass_value, mass_value, 0.0, 0.0, 0.0, 0.0)
        mass_count += 1

    total_mass_kg += MASS_ROOF_KG
    print(f"  Floor {MASS_FLOOR_ROOF} (roof): {MASS_ROOF_KG} kg distributed to {n_nodes_floor} nodes ({mass_per_node_kg*1000:.1f} g/node)")

print(f"\n  Total tige mass: {total_mass_kg:.2f} kg")
print(f"  Applied to {mass_count} nodes")

# ---------------------------------------------------------------------------
# Modal Analysis
# ---------------------------------------------------------------------------
print("\n--- MODAL ANALYSIS ---")

num_modes = 12
start = time.time()

try:
    eigenvalues = ops.eigen(num_modes)
    print(f"  Completed in {time.time()-start:.2f}s")

    periods = []
    frequencies = []

    print(f"\n  Modal Results ({len(eigenvalues)} modes):")
    print(f"  {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12}")
    print(f"  {'-'*30}")

    for i, ev in enumerate(eigenvalues[:6]):
        if ev > 0:
            omega = np.sqrt(ev)
            T = 2 * np.pi / omega
            f = 1 / T
            periods.append(T)
            frequencies.append(f)
            print(f"  {i+1:<6} {T:<12.4f} {f:<12.4f}")

    T1 = periods[0] if periods else 0
    print(f"\n  Fundamental Period T1 = {T1:.4f} s")

except Exception as e:
    print(f"  Modal analysis error: {e}")
    eigenvalues = []
    periods = []

# ---------------------------------------------------------------------------
# Response Spectrum Analysis
# ---------------------------------------------------------------------------
print("\n--- RESPONSE SPECTRUM ANALYSIS ---")

# EC8 Type 1 spectrum parameters (matching SAP2000)
ag = 0.4 * 9810  # Design ground acceleration in mm/s² (0.4g)
S = 1.0  # Soil factor
TB = 0.15
TC = 0.5
TD = 2.0
eta = 1.0  # Damping correction (5% damping)

def ec8_spectrum(T):
    """EC8 Type 1 elastic response spectrum"""
    if T < 0:
        return ag * S * 2.5
    elif T < TB:
        return ag * S * (1 + T/TB * (2.5*eta - 1))
    elif T < TC:
        return ag * S * 2.5 * eta
    elif T < TD:
        return ag * S * 2.5 * eta * TC / T
    else:
        return ag * S * 2.5 * eta * TC * TD / T**2

# Get mode shapes at top nodes for SRSS combination
print("  Computing modal displacements...")

rs_results = {'RSX': {'ux': 0, 'uy': 0}, 'RSY': {'ux': 0, 'uy': 0}}

if len(eigenvalues) > 0:
    # Get modal participation factors and compute response
    # For each direction, compute spectral displacement at each mode

    max_ux_x = 0  # Max X displacement from X loading
    max_uy_y = 0  # Max Y displacement from Y loading

    for node_id in pos_df['node_id'].tolist():
        ops_node = node_id + 1

        # Get eigenvectors at this node
        ux_modal = []
        uy_modal = []

        for mode in range(1, min(len(eigenvalues)+1, 7)):
            try:
                # Get eigenvector component
                phi_x = ops.nodeEigenvector(ops_node, mode, 1)  # DOF 1 = X
                phi_y = ops.nodeEigenvector(ops_node, mode, 2)  # DOF 2 = Y
                ux_modal.append(phi_x)
                uy_modal.append(phi_y)
            except:
                ux_modal.append(0)
                uy_modal.append(0)

        # Compute spectral response using SRSS
        ux_srss_x = 0  # X response from X loading
        uy_srss_y = 0  # Y response from Y loading

        for i, (T, phi_x, phi_y) in enumerate(zip(periods[:6], ux_modal[:6], uy_modal[:6])):
            Sa = ec8_spectrum(T)
            Sd = Sa * (T / (2*np.pi))**2  # Spectral displacement

            # SRSS combination
            ux_srss_x += (phi_x * Sd) ** 2  # X loading -> X displacement
            uy_srss_y += (phi_y * Sd) ** 2  # Y loading -> Y displacement

        ux_srss_x = np.sqrt(ux_srss_x)
        uy_srss_y = np.sqrt(uy_srss_y)

        max_ux_x = max(max_ux_x, abs(ux_srss_x))
        max_uy_y = max(max_uy_y, abs(uy_srss_y))

    rs_results['RSX']['ux'] = max_ux_x
    rs_results['RSY']['uy'] = max_uy_y

    print(f"\n  RS Results (approximate SRSS):")
    print(f"    RSX: Max Ux = {max_ux_x:.3f} mm")
    print(f"    RSY: Max Uy = {max_uy_y:.3f} mm")

# ---------------------------------------------------------------------------
# Time History Analysis
# ---------------------------------------------------------------------------
print("\n--- TIME HISTORY ANALYSIS ---")

# Reset for dynamic analysis
ops.wipeAnalysis()
ops.loadConst('-time', 0.0)

# Create time series from earthquake record
# Convert g to mm/s² (g = 9810 mm/s²)
# Note: With mass in N·s²/mm (=tonnes), acceleration in mm/s² gives force in N
acc_mms2 = acc_g * 9810.0  # mm/s²

# Create time series
ts_tag = 1
ops.timeSeries('Path', ts_tag, '-dt', dt, '-values', *acc_mms2.tolist(), '-factor', 1.0)

# Create uniform excitation pattern for X direction
pattern_tag_x = 1
ops.pattern('UniformExcitation', pattern_tag_x, 1, '-accel', ts_tag)  # DOF 1 = X

# Rayleigh damping (5% at first two modes)
if len(eigenvalues) >= 2:
    omega1 = np.sqrt(eigenvalues[0])
    omega2 = np.sqrt(eigenvalues[1])
    zeta = 0.05
    a0 = 2 * zeta * omega1 * omega2 / (omega1 + omega2)
    a1 = 2 * zeta / (omega1 + omega2)
    ops.rayleigh(a0, 0.0, 0.0, a1)

# Analysis settings
ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.algorithm('Newton')

# Time step for analysis
analysis_dt = 0.02  # Larger step for faster analysis
total_time = min(time_arr[-1], 10.0)  # Limit to 10s for speed
num_steps = int(total_time / analysis_dt)

ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')

print(f"  Running TH X-direction ({total_time:.1f}s, dt={analysis_dt}s)...")
start = time.time()

# Track maximum displacements
max_ux_th_x = 0
max_uy_th_x = 0

for i in range(num_steps):
    ok = ops.analyze(1, analysis_dt)
    if ok != 0:
        # Try smaller step
        ok = ops.analyze(10, analysis_dt/10)

    # Record max displacements at top nodes
    for node_id in top_nodes:
        ops_node = node_id + 1
        try:
            ux = ops.nodeDisp(ops_node, 1)
            uy = ops.nodeDisp(ops_node, 2)
            max_ux_th_x = max(max_ux_th_x, abs(ux))
            max_uy_th_x = max(max_uy_th_x, abs(uy))
        except:
            pass

    if (i+1) % 500 == 0:
        print(f"    Step {i+1}/{num_steps}, Max Ux={max_ux_th_x:.3f}mm")

print(f"  Completed in {time.time()-start:.1f}s")
print(f"  TH_X: Max Ux = {max_ux_th_x:.3f} mm, Max Uy = {max_uy_th_x:.3f} mm")

th_results = {
    'TH_X': {'ux': max_ux_th_x, 'uy': max_uy_th_x},
    'TH_Y': {'ux': 0, 'uy': 0}  # Would need to re-run with Y excitation
}

# ---------------------------------------------------------------------------
# Y-direction Time History
# ---------------------------------------------------------------------------
print("\n  Running TH Y-direction...")

# Reset model for Y direction
ops.wipeAnalysis()
ops.remove('loadPattern', pattern_tag_x)
ops.loadConst('-time', 0.0)
ops.setTime(0.0)

# Create pattern for Y direction
pattern_tag_y = 2
ops.timeSeries('Path', 2, '-dt', dt, '-values', *acc_mms2.tolist(), '-factor', 1.0)
ops.pattern('UniformExcitation', pattern_tag_y, 2, '-accel', 2)  # DOF 2 = Y

# Reset damping
if len(eigenvalues) >= 2:
    ops.rayleigh(a0, 0.0, 0.0, a1)

ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.algorithm('Newton')
ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')

start = time.time()
max_ux_th_y = 0
max_uy_th_y = 0

for i in range(num_steps):
    ok = ops.analyze(1, analysis_dt)
    if ok != 0:
        ok = ops.analyze(10, analysis_dt/10)

    for node_id in top_nodes:
        ops_node = node_id + 1
        try:
            ux = ops.nodeDisp(ops_node, 1)
            uy = ops.nodeDisp(ops_node, 2)
            max_ux_th_y = max(max_ux_th_y, abs(ux))
            max_uy_th_y = max(max_uy_th_y, abs(uy))
        except:
            pass

    if (i+1) % 500 == 0:
        print(f"    Step {i+1}/{num_steps}, Max Uy={max_uy_th_y:.3f}mm")

print(f"  Completed in {time.time()-start:.1f}s")
print(f"  TH_Y: Max Ux = {max_ux_th_y:.3f} mm, Max Uy = {max_uy_th_y:.3f} mm")

th_results['TH_Y'] = {'ux': max_ux_th_y, 'uy': max_uy_th_y}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("OPENSEESPY SUMMARY: MAXIMUM TOP DISPLACEMENTS")
print("=" * 70)

print(f"\nBuilding height: {max_z} m (model scale)")
print(f"Total tige mass: {total_mass_kg:.2f} kg")
print(f"Earthquake: Duzce 1999, PGA = {pga:.3f}g")

print("\n{:<15} {:>15} {:>15}".format("Analysis", "Max Ux (mm)", "Max Uy (mm)"))
print("-" * 45)

print("{:<15} {:>15.2f} {:>15.2f}".format("RS X-dir", rs_results['RSX']['ux'], rs_results['RSX']['uy']))
print("{:<15} {:>15.2f} {:>15.2f}".format("RS Y-dir", rs_results['RSY']['ux'], rs_results['RSY']['uy']))
print("{:<15} {:>15.2f} {:>15.2f}".format("TH X-dir", th_results['TH_X']['ux'], th_results['TH_X']['uy']))
print("{:<15} {:>15.2f} {:>15.2f}".format("TH Y-dir", th_results['TH_Y']['ux'], th_results['TH_Y']['uy']))

max_ux = max(rs_results['RSX']['ux'], th_results['TH_X']['ux'], th_results['TH_Y']['ux'])
max_uy = max(rs_results['RSY']['uy'], th_results['TH_X']['uy'], th_results['TH_Y']['uy'])

print("-" * 45)
print("{:<15} {:>15.2f} {:>15.2f}".format("ENVELOPE", max_ux, max_uy))

if max_ux > 0 or max_uy > 0:
    height_mm = max_z * 1000
    drift = max(max_ux, max_uy) / height_mm * 100
    print(f"\nMax Drift Ratio: {drift:.3f}%")

# Save results
results_df = pd.DataFrame({
    'Analysis': ['RSX', 'RSY', 'TH_X', 'TH_Y', 'ENVELOPE'],
    'Max_Ux_mm': [rs_results['RSX']['ux'], rs_results['RSY']['ux'],
                  th_results['TH_X']['ux'], th_results['TH_Y']['ux'], max_ux],
    'Max_Uy_mm': [rs_results['RSX']['uy'], rs_results['RSY']['uy'],
                  th_results['TH_X']['uy'], th_results['TH_Y']['uy'], max_uy]
})
results_df.to_csv(os.path.join(RESULTS_DATA_DIR, "earthquake_results_opensees.csv"), index=False)
print(f"\nResults saved to earthquake_results_opensees.csv")

# ---------------------------------------------------------------------------
# Comparison with SAP2000
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("COMPARISON: SAP2000 vs OpenSeesPy")
print("=" * 70)

try:
    sap_results = pd.read_csv(os.path.join(RESULTS_DATA_DIR, "earthquake_results.csv"))

    print("\n{:<15} {:>12} {:>12} {:>12}".format("Analysis", "SAP2000", "OpenSees", "Diff (%)"))
    print("-" * 55)

    # RSX Ux
    sap_rsx_ux = sap_results[sap_results['Analysis'] == 'RSX']['Max_Ux_mm'].values[0]
    ops_rsx_ux = rs_results['RSX']['ux']
    diff_rsx = abs(sap_rsx_ux - ops_rsx_ux) / max(sap_rsx_ux, ops_rsx_ux, 0.001) * 100
    print("{:<15} {:>12.2f} {:>12.2f} {:>12.1f}".format("RSX Ux", sap_rsx_ux, ops_rsx_ux, diff_rsx))

    # RSY Uy
    sap_rsy_uy = sap_results[sap_results['Analysis'] == 'RSY']['Max_Uy_mm'].values[0]
    ops_rsy_uy = rs_results['RSY']['uy']
    diff_rsy = abs(sap_rsy_uy - ops_rsy_uy) / max(sap_rsy_uy, ops_rsy_uy, 0.001) * 100
    print("{:<15} {:>12.2f} {:>12.2f} {:>12.1f}".format("RSY Uy", sap_rsy_uy, ops_rsy_uy, diff_rsy))

    # Envelope
    sap_env_ux = sap_results[sap_results['Analysis'] == 'ENVELOPE']['Max_Ux_mm'].values[0]
    sap_env_uy = sap_results[sap_results['Analysis'] == 'ENVELOPE']['Max_Uy_mm'].values[0]
    diff_env_ux = abs(sap_env_ux - max_ux) / max(sap_env_ux, max_ux, 0.001) * 100
    diff_env_uy = abs(sap_env_uy - max_uy) / max(sap_env_uy, max_uy, 0.001) * 100
    print("{:<15} {:>12.2f} {:>12.2f} {:>12.1f}".format("ENV Ux", sap_env_ux, max_ux, diff_env_ux))
    print("{:<15} {:>12.2f} {:>12.2f} {:>12.1f}".format("ENV Uy", sap_env_uy, max_uy, diff_env_uy))

except Exception as e:
    print(f"Could not load SAP2000 results for comparison: {e}")

ops.wipe()
print("\nAnalysis complete.")
