#!/usr/bin/env python3
"""
DASK 2026 Twin Towers - Modal Analysis with DASK 2025 Competition Weights
==========================================================================
Applies floor weights per DASK Technical Specification:
- Floor weights: ~1.60 kg every 18 cm (every 3 floors)
- Roof weight: ~2.22 kg (metal plate + wooden plate + accelerometer)

Author: Structural Analysis Script
Date: February 2026
Model: V8 Optimized Balsa Wood Twin Towers
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from pathlib import Path

# Set working directory
WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("DASK 2026 TWIN TOWERS - MODAL ANALYSIS WITH DASK 2025 WEIGHTS")
print("=" * 80)

# ==============================================================================
# 1. LOAD MODEL DATA
# ==============================================================================
print("\n[1] LOADING MODEL DATA...")

pos_df = pd.read_csv('data/twin_position_matrix.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix.csv')

print(f"    Nodes: {len(pos_df)}")
print(f"    Elements: {len(conn_df)}")
print(f"    Towers: {pos_df['tower'].unique().tolist()}")

# ==============================================================================
# 2. MATERIAL PROPERTIES (Balsa Wood)
# ==============================================================================
print("\n[2] MATERIAL PROPERTIES (Balsa Wood)...")

# Balsa wood properties (units: kN, cm, tonne, s)
# E = 3.5 GPa = 3.5e6 kN/m² = 3.5e6 / 10000 kN/cm² = 350 kN/cm²
E = 350.0         # kN/cm² (3.5 GPa)
G = 20.0          # kN/cm² (0.2 GPa - shear modulus)
rho = 0.16e-9     # tonne/cm³ (160 kg/m³)

# Section properties - 3mm x 3mm square balsa (in cm)
b = 0.3           # cm (3 mm)
A = b * b         # cm²
Iz = (b**4) / 12  # cm⁴
Iy = (b**4) / 12  # cm⁴
J = 0.141 * b**4  # cm⁴ (torsional constant for square)

print(f"    E = {E:.1f} kN/cm² (3.5 GPa)")
print(f"    G = {G:.1f} kN/cm² (0.2 GPa)")
print(f"    rho = {rho*1e9:.0f} kg/m³")
print(f"    Section: {b*10:.0f}mm x {b*10:.0f}mm")
print(f"    A = {A:.4f} cm² ({A*100:.2f} mm²)")
print(f"    Iz = Iy = {Iz:.6f} cm⁴")

# No scaling - coordinates already in cm
SCALE = 1.0  # cm (no conversion)

# ==============================================================================
# 3. BUILD OPENSEES MODEL
# ==============================================================================
print("\n[3] BUILDING OPENSEES MODEL...")

try:
    import openseespy.opensees as ops
except ImportError:
    print("ERROR: openseespy not installed. Installing...")
    os.system("pip install openseespy -q")
    import openseespy.opensees as ops

# Clear any previous model
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes (coordinates in cm)
print("    Creating nodes...")
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    ops.node(nid,
             row['x'],
             row['y'],
             row['z'])

# Fix base nodes (z = 0)
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)
print(f"    Fixed {len(base_nodes)} base nodes")

# Define geometric transformations for different element orientations
# For vertical elements: local z in global X direction
ops.geomTransf('Linear', 1, 1, 0, 0)
# For horizontal elements along X: local z in global Z direction  
ops.geomTransf('Linear', 2, 0, 0, 1)
# For horizontal elements along Y: local z in global Z direction
ops.geomTransf('Linear', 3, 0, 0, 1)

# Build node coordinate lookup for faster access
node_coords = {}
for _, row in pos_df.iterrows():
    node_coords[int(row['node_id'])] = (row['x'], row['y'], row['z'])

# Create elements
print("    Creating elements...")
elem_count = 0
skipped = 0
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    
    # Get node coordinates
    xi, yi, zi = node_coords.get(ni, (0, 0, 0))
    xj, yj, zj = node_coords.get(nj, (0, 0, 0))
    
    # Calculate element vector
    dx = xj - xi
    dy = yj - yi
    dz = zj - zi
    
    # Determine transformation based on element orientation
    if abs(dz) > max(abs(dx), abs(dy)):
        # Vertical element - use local z in X direction
        transf_tag = 1
    elif abs(dx) > abs(dy):
        # Horizontal along X
        transf_tag = 2
    else:
        # Horizontal along Y
        transf_tag = 3
    
    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A, E, G, J, Iy, Iz, transf_tag)
        elem_count += 1
    except Exception as e:
        skipped += 1

print(f"    Created {elem_count} elements (skipped {skipped})")

print(f"    Created {elem_count} elements")

# ==============================================================================
# 4. APPLY DASK 2025 COMPETITION WEIGHTS
# ==============================================================================
print("\n[4] APPLYING DASK 2025 COMPETITION WEIGHTS...")

# DASK Technical Specification Section 6.4 & A.3
# For kN-cm-s unit system: mass = kN·s²/cm
# Conversion: 1 kg = 1e-5 kN·s²/cm
MASS_CONVERSION = 1e-5      # kg to kN·s²/cm

FLOOR_WEIGHT_KG = 1.60      # kg (per weight level)
ROOF_WEIGHT_KG = 2.22       # kg (metal plate 1750g + wooden plate 300g + accelerometer 170g)
FLOOR_WEIGHT = FLOOR_WEIGHT_KG * MASS_CONVERSION   # kN·s²/cm
ROOF_WEIGHT = ROOF_WEIGHT_KG * MASS_CONVERSION     # kN·s²/cm

WEIGHT_SPACING = 18.0       # cm (every 3 floors)
FIRST_WEIGHT_Z = 18.0       # cm (2nd normal floor base)

# Building height (in cm from original data)
H_max_cm = pos_df['z'].max()

# Get available z-levels (excluding base)
available_z_cm = sorted(pos_df[pos_df['z'] > 0]['z'].unique())
print(f"    Building height: {H_max_cm:.1f} cm")
print(f"    Available z-levels: {len(available_z_cm)}")

# Find closest z-levels to target weight positions (every 18 cm)
target_z_levels = np.arange(FIRST_WEIGHT_Z, H_max_cm - 5, WEIGHT_SPACING)
actual_weight_levels_cm = []

for target_z in target_z_levels:
    closest_z = min(available_z_cm, key=lambda z: abs(z - target_z))
    if closest_z not in actual_weight_levels_cm and closest_z < H_max_cm - 5:
        actual_weight_levels_cm.append(closest_z)

print(f"    Target weight spacing: {WEIGHT_SPACING:.0f} cm")
print(f"    Actual weight levels: {actual_weight_levels_cm}")

# Tolerance for matching z-coordinates
Z_TOL = 0.5  # cm

# Apply floor weights at each level
total_floor_mass = 0
weight_distribution = []
total_floor_mass_kg = 0

print("\n    Applying weights:")
for z_level_cm in actual_weight_levels_cm:
    nodes_at_level = pos_df[np.abs(pos_df['z'] - z_level_cm) < Z_TOL]['node_id'].astype(int).tolist()
    n_nodes = len(nodes_at_level)
    
    if n_nodes > 0:
        mass_per_node = FLOOR_WEIGHT / n_nodes
        for nid in nodes_at_level:
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
        total_floor_mass += FLOOR_WEIGHT
        total_floor_mass_kg += FLOOR_WEIGHT_KG
        weight_distribution.append({
            'z_level_cm': z_level_cm,
            'n_nodes': n_nodes,
            'total_mass_kg': FLOOR_WEIGHT_KG,
            'mass_per_node_g': FLOOR_WEIGHT_KG * 1000 / n_nodes,
            'type': 'floor'
        })
        print(f"      z = {z_level_cm:6.1f} cm: {n_nodes:3d} nodes, {FLOOR_WEIGHT_KG:.2f} kg")

# Apply roof weight at top level
roof_nodes = pos_df[np.abs(pos_df['z'] - H_max_cm) < Z_TOL]['node_id'].astype(int).tolist()
n_roof_nodes = len(roof_nodes)
if n_roof_nodes > 0:
    roof_mass_per_node = ROOF_WEIGHT / n_roof_nodes
    for nid in roof_nodes:
        ops.mass(nid, roof_mass_per_node, roof_mass_per_node, roof_mass_per_node, 0, 0, 0)
    weight_distribution.append({
        'z_level_cm': H_max_cm,
        'n_nodes': n_roof_nodes,
        'total_mass_kg': ROOF_WEIGHT_KG,
        'mass_per_node_g': ROOF_WEIGHT_KG * 1000 / n_roof_nodes,
        'type': 'roof'
    })
    print(f"      z = {H_max_cm:6.1f} cm (ROOF): {n_roof_nodes:3d} nodes, {ROOF_WEIGHT_KG:.2f} kg")

TOTAL_MASS = total_floor_mass + ROOF_WEIGHT
TOTAL_MASS_KG = total_floor_mass_kg + ROOF_WEIGHT_KG

print(f"\n    " + "=" * 50)
print(f"    MASS SUMMARY")
print(f"    " + "=" * 50)
print(f"    Floor weights: {len(actual_weight_levels_cm)} x {FLOOR_WEIGHT_KG:.2f} kg = {total_floor_mass_kg:.2f} kg")
print(f"    Roof weight:   {ROOF_WEIGHT_KG:.2f} kg")
print(f"    TOTAL MASS:    {TOTAL_MASS_KG:.2f} kg")
print(f"    " + "=" * 50)

# ==============================================================================
# 5. EIGENVALUE ANALYSIS
# ==============================================================================
print("\n[5] RUNNING EIGENVALUE ANALYSIS...")

num_modes = 12
try:
    eigenvalues = ops.eigen('-genBandArpack', num_modes)
    print(f"    Successfully computed {len(eigenvalues)} modes")
except Exception as e:
    print(f"    Warning: Arpack failed, trying standard solver...")
    try:
        eigenvalues = ops.eigen(num_modes)
        print(f"    Successfully computed {len(eigenvalues)} modes")
    except Exception as e2:
        print(f"    ERROR: Eigenvalue analysis failed: {e2}")
        eigenvalues = []

# ==============================================================================
# 6. PROCESS MODAL RESULTS
# ==============================================================================
print("\n[6] PROCESSING MODAL RESULTS...")

# TBDY 2018 Design Spectrum Parameters (DD-2, Afyon Dinar)
SDS = 0.964     # Short period spectral acceleration
SD1 = 0.429     # 1-second spectral acceleration
TA = 0.089      # Corner period TA
TB = 0.445      # Corner period TB
TL = 6.0        # Long period transition

def get_spectral_acceleration(T):
    """Calculate elastic spectral acceleration per TBDY 2018"""
    if T < TA:
        return SDS * (0.4 + 0.6 * T / TA)
    elif T < TB:
        return SDS
    elif T < TL:
        return SD1 / T
    else:
        return SD1 * TL / (T * T)

modal_results = []
if eigenvalues:
    print(f"\n    {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12} {'Sae (g)':<10} {'Region':<12}")
    print("    " + "-" * 52)
    
    for i, ev in enumerate(eigenvalues):
        if ev > 0:
            omega = np.sqrt(ev)
            freq = omega / (2 * np.pi)
            period = 1.0 / freq if freq > 0 else 0
            
            # Get spectral acceleration
            Sae = get_spectral_acceleration(period)
            
            # Determine spectral region
            if period < TA:
                region = "Ascending"
            elif period < TB:
                region = "Plateau"
            elif period < TL:
                region = "Descending"
            else:
                region = "Long Period"
            
            modal_results.append({
                'mode': i + 1,
                'eigenvalue': ev,
                'omega_rad_s': omega,
                'frequency_hz': freq,
                'period_s': period,
                'Sae_g': Sae,
                'spectral_region': region
            })
            
            print(f"    {i+1:<6} {period:<12.4f} {freq:<12.2f} {Sae:<10.3f} {region:<12}")

# ==============================================================================
# 7. SAVE RESULTS TO FILES (NOT RAM)
# ==============================================================================
print("\n[7] SAVING RESULTS TO FILES...")

# Ensure output directories exist
os.makedirs('results/data', exist_ok=True)
os.makedirs('results/visualizations', exist_ok=True)

# Save modal results
modal_df = pd.DataFrame(modal_results)
modal_df.to_csv('results/data/modal_results_dask2025_weights.csv', index=False)
print(f"    Saved: results/data/modal_results_dask2025_weights.csv")

# Save weight distribution
weight_df = pd.DataFrame(weight_distribution)
weight_df.to_csv('results/data/weight_distribution_dask2025.csv', index=False)
print(f"    Saved: results/data/weight_distribution_dask2025.csv")

# Save comprehensive JSON results
results_json = {
    'model_info': {
        'total_nodes': len(pos_df),
        'total_elements': len(conn_df),
        'fixed_base_nodes': len(base_nodes),
        'height_cm': H_max_cm,
        'units': 'cm',
        'towers': pos_df['tower'].unique().tolist()
    },
    'material_properties': {
        'E_kN_cm2': E,
        'G_kN_cm2': G,
        'rho_tonne_cm3': rho,
        'section_cm': b,
        'A_cm2': A,
        'Iz_cm4': Iz
    },
    'dask_weights': {
        'floor_weight_kg': FLOOR_WEIGHT_KG,
        'roof_weight_kg': ROOF_WEIGHT_KG,
        'weight_spacing_cm': WEIGHT_SPACING,
        'num_floor_weight_levels': len(actual_weight_levels_cm),
        'total_mass_kg': TOTAL_MASS_KG,
        'weight_levels_cm': actual_weight_levels_cm
    },
    'spectrum_parameters': {
        'code': 'TBDY 2018',
        'earthquake_level': 'DD-2',
        'location': 'Afyon Dinar',
        'SDS': SDS,
        'SD1': SD1,
        'TA': TA,
        'TB': TB,
        'TL': TL
    },
    'modal_results': modal_results
}

with open('results/data/modal_analysis_dask2025.json', 'w') as f:
    json.dump(results_json, f, indent=2)
print(f"    Saved: results/data/modal_analysis_dask2025.json")

# Save modal periods in TSV format for documentation
if modal_results:
    with open('docs/modal_periods_dask2025.tsv', 'w') as f:
        f.write("Mode\tPeriod_s\tFrequency_Hz\tSae_g\tSpectral_Region\n")
        for mr in modal_results:
            f.write(f"{mr['mode']}\t{mr['period_s']:.4f}\t{mr['frequency_hz']:.2f}\t{mr['Sae_g']:.3f}\t{mr['spectral_region']}\n")
    print(f"    Saved: docs/modal_periods_dask2025.tsv")

# ==============================================================================
# 8. CREATE VISUALIZATION
# ==============================================================================
print("\n[8] CREATING VISUALIZATION...")

try:
    import matplotlib
    matplotlib.use('Agg')  # Non-interactive backend
    import matplotlib.pyplot as plt
    
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    
    # Plot 1: Modal Periods
    if modal_results:
        modes = [r['mode'] for r in modal_results[:8]]
        periods = [r['period_s'] for r in modal_results[:8]]
        colors = ['red' if r['spectral_region'] == 'Plateau' else 'blue' if r['spectral_region'] == 'Ascending' else 'green' 
                  for r in modal_results[:8]]
        
        axes[0].bar(modes, periods, color=colors, edgecolor='black')
        axes[0].set_xlabel('Mode Number')
        axes[0].set_ylabel('Period (s)')
        axes[0].set_title('Modal Periods (DASK 2025 Weights)')
        axes[0].axhline(y=TB, color='red', linestyle='--', label=f'TB = {TB}s')
        axes[0].axhline(y=TA, color='orange', linestyle='--', label=f'TA = {TA}s')
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
    
    # Plot 2: Design Spectrum with Modal Points
    T_range = np.linspace(0.01, 3.0, 300)
    Sa_range = [get_spectral_acceleration(t) for t in T_range]
    
    axes[1].plot(T_range, Sa_range, 'b-', linewidth=2, label='DD-2 Spectrum')
    axes[1].axvline(x=TA, color='orange', linestyle='--', alpha=0.7, label=f'TA = {TA}s')
    axes[1].axvline(x=TB, color='red', linestyle='--', alpha=0.7, label=f'TB = {TB}s')
    
    if modal_results:
        for i, mr in enumerate(modal_results[:6]):
            axes[1].plot(mr['period_s'], mr['Sae_g'], 'ro', markersize=10)
            axes[1].annotate(f"M{mr['mode']}", (mr['period_s'], mr['Sae_g']), 
                           textcoords="offset points", xytext=(5, 5), fontsize=8)
    
    axes[1].set_xlabel('Period T (s)')
    axes[1].set_ylabel('Spectral Acceleration Sae (g)')
    axes[1].set_title('TBDY 2018 DD-2 Design Spectrum')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    axes[1].set_xlim([0, 2.0])
    
    # Plot 3: Weight Distribution
    if weight_distribution:
        z_levels = [w['z_level_cm'] for w in weight_distribution]
        masses = [w['total_mass_kg'] for w in weight_distribution]
        types = [w['type'] for w in weight_distribution]
        colors = ['red' if t == 'roof' else 'blue' for t in types]
        
        axes[2].barh(z_levels, masses, color=colors, edgecolor='black', height=5)
        axes[2].set_xlabel('Weight (kg)')
        axes[2].set_ylabel('Height Z (cm)')
        axes[2].set_title('DASK 2025 Weight Distribution')
        axes[2].grid(True, alpha=0.3)
        
        # Add annotations
        for z, m, t in zip(z_levels, masses, types):
            label = f"{m:.2f} kg" + (" (roof)" if t == 'roof' else "")
            axes[2].annotate(label, (m, z), textcoords="offset points", xytext=(5, 0), fontsize=8)
    
    plt.tight_layout()
    plt.savefig('results/visualizations/modal_analysis_dask2025_weights.png', dpi=150, bbox_inches='tight')
    plt.close(fig)
    plt.close('all')  # Close all matplotlib figures
    del fig, axes  # Delete figure references
    print(f"    Saved: results/visualizations/modal_analysis_dask2025_weights.png")
    
except Exception as e:
    print(f"    Warning: Could not create visualization: {e}")

# ==============================================================================
# 9. SUMMARY
# ==============================================================================
print("\n" + "=" * 80)
print("ANALYSIS COMPLETE - SUMMARY")
print("=" * 80)

print(f"\nModel Statistics:")
print(f"  Total Nodes:     {len(pos_df)}")
print(f"  Total Elements:  {len(conn_df)}")
print(f"  Total Mass:      {TOTAL_MASS_KG:.2f} kg (DASK 2025 weights)")
print(f"  Height:          {H_max_cm:.1f} cm")

if modal_results:
    print(f"\nModal Results:")
    print("-" * 80)
    print(f"  Fundamental Period T1 = {modal_results[0]['period_s']:.4f} s")
    print(f"  Fundamental Frequency f1 = {modal_results[0]['frequency_hz']:.2f} Hz")
    print(f"  Spectral Acceleration Sae1 = {modal_results[0]['Sae_g']:.3f} g")
    print(f"  Spectral Region: {modal_results[0]['spectral_region']}")
    
    print(f"\nAll Modes:")
    for mr in modal_results[:8]:
        print(f"    Mode {mr['mode']}: T = {mr['period_s']:.4f} s, f = {mr['frequency_hz']:.2f} Hz, Sae = {mr['Sae_g']:.3f} g ({mr['spectral_region']})")

print(f"\nOutput Files:")
print(f"  - results/data/modal_results_dask2025_weights.csv")
print(f"  - results/data/weight_distribution_dask2025.csv")
print(f"  - results/data/modal_analysis_dask2025.json")
print(f"  - docs/modal_periods_dask2025.tsv")
print(f"  - results/visualizations/modal_analysis_dask2025_weights.png")

print("\n" + "=" * 80)

# ==============================================================================
# CLEANUP - Free all memory
# ==============================================================================
import gc

# Wipe OpenSees model
ops.wipe()

# Delete large objects
del pos_df
del conn_df
del node_coords
del modal_results
del weight_distribution
del results_json
del eigenvalues

# Force garbage collection
gc.collect()

print("\nMemory cleared: OpenSees wiped, all data deleted, garbage collected.")
