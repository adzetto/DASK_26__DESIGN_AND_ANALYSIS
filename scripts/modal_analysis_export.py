#!/usr/bin/env python3
"""
Modal Analysis with Mode Shape Extraction
Exports mode shapes and periods to TSV for pgfplots visualization
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os
import shutil

# =====================================================
# LOAD MODEL DATA
# =====================================================
print("="*60)
print("MODAL ANALYSIS WITH MODE SHAPES")
print("="*60)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'results', 'data')
DOCS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'docs')

# Material properties (Balsa 6x6mm)
E_BALSA = 3500.0        # MPa
RHO_BALSA = 160e-9      # kg/mm³
G_BALSA = E_BALSA / 2.6 # Shear modulus

# Section (6x6mm)
b = 6.0  # mm
A = b * b                    # 36 mm²
I = b**4 / 12               # 108 mm⁴
J = 0.1406 * b**4           # Torsional constant

# Model scale
MODEL_SCALE = 10.0

# Load from CSV
print("\nLoading model data...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_position_matrix.csv'))
conn_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_connectivity_matrix.csv'))

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")

# Convert to mm
pos_df['x_mm'] = pos_df['x'] * MODEL_SCALE
pos_df['y_mm'] = pos_df['y'] * MODEL_SCALE
pos_df['z_mm'] = pos_df['z'] * MODEL_SCALE

max_z = pos_df['z'].max()
max_z_mm = max_z * MODEL_SCALE
print(f"  Height: {max_z:.0f}m -> {max_z_mm:.0f}mm")

# =====================================================
# BUILD OPENSEES MODEL
# =====================================================
print("\nBuilding OpenSees model...")
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Transformations
ops.geomTransf('Linear', 1, 0, 1, 0)   # Vertical
ops.geomTransf('Linear', 2, 0, 0, 1)   # Horizontal

# Create nodes
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    ops.node(nid, row['x_mm'], row['y_mm'], row['z_mm'])

# Fix base nodes
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].tolist()
for nid in base_nodes:
    ops.fix(int(nid), 1, 1, 1, 1, 1, 1)
print(f"  Fixed {len(base_nodes)} base nodes")

# Create elements
elem_count = 0
for _, row in conn_df.iterrows():
    try:
        n1 = int(row['node1'])
        n2 = int(row['node2'])
        eid = elem_count + 1
        
        z1 = pos_df[pos_df['node_id'] == n1]['z_mm'].values[0]
        z2 = pos_df[pos_df['node_id'] == n2]['z_mm'].values[0]
        is_vertical = abs(z2 - z1) > 1
        
        transf = 1 if is_vertical else 2
        ops.element('elasticBeamColumn', eid, n1, n2, A, E_BALSA, G_BALSA, J, I, I, transf)
        elem_count += 1
    except Exception as e:
        pass

print(f"  Created {elem_count} elements")

# =====================================================
# APPLY LUMPED MASS
# =====================================================
print("\nApplying mass (every 3 floors):")

floor_zs = sorted(pos_df['z'].unique())
mass_floor_indices = list(range(3, len(floor_zs), 3))
if len(floor_zs) - 1 not in mass_floor_indices:
    mass_floor_indices.append(len(floor_zs) - 1)

total_mass = 0
for idx in mass_floor_indices:
    z = floor_zs[idx]
    floor_nodes = pos_df[pos_df['z'] == z]['node_id'].tolist()
    
    is_roof = (idx == len(floor_zs) - 1)
    floor_mass = 2.22 if is_roof else 1.60
    node_mass = floor_mass / len(floor_nodes)
    
    for nid in floor_nodes:
        ops.mass(int(nid), node_mass, node_mass, node_mass, 0.0, 0.0, 0.0)
    
    total_mass += floor_mass
    print(f"  Floor {idx}: {floor_mass:.2f} kg -> {len(floor_nodes)} nodes")

print(f"\n  Total test mass: {total_mass:.2f} kg")

# =====================================================
# EIGEN ANALYSIS
# =====================================================
print("\n" + "="*60)
print("EIGENVALUE ANALYSIS")
print("="*60)

num_modes = 10
eigenvalues = ops.eigen(num_modes)

periods = []
frequencies = []

print(f"\n{'Mode':<6}{'Period (s)':<15}{'Frequency (Hz)':<18}{'ω (rad/s)':<15}")
print("-"*54)

for i, ev in enumerate(eigenvalues):
    omega = np.sqrt(ev)
    freq = omega / (2 * np.pi)
    period = 1 / freq if freq > 0 else 0
    periods.append(period)
    frequencies.append(freq)
    print(f"{i+1:<6}{period:<15.4f}{freq:<18.4f}{omega:<15.4f}")

T1 = periods[0]
print(f"\n>>> FUNDAMENTAL PERIOD T1 = {T1:.4f} s <<<")

# =====================================================
# EXTRACT MODE SHAPES
# =====================================================
print("\n" + "="*60)
print("EXTRACTING MODE SHAPES")
print("="*60)

# Get center-line nodes (for mode shape viz)
center_x = 15.0
center_y = 8.0

mode_shape_nodes = []
for z in sorted(floor_zs):
    z_mm = z * MODEL_SCALE
    candidates = pos_df[
        (abs(pos_df['x'] - center_x) < 2) &
        (abs(pos_df['y'] - center_y) < 2) &
        (pos_df['z'] == z)
    ]
    if len(candidates) > 0:
        mode_shape_nodes.append({
            'node_id': int(candidates.iloc[0]['node_id']),
            'z': z,
            'z_mm': z_mm
        })

print(f"  Mode shape nodes: {len(mode_shape_nodes)}")

# Extract mode shapes for modes 1-7
mode_shapes = {}
for mode in range(1, 8):
    mode_data = []
    for node_info in mode_shape_nodes:
        nid = node_info['node_id']
        z = node_info['z']
        try:
            phi_x = ops.nodeEigenvector(nid, mode, 1)
            phi_y = ops.nodeEigenvector(nid, mode, 2)
            mode_data.append({'z': z, 'phi_x': phi_x, 'phi_y': phi_y})
        except:
            pass
    
    if mode_data:
        max_phi = max(max(abs(d['phi_x']), abs(d['phi_y'])) for d in mode_data)
        if max_phi > 0:
            for d in mode_data:
                d['phi_x'] /= max_phi
                d['phi_y'] /= max_phi
        
        mode_shapes[mode] = mode_data
        print(f"  Mode {mode}: T = {periods[mode-1]:.4f}s, {len(mode_data)} points")

# =====================================================
# EXPORT TO TSV
# =====================================================
print("\n" + "="*60)
print("EXPORTING DATA")
print("="*60)

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# 1. Modal periods TSV
periods_tsv = os.path.join(OUTPUT_DIR, "modal_periods.tsv")
with open(periods_tsv, 'w') as f:
    f.write("Mode\tPeriod\tFrequency\tOmega\n")
    for i in range(min(10, len(periods))):
        omega = 2 * np.pi * frequencies[i]
        f.write(f"{i+1}\t{periods[i]:.6f}\t{frequencies[i]:.4f}\t{omega:.4f}\n")
print(f"  Saved: {periods_tsv}")
shutil.copy(periods_tsv, os.path.join(DOCS_DIR, "modal_periods.tsv"))

# 2. Mode shapes TSV
for mode, data in mode_shapes.items():
    mode_tsv = os.path.join(OUTPUT_DIR, f"mode_shape_{mode}.tsv")
    with open(mode_tsv, 'w') as f:
        f.write("z\tphi_x\tphi_y\n")
        for d in sorted(data, key=lambda x: x['z']):
            f.write(f"{d['z']:.1f}\t{d['phi_x']:.6f}\t{d['phi_y']:.6f}\n")
    print(f"  Saved: {mode_tsv}")
    shutil.copy(mode_tsv, os.path.join(DOCS_DIR, f"mode_shape_{mode}.tsv"))

# 3. Combined for bar chart
combined_tsv = os.path.join(OUTPUT_DIR, "mode_periods_bar.tsv")
with open(combined_tsv, 'w') as f:
    f.write("Mode\tPeriod\n")
    for i in range(7):
        f.write(f"{i+1}\t{periods[i]:.6f}\n")
print(f"  Saved: {combined_tsv}")
shutil.copy(combined_tsv, os.path.join(DOCS_DIR, "mode_periods_bar.tsv"))

# =====================================================
# SUMMARY
# =====================================================
print("\n" + "="*60)
print("MODAL ANALYSIS SUMMARY")
print("="*60)
print(f"\nFundamental Period: T1 = {T1:.4f} s")
print(f"TBDY2018 Check: TA = 0.0729s, TB = 0.3646s")
if T1 < 0.0729:
    print(f"  Status: ASCENDING (T1 < TA) ✓")
elif T1 <= 0.3646:
    print(f"  Status: PLATEAU ✗")
else:
    print(f"  Status: DESCENDING")

print(f"\nFirst 7 Modes:")
for i in range(7):
    print(f"  Mode {i+1}: T = {periods[i]:.4f} s, f = {frequencies[i]:.2f} Hz")

print("="*60)
ops.wipe()
print("Process 0 Terminating")
