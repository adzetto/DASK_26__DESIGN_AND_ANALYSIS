#!/usr/bin/env python3
"""
CALIBRATED Modal Analysis - DASK 2026 Twin Towers
==================================================
Uses calibrated E value from free vibration test (friend's approach)
Target period: T ≈ 0.20s

Key calibration:
- E = 20 kN/cm² (200 MPa) instead of theoretical 3500 MPa
- All sections: 6mm x 6mm (uniform)
- This accounts for joint flexibility in physical model
"""

import numpy as np
import pandas as pd
import json
import os
from pathlib import Path

# Set working directory
WORK_DIR = Path(__file__).parent.parent
os.chdir(WORK_DIR)

print("=" * 80)
print("CALIBRATED MODAL ANALYSIS - E = 20 kN/cm² (Free Vibration Calibration)")
print("=" * 80)

# ==============================================================================
# 1. LOAD MODEL DATA
# ==============================================================================
print("\n[1] LOADING MODEL DATA...")

pos_df = pd.read_csv('data/twin_position_matrix.csv')
conn_df = pd.read_csv('data/twin_connectivity_matrix.csv')

print(f"    Nodes: {len(pos_df)}")
print(f"    Elements: {len(conn_df)}")

# ==============================================================================
# 2. CALIBRATED MATERIAL PROPERTIES
# ==============================================================================
print("\n[2] CALIBRATED MATERIAL PROPERTIES...")

# CALIBRATED E for T = 0.20s with 6mm sections
# From E=350 gives T=0.139s. Using T ∝ 1/√E:
# E = 350 × (0.139/0.20)² ≈ 170 kN/cm²
E = 170.0         # kN/cm² (1.7 GPa - calibrated for T=0.20s with 6mm)
G = E / 2.6       # kN/cm² (based on nu=0.3)
nu = 0.3

# ALL SECTIONS: 6mm x 6mm = 0.6cm x 0.6cm (uniform)
b = 0.6           # cm (6 mm)
A = b * b         # cm² = 0.36 cm²
Iz = (b**4) / 12  # cm⁴
Iy = (b**4) / 12  # cm⁴
J = 0.1406 * b**4 # cm⁴ (torsional constant for square)

print(f"    E = {E:.1f} kN/cm² ({E/100:.1f} GPa) [CALIBRATED for T=0.20s target]")
print(f"    G = {G:.4f} kN/cm²")
print(f"    ν = {nu}")
print(f"    Section: {b*10:.0f}mm x {b*10:.0f}mm (ALL MEMBERS UNIFORM)")
print(f"    A = {A:.4f} cm² ({A*100:.2f} mm²)")
print(f"    Iz = Iy = {Iz:.6f} cm⁴")
print(f"    J = {J:.6f} cm⁴")

# Coordinates already in cm - no conversion needed
SCALE = 1.0

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
node_coords = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = row['x'], row['y'], row['z']
    ops.node(nid, x, y, z)
    node_coords[nid] = (x, y, z)

# Fix base nodes (z = 0)
base_nodes = pos_df[pos_df['z'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)
print(f"    Fixed {len(base_nodes)} base nodes")

# Define geometric transformations
ops.geomTransf('Linear', 1, 1, 0, 0)  # For vertical elements
ops.geomTransf('Linear', 2, 0, 0, 1)  # For horizontal X elements
ops.geomTransf('Linear', 3, 0, 0, 1)  # For horizontal Y elements

# Create elements - ALL with same 6x6 section
print("    Creating elements (ALL 6mm x 6mm sections)...")
elem_count = 0
skipped = 0

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    
    if ni not in node_coords or nj not in node_coords:
        skipped += 1
        continue
    
    # Get node coordinates
    xi, yi, zi = node_coords[ni]
    xj, yj, zj = node_coords[nj]
    
    # Check for zero-length elements
    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 1e-6:
        skipped += 1
        continue
    
    # Calculate element direction
    dx = abs(xj - xi)
    dy = abs(yj - yi)
    dz = abs(zj - zi)
    
    # Determine transformation based on element orientation
    if dz > max(dx, dy) * 0.9:
        transf_tag = 1  # Vertical
    elif dx > dy:
        transf_tag = 2  # Horizontal X
    else:
        transf_tag = 3  # Horizontal Y
    
    try:
        # ALL elements use same section: 6mm x 6mm
        ops.element('elasticBeamColumn', eid, ni, nj, A, E, G, J, Iy, Iz, transf_tag)
        elem_count += 1
    except Exception as e:
        skipped += 1

print(f"    Created {elem_count} elements (skipped {skipped})")

# ==============================================================================
# 4. APPLY DASK 2025 COMPETITION WEIGHTS
# ==============================================================================
print("\n[4] APPLYING DASK 2025 COMPETITION WEIGHTS...")

# Mass conversion: kg to kN·s²/cm
MASS_CONVERSION = 1e-5  # 1 kg = 1e-5 kN·s²/cm

FLOOR_WEIGHT_KG = 1.60
ROOF_WEIGHT_KG = 2.22
FLOOR_WEIGHT = FLOOR_WEIGHT_KG * MASS_CONVERSION
ROOF_WEIGHT = ROOF_WEIGHT_KG * MASS_CONVERSION

WEIGHT_SPACING = 18.0  # cm
H_max = pos_df['z'].max()

# Get z-levels for weight placement
available_z = sorted(pos_df[pos_df['z'] > 0]['z'].unique())
target_z_levels = np.arange(18.0, H_max - 5, WEIGHT_SPACING)

actual_weight_levels = []
for target_z in target_z_levels:
    closest_z = min(available_z, key=lambda z: abs(z - target_z))
    if closest_z not in actual_weight_levels and closest_z < H_max - 5:
        actual_weight_levels.append(closest_z)

Z_TOL = 0.5
total_floor_mass_kg = 0

print("    Applying weights:")
for z_level in actual_weight_levels:
    nodes_at_level = pos_df[np.abs(pos_df['z'] - z_level) < Z_TOL]['node_id'].astype(int).tolist()
    n_nodes = len(nodes_at_level)
    
    if n_nodes > 0:
        mass_per_node = FLOOR_WEIGHT / n_nodes
        for nid in nodes_at_level:
            ops.mass(nid, mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)
        total_floor_mass_kg += FLOOR_WEIGHT_KG
        print(f"      z = {z_level:6.1f} cm: {n_nodes:3d} nodes, {FLOOR_WEIGHT_KG:.2f} kg")

# Roof mass
roof_nodes = pos_df[np.abs(pos_df['z'] - H_max) < Z_TOL]['node_id'].astype(int).tolist()
if roof_nodes:
    roof_mass_per_node = ROOF_WEIGHT / len(roof_nodes)
    for nid in roof_nodes:
        ops.mass(nid, roof_mass_per_node, roof_mass_per_node, roof_mass_per_node, 0, 0, 0)
    print(f"      z = {H_max:6.1f} cm (ROOF): {len(roof_nodes):3d} nodes, {ROOF_WEIGHT_KG:.2f} kg")

TOTAL_MASS_KG = total_floor_mass_kg + ROOF_WEIGHT_KG
print(f"\n    TOTAL MASS: {TOTAL_MASS_KG:.2f} kg")

# ==============================================================================
# 5. EIGENVALUE ANALYSIS
# ==============================================================================
print("\n[5] RUNNING EIGENVALUE ANALYSIS...")

num_modes = 12
try:
    eigenvalues = ops.eigen('-genBandArpack', num_modes)
    print(f"    Successfully computed {len(eigenvalues)} modes")
except:
    try:
        eigenvalues = ops.eigen(num_modes)
        print(f"    Successfully computed {len(eigenvalues)} modes (default solver)")
    except Exception as e:
        print(f"    ERROR: {e}")
        eigenvalues = []

# ==============================================================================
# 6. PROCESS RESULTS WITH AFAD SPECTRUM PARAMETERS
# ==============================================================================
print("\n[6] MODAL RESULTS WITH AFAD SPECTRUM (DD-1 to DD-4)...")

# TBDY 2018 spectrum parameters from AFAD Reports
# Location: 41.002136°N, 29.106832°E (İstanbul)
# Soil Class: ZD
AFAD_SPECTRUM = {
    'DD-1': {  # 2475 year return period (2% in 50 years)
        'SS': 1.544, 'S1': 0.427, 'FS': 1.000, 'F1': 1.873,
        'SDS': 1.544, 'SD1': 0.800,
        'TA': 0.104, 'TB': 0.518, 'TL': 6.0,
        'PGA': 0.628, 'PGV': 38.949
    },
    'DD-2': {  # 475 year return period (10% in 50 years) - DESIGN EARTHQUAKE
        'SS': 0.877, 'S1': 0.243, 'FS': 1.149, 'F1': 2.114,
        'SDS': 1.008, 'SD1': 0.514,
        'TA': 0.102, 'TB': 0.510, 'TL': 6.0,
        'PGA': 0.362, 'PGV': 22.389
    },
    'DD-3': {  # 72 year return period (50% in 50 years)
        'SS': 0.358, 'S1': 0.099, 'FS': 1.514, 'F1': 2.400,
        'SDS': 0.542, 'SD1': 0.238,
        'TA': 0.088, 'TB': 0.438, 'TL': 6.0,
        'PGA': 0.152, 'PGV': 9.459
    },
    'DD-4': {  # 43 year return period (68% in 50 years)
        'SS': 0.240, 'S1': 0.066, 'FS': 1.600, 'F1': 2.400,
        'SDS': 0.384, 'SD1': 0.158,
        'TA': 0.083, 'TB': 0.412, 'TL': 6.0,
        'PGA': 0.102, 'PGV': 6.370
    }
}

def get_spectral_acceleration(T, dd_level='DD-2'):
    """Calculate Sae(T) per TBDY 2018 for given DD level"""
    params = AFAD_SPECTRUM[dd_level]
    SDS = params['SDS']
    SD1 = params['SD1']
    TA = params['TA']
    TB = params['TB']
    TL = params['TL']
    
    if T < TA:
        return SDS * (0.4 + 0.6 * T / TA)
    elif T < TB:
        return SDS
    elif T < TL:
        return SD1 / T
    else:
        return SD1 * TL / (T * T)

def get_spectral_region(T, dd_level='DD-2'):
    """Determine spectral region for period T"""
    params = AFAD_SPECTRUM[dd_level]
    TA = params['TA']
    TB = params['TB']
    TL = params['TL']
    
    if T < TA:
        return "Ascending"
    elif T < TB:
        return "Plateau"
    elif T < TL:
        return "Descending"
    else:
        return "Long Period"

modal_results = []
if eigenvalues:
    # Use DD-2 as primary (design earthquake)
    dd_primary = 'DD-2'
    
    print(f"\n    Modal Results (using {dd_primary} spectrum):")
    print(f"    {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12} {'Sae (g)':<10} {'Region':<12}")
    print("    " + "-" * 52)
    
    for i, ev in enumerate(eigenvalues):
        if ev > 0:
            omega = np.sqrt(ev)
            freq = omega / (2 * np.pi)
            period = 1.0 / freq if freq > 0 else 0
            
            Sae = get_spectral_acceleration(period, dd_primary)
            region = get_spectral_region(period, dd_primary)
            
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
# 7. SPECTRUM ANALYSIS FOR ALL DD LEVELS
# ==============================================================================
print("\n" + "=" * 80)
print("SPECTRUM ANALYSIS FOR ALL DD LEVELS (AFAD)")
print("=" * 80)

if modal_results:
    T1 = modal_results[0]['period_s']
    
    print(f"\n    Fundamental Period: T₁ = {T1:.4f} s ({T1*1000:.1f} ms)")
    print(f"\n    {'DD Level':<10} {'SDS':<8} {'SD1':<8} {'TA (s)':<8} {'TB (s)':<8} {'Region':<12} {'Sae(T₁)':<10}")
    print("    " + "-" * 72)
    
    spectrum_results = {}
    for dd_level in ['DD-1', 'DD-2', 'DD-3', 'DD-4']:
        params = AFAD_SPECTRUM[dd_level]
        Sae = get_spectral_acceleration(T1, dd_level)
        region = get_spectral_region(T1, dd_level)
        
        spectrum_results[dd_level] = {
            'SDS': params['SDS'],
            'SD1': params['SD1'],
            'TA': params['TA'],
            'TB': params['TB'],
            'Sae_T1': Sae,
            'region': region,
            'PGA': params['PGA']
        }
        
        print(f"    {dd_level:<10} {params['SDS']:<8.3f} {params['SD1']:<8.3f} {params['TA']:<8.3f} {params['TB']:<8.3f} {region:<12} {Sae:<10.3f}g")
    
    # Detailed analysis
    print(f"\n    Detailed Analysis:")
    for dd_level in ['DD-1', 'DD-2', 'DD-3', 'DD-4']:
        params = AFAD_SPECTRUM[dd_level]
        region = get_spectral_region(T1, dd_level)
        Sae = get_spectral_acceleration(T1, dd_level)
        
        if region == "Ascending":
            status = "✅ Ascending (reduced Sae)"
            note = f"Sae = {Sae:.3f}g ({Sae/params['SDS']*100:.1f}% of SDS)"
        elif region == "Plateau":
            status = "⚠️  Plateau (max Sae)"
            note = f"Sae = SDS = {params['SDS']:.3f}g"
        else:
            status = "📉 Descending"
            note = f"Sae = {Sae:.3f}g ({Sae/params['SDS']*100:.1f}% of SDS)"
        
        print(f"      {dd_level}: {status} - {note}")

# ==============================================================================
# 7b. STIFFNESS REQUIREMENTS ANALYSIS
# ==============================================================================
print("\n" + "=" * 80)
print("STIFFNESS REQUIREMENTS TO REACH ASCENDING REGION")
print("=" * 80)

if modal_results:
    T1 = modal_results[0]['period_s']
    
    print(f"\n    Current Period: T₁ = {T1:.4f} s = {T1*1000:.1f} ms")
    print(f"\n    To reach ASCENDING region, period must be < TA for each DD level:")
    print(f"\n    {'DD Level':<10} {'TA (s)':<10} {'Target T':<12} {'Required K↑':<15} {'Required E':<15} {'Sae Reduction':<15}")
    print("    " + "-" * 85)
    
    for dd_level in ['DD-1', 'DD-2', 'DD-3', 'DD-4']:
        params = AFAD_SPECTRUM[dd_level]
        TA = params['TA']
        
        # Target period = 90% of TA (with safety margin)
        target_T = TA * 0.90
        
        # Stiffness ratio: T ∝ 1/√K → K₂/K₁ = (T₁/T₂)²
        stiffness_ratio = (T1 / target_T) ** 2
        
        # Required E value (current E = 170 kN/cm²)
        current_E = E
        required_E = current_E * stiffness_ratio
        
        # Sae at target period (in ascending region)
        Sae_current = get_spectral_acceleration(T1, dd_level)
        Sae_target = get_spectral_acceleration(target_T, dd_level)
        Sae_reduction = (1 - Sae_target / Sae_current) * 100
        
        print(f"    {dd_level:<10} {TA:<10.3f} {target_T*1000:.1f} ms      {stiffness_ratio:<15.1f}x {required_E:<15.0f} kN/cm²  {Sae_reduction:<15.1f}%")
    
    print(f"\n    INTERPRETATION:")
    print(f"    ─────────────────────────────────────────────────────────────────────────────")
    
    # Find the most demanding case (DD-3 or DD-4 have lowest TA)
    ta_values = {dd: AFAD_SPECTRUM[dd]['TA'] for dd in ['DD-1', 'DD-2', 'DD-3', 'DD-4']}
    min_ta_dd = min(ta_values, key=ta_values.get)
    min_ta = ta_values[min_ta_dd]
    target_critical = min_ta * 0.90
    stiffness_critical = (T1 / target_critical) ** 2
    
    print(f"    • Most demanding: {min_ta_dd} with TA = {min_ta:.3f}s")
    print(f"    • To be in Ascending for ALL DD levels: T < {min_ta:.3f}s")
    print(f"    • Recommended target: T ≈ {target_critical*1000:.0f} ms ({target_critical:.3f}s)")
    print(f"    • Required stiffness increase: {stiffness_critical:.1f}x")
    
    print(f"\n    OPTIONS TO INCREASE STIFFNESS:")
    print(f"    ─────────────────────────────────────────────────────────────────────────────")
    print(f"    1. Increase E modulus:")
    print(f"       Current: E = {E:.0f} kN/cm² ({E/100:.2f} GPa)")
    print(f"       Required: E = {E * stiffness_critical:.0f} kN/cm² ({E * stiffness_critical/100:.2f} GPa)")
    print(f"       Note: Standard balsa E ≈ 350 kN/cm², so this is {E * stiffness_critical / 350:.1f}x balsa")
    
    print(f"\n    2. Increase section size (I ∝ b⁴):")
    section_ratio = stiffness_critical ** 0.25  # I ∝ b⁴, so b ratio = (K ratio)^0.25
    new_section = b * 10 * section_ratio  # in mm
    print(f"       Current: {b*10:.0f}mm x {b*10:.0f}mm")
    print(f"       Required: ~{new_section:.1f}mm x {new_section:.1f}mm")
    
    print(f"\n    3. Add diagonal bracing (tijler):")
    print(f"       Braces add significant lateral stiffness")
    print(f"       Friend's approach: Add tijler in phase 2 of design")
    
    print(f"\n    4. Add shear walls (3mm balsa panels):")
    print(f"       Shear walls provide very high in-plane stiffness")
    print(f"       Current model has {len(conn_df[conn_df['element_type'].str.contains('shear')])} shear elements")
    
    # Calculate what period gives 50% Sae reduction for DD-2
    print(f"\n    PRACTICAL TARGETS:")
    print(f"    ─────────────────────────────────────────────────────────────────────────────")
    dd2_params = AFAD_SPECTRUM['DD-2']
    
    # Period for 50% of SDS
    # In ascending: Sae = SDS * (0.4 + 0.6*T/TA)
    # 0.5 * SDS = SDS * (0.4 + 0.6*T/TA)
    # 0.5 = 0.4 + 0.6*T/TA
    # 0.1 = 0.6*T/TA
    # T = TA * 0.1/0.6 = TA/6
    T_50pct = dd2_params['TA'] / 6
    
    # Period for 70% of SDS
    # 0.7 = 0.4 + 0.6*T/TA → T = TA * 0.5
    T_70pct = dd2_params['TA'] * 0.5
    
    # Period for 60% of SDS
    # 0.6 = 0.4 + 0.6*T/TA → T = TA * 0.333
    T_60pct = dd2_params['TA'] * (0.6 - 0.4) / 0.6
    
    print(f"    For DD-2 (Design Earthquake):")
    print(f"    ┌────────────────┬─────────────┬─────────────┬─────────────┐")
    print(f"    │ Target         │ Period (s)  │ Stiffness ↑ │ Sae (g)     │")
    print(f"    ├────────────────┼─────────────┼─────────────┼─────────────┤")
    print(f"    │ At TA (100%)   │ {dd2_params['TA']:.4f}      │ {(T1/dd2_params['TA'])**2:.1f}x         │ {dd2_params['SDS']:.3f}       │")
    print(f"    │ 70% of SDS     │ {T_70pct:.4f}      │ {(T1/T_70pct)**2:.1f}x         │ {0.7*dd2_params['SDS']:.3f}       │")
    print(f"    │ 60% of SDS     │ {T_60pct:.4f}      │ {(T1/T_60pct)**2:.1f}x         │ {0.6*dd2_params['SDS']:.3f}       │")
    print(f"    │ 50% of SDS     │ {T_50pct:.4f}      │ {(T1/T_50pct)**2:.1f}x        │ {0.5*dd2_params['SDS']:.3f}       │")
    print(f"    └────────────────┴─────────────┴─────────────┴─────────────┘")
    
    print(f"\n    RECOMMENDATION:")
    print(f"    ─────────────────────────────────────────────────────────────────────────────")
    print(f"    • Achieving T < {min_ta*1000:.0f} ms requires ~{stiffness_critical:.0f}x stiffness increase")
    print(f"    • This is likely VERY DIFFICULT with balsa wood model")
    print(f"    • The friend's T = 0.20s is already a good result")
    print(f"    • At T = 0.20s, you're in Plateau but at reasonable Sae values")

# ==============================================================================
# 8. SAVE RESULTS
# ==============================================================================
print("\n[8] SAVING RESULTS...")

os.makedirs('results/data', exist_ok=True)

# Save modal results
modal_df = pd.DataFrame(modal_results)
modal_df.to_csv('results/data/modal_results_calibrated.csv', index=False)

# Save comprehensive JSON
results_json = {
    'calibration_info': {
        'method': 'AFAD spectrum parameters from PDF reports',
        'location': {'lat': 41.002136, 'lon': 29.106832, 'desc': 'Istanbul'},
        'soil_class': 'ZD',
        'E_kN_cm2': E,
        'section_mm': f'{b*10:.0f}x{b*10:.0f}'
    },
    'model_info': {
        'total_nodes': len(pos_df),
        'total_elements': elem_count,
        'fixed_base_nodes': len(base_nodes),
        'height_cm': H_max,
        'units': 'kN, cm, s'
    },
    'material_properties': {
        'E_kN_cm2': E,
        'G_kN_cm2': G,
        'nu': nu,
        'section_cm': b,
        'A_cm2': A,
        'Iz_cm4': Iz
    },
    'mass_configuration': {
        'floor_weight_kg': FLOOR_WEIGHT_KG,
        'roof_weight_kg': ROOF_WEIGHT_KG,
        'total_mass_kg': TOTAL_MASS_KG,
        'weight_levels': actual_weight_levels
    },
    'afad_spectrum_parameters': AFAD_SPECTRUM,
    'spectrum_analysis': spectrum_results if 'spectrum_results' in dir() else {},
    'modal_results': modal_results
}

with open('results/data/modal_analysis_calibrated.json', 'w') as f:
    json.dump(results_json, f, indent=2)

# Save TSV for documentation
with open('docs/modal_periods_calibrated.tsv', 'w') as f:
    f.write("Mode\tPeriod_s\tFrequency_Hz\tSae_g\tSpectral_Region\n")
    for mr in modal_results:
        f.write(f"{mr['mode']}\t{mr['period_s']:.4f}\t{mr['frequency_hz']:.2f}\t{mr['Sae_g']:.3f}\t{mr['spectral_region']}\n")

print(f"    Saved: results/data/modal_results_calibrated.csv")
print(f"    Saved: results/data/modal_analysis_calibrated.json")
print(f"    Saved: docs/modal_periods_calibrated.tsv")

# ==============================================================================
# 9. CLEANUP
# ==============================================================================
ops.wipe()

print("\n" + "=" * 80)
print("CALIBRATED MODAL ANALYSIS COMPLETE")
print("=" * 80)
