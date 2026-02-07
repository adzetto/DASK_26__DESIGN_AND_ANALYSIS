"""
OpenSeesPy Earthquake & Stress Analysis for DASK 2026 Twin Towers
- Reads twin_building_data.npz and CSV files
- Modal analysis, response spectrum, time history
- Element stress/force analysis
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

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
RESULTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'results', 'data')
AT2_FILE = os.path.join(os.path.dirname(SCRIPT_DIR), 'ground_motion', 'BOL090.AT2')

os.makedirs(RESULTS_DIR, exist_ok=True)

# Material properties (Balsa wood)
BALSA_E = 3500.0        # MPa = N/mm²
BALSA_DENSITY = 160e-9  # kg/mm³ (160 kg/m³)
BALSA_NU = 0.3
BALSA_G = BALSA_E / (2 * (1 + BALSA_NU))  # Shear modulus

# Section properties (6x6 mm frame members - maket scale)
FRAME_SIZE = 6.0   # mm
FRAME_A = FRAME_SIZE ** 2                  # mm²
FRAME_I = (FRAME_SIZE ** 4) / 12           # mm⁴
FRAME_J = 0.1406 * FRAME_SIZE ** 4         # Torsional constant for square

# DASK 2026 Mass configuration (Twin Towers)
# Test loads: 1.60 kg at floors 3,6,9..24, 2.22 kg at roof (per tower)
# These are TEST LOADS, not actual structural mass
# For modal analysis, we use actual structural mass from self-weight
# Estimated structural mass: ~0.5-0.8 kg per tower for balsa maket

# MODEL SCALE: The model coordinates are in METERS (real building scale)
# but the physical maket is at 1:100 scale
# Model height: 153m = 1530mm physical maket
MODEL_SCALE = 10.0  # mm per model unit (1m = 10mm in maket)

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
print("DASK 2026 TWIN TOWERS - OPENSEES ANALYSIS")
print("=" * 70)

# Load earthquake data
print(f"\nLoading earthquake: {os.path.basename(AT2_FILE)}")
time_arr, acc_g, dt, npts = parse_at2(AT2_FILE)
pga = np.max(np.abs(acc_g))
print(f"  Duration: {time_arr[-1]:.1f}s, PGA: {pga:.4f}g")

# Load model data
print("\nLoading twin towers model data...")
npz_path = os.path.join(DATA_DIR, 'twin_building_data.npz')
if not os.path.exists(npz_path):
    print(f"ERROR: {npz_path} not found!")
    print("Run the twin_towers.ipynb notebook first.")
    sys.exit(1)

npz = np.load(npz_path)
coords = npz['coords']
z_coords = npz['z_coords']

pos_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_position_matrix.csv'))
conn_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_connectivity_matrix.csv'))

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")

# Convert to mm (model coords are in meters, scale to maket mm)
# 1m model = 10mm maket (1:100 scale representation)
pos_df['x_mm'] = pos_df['x'] * MODEL_SCALE
pos_df['y_mm'] = pos_df['y'] * MODEL_SCALE
pos_df['z_mm'] = pos_df['z'] * MODEL_SCALE

max_z = pos_df['z'].max()
max_z_mm = max_z * MODEL_SCALE
top_nodes = pos_df[pos_df['z'] == max_z]['node_id'].tolist()
print(f"  Height: {max_z:.0f}m -> {max_z_mm:.0f}mm (maket), Top nodes: {len(top_nodes)}")

# ---------------------------------------------------------------------------
# Initialize OpenSees Model
# ---------------------------------------------------------------------------
print("\n--- BUILDING OPENSEES MODEL ---")
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Coordinate transformations
ops.geomTransf('Linear', 1, 0, 1, 0)   # For vertical elements (Z-axis)
ops.geomTransf('Linear', 2, 0, 0, 1)   # For Y-direction elements
ops.geomTransf('Linear', 3, 0, 1, 0)   # For X-direction elements

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
mat_tag = 1
ops.uniaxialMaterial('Elastic', mat_tag, BALSA_E)

# ---------------------------------------------------------------------------
# Create Elements
# ---------------------------------------------------------------------------
print("Creating elements...")

frame_count = 0
element_data = []

for idx, row in conn_df.iterrows():
    etype = row['element_type']
    n1, n2 = int(row['node_i']), int(row['node_j'])
    elem_id = int(row['element_id']) + 1

    # Get coordinates
    p1 = node_coords.get(n1)
    p2 = node_coords.get(n2)
    
    if p1 is None or p2 is None:
        continue

    # Determine transformation based on element orientation
    dz = abs(p2[2] - p1[2])
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    if dz > max(dx, dy):
        transf_tag = 1  # Vertical
    elif dx > dy:
        transf_tag = 3  # X-direction
    else:
        transf_tag = 2  # Y-direction

    # Create frame element
    try:
        ops.element('elasticBeamColumn', elem_id,
                   n1 + 1, n2 + 1,
                   FRAME_A, BALSA_E, BALSA_G, FRAME_J, FRAME_I, FRAME_I,
                   transf_tag)
        
        # Calculate element length
        length = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)
        element_data.append({
            'elem_id': elem_id,
            'type': etype,
            'node_i': n1,
            'node_j': n2,
            'length': length,
            'tower': row.get('tower', 'unknown')
        })
        frame_count += 1
    except Exception as e:
        if frame_count < 5:
            print(f"  Element error: {e}")

print(f"Created {frame_count} frame elements")

# ---------------------------------------------------------------------------
# Add Masses (Self-weight based)
# ---------------------------------------------------------------------------
print("\n--- ADDING MASS (Self-weight) ---")

# Calculate total structural mass from element lengths
total_length_mm = 0
for elem in element_data:
    total_length_mm += elem['length']

# Balsa density = 160 kg/m³ = 160e-9 kg/mm³
# 6x6mm section = 36 mm² = 36e-6 m²/mm length
structural_mass_kg = total_length_mm * FRAME_A * BALSA_DENSITY
print(f"  Total element length: {total_length_mm:.0f} mm")
print(f"  Estimated structural mass: {structural_mass_kg:.3f} kg")

# Distribute mass to all non-base nodes proportionally
base_z = pos_df['z_mm'].min()
non_base_nodes = pos_df[pos_df['z_mm'] > base_z + 1.0]['node_id'].tolist()
n_mass_nodes = len(non_base_nodes)

# For dynamic analysis, use test load distribution (DASK specs)
# Test loads: 1.60 kg at floors 3,6,9..24, 2.22 kg at roof
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_FLOOR_ROOF = 25
MASS_PER_FLOOR_KG = 1.60  # kg per floor (both towers combined)
MASS_ROOF_KG = 2.22       # kg total for roof

# Group nodes by floor
floor_nodes = {}
for idx, row in pos_df.iterrows():
    floor = int(row['floor'])
    node_id = int(row['node_id'])
    if floor not in floor_nodes:
        floor_nodes[floor] = []
    floor_nodes[floor].append(node_id)

MASS_CONVERSION = 1e-3  # kg to N·s²/mm (since F=N, a=mm/s², m must be in N·s²/mm)

total_mass_kg = 0.0
mass_count = 0

print(f"\n  Applying test load mass distribution:")

# 1.60 kg floors
for floor in MASS_FLOORS:
    if floor in floor_nodes:
        n_nodes_floor = len(floor_nodes[floor])
        mass_per_node_kg = MASS_PER_FLOOR_KG / n_nodes_floor
        mass_value = mass_per_node_kg * MASS_CONVERSION
        
        for node_id in floor_nodes[floor]:
            ops.mass(node_id + 1, mass_value, mass_value, 0.0, 0.0, 0.0, 0.0)
            mass_count += 1
        
        total_mass_kg += MASS_PER_FLOOR_KG
        print(f"    Floor {floor}: {MASS_PER_FLOOR_KG:.2f} kg -> {n_nodes_floor} nodes")

# Roof mass
if MASS_FLOOR_ROOF in floor_nodes:
    n_nodes_floor = len(floor_nodes[MASS_FLOOR_ROOF])
    mass_per_node_kg = MASS_ROOF_KG / n_nodes_floor
    mass_value = mass_per_node_kg * MASS_CONVERSION
    
    for node_id in floor_nodes[MASS_FLOOR_ROOF]:
        ops.mass(node_id + 1, mass_value, mass_value, 0.0, 0.0, 0.0, 0.0)
        mass_count += 1
    
    total_mass_kg += MASS_ROOF_KG
    print(f"    Floor {MASS_FLOOR_ROOF} (roof): {MASS_ROOF_KG:.2f} kg -> {n_nodes_floor} nodes")

print(f"\n  Total test load mass: {total_mass_kg:.2f} kg applied to {mass_count} nodes")

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

    print(f"\n  {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12}")
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
# Static Analysis for Element Forces
# ---------------------------------------------------------------------------
print("\n--- STATIC ANALYSIS (Stress Check) ---")

# Reset for static analysis
ops.wipeAnalysis()
ops.loadConst('-time', 0.0)

# Create static load pattern (gravity + lateral)
g_accel = 9810  # mm/s²
lateral_factor = 0.4  # 0.4g lateral load

# Pattern for lateral load (X direction)
ops.timeSeries('Linear', 100)
ops.pattern('Plain', 100, 100)

# Apply lateral forces at mass locations
print("  Applying lateral loads (0.4g X-direction)...")
for floor in MASS_FLOORS + [MASS_FLOOR_ROOF]:
    if floor in floor_nodes:
        n_nodes_floor = len(floor_nodes[floor])
        if floor == MASS_FLOOR_ROOF:
            floor_mass = MASS_ROOF_KG
        else:
            floor_mass = MASS_PER_FLOOR_KG
        
        force_per_node = (floor_mass * g_accel * lateral_factor) / n_nodes_floor  # N
        
        for node_id in floor_nodes[floor]:
            try:
                ops.load(node_id + 1, force_per_node, 0.0, 0.0, 0.0, 0.0, 0.0)
            except:
                pass

# Run static analysis
ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.algorithm('Newton')
ops.integrator('LoadControl', 1.0)
ops.analysis('Static')

start = time.time()
ok = ops.analyze(1)

if ok == 0:
    print(f"  Static analysis completed in {time.time()-start:.2f}s")
else:
    print(f"  Static analysis failed!")

# Get element forces
print("\n--- ELEMENT FORCES & STRESSES ---")

stress_results = []

for elem in element_data:
    elem_id = elem['elem_id']
    etype = elem['type']
    length = elem['length']
    
    try:
        # Get element forces [P, Vy, Vz, T, My, Mz] at node i
        forces_i = ops.eleForce(elem_id)  # Returns 12 values (6 at each end)
        
        if len(forces_i) >= 6:
            # Axial force (tension positive)
            P = forces_i[0]  # N
            Vy = forces_i[1]
            Vz = forces_i[2]
            T = forces_i[3]   # Torsion
            My = forces_i[4]  # Moment about Y
            Mz = forces_i[5]  # Moment about Z
            
            # Calculate stresses
            axial_stress = P / FRAME_A  # MPa (N/mm²)
            
            # Bending stress (max at extreme fiber)
            c = FRAME_SIZE / 2  # Distance to extreme fiber
            bending_stress_y = My * c / FRAME_I
            bending_stress_z = Mz * c / FRAME_I
            
            # Combined stress (max)
            max_stress = abs(axial_stress) + abs(bending_stress_y) + abs(bending_stress_z)
            
            # Shear stress
            shear_stress = np.sqrt(Vy**2 + Vz**2) / FRAME_A * 1.5  # Factor for rectangular section
            
            stress_results.append({
                'elem_id': elem_id,
                'type': etype,
                'tower': elem['tower'],
                'length': length,
                'axial_force_N': P,
                'shear_Vy_N': Vy,
                'shear_Vz_N': Vz,
                'torsion_Nmm': T,
                'moment_My_Nmm': My,
                'moment_Mz_Nmm': Mz,
                'axial_stress_MPa': axial_stress,
                'bending_stress_MPa': abs(bending_stress_y) + abs(bending_stress_z),
                'combined_stress_MPa': max_stress,
                'shear_stress_MPa': shear_stress
            })
    except Exception as e:
        pass

stress_df = pd.DataFrame(stress_results)

if len(stress_df) > 0:
    print(f"\n  Analyzed {len(stress_df)} elements")
    
    # Summary by element type
    print("\n  STRESS SUMMARY BY ELEMENT TYPE:")
    print(f"  {'Type':<20} {'Count':<8} {'Max Axial':<12} {'Max Combined':<12} {'Max Shear'}")
    print(f"  {'-'*20} {'-'*8} {'-'*12} {'-'*12} {'-'*10}")
    
    for etype in stress_df['type'].unique():
        type_df = stress_df[stress_df['type'] == etype]
        count = len(type_df)
        max_axial = type_df['axial_stress_MPa'].abs().max()
        max_combined = type_df['combined_stress_MPa'].max()
        max_shear = type_df['shear_stress_MPa'].max()
        print(f"  {etype:<20} {count:<8} {max_axial:<12.3f} {max_combined:<12.3f} {max_shear:.3f}")
    
    # Overall maximum
    print(f"\n  OVERALL MAXIMUM STRESSES:")
    print(f"    Max Axial Stress:    {stress_df['axial_stress_MPa'].abs().max():.3f} MPa")
    print(f"    Max Combined Stress: {stress_df['combined_stress_MPa'].max():.3f} MPa")
    print(f"    Max Shear Stress:    {stress_df['shear_stress_MPa'].max():.3f} MPa")
    
    # Critical elements (top 10 by combined stress)
    print("\n  TOP 10 CRITICAL ELEMENTS (by combined stress):")
    critical = stress_df.nlargest(10, 'combined_stress_MPa')
    print(f"  {'ID':<6} {'Type':<18} {'Tower':<8} {'Combined (MPa)':<15} {'Axial (MPa)'}")
    for _, row in critical.iterrows():
        print(f"  {row['elem_id']:<6} {row['type']:<18} {row['tower']:<8} {row['combined_stress_MPa']:<15.3f} {row['axial_stress_MPa']:.3f}")
    
    # Save stress results
    stress_df.to_csv(os.path.join(RESULTS_DIR, 'twin_towers_stress_results.csv'), index=False)
    print(f"\n  Stress results saved to twin_towers_stress_results.csv")

# ---------------------------------------------------------------------------
# Response Spectrum Analysis
# ---------------------------------------------------------------------------
print("\n--- RESPONSE SPECTRUM ANALYSIS ---")

# EC8 Type 1 spectrum parameters
ag = 0.4 * 9810  # Design ground acceleration in mm/s² (0.4g)
S = 1.0
TB, TC, TD = 0.15, 0.5, 2.0
eta = 1.0

def ec8_spectrum(T):
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

print("  Computing spectral response...")

rs_results = {'RSX': {'ux': 0, 'uy': 0}, 'RSY': {'ux': 0, 'uy': 0}}

if len(eigenvalues) > 0:
    max_ux_x = 0
    max_uy_y = 0

    for node_id in pos_df['node_id'].tolist():
        ops_node = node_id + 1
        
        ux_modal = []
        uy_modal = []
        
        for mode in range(1, min(len(eigenvalues)+1, 7)):
            try:
                phi_x = ops.nodeEigenvector(ops_node, mode, 1)
                phi_y = ops.nodeEigenvector(ops_node, mode, 2)
                ux_modal.append(phi_x)
                uy_modal.append(phi_y)
            except:
                ux_modal.append(0)
                uy_modal.append(0)
        
        ux_srss_x = 0
        uy_srss_y = 0
        
        for i, (T, phi_x, phi_y) in enumerate(zip(periods[:6], ux_modal[:6], uy_modal[:6])):
            Sa = ec8_spectrum(T)
            Sd = Sa * (T / (2*np.pi))**2
            ux_srss_x += (phi_x * Sd) ** 2
            uy_srss_y += (phi_y * Sd) ** 2
        
        ux_srss_x = np.sqrt(ux_srss_x)
        uy_srss_y = np.sqrt(uy_srss_y)
        
        max_ux_x = max(max_ux_x, abs(ux_srss_x))
        max_uy_y = max(max_uy_y, abs(uy_srss_y))

    rs_results['RSX']['ux'] = max_ux_x
    rs_results['RSY']['uy'] = max_uy_y
    
    print(f"\n  RS Results (SRSS):")
    print(f"    RSX: Max Ux = {max_ux_x:.3f} mm")
    print(f"    RSY: Max Uy = {max_uy_y:.3f} mm")

# ---------------------------------------------------------------------------
# Time History Analysis (X direction)
# ---------------------------------------------------------------------------
print("\n--- TIME HISTORY ANALYSIS ---")

ops.wipeAnalysis()
ops.remove('loadPattern', 100)
ops.loadConst('-time', 0.0)
ops.setTime(0.0)

# Create time series
acc_mms2 = acc_g * 9810.0  # mm/s²
ts_tag = 1
ops.timeSeries('Path', ts_tag, '-dt', dt, '-values', *acc_mms2.tolist(), '-factor', 1.0)

# X-direction excitation
ops.pattern('UniformExcitation', 1, 1, '-accel', ts_tag)

# Rayleigh damping
if len(eigenvalues) >= 2:
    omega1 = np.sqrt(eigenvalues[0])
    omega2 = np.sqrt(eigenvalues[1])
    zeta = 0.05
    a0 = 2 * zeta * omega1 * omega2 / (omega1 + omega2)
    a1 = 2 * zeta / (omega1 + omega2)
    ops.rayleigh(a0, 0.0, 0.0, a1)

ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.algorithm('Newton')

analysis_dt = 0.02
total_time = min(time_arr[-1], 10.0)
num_steps = int(total_time / analysis_dt)

ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')

print(f"  Running TH X-direction ({total_time:.1f}s)...")
start = time.time()

max_ux_th = 0
max_uy_th = 0

for i in range(num_steps):
    ok = ops.analyze(1, analysis_dt)
    if ok != 0:
        ok = ops.analyze(10, analysis_dt/10)
    
    for node_id in top_nodes:
        try:
            ux = ops.nodeDisp(node_id + 1, 1)
            uy = ops.nodeDisp(node_id + 1, 2)
            max_ux_th = max(max_ux_th, abs(ux))
            max_uy_th = max(max_uy_th, abs(uy))
        except:
            pass
    
    if (i+1) % 250 == 0:
        print(f"    Step {i+1}/{num_steps}, Max Ux={max_ux_th:.3f}mm")

print(f"  Completed in {time.time()-start:.1f}s")
print(f"  TH_X: Max Ux = {max_ux_th:.3f} mm, Max Uy = {max_uy_th:.3f} mm")

th_results = {'TH_X': {'ux': max_ux_th, 'uy': max_uy_th}}

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("TWIN TOWERS ANALYSIS SUMMARY")
print("=" * 70)

print(f"\nModel:")
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")
print(f"  Height: {max_z:.0f}m model -> {max_z_mm:.0f}mm maket")
print(f"  Total test load mass: {total_mass_kg:.2f} kg")

print(f"\nModal Analysis:")
print(f"  Fundamental Period T1 = {T1:.4f} s")

print(f"\nDisplacements:")
print(f"  {'Analysis':<15} {'Max Ux (mm)':<15} {'Max Uy (mm)'}")
print(f"  {'-'*45}")
print(f"  {'RS X-dir':<15} {rs_results['RSX']['ux']:<15.2f} {rs_results['RSX']['uy']:.2f}")
print(f"  {'RS Y-dir':<15} {rs_results['RSY']['ux']:<15.2f} {rs_results['RSY']['uy']:.2f}")
print(f"  {'TH X-dir':<15} {th_results['TH_X']['ux']:<15.2f} {th_results['TH_X']['uy']:.2f}")

max_disp = max(rs_results['RSX']['ux'], rs_results['RSY']['uy'], th_results['TH_X']['ux'])
drift_ratio = max_disp / max_z_mm * 100
print(f"\n  Max Displacement: {max_disp:.2f} mm")
print(f"  Drift Ratio: {drift_ratio:.3f}%")

if len(stress_df) > 0:
    print(f"\nStress Analysis (0.4g static):")
    print(f"  Max Combined Stress: {stress_df['combined_stress_MPa'].max():.3f} MPa")
    print(f"  Max Shear Stress: {stress_df['shear_stress_MPa'].max():.3f} MPa")

# Save summary results
summary_df = pd.DataFrame({
    'Analysis': ['RSX', 'RSY', 'TH_X', 'ENVELOPE'],
    'Max_Ux_mm': [rs_results['RSX']['ux'], rs_results['RSY']['ux'], 
                  th_results['TH_X']['ux'], max_disp],
    'Max_Uy_mm': [rs_results['RSX']['uy'], rs_results['RSY']['uy'],
                  th_results['TH_X']['uy'], max(rs_results['RSY']['uy'], th_results['TH_X']['uy'])]
})
summary_df.to_csv(os.path.join(RESULTS_DIR, 'twin_towers_earthquake_results.csv'), index=False)
print(f"\nResults saved to {RESULTS_DIR}")

ops.wipe()
print("\nAnalysis complete.")
