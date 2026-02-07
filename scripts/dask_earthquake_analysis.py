"""
DASK Competition Earthquake Analysis
Based on Technical Specification 2025

Earthquake Levels:
- KYH1: 72-year return period (PGA ≈ 0.42g)
- KYH2: 475-year return period (PGA ≈ 0.70g) - Design earthquake
- KYH3: 2475-year return period (PGA ≈ 0.98g) - Maximum considered

Output: Maximum roof acceleration and relative displacement for each level
"""

import sys
import os
import re
import numpy as np
import pandas as pd
import comtypes.client
import time

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
AT2_FILE = os.path.join(DATA_DIR, "ground_motion", "BOL090.AT2")

# Competition parameters (from specification)
RETURN_PERIODS = {
    'KYH1': 72,    # years
    'KYH2': 475,   # years (design earthquake)
    'KYH3': 2475   # years (maximum considered)
}

# PGA values from Afyon Dinar elastic spectrum (approximate from spec)
PGA_VALUES = {
    'KYH1': 0.42,  # g
    'KYH2': 0.70,  # g
    'KYH3': 0.98   # g
}

# Scale factors to match target PGA (BOL090 has PGA = 0.8224g)
ORIGINAL_PGA = 0.8224  # g (from BOL090.AT2)

def parse_at2(filepath):
    """Parse PEER AT2 format earthquake record."""
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    header = lines[3]
    npts = int(re.search(r'NPTS\s*=\s*(\d+)', header).group(1))
    dt = float(re.search(r'DT\s*=\s*([.\d]+)', header).group(1))
    
    acc = []
    for line in lines[4:]:
        for val in line.split():
            try:
                acc.append(float(val))
            except:
                pass
    
    return np.arange(npts) * dt, np.array(acc[:npts]), dt, npts

print("=" * 70)
print("DASK COMPETITION - EARTHQUAKE ANALYSIS")
print("=" * 70)

# Load earthquake record
print(f"\nLoading earthquake: {os.path.basename(AT2_FILE)}")
time_arr, acc_g, dt, npts = parse_at2(AT2_FILE)
print(f"  Duration: {time_arr[-1]:.1f}s, Original PGA: {ORIGINAL_PGA:.4f}g")

# Calculate scale factors for each earthquake level
scale_factors = {}
for level, target_pga in PGA_VALUES.items():
    scale_factors[level] = target_pga / ORIGINAL_PGA
    print(f"  {level}: Target PGA = {target_pga}g, Scale Factor = {scale_factors[level]:.4f}")

# Connect to SAP2000
print("\nConnecting to SAP2000...")
try:
    sap_object = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    sap_model = sap_object.SapModel
    print("  Connected successfully")
except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

# Load node data
pos_df = pd.read_csv(os.path.join(DATA_DIR, "position_matrix.csv"))
max_z = pos_df['z'].max()  # Top floor level (m)
min_z = pos_df[pos_df['z'] > 0]['z'].min()  # First floor level
building_height = max_z  # Total height in meters

top_nodes = pos_df[pos_df['z'] == max_z]['node_id'].tolist()
print(f"\nBuilding height: {building_height} m")
print(f"Top floor nodes: {len(top_nodes)}")

# =========================================================================
# STEP 1: Setup Mass
# =========================================================================
print("\n--- MASS SETUP ---")

# Floor mass (kg) - typical for office/hotel building
# Assuming 8m x 8m tributary area, 500 kg/m² (from spec typical values)
MASS_PER_NODE = 32000  # kg
mass_value = MASS_PER_NODE / 1e6  # Convert to kN·s²/mm

mass_count = 0
for idx, row in pos_df.iterrows():
    if int(row['floor']) > 0:
        node_name = f"N{int(row['node_id'])}"
        try:
            ret = sap_model.PointObj.SetMass(node_name, [mass_value, mass_value, 0, 0, 0, 0], 0, True)
            mass_count += 1
        except:
            pass

total_mass = mass_count * MASS_PER_NODE / 1000  # tonnes
print(f"  Added mass to {mass_count} nodes")
print(f"  Total building mass: {total_mass:.0f} tonnes")

# =========================================================================
# STEP 2: Define Response Spectra for Each Earthquake Level
# =========================================================================
print("\n--- RESPONSE SPECTRA ---")

# Afyon Dinar design spectrum parameters (from EK C of specification)
# Type 1 elastic spectrum, Soil class C (assumed)
# Spectral shape parameters
TB = 0.15  # Corner period (s)
TC = 0.40  # Corner period (s)
TD = 2.00  # Corner period (s)
S = 1.15   # Soil factor

def create_spectrum_points(pga, s=S, tb=TB, tc=TC, td=TD):
    """Create elastic design spectrum per Turkish Building Code / Eurocode 8."""
    # Spectral acceleration = ag * S * η * β(T)
    # Where β(T) is the spectral shape
    eta = 1.0  # Damping correction (5% damping)
    
    T_vals = [0.0, tb, tc, 1.0, td, 4.0]
    Sa_vals = []
    
    for T in T_vals:
        if T < tb:
            beta = 1 + (2.5 - 1) * T / tb
        elif T < tc:
            beta = 2.5
        elif T < td:
            beta = 2.5 * tc / T
        else:
            beta = 2.5 * tc * td / (T * T)
        
        Sa = pga * s * eta * beta
        Sa_vals.append(Sa)
    
    return T_vals, Sa_vals

for level, pga in PGA_VALUES.items():
    spec_name = f"SPEC_{level}"
    
    try:
        sap_model.Func.Delete(spec_name)
    except:
        pass
    
    T_vals, Sa_vals = create_spectrum_points(pga)
    
    try:
        ret = sap_model.Func.FuncRS.SetUser(spec_name, len(T_vals), T_vals, Sa_vals, 0.05)
        print(f"  Created {spec_name}: PGA={pga}g, max Sa={max(Sa_vals):.3f}g")
    except Exception as e:
        print(f"  Error creating {spec_name}: {e}")

# =========================================================================
# STEP 3: Define Response Spectrum Load Cases
# =========================================================================
print("\n--- LOAD CASES ---")

GRAVITY = 9810.0  # mm/s² (model in mm)

for level in ['KYH1', 'KYH2', 'KYH3']:
    spec_name = f"SPEC_{level}"
    
    for direction in ['X', 'Y']:
        case_name = f"{level}_{direction}"
        load_dir = "U1" if direction == 'X' else "U2"
        
        try:
            sap_model.LoadCases.Delete(case_name)
        except:
            pass
        
        try:
            ret = sap_model.LoadCases.ResponseSpectrum.SetCase(case_name)
            ret = sap_model.LoadCases.ResponseSpectrum.SetLoads(
                case_name, 1, [load_dir], [spec_name], [GRAVITY], ["Global"], [0.0]
            )
            print(f"  Created {case_name}")
        except Exception as e:
            print(f"  Error {case_name}: {e}")

# =========================================================================
# STEP 4: Modal Analysis
# =========================================================================
print("\n--- MODAL ANALYSIS ---")

try:
    sap_model.LoadCases.Delete("MODAL")
except:
    pass

sap_model.LoadCases.ModalEigen.SetCase("MODAL")
sap_model.LoadCases.ModalEigen.SetNumberModes("MODAL", 12, 1)

sap_model.Analyze.SetRunCaseFlag("", False, True)
sap_model.Analyze.SetRunCaseFlag("MODAL", True, False)

print("  Running modal analysis...")
start = time.time()
ret = sap_model.Analyze.RunAnalysis()
print(f"  Completed in {time.time()-start:.1f}s")

# Get fundamental period
try:
    ret = sap_model.Results.Modal.PeriodFreq()
    if isinstance(ret, (list, tuple)) and len(ret) > 4:
        periods = ret[4]
        if periods:
            T1 = periods[0]
            print(f"  Fundamental period T1 = {T1:.3f} s")
except:
    T1 = 0
    print("  Could not retrieve period")

# =========================================================================
# STEP 5: Run All Response Spectrum Cases
# =========================================================================
print("\n--- RUNNING ANALYSES ---")

all_cases = [f"{level}_{d}" for level in ['KYH1', 'KYH2', 'KYH3'] for d in ['X', 'Y']]

sap_model.Analyze.SetRunCaseFlag("", False, True)
for case in all_cases:
    sap_model.Analyze.SetRunCaseFlag(case, True, False)

start = time.time()
ret = sap_model.Analyze.RunAnalysis()
print(f"  All cases completed in {time.time()-start:.1f}s")

# =========================================================================
# STEP 6: Extract Results
# =========================================================================
print("\n" + "=" * 70)
print("RESULTS: MAXIMUM TOP DISPLACEMENTS")
print("=" * 70)

results = {}

for level in ['KYH1', 'KYH2', 'KYH3']:
    results[level] = {'ux': 0, 'uy': 0, 'drift_x': 0, 'drift_y': 0}
    
    for direction in ['X', 'Y']:
        case_name = f"{level}_{direction}"
        
        sap_model.Results.Setup.DeselectAllCasesAndCombosForOutput()
        sap_model.Results.Setup.SetCaseSelectedForOutput(case_name, True)
        
        max_ux = 0
        max_uy = 0
        
        for node_id in top_nodes:
            node_name = f"N{node_id}"
            
            try:
                ret = sap_model.Results.JointDispl(node_name, 0)
                
                if isinstance(ret, (list, tuple)) and len(ret) > 7:
                    n_res = ret[0] if isinstance(ret[0], int) else 0
                    u1 = ret[6] if len(ret) > 6 else []
                    u2 = ret[7] if len(ret) > 7 else []
                    
                    for i in range(n_res):
                        ux = abs(u1[i]) if i < len(u1) else 0
                        uy = abs(u2[i]) if i < len(u2) else 0
                        max_ux = max(max_ux, ux)
                        max_uy = max(max_uy, uy)
            except:
                pass
        
        if direction == 'X':
            results[level]['ux'] = max(results[level]['ux'], max_ux)
        else:
            results[level]['uy'] = max(results[level]['uy'], max_uy)

# Calculate drift ratios
height_mm = building_height * 1000  # Convert to mm
for level in results:
    results[level]['drift_x'] = results[level]['ux'] / height_mm * 100
    results[level]['drift_y'] = results[level]['uy'] / height_mm * 100

# Print results table
print(f"\nLocation: Afyon Dinar")
print(f"Building Height: {building_height} m")
print(f"Total Mass: {total_mass:.0f} tonnes")
if T1 > 0:
    print(f"Fundamental Period: {T1:.3f} s")

print("\n" + "-" * 80)
print(f"{'Level':<10} {'Return':<10} {'PGA':<8} {'Max Ux':<12} {'Max Uy':<12} {'Drift X':<10} {'Drift Y':<10}")
print(f"{'':10} {'Period':10} {'(g)':8} {'(mm)':12} {'(mm)':12} {'(%)':10} {'(%)':10}")
print("-" * 80)

for level in ['KYH1', 'KYH2', 'KYH3']:
    r = results[level]
    print(f"{level:<10} {RETURN_PERIODS[level]:<10} {PGA_VALUES[level]:<8.2f} "
          f"{r['ux']:<12.2f} {r['uy']:<12.2f} {r['drift_x']:<10.3f} {r['drift_y']:<10.3f}")

print("-" * 80)

# Maximum envelope
max_ux = max(r['ux'] for r in results.values())
max_uy = max(r['uy'] for r in results.values())
max_drift = max(max(r['drift_x'], r['drift_y']) for r in results.values())

print(f"{'ENVELOPE':<10} {'-':<10} {'-':<8} {max_ux:<12.2f} {max_uy:<12.2f} {max_drift:<10.3f} {'-':<10}")

# =========================================================================
# STEP 7: Competition Predictions Format
# =========================================================================
print("\n" + "=" * 70)
print("COMPETITION SUBMISSION DATA")
print("=" * 70)

print("\nDeprem Davranışı Tahminleri (Earthquake Response Predictions):")
print("-" * 60)

for level in ['KYH1', 'KYH2', 'KYH3']:
    r = results[level]
    max_disp = max(r['ux'], r['uy'])
    # Estimate acceleration amplification (Sa at T1 / PGA)
    if T1 > 0 and T1 < 0.4:
        acc_amp = 2.5
    elif T1 < 2.0:
        acc_amp = 2.5 * 0.4 / T1
    else:
        acc_amp = 2.5 * 0.4 * 2.0 / (T1 * T1)
    
    roof_acc = PGA_VALUES[level] * acc_amp
    
    print(f"\n{level} (TR = {RETURN_PERIODS[level]} yıl, PGA = {PGA_VALUES[level]}g):")
    print(f"  Maksimum Çatı Ötelemesi (Max Roof Displacement): {max_disp:.2f} mm")
    print(f"  Göreli Çatı Ötelemesi (Relative Drift): {max_disp/height_mm*100:.3f}%")
    print(f"  Tahmini Çatı İvmesi (Est. Roof Acceleration): {roof_acc:.3f}g")

# Save results
results_df = pd.DataFrame({
    'Level': ['KYH1', 'KYH2', 'KYH3'],
    'Return_Period_years': [72, 475, 2475],
    'PGA_g': [0.42, 0.70, 0.98],
    'Max_Ux_mm': [results[l]['ux'] for l in ['KYH1', 'KYH2', 'KYH3']],
    'Max_Uy_mm': [results[l]['uy'] for l in ['KYH1', 'KYH2', 'KYH3']],
    'Drift_X_percent': [results[l]['drift_x'] for l in ['KYH1', 'KYH2', 'KYH3']],
    'Drift_Y_percent': [results[l]['drift_y'] for l in ['KYH1', 'KYH2', 'KYH3']]
})

results_file = os.path.join(DATA_DIR, "dask_earthquake_results.csv")
results_df.to_csv(results_file, index=False)
print(f"\nResults saved to: {results_file}")

# Save model
sap_model.File.Save(os.path.join(DATA_DIR, "DASK_Building_v2.sdb"))
print("Model saved.")

print("\n" + "=" * 70)
print("NOTES:")
print("-" * 70)
print("1. These are Response Spectrum Analysis results")
print("2. For competition submission, also perform Time History Analysis")
print("3. KYH2 (475-year) is the design earthquake - key for damage assessment")
print("4. Maximum drift should be < 2% for life safety performance level")
print("=" * 70)
