"""
TIME HISTORY ANALYSIS FOR MODEL V8 (1:50 SCALE)
================================================
- Uses scaled ground motion: 1/sqrt(50) acceleration scaling
- Modal analysis with natural periods
- Time history analysis with Newmark integration
- AFAD spectrum comparison (DD1 parameters)

Scale Model Similitude (1:50):
- Geometric Scale: lambda = 50
- Acceleration Scale: 1/sqrt(lambda) = 0.1414
- Time Scale: sqrt(lambda) = 7.071 (for prototype-to-model)
- Period Scale: sqrt(lambda) = 7.071 (T_model = T_prototype / sqrt(lambda))
"""

import os
import sys
import numpy as np
import pandas as pd
import openseespy.opensees as ops
import time
import re

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, 'data')
RESULTS_DIR = os.path.join(BASE_DIR, 'results', 'data')
GROUND_MOTION_DIR = os.path.join(BASE_DIR, 'ground_motion')

# Use SCALED ground motion for 1:50 model
SCALED_AT2_FILE = os.path.join(GROUND_MOTION_DIR, 'BOL090_scaled_1_50.AT2')
ORIGINAL_AT2_FILE = os.path.join(GROUND_MOTION_DIR, 'BOL090.AT2')

os.makedirs(RESULTS_DIR, exist_ok=True)

# ===========================================================================
# SCALE MODEL PARAMETERS (1:50)
# ===========================================================================
SCALE_FACTOR = 50
ACC_SCALE = 1.0 / np.sqrt(SCALE_FACTOR)  # 0.1414
TIME_SCALE = np.sqrt(SCALE_FACTOR)        # 7.071
PERIOD_SCALE = np.sqrt(SCALE_FACTOR)      # T_prototype = T_model * sqrt(50)

print("=" * 70)
print("DASK 2026 MODEL V8 - TIME HISTORY ANALYSIS (1:50 SCALE)")
print("=" * 70)
print(f"\nScale Model: 1:{SCALE_FACTOR}")
print(f"  Acceleration Scale: 1/sqrt({SCALE_FACTOR}) = {ACC_SCALE:.4f}")
print(f"  Time/Period Scale: sqrt({SCALE_FACTOR}) = {TIME_SCALE:.3f}")

# ===========================================================================
# AFAD SPECTRUM PARAMETERS (DD-1 DUZCE)
# ===========================================================================
# From afad_reports/DD1.pdf
AFAD_SS = 1.544      # Short period spectral acceleration coefficient
AFAD_S1 = 0.427      # 1.0 sec period spectral acceleration coefficient
AFAD_PGA = 0.628     # Peak ground acceleration (g)
AFAD_PGV = 38.949    # Peak ground velocity (cm/s)

# Site coefficients for ZD soil
AFAD_FS = 1.000      # Short period site factor
AFAD_F1 = 1.873      # 1.0 sec period site factor

# Design spectral accelerations
AFAD_SDS = AFAD_SS * AFAD_FS  # 1.544 g
AFAD_SD1 = AFAD_S1 * AFAD_F1  # 0.800 g

# Corner periods
AFAD_TA = 0.104      # s
AFAD_TB = 0.518      # s
AFAD_TL = 6.000      # s

print("\nAFAD DD-1 Spectrum Parameters:")
print(f"  SDS = {AFAD_SDS:.3f} g")
print(f"  SD1 = {AFAD_SD1:.3f} g")
print(f"  TA = {AFAD_TA:.3f} s, TB = {AFAD_TB:.3f} s, TL = {AFAD_TL:.3f} s")

# ===========================================================================
# MATERIAL PROPERTIES (Balsa Wood)
# ===========================================================================
BALSA_E = 3500.0        # MPa = N/mm^2
BALSA_DENSITY = 160e-9  # kg/mm^3 (160 kg/m^3)
BALSA_NU = 0.3
BALSA_G = BALSA_E / (2 * (1 + BALSA_NU))

# Section properties (6x6 mm frame members)
FRAME_SIZE = 6.0   # mm
FRAME_A = FRAME_SIZE ** 2                  # 36 mm^2
FRAME_I = (FRAME_SIZE ** 4) / 12           # 108 mm^4
FRAME_J = 0.1406 * FRAME_SIZE ** 4         # Torsional constant

# Model scale: coordinates in CM, convert to MM for OpenSees
COORD_SCALE = 10.0  # 1 cm = 10 mm

# ===========================================================================
# PARSE AT2 FILE
# ===========================================================================
def parse_at2(filepath):
    """Parse PEER AT2 format ground motion file."""
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

    time_arr = np.arange(npts) * dt
    return time_arr, np.array(acc_values[:npts]), dt, npts

# ===========================================================================
# AFAD TBDY 2018 SPECTRUM FUNCTION
# ===========================================================================
def afad_spectrum(T, SDS=AFAD_SDS, SD1=AFAD_SD1, TA=AFAD_TA, TB=AFAD_TB, TL=AFAD_TL):
    """
    TBDY 2018 Horizontal Elastic Design Spectrum
    Returns Sae(T) in g units
    """
    if T <= 0:
        return SDS
    elif T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T < TB:
        return SDS
    elif T < TL:
        return SD1 / T
    else:
        return SD1 * TL / (T ** 2)

# ===========================================================================
# LOAD GROUND MOTION
# ===========================================================================
print("\n--- LOADING GROUND MOTION ---")

# Check if scaled file exists
if os.path.exists(SCALED_AT2_FILE):
    print(f"Using SCALED ground motion: BOL090_scaled_1_50.AT2")
    time_arr, acc_g, dt, npts = parse_at2(SCALED_AT2_FILE)
    ground_motion_type = "SCALED (1/sqrt(50))"
else:
    print(f"Scaled file not found! Using original and applying scale factor.")
    time_arr, acc_g_orig, dt, npts = parse_at2(ORIGINAL_AT2_FILE)
    acc_g = acc_g_orig * ACC_SCALE
    ground_motion_type = "ORIGINAL * ACC_SCALE"

pga = np.max(np.abs(acc_g))
print(f"  Ground Motion Type: {ground_motion_type}")
print(f"  Duration: {time_arr[-1]:.1f} s")
print(f"  Time Step: {dt} s")
print(f"  NPTS: {npts}")
print(f"  PGA (scaled): {pga:.4f} g ({pga * 9.81:.3f} m/s^2)")

# ===========================================================================
# LOAD MODEL DATA
# ===========================================================================
print("\n--- LOADING MODEL V8 DATA ---")

pos_csv = os.path.join(DATA_DIR, 'twin_position_matrix.csv')
conn_csv = os.path.join(DATA_DIR, 'twin_connectivity_matrix.csv')

if not os.path.exists(pos_csv) or not os.path.exists(conn_csv):
    print("ERROR: Model data files not found!")
    print("Run regenerate_twin_model_v8.py first.")
    sys.exit(1)

pos_df = pd.read_csv(pos_csv)
conn_df = pd.read_csv(conn_csv)

n_nodes = len(pos_df)
n_elements = len(conn_df)

# Convert coordinates from CM to MM
pos_df['x_mm'] = pos_df['x'] * COORD_SCALE
pos_df['y_mm'] = pos_df['y'] * COORD_SCALE
pos_df['z_mm'] = pos_df['z'] * COORD_SCALE

max_z_cm = pos_df['z'].max()
max_z_mm = max_z_cm * COORD_SCALE
total_floors = pos_df['floor'].max() + 1

print(f"  Nodes: {n_nodes}")
print(f"  Elements: {n_elements}")
print(f"  Floors: {total_floors}")
print(f"  Height: {max_z_cm:.1f} cm = {max_z_mm:.0f} mm")

# Get roof nodes
roof_nodes = pos_df[pos_df['z'] == max_z_cm]['node_id'].tolist()
print(f"  Roof nodes: {len(roof_nodes)}")

# ===========================================================================
# BUILD OPENSEES MODEL
# ===========================================================================
print("\n--- BUILDING OPENSEES MODEL ---")

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Geometric transformations
ops.geomTransf('Linear', 1, 0, 1, 0)   # Vertical (Z-axis)
ops.geomTransf('Linear', 2, 0, 0, 1)   # Y-direction
ops.geomTransf('Linear', 3, 0, 1, 0)   # X-direction

# Create nodes
print(f"  Creating {n_nodes} nodes...")
node_coords = {}

for _, row in pos_df.iterrows():
    nid = int(row['node_id']) + 1
    x, y, z = float(row['x_mm']), float(row['y_mm']), float(row['z_mm'])
    node_coords[int(row['node_id'])] = (x, y, z)
    ops.node(nid, x, y, z)

# Fix base nodes
base_z = pos_df['z_mm'].min()
count_fix = 0
for _, row in pos_df.iterrows():
    if abs(row['z_mm'] - base_z) < 1.0:
        nid = int(row['node_id']) + 1
        ops.fix(nid, 1, 1, 1, 1, 1, 1)
        count_fix += 1

print(f"  Fixed {count_fix} base nodes")

# Create material
mat_tag = 1
ops.uniaxialMaterial('Elastic', mat_tag, BALSA_E)

# Create elements
print(f"  Creating elements...")
frame_count = 0
element_data = []

for _, row in conn_df.iterrows():
    etype = row['element_type']
    n1, n2 = int(row['node_i']), int(row['node_j'])
    elem_id = int(row['element_id']) + 1

    p1 = node_coords.get(n1)
    p2 = node_coords.get(n2)

    if p1 is None or p2 is None:
        continue

    # Determine transformation
    dz = abs(p2[2] - p1[2])
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    if dz > max(dx, dy):
        transf_tag = 1
    elif dx > dy:
        transf_tag = 3
    else:
        transf_tag = 2

    try:
        ops.element('elasticBeamColumn', elem_id,
                   n1 + 1, n2 + 1,
                   FRAME_A, BALSA_E, BALSA_G, FRAME_J, FRAME_I, FRAME_I,
                   transf_tag)

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
        pass

print(f"  Created {frame_count} frame elements")

# ===========================================================================
# MASS DISTRIBUTION (DASK 2026 Test Loads)
# ===========================================================================
print("\n--- APPLYING MASS DISTRIBUTION ---")

# DASK 2026 test loads per tower:
# 1.60 kg at floors 3, 6, 9, 12, 15, 18, 21, 24
# 2.22 kg at roof (floor 25)
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_FLOOR_ROOF = 25
MASS_PER_FLOOR_KG = 1.60
MASS_ROOF_KG = 2.22

# Group nodes by floor
floor_nodes = {}
for _, row in pos_df.iterrows():
    floor = int(row['floor'])
    node_id = int(row['node_id'])
    if floor not in floor_nodes:
        floor_nodes[floor] = []
    floor_nodes[floor].append(node_id)

# Mass conversion: kg to N*s^2/mm
MASS_CONVERSION = 1e-3

total_mass_kg = 0.0
mass_count = 0

# Apply floor masses
for floor in MASS_FLOORS:
    if floor in floor_nodes:
        n_floor_nodes = len(floor_nodes[floor])
        mass_per_node = MASS_PER_FLOOR_KG / n_floor_nodes * MASS_CONVERSION

        for node_id in floor_nodes[floor]:
            ops.mass(node_id + 1, mass_per_node, mass_per_node, 0.0, 0.0, 0.0, 0.0)
            mass_count += 1

        total_mass_kg += MASS_PER_FLOOR_KG

# Apply roof mass
if MASS_FLOOR_ROOF in floor_nodes:
    n_floor_nodes = len(floor_nodes[MASS_FLOOR_ROOF])
    mass_per_node = MASS_ROOF_KG / n_floor_nodes * MASS_CONVERSION

    for node_id in floor_nodes[MASS_FLOOR_ROOF]:
        ops.mass(node_id + 1, mass_per_node, mass_per_node, 0.0, 0.0, 0.0, 0.0)
        mass_count += 1

    total_mass_kg += MASS_ROOF_KG

print(f"  Total test load mass: {total_mass_kg:.2f} kg")
print(f"  Mass applied to {mass_count} nodes")

# ===========================================================================
# MODAL ANALYSIS
# ===========================================================================
print("\n--- MODAL ANALYSIS ---")

num_modes = 12
start_time = time.time()

try:
    eigenvalues = ops.eigen(num_modes)
    print(f"  Completed in {time.time() - start_time:.2f}s")

    periods_model = []
    frequencies = []

    print(f"\n  MODE SHAPES AND PERIODS:")
    print(f"  {'Mode':<6} {'T_model (s)':<14} {'f (Hz)':<12} {'T_prototype (s)':<16} {'Sae (g)'}")
    print(f"  {'-'*70}")

    for i, ev in enumerate(eigenvalues[:8]):
        if ev > 0:
            omega = np.sqrt(ev)
            T_model = 2 * np.pi / omega
            f = 1 / T_model
            T_prototype = T_model * PERIOD_SCALE  # Scale to prototype
            Sae = afad_spectrum(T_prototype)

            periods_model.append(T_model)
            frequencies.append(f)

            print(f"  {i+1:<6} {T_model:<14.4f} {f:<12.2f} {T_prototype:<16.4f} {Sae:.3f}")

    T1_model = periods_model[0] if periods_model else 0
    T1_prototype = T1_model * PERIOD_SCALE

    print(f"\n  FUNDAMENTAL PERIOD:")
    print(f"    Model (1:{SCALE_FACTOR}): T1 = {T1_model:.4f} s ({1/T1_model:.2f} Hz)")
    print(f"    Prototype:       T1 = {T1_prototype:.4f} s ({1/T1_prototype:.2f} Hz)")

except Exception as e:
    print(f"  Modal analysis error: {e}")
    eigenvalues = []
    periods_model = []

# ===========================================================================
# TIME HISTORY ANALYSIS
# ===========================================================================
print("\n--- TIME HISTORY ANALYSIS ---")

ops.wipeAnalysis()
ops.loadConst('-time', 0.0)
ops.setTime(0.0)

# Convert acceleration to mm/s^2
acc_mms2 = acc_g * 9810.0

# Create time series
ts_tag = 1
ops.timeSeries('Path', ts_tag, '-dt', dt, '-values', *acc_mms2.tolist(), '-factor', 1.0)

# X-direction excitation
ops.pattern('UniformExcitation', 1, 1, '-accel', ts_tag)

# Rayleigh damping (5%)
if len(eigenvalues) >= 2:
    omega1 = np.sqrt(eigenvalues[0])
    omega2 = np.sqrt(eigenvalues[1])
    zeta = 0.05
    a0 = 2 * zeta * omega1 * omega2 / (omega1 + omega2)
    a1 = 2 * zeta / (omega1 + omega2)
    ops.rayleigh(a0, 0.0, 0.0, a1)
    print(f"  Rayleigh damping: zeta = {zeta*100:.0f}%")

# Analysis parameters
ops.constraints('Plain')
ops.numberer('RCM')
ops.system('BandGeneral')
ops.test('NormDispIncr', 1.0e-6, 100)
ops.algorithm('Newton')

# Time stepping
analysis_dt = 0.005  # 5ms for accuracy
total_time = min(time_arr[-1], 20.0)  # First 20 seconds
num_steps = int(total_time / analysis_dt)

ops.integrator('Newmark', 0.5, 0.25)
ops.analysis('Transient')

print(f"  Duration: {total_time:.1f} s")
print(f"  Time step: {analysis_dt} s")
print(f"  Total steps: {num_steps}")
print(f"\n  Running time history analysis (X-direction)...")

start_time = time.time()

# Storage for results
time_history = []
max_ux = 0
max_uy = 0
max_uz = 0
max_base_shear = 0

for step in range(num_steps):
    ok = ops.analyze(1, analysis_dt)

    if ok != 0:
        # Try smaller time steps
        ok = ops.analyze(10, analysis_dt / 10)

    current_time = ops.getTime()

    # Record roof displacements
    ux_max_step = 0
    uy_max_step = 0

    for node_id in roof_nodes:
        try:
            ux = ops.nodeDisp(node_id + 1, 1)
            uy = ops.nodeDisp(node_id + 1, 2)
            uz = ops.nodeDisp(node_id + 1, 3)

            ux_max_step = max(ux_max_step, abs(ux))
            uy_max_step = max(uy_max_step, abs(uy))
            max_uz = max(max_uz, abs(uz))
        except:
            pass

    max_ux = max(max_ux, ux_max_step)
    max_uy = max(max_uy, uy_max_step)

    # Record time history
    if step % 20 == 0:
        time_history.append({
            'time': current_time,
            'ux': ux_max_step,
            'uy': uy_max_step
        })

    # Progress
    if (step + 1) % 500 == 0:
        print(f"    Step {step+1}/{num_steps}, t={current_time:.2f}s, max_Ux={max_ux:.3f}mm")

elapsed = time.time() - start_time
print(f"\n  Analysis completed in {elapsed:.1f}s")

# ===========================================================================
# RESULTS SUMMARY
# ===========================================================================
print("\n" + "=" * 70)
print("TIME HISTORY ANALYSIS RESULTS")
print("=" * 70)

print(f"\nGROUND MOTION:")
print(f"  File: BOL090_scaled_1_50.AT2 (Bolu, Duzce 1999)")
print(f"  PGA (scaled): {pga:.4f} g")
print(f"  Scale Factor: 1/sqrt({SCALE_FACTOR}) = {ACC_SCALE:.4f}")

print(f"\nMODAL PERIODS:")
print(f"  {'Mode':<6} {'T_model (s)':<14} {'T_prototype (s)':<16} {'Spectral Region'}")
print(f"  {'-'*55}")

for i, T in enumerate(periods_model[:6]):
    T_proto = T * PERIOD_SCALE
    if T_proto < AFAD_TA:
        region = "Ascending"
    elif T_proto < AFAD_TB:
        region = "Plateau (SDS)"
    elif T_proto < AFAD_TL:
        region = "Descending (1/T)"
    else:
        region = "Long period (1/T^2)"
    print(f"  {i+1:<6} {T:<14.4f} {T_proto:<16.4f} {region}")

print(f"\nMAXIMUM DISPLACEMENTS:")
print(f"  Max Ux (X-dir): {max_ux:.3f} mm")
print(f"  Max Uy (Y-dir): {max_uy:.3f} mm")
print(f"  Max Uz (Z-dir): {max_uz:.3f} mm")

# Drift ratio
drift_ratio = max_ux / max_z_mm * 100
print(f"\nDRIFT ANALYSIS:")
print(f"  Building Height: {max_z_mm:.0f} mm")
print(f"  Max Roof Drift: {max_ux:.3f} mm")
print(f"  Drift Ratio: {drift_ratio:.4f}%")

# AFAD comparison
print(f"\nAFAD SPECTRUM COMPARISON:")
print(f"  {'Period':<20} {'Sae (g)':<12} {'Region'}")
print(f"  {'-'*45}")
print(f"  {'T1_prototype':<20} {afad_spectrum(T1_prototype):<12.3f} {'Plateau' if AFAD_TA <= T1_prototype <= AFAD_TB else 'Ascending/Descending'}")
print(f"  {'TA = 0.104s':<20} {afad_spectrum(AFAD_TA):<12.3f} {'Corner'}")
print(f"  {'TB = 0.518s':<20} {afad_spectrum(AFAD_TB):<12.3f} {'Corner'}")

# ===========================================================================
# SAVE RESULTS
# ===========================================================================
print("\n--- SAVING RESULTS ---")

# Modal results
modal_results = []
for i, T in enumerate(periods_model):
    modal_results.append({
        'Mode': i + 1,
        'Period_model_s': T,
        'Frequency_Hz': 1/T if T > 0 else 0,
        'Period_prototype_s': T * PERIOD_SCALE,
        'Sae_g': afad_spectrum(T * PERIOD_SCALE)
    })

modal_df = pd.DataFrame(modal_results)
modal_df.to_csv(os.path.join(RESULTS_DIR, 'modal_results_v8_1to50.csv'), index=False)
print(f"  Modal results: modal_results_v8_1to50.csv")

# Time history results
th_df = pd.DataFrame(time_history)
th_df.to_csv(os.path.join(RESULTS_DIR, 'time_history_v8.csv'), index=False)
print(f"  Time history: time_history_v8.csv")

# Summary results
summary = {
    'Parameter': [
        'Scale_Factor', 'Acc_Scale', 'Time_Scale',
        'T1_model_s', 'T1_prototype_s', 'f1_Hz',
        'Max_Ux_mm', 'Max_Uy_mm', 'Max_Uz_mm',
        'Drift_Ratio_pct', 'Height_mm',
        'PGA_scaled_g', 'Sae_T1_g',
        'SDS_g', 'SD1_g', 'TA_s', 'TB_s'
    ],
    'Value': [
        SCALE_FACTOR, ACC_SCALE, TIME_SCALE,
        T1_model, T1_prototype, 1/T1_model if T1_model > 0 else 0,
        max_ux, max_uy, max_uz,
        drift_ratio, max_z_mm,
        pga, afad_spectrum(T1_prototype),
        AFAD_SDS, AFAD_SD1, AFAD_TA, AFAD_TB
    ]
}
summary_df = pd.DataFrame(summary)
summary_df.to_csv(os.path.join(RESULTS_DIR, 'th_summary_v8.csv'), index=False)
print(f"  Summary: th_summary_v8.csv")

# Cleanup
ops.wipe()

print("\n" + "=" * 70)
print("ANALYSIS COMPLETE")
print("=" * 70)
print(f"\nKey Results:")
print(f"  - Fundamental Period (model): {T1_model:.4f} s")
print(f"  - Fundamental Period (prototype): {T1_prototype:.4f} s")
print(f"  - Maximum Roof Displacement: {max_ux:.3f} mm")
print(f"  - Drift Ratio: {drift_ratio:.4f}%")
print(f"  - Spectral Acceleration at T1: {afad_spectrum(T1_prototype):.3f} g")
