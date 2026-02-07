#!/usr/bin/env python3
"""
Quick Modal Analysis using OpenSeesPy
=====================================
Finds fundamental period of the twin towers structure.
Mass placed every 3 floors as per DASK specification.
"""

import numpy as np
import pandas as pd
import openseespy.opensees as ops
import os
import sys

print("=" * 60)
print("MODAL ANALYSIS - OpenSeesPy")
print("=" * 60)

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')

# =====================================================
# UNITS: cm (coordinates), N, kg
# Model coordinates are in cm (30x16x159 cm)
# =====================================================

# Material properties (Balsa 6mm x 6mm = 0.6cm x 0.6cm)
# E = 3500 MPa = 3500 N/mm² = 35000 N/cm² (1 MPa = 10 N/cm²)
E_BALSA = 35000.0       # N/cm²
G_BALSA = E_BALSA / 2.6 # Shear modulus N/cm²

# Section (6mm = 0.6cm)
b = 0.6  # cm
A = b * b                    # 0.36 cm²
I = b**4 / 12               # 0.0108 cm⁴
J = 0.1406 * b**4           # Torsional constant cm⁴

# No scaling - coordinates already in cm
MODEL_SCALE = 1.0

# Load data
print("\nLoading model data...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_position_matrix.csv'))
conn_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_connectivity_matrix.csv'))

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")

# Coordinates in cm (no conversion)
pos_df['x_cm'] = pos_df['x']
pos_df['y_cm'] = pos_df['y']
pos_df['z_cm'] = pos_df['z']

max_z = pos_df['z'].max()
print(f"  Height: {max_z:.0f} cm (model scale)")

# Initialize OpenSees
print("\nBuilding OpenSees model...")
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Transformations
ops.geomTransf('Linear', 1, 0, 1, 0)   # Vertical
ops.geomTransf('Linear', 2, 0, 0, 1)   # Y-direction
ops.geomTransf('Linear', 3, 0, 1, 0)   # X-direction

# Create nodes (coordinates in cm)
node_coords = {}
for idx, row in pos_df.iterrows():
    nid = int(row['node_id']) + 1
    x, y, z = float(row['x_cm']), float(row['y_cm']), float(row['z_cm'])
    node_coords[int(row['node_id'])] = (x, y, z)
    ops.node(nid, x, y, z)

# Fix base
base_z = pos_df['z_cm'].min()
fix_count = 0
for idx, row in pos_df.iterrows():
    if abs(row['z_cm'] - base_z) < 0.1:
        ops.fix(int(row['node_id']) + 1, 1, 1, 1, 1, 1, 1)
        fix_count += 1
print(f"  Fixed {fix_count} base nodes")

# Create elements
elem_count = 0
for idx, row in conn_df.iterrows():
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
        transf = 1
    elif dx > dy:
        transf = 3
    else:
        transf = 2

    try:
        ops.element('elasticBeamColumn', elem_id,
                   n1 + 1, n2 + 1,
                   A, E_BALSA, G_BALSA, J, I, I, transf)
        elem_count += 1
    except:
        pass

print(f"  Created {elem_count} elements")

# Add mass - DASK spec: every 3 floors
# Test loads: 1.60 kg at floors 3,6,9...24, 2.22 kg at roof (floor 25)
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_ROOF_FLOOR = 25  # Max floor (roof)
MASS_PER_FLOOR = 1.60  # kg
MASS_ROOF = 2.22       # kg

# Group nodes by floor
floor_nodes = {}
for idx, row in pos_df.iterrows():
    floor = int(row['floor'])
    node_id = int(row['node_id'])
    if floor not in floor_nodes:
        floor_nodes[floor] = []
    floor_nodes[floor].append(node_id)

# Mass unit conversion: kg -> N·s²/cm
# 1 kg = 1 N·s²/m = 0.01 N·s²/cm (since 1 m = 100 cm)
MASS_CONV = 0.01

total_mass = 0.0
print("\nApplying mass (every 3 floors):")

for floor in MASS_FLOORS:
    if floor in floor_nodes:
        n_floor_nodes = len(floor_nodes[floor])
        mass_per_node = MASS_PER_FLOOR / n_floor_nodes * MASS_CONV
        for node_id in floor_nodes[floor]:
            ops.mass(node_id + 1, mass_per_node, mass_per_node, 0.0, 0.0, 0.0, 0.0)
        total_mass += MASS_PER_FLOOR
        print(f"  Floor {floor}: {MASS_PER_FLOOR:.2f} kg -> {n_floor_nodes} nodes")

# Check for roof floor
max_floor = max(floor_nodes.keys())
if max_floor in floor_nodes:
    n_floor_nodes = len(floor_nodes[max_floor])
    mass_per_node = MASS_ROOF / n_floor_nodes * MASS_CONV
    for node_id in floor_nodes[max_floor]:
        ops.mass(node_id + 1, mass_per_node, mass_per_node, 0.0, 0.0, 0.0, 0.0)
    total_mass += MASS_ROOF
    print(f"  Floor {max_floor} (roof): {MASS_ROOF:.2f} kg -> {n_floor_nodes} nodes")

print(f"\n  Total test mass: {total_mass:.2f} kg")

# Modal analysis
print("\n" + "=" * 60)
print("MODAL ANALYSIS")
print("=" * 60)

try:
    num_modes = 10
    eigenvalues = ops.eigen(num_modes)

    print(f"\n{'Mode':<6} {'Period (s)':<12} {'Frequency (Hz)':<15} {'ω (rad/s)'}")
    print("-" * 50)

    periods = []
    for i, ev in enumerate(eigenvalues):
        if ev > 0:
            omega = np.sqrt(ev)
            T = 2 * np.pi / omega
            f = 1 / T
            periods.append(T)
            print(f"{i+1:<6} {T:<12.4f} {f:<15.4f} {omega:.4f}")

    T1 = periods[0] if periods else 0
    print(f"\n>>> FUNDAMENTAL PERIOD T1 = {T1:.4f} s <<<")

    # Export to TSV for pgfplots
    import shutil
    output_dir = os.path.join(os.path.dirname(SCRIPT_DIR), 'results', 'data')
    docs_dir = os.path.join(os.path.dirname(SCRIPT_DIR), 'docs')
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(docs_dir, exist_ok=True)
    
    # Modal periods TSV
    periods_tsv = os.path.join(output_dir, 'modal_periods.tsv')
    with open(periods_tsv, 'w') as f:
        f.write("Mode\tPeriod\tFrequency\n")
        for i, T in enumerate(periods[:10]):
            freq = 1/T if T > 0 else 0
            f.write(f"{i+1}\t{T:.6f}\t{freq:.4f}\n")
    shutil.copy(periods_tsv, docs_dir)
    print(f"\n  Exported: {periods_tsv}")
    
    # Mode periods bar chart data
    bar_tsv = os.path.join(output_dir, 'mode_periods_bar.tsv')
    with open(bar_tsv, 'w') as f:
        f.write("Mode\tPeriod\n")
        for i in range(min(8, len(periods))):  # 8 modes
            f.write(f"{i+1}\t{periods[i]:.6f}\n")
    shutil.copy(bar_tsv, docs_dir)
    
    # Extract mode shapes
    print("\n  Extracting mode shapes...")
    center_x, center_y = 15.0, 8.0
    mode_shape_nodes = []
    floor_zs = sorted(pos_df['z'].unique())
    
    for z in floor_zs:
        candidates = pos_df[
            (abs(pos_df['x'] - center_x) < 2) &
            (abs(pos_df['y'] - center_y) < 2) &
            (pos_df['z'] == z)
        ]
        if len(candidates) > 0:
            mode_shape_nodes.append({
                'node_id': int(candidates.iloc[0]['node_id']),
                'z': z
            })
    
    for mode in range(1, 9):  # Mode 1 to 8
        mode_data = []
        for node_info in mode_shape_nodes:
            nid = node_info['node_id']
            z = node_info['z']
            try:
                phi_x = ops.nodeEigenvector(nid + 1, mode, 1)
                phi_y = ops.nodeEigenvector(nid + 1, mode, 2)
                mode_data.append({'z': z, 'phi_x': phi_x, 'phi_y': phi_y})
            except:
                pass
        
        if mode_data:
            max_phi = max(max(abs(d['phi_x']), abs(d['phi_y'])) for d in mode_data)
            if max_phi > 0:
                for d in mode_data:
                    d['phi_x'] /= max_phi
                    d['phi_y'] /= max_phi
            
            mode_tsv = os.path.join(output_dir, f'mode_shape_{mode}.tsv')
            with open(mode_tsv, 'w') as f:
                f.write("z\tphi_x\tphi_y\n")
                for d in sorted(mode_data, key=lambda x: x['z']):
                    f.write(f"{d['z']:.1f}\t{d['phi_x']:.6f}\t{d['phi_y']:.6f}\n")
            shutil.copy(mode_tsv, docs_dir)
    
    print("  Mode shapes exported to TSV")

    # TBDY2018 check - İstanbul Finans Merkezi (Ataşehir)
    # DD-2 (475-year return period), ZD soil class
    # Coordinates: 40.99°N, 29.13°E
    SS, S1 = 1.187, 0.323  # AFAD TDTH values for IFM
    FS, F1 = 1.10, 1.58    # ZD soil class coefficients (Table 4.1)
    SDS = SS * FS          # 1.306g
    SD1 = S1 * F1          # 0.510g
    TA = 0.2 * SD1 / SDS   # 0.078s
    TB = SD1 / SDS         # 0.391s

    print(f"\nTBDY2018 Spectrum Check:")
    print(f"  Location: Istanbul Finans Merkezi (DD-2, ZD)")
    print(f"  SS = {SS}, S1 = {S1}")
    print(f"  FS = {FS}, F1 = {F1}")
    print(f"  SDS = {SDS:.3f}g, SD1 = {SD1:.3f}g")
    print(f"  TA = {TA:.4f}s, TB = {TB:.4f}s")
    print(f"  Plateau region: {TA:.4f}s to {TB:.4f}s")

    if T1 < TA:
        region = "ASCENDING (T < TA)"
        Sae = SDS * (0.4 + 0.6 * T1 / TA)
    elif T1 <= TB:
        region = "PLATEAU (TA ≤ T ≤ TB)"
        Sae = SDS
    else:
        region = "DESCENDING (T > TB)"
        Sae = SD1 / T1

    print(f"\n  T1 = {T1:.4f}s -> {region}")
    print(f"  Spectral acceleration Sae = {Sae:.3f}g")

except Exception as e:
    print(f"Modal analysis error: {e}")
    import traceback
    traceback.print_exc()

ops.wipe()
print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
