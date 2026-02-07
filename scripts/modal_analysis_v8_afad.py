"""
MODAL ANALYSIS FOR MODEL V8 WITH AFAD SPECTRUM COMPARISON
==========================================================
1:50 Scale Model - Twin Towers DASK 2026

Key Parameters (Calibrated):
- E = 170 kN/cm^2 (calibrated for T ~ 0.20s)
- Section: 6mm x 6mm (all members)
- Units: kN, cm, s

AFAD Spectrum Parameters (DD-1 to DD-4):
- Location: Istanbul (41.002N, 29.107E)
- Soil Class: ZD
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path

# Set working directory
WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("MODAL ANALYSIS - MODEL V8 (1:50 SCALE) WITH AFAD SPECTRUM")
print("=" * 80)

# ==============================================================================
# 1. LOAD MODEL DATA
# ==============================================================================
print("\n[1] LOADING MODEL V8 DATA...")

pos_df = pd.read_csv('data/twin_position_matrix.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix.csv')

n_nodes = len(pos_df)
n_elements = len(conn_df)
H_max = pos_df['z'].max()
total_floors = pos_df['floor'].max() + 1

print(f"    Nodes: {n_nodes}")
print(f"    Elements: {n_elements}")
print(f"    Floors: {total_floors}")
print(f"    Height: {H_max} cm = {H_max/100:.2f} m (model)")
print(f"    Prototype Height: {H_max * 50 / 100:.1f} m (1:50 scale)")

# ==============================================================================
# 2. CALIBRATED MATERIAL PROPERTIES
# ==============================================================================
print("\n[2] CALIBRATED MATERIAL PROPERTIES...")

# CALIBRATED E for target T ~ 0.20s
# Standard balsa E ~ 350 kN/cm^2, but joints reduce effective stiffness
E = 170.0         # kN/cm^2 (CALIBRATED)
G = E / 2.6       # kN/cm^2 (nu = 0.3)
nu = 0.3

# Section: 6mm x 6mm = 0.6cm x 0.6cm
b = 0.6           # cm
A = b * b         # cm^2 = 0.36
Iz = (b**4) / 12  # cm^4
Iy = (b**4) / 12  # cm^4
J = 0.1406 * b**4 # cm^4 (torsional constant)

print(f"    E = {E:.1f} kN/cm^2 ({E*10:.0f} MPa) [CALIBRATED]")
print(f"    G = {G:.2f} kN/cm^2")
print(f"    Section: {b*10:.0f}mm x {b*10:.0f}mm")
print(f"    A = {A:.4f} cm^2")
print(f"    I = {Iz:.6f} cm^4")

# ==============================================================================
# 3. AFAD SPECTRUM PARAMETERS
# ==============================================================================
print("\n[3] AFAD SPECTRUM PARAMETERS (TBDY 2018)...")

AFAD_SPECTRUM = {
    'DD-1': {  # 2475 year return (2% in 50 years) - Maximum Considered
        'SS': 1.544, 'S1': 0.427, 'FS': 1.000, 'F1': 1.873,
        'SDS': 1.544, 'SD1': 0.800,
        'TA': 0.104, 'TB': 0.518, 'TL': 6.0,
        'PGA': 0.628
    },
    'DD-2': {  # 475 year return (10% in 50 years) - Design Earthquake
        'SS': 0.877, 'S1': 0.243, 'FS': 1.149, 'F1': 2.114,
        'SDS': 1.008, 'SD1': 0.514,
        'TA': 0.102, 'TB': 0.510, 'TL': 6.0,
        'PGA': 0.362
    },
    'DD-3': {  # 72 year return (50% in 50 years)
        'SS': 0.358, 'S1': 0.099, 'FS': 1.514, 'F1': 2.400,
        'SDS': 0.542, 'SD1': 0.238,
        'TA': 0.088, 'TB': 0.438, 'TL': 6.0,
        'PGA': 0.152
    },
    'DD-4': {  # 43 year return (68% in 50 years) - Serviceability
        'SS': 0.240, 'S1': 0.066, 'FS': 1.600, 'F1': 2.400,
        'SDS': 0.384, 'SD1': 0.158,
        'TA': 0.083, 'TB': 0.412, 'TL': 6.0,
        'PGA': 0.102
    }
}

print(f"\n    {'Level':<8} {'SDS (g)':<10} {'SD1 (g)':<10} {'TA (s)':<10} {'TB (s)':<10} {'PGA (g)'}")
print("    " + "-" * 58)
for dd, params in AFAD_SPECTRUM.items():
    print(f"    {dd:<8} {params['SDS']:<10.3f} {params['SD1']:<10.3f} {params['TA']:<10.3f} {params['TB']:<10.3f} {params['PGA']:.3f}")

# Spectrum functions
def get_Sae(T, dd='DD-2'):
    """TBDY 2018 Horizontal Elastic Design Spectrum Sae(T)"""
    p = AFAD_SPECTRUM[dd]
    if T <= 0:
        return p['SDS']
    elif T < p['TA']:
        return p['SDS'] * (0.4 + 0.6 * T / p['TA'])
    elif T < p['TB']:
        return p['SDS']
    elif T < p['TL']:
        return p['SD1'] / T
    else:
        return p['SD1'] * p['TL'] / (T**2)

def get_region(T, dd='DD-2'):
    """Determine spectral region"""
    p = AFAD_SPECTRUM[dd]
    if T < p['TA']:
        return "Ascending"
    elif T < p['TB']:
        return "Plateau"
    elif T < p['TL']:
        return "Descending"
    else:
        return "Long Period"

# ==============================================================================
# 4. BUILD OPENSEES MODEL
# ==============================================================================
print("\n[4] BUILDING OPENSEES MODEL...")

import openseespy.opensees as ops

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes (coordinates in CM)
print("    Creating nodes...")
node_coords = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x'], row['y'], row['z']
    ops.node(nid, x, y, z)
    node_coords[nid] = (x, y, z)

# Fix base nodes
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)
print(f"    Fixed {len(base_nodes)} base nodes")

# Geometric transformations
ops.geomTransf('Linear', 1, 1, 0, 0)  # Vertical
ops.geomTransf('Linear', 2, 0, 0, 1)  # Horizontal X
ops.geomTransf('Linear', 3, 0, 0, 1)  # Horizontal Y

# Create elements
print("    Creating elements...")
elem_count = 0
skipped = 0

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])

    if ni not in node_coords or nj not in node_coords:
        skipped += 1
        continue

    xi, yi, zi = node_coords[ni]
    xj, yj, zj = node_coords[nj]

    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 1e-6:
        skipped += 1
        continue

    dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)

    if dz > max(dx, dy) * 0.9:
        transf_tag = 1  # Vertical
    elif dx > dy:
        transf_tag = 2  # X-direction
    else:
        transf_tag = 3  # Y-direction

    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A, E, G, J, Iy, Iz, transf_tag)
        elem_count += 1
    except:
        skipped += 1

print(f"    Created {elem_count} elements (skipped {skipped})")

# ==============================================================================
# 5. APPLY DASK TEST MASSES
# ==============================================================================
print("\n[5] APPLYING DASK TEST MASSES...")

# Mass conversion: kg to kN*s^2/cm
# F = ma -> m = F/a, units: kN / (cm/s^2) = kN*s^2/cm
# 1 kg = 0.00981 kN / (981 cm/s^2) = 1e-5 kN*s^2/cm
MASS_CONV = 1e-5  # kg to kN*s^2/cm

FLOOR_MASS_KG = 1.60  # kg per floor level
ROOF_MASS_KG = 2.22   # kg at roof
WEIGHT_SPACING = 18.0 # cm between weight levels

# Find weight placement levels
available_z = sorted(pos_df[pos_df['z'] > 0]['z'].unique())
target_z = np.arange(18.0, H_max - 5, WEIGHT_SPACING)

weight_levels = []
for tz in target_z:
    closest = min(available_z, key=lambda z: abs(z - tz))
    if closest not in weight_levels and closest < H_max - 5:
        weight_levels.append(closest)

total_mass_kg = 0
Z_TOL = 0.5

print(f"\n    Weight placement (every {WEIGHT_SPACING} cm):")
for z_level in weight_levels:
    nodes_at_z = pos_df[np.abs(pos_df['z'] - z_level) < Z_TOL]['node_id'].astype(int).tolist()
    n = len(nodes_at_z)
    if n > 0:
        mass_per_node = FLOOR_MASS_KG * MASS_CONV / n
        for nid in nodes_at_z:
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
        total_mass_kg += FLOOR_MASS_KG
        print(f"      z = {z_level:6.1f} cm: {n:3d} nodes, {FLOOR_MASS_KG:.2f} kg")

# Roof mass
roof_nodes = pos_df[np.abs(pos_df['z'] - H_max) < Z_TOL]['node_id'].astype(int).tolist()
if roof_nodes:
    mass_per_node = ROOF_MASS_KG * MASS_CONV / len(roof_nodes)
    for nid in roof_nodes:
        ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
    total_mass_kg += ROOF_MASS_KG
    print(f"      z = {H_max:6.1f} cm (ROOF): {len(roof_nodes):3d} nodes, {ROOF_MASS_KG:.2f} kg")

print(f"\n    TOTAL TEST MASS: {total_mass_kg:.2f} kg")

# ==============================================================================
# 6. EIGENVALUE ANALYSIS
# ==============================================================================
print("\n[6] EIGENVALUE ANALYSIS...")

num_modes = 12
try:
    eigenvalues = ops.eigen('-genBandArpack', num_modes)
    print(f"    Computed {len(eigenvalues)} modes successfully")
except:
    eigenvalues = ops.eigen(num_modes)
    print(f"    Computed {len(eigenvalues)} modes (default solver)")

# ==============================================================================
# 7. MODAL RESULTS
# ==============================================================================
print("\n" + "=" * 80)
print("MODAL ANALYSIS RESULTS")
print("=" * 80)

modal_results = []

print(f"\n    {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12} {'omega (rad/s)':<14}")
print("    " + "-" * 44)

for i, ev in enumerate(eigenvalues):
    if ev > 0:
        omega = np.sqrt(ev)
        freq = omega / (2 * np.pi)
        period = 1.0 / freq if freq > 0 else 0

        modal_results.append({
            'mode': i + 1,
            'eigenvalue': ev,
            'omega_rad_s': omega,
            'frequency_hz': freq,
            'period_s': period
        })

        print(f"    {i+1:<6} {period:<12.4f} {freq:<12.2f} {omega:<14.2f}")

T1 = modal_results[0]['period_s'] if modal_results else 0
f1 = modal_results[0]['frequency_hz'] if modal_results else 0

print(f"\n    FUNDAMENTAL PERIOD: T1 = {T1:.4f} s ({T1*1000:.1f} ms)")
print(f"    FUNDAMENTAL FREQUENCY: f1 = {f1:.2f} Hz")

# ==============================================================================
# 8. AFAD SPECTRUM COMPARISON
# ==============================================================================
print("\n" + "=" * 80)
print("AFAD SPECTRUM COMPARISON")
print("=" * 80)

print(f"\n    Fundamental Period T1 = {T1:.4f} s")
print(f"\n    {'DD Level':<10} {'TA (s)':<10} {'TB (s)':<10} {'Region':<14} {'Sae(T1) (g)':<12} {'Status'}")
print("    " + "-" * 70)

for dd in ['DD-1', 'DD-2', 'DD-3', 'DD-4']:
    p = AFAD_SPECTRUM[dd]
    region = get_region(T1, dd)
    Sae = get_Sae(T1, dd)

    if region == "Ascending":
        status = "[OK] Reduced demand"
    elif region == "Plateau":
        status = "[!!] Maximum demand"
    else:
        status = "[OK] Reduced demand"

    # Store in results
    modal_results[0][f'Sae_{dd}'] = Sae
    modal_results[0][f'region_{dd}'] = region

    print(f"    {dd:<10} {p['TA']:<10.3f} {p['TB']:<10.3f} {region:<14} {Sae:<12.3f} {status}")

# ==============================================================================
# 9. PERIOD ANALYSIS FOR ALL MODES
# ==============================================================================
print("\n" + "=" * 80)
print("ALL MODES vs AFAD DD-2 SPECTRUM")
print("=" * 80)

dd = 'DD-2'
p = AFAD_SPECTRUM[dd]

print(f"\n    DD-2 Parameters: SDS = {p['SDS']:.3f}g, SD1 = {p['SD1']:.3f}g")
print(f"    Corner Periods: TA = {p['TA']:.3f}s, TB = {p['TB']:.3f}s")
print(f"\n    {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12} {'Sae (g)':<10} {'Region':<14}")
print("    " + "-" * 54)

for mr in modal_results:
    T = mr['period_s']
    Sae = get_Sae(T, dd)
    region = get_region(T, dd)

    mr['Sae_DD2'] = Sae
    mr['region_DD2'] = region

    print(f"    {mr['mode']:<6} {T:<12.4f} {mr['frequency_hz']:<12.2f} {Sae:<10.3f} {region:<14}")

# ==============================================================================
# 10. SCALE MODEL INTERPRETATION
# ==============================================================================
print("\n" + "=" * 80)
print("SCALE MODEL INTERPRETATION (1:50)")
print("=" * 80)

SCALE = 50
T1_prototype = T1 * np.sqrt(SCALE)

print(f"\n    Scale Factor: 1:{SCALE}")
print(f"\n    MODEL (Physical Maket):")
print(f"      Height: {H_max} cm")
print(f"      Period T1: {T1:.4f} s ({f1:.2f} Hz)")
print(f"\n    PROTOTYPE (Scaled Building):")
print(f"      Height: {H_max * SCALE / 100:.1f} m")
print(f"      Period T1: {T1_prototype:.4f} s ({1/T1_prototype:.2f} Hz)")

print(f"\n    SIMILITUDE SCALING:")
print(f"      Length: lambda = {SCALE}")
print(f"      Time/Period: sqrt(lambda) = {np.sqrt(SCALE):.3f}")
print(f"      Acceleration: 1 (same)")
print(f"      Frequency: 1/sqrt(lambda) = {1/np.sqrt(SCALE):.4f}")

# ==============================================================================
# 11. SAVE RESULTS
# ==============================================================================
print("\n[11] SAVING RESULTS...")

os.makedirs('results/data', exist_ok=True)

# Save modal results
modal_df = pd.DataFrame(modal_results)
modal_df.to_csv('results/data/modal_results_v8_afad.csv', index=False)

# Summary table
summary = {
    'Parameter': [
        'Model_Height_cm', 'Prototype_Height_m', 'Scale_Factor',
        'T1_model_s', 'T1_prototype_s', 'f1_Hz',
        'E_kN_cm2', 'Section_mm', 'Total_Mass_kg',
        'Sae_DD1_g', 'Sae_DD2_g', 'Region_DD2',
        'TA_DD2_s', 'TB_DD2_s', 'SDS_DD2_g', 'SD1_DD2_g'
    ],
    'Value': [
        H_max, H_max * SCALE / 100, SCALE,
        T1, T1_prototype, f1,
        E, b*10, total_mass_kg,
        get_Sae(T1, 'DD-1'), get_Sae(T1, 'DD-2'), get_region(T1, 'DD-2'),
        AFAD_SPECTRUM['DD-2']['TA'], AFAD_SPECTRUM['DD-2']['TB'],
        AFAD_SPECTRUM['DD-2']['SDS'], AFAD_SPECTRUM['DD-2']['SD1']
    ]
}
summary_df = pd.DataFrame(summary)
summary_df.to_csv('results/data/modal_summary_v8_afad.csv', index=False)

print(f"    Saved: results/data/modal_results_v8_afad.csv")
print(f"    Saved: results/data/modal_summary_v8_afad.csv")

# Cleanup
ops.wipe()

print("\n" + "=" * 80)
print("MODAL ANALYSIS COMPLETE")
print("=" * 80)
print(f"\n    KEY RESULTS:")
print(f"    - Fundamental Period (Model): T1 = {T1:.4f} s")
print(f"    - Fundamental Frequency: f1 = {f1:.2f} Hz")
print(f"    - Spectral Region (DD-2): {get_region(T1, 'DD-2')}")
print(f"    - Spectral Acceleration Sae(T1): {get_Sae(T1, 'DD-2'):.3f} g")
