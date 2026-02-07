"""
Simplified OpenSees Modal Analysis for DASK 2026 Twin Towers
Faster analysis with better error handling
"""

import numpy as np
import pandas as pd
from pathlib import Path
import sys

SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
RESULTS_DIR = SCRIPT_DIR.parent / 'results' / 'data'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("OPENSEES MODAL ANALYSIS - DASK 2026 Twin Towers")
print("=" * 70)

# Material Properties - Balsa Wood
E_BALSA = 3500.0  # MPa
DENSITY = 160.0   # kg/m³
NU = 0.3
G_BALSA = E_BALSA / (2 * (1 + NU))

# Section: 6mm x 6mm
b = 6.0  # mm
A = b * b  # 36 mm²
I = (b * b**3) / 12  # 108 mm⁴
J = 0.1406 * b**4  # 182 mm⁴

print(f"\nMaterial: E={E_BALSA} MPa, G={G_BALSA:.1f} MPa")
print(f"Section: {b}x{b} mm, A={A} mm², I={I} mm⁴")

# Load data
print("\nLoading model data...")
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')

print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# Scale: Model is in meters, we work in mm (scale 1:100, so 1m model = 10mm maket)
SCALE = 10.0  # mm per model meter

try:
    import openseespy.opensees as ops
    print("\nOpenSeesPy loaded successfully")
except ImportError:
    print("ERROR: OpenSeesPy not available")
    sys.exit(1)

# Build model
print("\nBuilding OpenSees model...")
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes
node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x = row['x'] * SCALE
    y = row['y'] * SCALE
    z = row['z'] * SCALE
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

print(f"  Nodes created: {len(node_map)}")

# Fix base nodes
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)
print(f"  Base nodes fixed: {len(base_nodes)}")

# Geometric transformations (one for each primary direction)
ops.geomTransf('Linear', 1, 0, 1, 0)  # Elements in XZ plane
ops.geomTransf('Linear', 2, 1, 0, 0)  # Elements in YZ plane
ops.geomTransf('Linear', 3, 1, 0, 0)  # Columns (vertical)

# Create elements - simplified approach
print("  Creating elements...")
elem_created = 0
elem_failed = 0

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])

    if ni not in node_map or nj not in node_map:
        elem_failed += 1
        continue

    xi, yi, zi = node_map[ni]
    xj, yj, zj = node_map[nj]

    # Check for zero-length elements
    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 0.1:
        elem_failed += 1
        continue

    dx = abs(xj - xi)
    dy = abs(yj - yi)
    dz = abs(zj - zi)

    # Choose transformation based on element direction
    if dz > max(dx, dy):
        transf = 3  # Vertical
    elif dx >= dy:
        transf = 1  # X-dominant
    else:
        transf = 2  # Y-dominant

    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A, E_BALSA, G_BALSA, J, I, I, transf)
        elem_created += 1
    except Exception as e:
        elem_failed += 1

print(f"  Elements created: {elem_created}")
print(f"  Elements failed: {elem_failed}")

# Add masses at key floors
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PER_FLOOR = 1.60  # kg
ROOF_MASS = 2.22  # kg
ROOF_FLOOR = pos_df['floor'].max()

print("\nAdding masses...")
for floor in MASS_FLOORS:
    floor_nodes = pos_df[pos_df['floor'] == floor]['node_id'].astype(int).tolist()
    if floor_nodes:
        mass_each = MASS_PER_FLOOR / len(floor_nodes)
        for nid in floor_nodes:
            ops.mass(nid, mass_each, mass_each, mass_each, 0, 0, 0)

# Roof mass
roof_nodes = pos_df[pos_df['floor'] == ROOF_FLOOR]['node_id'].astype(int).tolist()
if roof_nodes:
    mass_each = ROOF_MASS / len(roof_nodes)
    for nid in roof_nodes:
        ops.mass(nid, mass_each, mass_each, mass_each, 0, 0, 0)

total_mass = len(MASS_FLOORS) * MASS_PER_FLOOR + ROOF_MASS
print(f"  Total lumped mass: {total_mass:.2f} kg")

# Eigenvalue analysis
print("\nPerforming eigenvalue analysis...")
n_modes = 10

try:
    eigenvalues = ops.eigen('-genBandArpack', n_modes)

    print(f"\n{'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12}")
    print("-" * 32)

    periods = []
    for i, ev in enumerate(eigenvalues):
        if ev > 0:
            omega = np.sqrt(ev)
            freq = omega / (2 * np.pi)
            period = 1 / freq
            periods.append(period)
            print(f"{i+1:<6} {period:<12.5f} {freq:<12.3f}")
        else:
            periods.append(0)
            print(f"{i+1:<6} {'N/A':<12} {'N/A':<12}")

    T1 = periods[0] if periods else 0

except Exception as e:
    print(f"Eigenvalue analysis failed: {e}")
    print("Trying alternative solver...")

    try:
        eigenvalues = ops.eigen(n_modes)

        periods = []
        print(f"\n{'Mode':<6} {'Period (s)':<12} {'Freq (Hz)':<12}")
        print("-" * 32)

        for i, ev in enumerate(eigenvalues):
            if ev > 0:
                omega = np.sqrt(ev)
                freq = omega / (2 * np.pi)
                period = 1 / freq
                periods.append(period)
                print(f"{i+1:<6} {period:<12.5f} {freq:<12.3f}")
            else:
                periods.append(0)

        T1 = periods[0] if periods else 0

    except Exception as e2:
        print(f"Alternative solver also failed: {e2}")
        # Use empirical formula
        H = pos_df['z'].max()  # Height in model meters
        H_maket = H / 100  # Height in maket meters
        T1 = 0.05 * (H_maket ** 0.75)
        print(f"Using empirical: T1 = {T1:.5f} s")
        periods = [T1]

# TBDY 2018 Spectrum Analysis
print("\n" + "=" * 70)
print("TBDY 2018 SPECTRUM ANALYSIS")
print("=" * 70)

TA = 0.061  # s
TB = 0.303  # s
SDS = 2.046  # g
SD1 = 0.619  # g

print(f"\nSpectrum Parameters:")
print(f"  SDS = {SDS} g")
print(f"  SD1 = {SD1} g")
print(f"  TA = {TA:.3f} s")
print(f"  TB = {TB:.3f} s")

if T1 < TA:
    region = "ASCENDING"
    Sae = SDS * (0.4 + 0.6 * T1 / TA)
elif T1 <= TB:
    region = "PLATEAU"
    Sae = SDS
else:
    region = "DESCENDING"
    Sae = SD1 / T1

print(f"\n  Fundamental Period: T₁ = {T1:.5f} s ({T1*1000:.2f} ms)")
print(f"  Spectrum Region: {region}")
print(f"  Spectral Acceleration: Sae = {Sae:.3f} g")

if region == "PLATEAU":
    print(f"\n  ⚠️  Building at MAXIMUM spectral acceleration!")
    print(f"     Target: T < {TA:.3f}s to reach ascending region")
    req_factor = (T1 / TA) ** 2
    print(f"     Required stiffness increase: ~{req_factor:.1f}x")
elif region == "ASCENDING":
    print(f"\n  ✓ Building in ASCENDING region - OPTIMAL!")
    print(f"     Sae is {Sae/SDS*100:.1f}% of maximum")
else:
    print(f"\n  Building in DESCENDING region")
    print(f"     Sae is reduced from peak")

# Save results
results = {
    'T1': T1,
    'region': region,
    'Sae': Sae,
    'TA': TA,
    'TB': TB,
    'SDS': SDS,
    'total_mass': total_mass,
    'n_elements': elem_created,
    'n_nodes': len(node_map)
}

import json
with open(RESULTS_DIR / 'modal_analysis_results.json', 'w') as f:
    json.dump(results, f, indent=2)

if periods:
    pd.DataFrame({
        'mode': range(1, len(periods)+1),
        'period_s': periods,
        'frequency_hz': [1/p if p > 0 else 0 for p in periods]
    }).to_csv(RESULTS_DIR / 'modal_periods.csv', index=False)

print(f"\nResults saved to: {RESULTS_DIR}")

ops.wipe()
print("\n" + "=" * 70)
print("MODAL ANALYSIS COMPLETE")
print("=" * 70)
