"""
Earthquake Analysis Script v3
- Uses Modal Response Spectrum Analysis (simpler, more reliable)
- Also runs Time History for comparison
"""

import sys
import os
import re
import numpy as np
import pandas as pd
import comtypes.client
import time

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Use paths from config
DATA_DIR = config.DATA_DIR
SAP2000_DIR = config.SAP2000_DIR
RESULTS_DATA_DIR = config.RESULTS_DATA_DIR
AT2_FILE = config.EARTHQUAKE_FILE

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

print("=" * 70)
print("EARTHQUAKE ANALYSIS")
print("=" * 70)

# Load earthquake data
print(f"\nLoading: {AT2_FILE}")
time_arr, acc_g, dt, npts = parse_at2(AT2_FILE)
pga = np.max(np.abs(acc_g))
print(f"  Duration: {time_arr[-1]:.1f}s, PGA: {pga:.4f}g")

# Connect to SAP2000
print("\nConnecting to SAP2000...")
try:
    sap_object = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
    sap_model = sap_object.SapModel
    print("  Connected")
except Exception as e:
    print(f"  Error: {e}")
    sys.exit(1)

# Load position data
pos_df = pd.read_csv(os.path.join(DATA_DIR, "position_matrix.csv"))
max_z = pos_df['z'].max()
top_nodes = pos_df[pos_df['z'] == max_z]['node_id'].tolist()
print(f"  Top nodes at Z={max_z}m: {len(top_nodes)} nodes")

# ---------------------------------------------------------------------------
# STEP 1: Add Mass to Model (DASK Competition Specs)
# ---------------------------------------------------------------------------
print("\n--- ADDING MASS (DASK SPECS) ---")

# DASK 2025 Competition Masses:
# - 1.60 kg every 3 floors (at floors 3, 6, 9, 12, 15, 18, 21, 24)
# - 2.22 kg at roof (floor 25)
# Mass is distributed across all nodes at that floor

MASS_FLOORS_1_60 = [3, 6, 9, 12, 15, 18, 21, 24]  # 1.60 kg per floor
MASS_FLOOR_ROOF = 25  # 2.22 kg
MASS_1_60_KG = 1.60
MASS_ROOF_KG = 2.22

# Clear any existing masses first
for idx, row in pos_df.iterrows():
    node_name = f"N{int(row['node_id'])}"
    try:
        sap_model.PointObj.SetMass(node_name, [0, 0, 0, 0, 0, 0], 0, True)
    except:
        pass

# Count nodes per floor for distribution
floor_nodes = {}
for idx, row in pos_df.iterrows():
    floor = int(row['floor'])
    if floor not in floor_nodes:
        floor_nodes[floor] = []
    floor_nodes[floor].append(int(row['node_id']))

mass_count = 0
total_mass_kg = 0.0

# Apply 1.60 kg to floors 3, 6, 9, 12, 15, 18, 21, 24
for floor in MASS_FLOORS_1_60:
    if floor in floor_nodes:
        n_nodes = len(floor_nodes[floor])
        mass_per_node_kg = MASS_1_60_KG / n_nodes
        mass_value = mass_per_node_kg / 1e6  # Convert kg to kN*s2/mm

        for node_id in floor_nodes[floor]:
            node_name = f"N{node_id}"
            try:
                ret = sap_model.PointObj.SetMass(node_name, [mass_value, mass_value, 0, 0, 0, 0], 0, True)
                mass_count += 1
            except:
                pass

        total_mass_kg += MASS_1_60_KG
        print(f"  Floor {floor}: {MASS_1_60_KG} kg distributed to {n_nodes} nodes ({mass_per_node_kg*1000:.1f} g/node)")

# Apply 2.22 kg to roof (floor 25)
if MASS_FLOOR_ROOF in floor_nodes:
    n_nodes = len(floor_nodes[MASS_FLOOR_ROOF])
    mass_per_node_kg = MASS_ROOF_KG / n_nodes
    mass_value = mass_per_node_kg / 1e6  # Convert kg to kN*s2/mm

    for node_id in floor_nodes[MASS_FLOOR_ROOF]:
        node_name = f"N{node_id}"
        try:
            ret = sap_model.PointObj.SetMass(node_name, [mass_value, mass_value, 0, 0, 0, 0], 0, True)
            mass_count += 1
        except:
            pass

    total_mass_kg += MASS_ROOF_KG
    print(f"  Floor {MASS_FLOOR_ROOF} (roof): {MASS_ROOF_KG} kg distributed to {n_nodes} nodes ({mass_per_node_kg*1000:.1f} g/node)")

print(f"\n  Total tige mass: {total_mass_kg:.2f} kg")
print(f"  Applied to {mass_count} nodes")
total_mass = total_mass_kg

# Save and refresh
sap_model.File.Save(os.path.join(SAP2000_DIR, "DASK_Building_v2.sdb"))

# ---------------------------------------------------------------------------
# STEP 2: Modal Analysis
# ---------------------------------------------------------------------------
print("\n--- MODAL ANALYSIS ---")

try:
    sap_model.LoadCases.Delete("MODAL")
except:
    pass

ret = sap_model.LoadCases.ModalEigen.SetCase("MODAL")
ret = sap_model.LoadCases.ModalEigen.SetNumberModes("MODAL", 12, 1)
print(f"  Created MODAL case")

# Run modal
sap_model.Analyze.SetRunCaseFlag("", False, True)
sap_model.Analyze.SetRunCaseFlag("MODAL", True, False)

print("  Running modal analysis...")
start = time.time()
ret = sap_model.Analyze.RunAnalysis()
print(f"  Completed in {time.time()-start:.1f}s")

# Get periods - try different API methods
try:
    # Set output for MODAL case
    sap_model.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap_model.Results.Setup.SetCaseSelectedForOutput("MODAL", True)

    # Try ModalPeriod method (SAP2000 v19+)
    ret = sap_model.Results.ModalPeriod("MODAL")
    print(f"  ModalPeriod result: {ret[:3] if isinstance(ret, (list,tuple)) else ret}...")

    if isinstance(ret, (list, tuple)) and len(ret) > 3:
        n_modes = ret[0] if isinstance(ret[0], int) else 0
        periods = ret[2] if len(ret) > 2 else []
        freqs = ret[3] if len(ret) > 3 else []

        if periods and len(periods) > 0:
            print(f"\n  Modal Results ({n_modes} modes):")
            print(f"  {'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12}")
            print(f"  {'-'*30}")
            for i in range(min(6, len(periods))):
                T = periods[i] if i < len(periods) else 0
                f = freqs[i] if i < len(freqs) else 0
                print(f"  {i+1:<6} {T:<12.4f} {f:<12.4f}")

            T1 = periods[0] if len(periods) > 0 else 0
            print(f"\n  Fundamental Period T1 = {T1:.4f} s")
        else:
            print("  No periods found")
    else:
        print(f"  Unexpected result: {type(ret)}, len={len(ret) if isinstance(ret,(list,tuple)) else 'N/A'}")
except Exception as e:
    print(f"  Period extraction error: {e}")

# ---------------------------------------------------------------------------
# STEP 3: Response Spectrum Function
# ---------------------------------------------------------------------------
print("\n--- RESPONSE SPECTRUM ---")

# Create a simple design spectrum (Eurocode 8 Type 1, Soil C, ag=0.4g)
# This is easier than time history for verification
spec_name = "EC8_SPECTRUM"

try:
    sap_model.Func.Delete(spec_name)
except:
    pass

# Define spectrum points (T, Sa/g)
T_vals = [0, 0.15, 0.2, 0.6, 2.0, 4.0]
Sa_vals = [0.4*2.5, 0.4*2.5, 0.4*2.5, 0.4*2.5*0.6/0.6, 0.4*2.5*0.6*0.2/2.0, 0.4*2.5*0.6*0.2/4.0]

try:
    ret = sap_model.Func.FuncRS.SetUser(spec_name, len(T_vals), T_vals, Sa_vals, 0.05)
    print(f"  Created response spectrum function: {ret}")
except Exception as e:
    print(f"  Spectrum function error: {e}")

# ---------------------------------------------------------------------------
# STEP 4: Response Spectrum Load Cases
# ---------------------------------------------------------------------------
print("\n--- RS LOAD CASES ---")

for case in ["RSX", "RSY"]:
    try:
        sap_model.LoadCases.Delete(case)
    except:
        pass

try:
    # Create RS cases
    ret = sap_model.LoadCases.ResponseSpectrum.SetCase("RSX")
    print(f"  Created RSX: {ret}")

    # Set direction (U1 for X)
    ret = sap_model.LoadCases.ResponseSpectrum.SetLoads("RSX", 1, ["U1"], [spec_name], [9810.0], ["Global"], [0.0])
    print(f"  Set RSX loads: {ret}")

    ret = sap_model.LoadCases.ResponseSpectrum.SetCase("RSY")
    ret = sap_model.LoadCases.ResponseSpectrum.SetLoads("RSY", 1, ["U2"], [spec_name], [9810.0], ["Global"], [0.0])
    print(f"  Created RSY")

except Exception as e:
    print(f"  RS case error: {e}")

# ---------------------------------------------------------------------------
# STEP 5: Run RS Analysis
# ---------------------------------------------------------------------------
print("\n--- RUNNING RS ANALYSIS ---")

sap_model.Analyze.SetRunCaseFlag("", False, True)
sap_model.Analyze.SetRunCaseFlag("RSX", True, False)
sap_model.Analyze.SetRunCaseFlag("RSY", True, False)

start = time.time()
ret = sap_model.Analyze.RunAnalysis()
print(f"  Analysis returned: {ret}")
print(f"  Completed in {time.time()-start:.1f}s")

# Check case status
try:
    for case in ["RSX", "RSY"]:
        status = sap_model.Analyze.GetCaseStatus(case)
        print(f"  {case} status: {status}")
except Exception as e:
    print(f"  Status check error: {e}")

# ---------------------------------------------------------------------------
# STEP 6: Extract RS Results
# ---------------------------------------------------------------------------
print("\n--- RS RESULTS ---")

sap_model.Results.Setup.DeselectAllCasesAndCombosForOutput()
sap_model.Results.Setup.SetCaseSelectedForOutput("RSX", True)
sap_model.Results.Setup.SetCaseSelectedForOutput("RSY", True)

rs_results = {'RSX': {'ux': 0, 'uy': 0}, 'RSY': {'ux': 0, 'uy': 0}}

# Check all nodes, not just top
all_node_ids = pos_df['node_id'].tolist()

for node_id in all_node_ids:
    node_name = f"N{node_id}"
    try:
        ret = sap_model.Results.JointDispl(node_name, 0)

        if isinstance(ret, (list, tuple)) and len(ret) > 7:
            n_res = ret[0] if isinstance(ret[0], int) else 0
            cases = ret[3] if len(ret) > 3 else []
            u1 = ret[6] if len(ret) > 6 else []
            u2 = ret[7] if len(ret) > 7 else []

            # Debug first top node
            if node_id == top_nodes[0]:
                print(f"\n  Top node {node_name}: {n_res} results")
                for i in range(min(n_res, 4)):
                    c = cases[i] if i < len(cases) else "?"
                    x = u1[i] if i < len(u1) else 0
                    y = u2[i] if i < len(u2) else 0
                    print(f"    {c}: Ux={x:.6f}mm, Uy={y:.6f}mm")

            for i in range(n_res):
                case = cases[i] if i < len(cases) else ""
                ux = abs(u1[i]) if i < len(u1) else 0
                uy = abs(u2[i]) if i < len(u2) else 0

                if case in rs_results:
                    rs_results[case]['ux'] = max(rs_results[case]['ux'], ux)
                    rs_results[case]['uy'] = max(rs_results[case]['uy'], uy)

    except Exception as e:
        if node_id == top_nodes[0]:
            print(f"  Error: {e}")

# Print max values found
print(f"\n  Max across all nodes:")
print(f"    RSX: Ux={rs_results['RSX']['ux']:.3f}mm, Uy={rs_results['RSX']['uy']:.3f}mm")
print(f"    RSY: Ux={rs_results['RSY']['ux']:.3f}mm, Uy={rs_results['RSY']['uy']:.3f}mm")

# ---------------------------------------------------------------------------
# STEP 7: Time History Analysis (if RS works)
# ---------------------------------------------------------------------------
print("\n--- TIME HISTORY ---")

func_name = "DUZCE_EQ"
try:
    sap_model.Func.Delete(func_name)
except:
    pass

try:
    ret = sap_model.Func.FuncTH.SetFromFile(func_name, AT2_FILE, 0, 0, 1, 2, True)
    print(f"  Loaded TH function from file")
except Exception as e:
    print(f"  TH function error: {e}")

for case in ["TH_X", "TH_Y"]:
    try:
        sap_model.LoadCases.Delete(case)
    except:
        pass

# Use modal time history (faster than direct integration)
output_dt = 0.02  # 50 Hz output
num_steps = int(time_arr[-1] / output_dt)

try:
    # Modal Time History is typically faster
    ret = sap_model.LoadCases.ModHistLinear.SetCase("TH_X")
    ret = sap_model.LoadCases.ModHistLinear.SetTimeStep("TH_X", num_steps, output_dt)
    ret = sap_model.LoadCases.ModHistLinear.SetLoads("TH_X", 1, ["Accel"], ["U1"],
                                                      [func_name], [9810.0], [1.0], [0.0], ["Global"], [0.0])
    print(f"  Created TH_X (Modal): {ret}")

    ret = sap_model.LoadCases.ModHistLinear.SetCase("TH_Y")
    ret = sap_model.LoadCases.ModHistLinear.SetTimeStep("TH_Y", num_steps, output_dt)
    ret = sap_model.LoadCases.ModHistLinear.SetLoads("TH_Y", 1, ["Accel"], ["U2"],
                                                      [func_name], [9810.0], [1.0], [0.0], ["Global"], [0.0])
    print(f"  Created TH_Y (Modal)")

except Exception as e:
    print(f"  TH case error: {e}")
    # Fallback to direct integration
    try:
        ret = sap_model.LoadCases.DirHistLinear.SetCase("TH_X")
        ret = sap_model.LoadCases.DirHistLinear.SetTimeStep("TH_X", num_steps, output_dt)
        ret = sap_model.LoadCases.DirHistLinear.SetLoads("TH_X", 1, ["Accel"], ["U1"],
                                                          [func_name], [9810.0], [1.0], [0.0], ["Global"], [0.0])
        ret = sap_model.LoadCases.DirHistLinear.SetCase("TH_Y")
        ret = sap_model.LoadCases.DirHistLinear.SetTimeStep("TH_Y", num_steps, output_dt)
        ret = sap_model.LoadCases.DirHistLinear.SetLoads("TH_Y", 1, ["Accel"], ["U2"],
                                                          [func_name], [9810.0], [1.0], [0.0], ["Global"], [0.0])
        print(f"  Using Direct Integration fallback")
    except Exception as e2:
        print(f"  Direct integration also failed: {e2}")

# Run TH
sap_model.Analyze.SetRunCaseFlag("", False, True)
sap_model.Analyze.SetRunCaseFlag("TH_X", True, False)
sap_model.Analyze.SetRunCaseFlag("TH_Y", True, False)

print("  Running time history (may take a few minutes)...")
start = time.time()
ret = sap_model.Analyze.RunAnalysis()
print(f"  Completed in {time.time()-start:.1f}s")

# Extract TH results
sap_model.Results.Setup.DeselectAllCasesAndCombosForOutput()
sap_model.Results.Setup.SetCaseSelectedForOutput("TH_X", True)
sap_model.Results.Setup.SetCaseSelectedForOutput("TH_Y", True)
sap_model.Results.Setup.SetOptionDirectHist(0)  # Envelopes

th_results = {'TH_X': {'ux': 0, 'uy': 0}, 'TH_Y': {'ux': 0, 'uy': 0}}

for node_id in top_nodes:
    node_name = f"N{node_id}"
    try:
        ret = sap_model.Results.JointDispl(node_name, 0)

        if isinstance(ret, (list, tuple)) and len(ret) > 7:
            n_res = ret[0] if isinstance(ret[0], int) else 0
            cases = ret[3] if len(ret) > 3 else []
            u1 = ret[6] if len(ret) > 6 else []
            u2 = ret[7] if len(ret) > 7 else []

            if node_id == top_nodes[0]:
                print(f"\n  TH {node_name}: {n_res} results")
                for i in range(min(n_res, 4)):
                    print(f"    {cases[i]}: Ux={u1[i]:.3f}, Uy={u2[i]:.3f}")

            for i in range(n_res):
                case = cases[i] if i < len(cases) else ""
                ux = abs(u1[i]) if i < len(u1) else 0
                uy = abs(u2[i]) if i < len(u2) else 0

                if case in th_results:
                    th_results[case]['ux'] = max(th_results[case]['ux'], ux)
                    th_results[case]['uy'] = max(th_results[case]['uy'], uy)

    except:
        pass

# ---------------------------------------------------------------------------
# SUMMARY
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("SUMMARY: MAXIMUM TOP DISPLACEMENTS")
print("=" * 70)

print(f"\nBuilding height: {max_z} m (model scale)")
print(f"Total tige mass: {total_mass:.2f} kg")
print(f"Earthquake: Duzce 1999, PGA = {pga:.3f}g")

print("\n{:<15} {:>15} {:>15}".format("Analysis", "Max Ux (mm)", "Max Uy (mm)"))
print("-" * 45)

print("{:<15} {:>15.2f} {:>15.2f}".format("RS X-dir", rs_results['RSX']['ux'], rs_results['RSX']['uy']))
print("{:<15} {:>15.2f} {:>15.2f}".format("RS Y-dir", rs_results['RSY']['ux'], rs_results['RSY']['uy']))
print("{:<15} {:>15.2f} {:>15.2f}".format("TH X-dir", th_results['TH_X']['ux'], th_results['TH_X']['uy']))
print("{:<15} {:>15.2f} {:>15.2f}".format("TH Y-dir", th_results['TH_Y']['ux'], th_results['TH_Y']['uy']))

max_ux = max(rs_results['RSX']['ux'], rs_results['RSY']['ux'],
             th_results['TH_X']['ux'], th_results['TH_Y']['ux'])
max_uy = max(rs_results['RSX']['uy'], rs_results['RSY']['uy'],
             th_results['TH_X']['uy'], th_results['TH_Y']['uy'])

print("-" * 45)
print("{:<15} {:>15.2f} {:>15.2f}".format("ENVELOPE", max_ux, max_uy))

if max_ux > 0 or max_uy > 0:
    height_mm = max_z * 1000
    drift = max(max_ux, max_uy) / height_mm * 100
    print(f"\nMax Drift Ratio: {drift:.3f}%")

# Save
results_df = pd.DataFrame({
    'Analysis': ['RSX', 'RSY', 'TH_X', 'TH_Y', 'ENVELOPE'],
    'Max_Ux_mm': [rs_results['RSX']['ux'], rs_results['RSY']['ux'],
                  th_results['TH_X']['ux'], th_results['TH_Y']['ux'], max_ux],
    'Max_Uy_mm': [rs_results['RSX']['uy'], rs_results['RSY']['uy'],
                  th_results['TH_X']['uy'], th_results['TH_Y']['uy'], max_uy]
})
results_df.to_csv(os.path.join(RESULTS_DATA_DIR, "earthquake_results.csv"), index=False)
print(f"\nResults saved to earthquake_results.csv")

sap_model.File.Save(os.path.join(SAP2000_DIR, "DASK_Building_v2.sdb"))
print("Model saved.")
