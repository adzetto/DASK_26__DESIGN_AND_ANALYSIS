"""
MODAL ANALYSIS FOR MODEL V9 WITH AFAD SPECTRUM COMPARISON
==========================================================
V9: Stiffened version with additional bracing
Goal: Reduce period toward ascending region

Uses V9 model files: twin_position_matrix_v9.csv, twin_connectivity_matrix_v9.csv
"""

import numpy as np
import pandas as pd
import os
from pathlib import Path

WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("MODAL ANALYSIS - MODEL V9 (STIFFENED) WITH AFAD SPECTRUM")
print("=" * 80)

# ==============================================================================
# 1. LOAD MODEL V9 DATA
# ==============================================================================
print("\n[1] LOADING MODEL V9 DATA...")

pos_df = pd.read_csv('data/twin_position_matrix_v9.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix_v9.csv')

n_nodes = len(pos_df)
n_elements = len(conn_df)
H_max = pos_df['z'].max()
total_floors = pos_df['floor'].max() + 1

print(f"    Nodes: {n_nodes}")
print(f"    Elements: {n_elements}")
print(f"    Floors: {total_floors}")
print(f"    Height: {H_max} cm")

# ==============================================================================
# 2. CALIBRATED MATERIAL PROPERTIES (Same as V8)
# ==============================================================================
print("\n[2] MATERIAL PROPERTIES...")

E = 170.0         # kN/cm^2 (CALIBRATED)
G = E / 2.6
nu = 0.3

b = 0.6           # cm (6mm section)
A = b * b
Iz = (b**4) / 12
Iy = (b**4) / 12
J = 0.1406 * b**4

print(f"    E = {E:.1f} kN/cm^2 ({E*10:.0f} MPa)")
print(f"    Section: {b*10:.0f}mm x {b*10:.0f}mm")

# ==============================================================================
# 3. AFAD SPECTRUM PARAMETERS
# ==============================================================================
AFAD_SPECTRUM = {
    'DD-1': {'SDS': 1.544, 'SD1': 0.800, 'TA': 0.104, 'TB': 0.518, 'TL': 6.0, 'PGA': 0.628},
    'DD-2': {'SDS': 1.008, 'SD1': 0.514, 'TA': 0.102, 'TB': 0.510, 'TL': 6.0, 'PGA': 0.362},
    'DD-3': {'SDS': 0.542, 'SD1': 0.238, 'TA': 0.088, 'TB': 0.438, 'TL': 6.0, 'PGA': 0.152},
    'DD-4': {'SDS': 0.384, 'SD1': 0.158, 'TA': 0.083, 'TB': 0.412, 'TL': 6.0, 'PGA': 0.102}
}

def get_Sae(T, dd='DD-2'):
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
print("\n[3] BUILDING OPENSEES MODEL...")

import openseespy.opensees as ops

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes
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
ops.geomTransf('Linear', 1, 1, 0, 0)
ops.geomTransf('Linear', 2, 0, 0, 1)
ops.geomTransf('Linear', 3, 0, 0, 1)

# Create elements
elem_count = 0
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])

    if ni not in node_coords or nj not in node_coords:
        continue

    xi, yi, zi = node_coords[ni]
    xj, yj, zj = node_coords[nj]

    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 1e-6:
        continue

    dx, dy, dz = abs(xj-xi), abs(yj-yi), abs(zj-zi)

    if dz > max(dx, dy) * 0.9:
        transf_tag = 1
    elif dx > dy:
        transf_tag = 2
    else:
        transf_tag = 3

    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A, E, G, J, Iy, Iz, transf_tag)
        elem_count += 1
    except:
        pass

print(f"    Created {elem_count} elements")

# ==============================================================================
# 5. APPLY DASK TEST MASSES
# ==============================================================================
print("\n[4] APPLYING DASK TEST MASSES...")

MASS_CONV = 1e-5
FLOOR_MASS_KG = 1.60
ROOF_MASS_KG = 2.22
WEIGHT_SPACING = 18.0

available_z = sorted(pos_df[pos_df['z'] > 0]['z'].unique())
target_z = np.arange(18.0, H_max - 5, WEIGHT_SPACING)

weight_levels = []
for tz in target_z:
    closest = min(available_z, key=lambda z: abs(z - tz))
    if closest not in weight_levels and closest < H_max - 5:
        weight_levels.append(closest)

total_mass_kg = 0
Z_TOL = 0.5

for z_level in weight_levels:
    nodes_at_z = pos_df[np.abs(pos_df['z'] - z_level) < Z_TOL]['node_id'].astype(int).tolist()
    n = len(nodes_at_z)
    if n > 0:
        mass_per_node = FLOOR_MASS_KG * MASS_CONV / n
        for nid in nodes_at_z:
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
        total_mass_kg += FLOOR_MASS_KG

roof_nodes = pos_df[np.abs(pos_df['z'] - H_max) < Z_TOL]['node_id'].astype(int).tolist()
if roof_nodes:
    mass_per_node = ROOF_MASS_KG * MASS_CONV / len(roof_nodes)
    for nid in roof_nodes:
        ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
    total_mass_kg += ROOF_MASS_KG

print(f"    Total test mass: {total_mass_kg:.2f} kg")

# ==============================================================================
# 6. EIGENVALUE ANALYSIS
# ==============================================================================
print("\n[5] EIGENVALUE ANALYSIS...")

num_modes = 12
try:
    eigenvalues = ops.eigen('-genBandArpack', num_modes)
    print(f"    Computed {len(eigenvalues)} modes")
except:
    eigenvalues = ops.eigen(num_modes)

# ==============================================================================
# 7. MODAL RESULTS
# ==============================================================================
print("\n" + "=" * 80)
print("MODAL ANALYSIS RESULTS - V9")
print("=" * 80)

modal_results = []

print(f"\n    {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12} {'Sae DD-2 (g)':<14} {'Region'}")
print("    " + "-" * 54)

for i, ev in enumerate(eigenvalues):
    if ev > 0:
        omega = np.sqrt(ev)
        freq = omega / (2 * np.pi)
        period = 1.0 / freq if freq > 0 else 0
        Sae = get_Sae(period, 'DD-2')
        region = get_region(period, 'DD-2')

        modal_results.append({
            'mode': i + 1,
            'period_s': period,
            'frequency_hz': freq,
            'Sae_DD2': Sae,
            'region': region
        })

        print(f"    {i+1:<6} {period:<12.4f} {freq:<12.2f} {Sae:<14.3f} {region}")

T1 = modal_results[0]['period_s'] if modal_results else 0
f1 = modal_results[0]['frequency_hz'] if modal_results else 0

print(f"\n    FUNDAMENTAL PERIOD: T1 = {T1:.4f} s ({T1*1000:.1f} ms)")
print(f"    FUNDAMENTAL FREQUENCY: f1 = {f1:.2f} Hz")

# ==============================================================================
# 8. SPECTRUM COMPARISON
# ==============================================================================
print("\n" + "=" * 80)
print("AFAD SPECTRUM COMPARISON - V9")
print("=" * 80)

print(f"\n    {'DD Level':<10} {'TA (s)':<10} {'T1 vs TA':<12} {'Region':<14} {'Sae (g)'}")
print("    " + "-" * 60)

for dd in ['DD-1', 'DD-2', 'DD-3', 'DD-4']:
    p = AFAD_SPECTRUM[dd]
    region = get_region(T1, dd)
    Sae = get_Sae(T1, dd)
    comparison = "T1 < TA" if T1 < p['TA'] else "T1 >= TA"

    print(f"    {dd:<10} {p['TA']:<10.3f} {comparison:<12} {region:<14} {Sae:.3f}")

# ==============================================================================
# 9. SAVE RESULTS
# ==============================================================================
print("\n[6] SAVING RESULTS...")

modal_df = pd.DataFrame(modal_results)
modal_df.to_csv('results/data/modal_results_v9_afad.csv', index=False)
print(f"    Saved: results/data/modal_results_v9_afad.csv")

ops.wipe()

print("\n" + "=" * 80)
print("V9 MODAL ANALYSIS COMPLETE")
print("=" * 80)
print(f"\n    T1 = {T1:.4f} s, f1 = {f1:.2f} Hz")
print(f"    Region (DD-2): {get_region(T1, 'DD-2')}")
