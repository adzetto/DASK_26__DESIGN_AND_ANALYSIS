"""
OpenSees Modal Analysis v2 - DASK 2026 Twin Towers
Consistent units: m, kN, tonne, s
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
print("OPENSEES MODAL ANALYSIS v2 - DASK 2026 Twin Towers")
print("=" * 70)
print("Units: m, kN, tonne, s")

# ============================================
# CONSISTENT UNITS: m, kN, tonne, s
# ============================================
# Force: kN
# Length: m
# Mass: tonne (1 tonne = 1000 kg)
# Time: s
# Stress: kN/m² = kPa (1 MPa = 1000 kPa)

# Material Properties - Balsa Wood
E_MPA = 3500.0  # MPa
E_KPA = E_MPA * 1000  # 3,500,000 kPa = kN/m²
NU = 0.3
G_KPA = E_KPA / (2 * (1 + NU))

# Section: 6mm x 6mm = 0.006m x 0.006m (for frame elements)
b_frame = 0.006  # m
A_frame = b_frame * b_frame  # m²
I_frame = (b_frame * b_frame**3) / 12  # m⁴
J_frame = 0.1406 * b_frame**4  # m⁴ (approx for square)

# Panel Section: 3mm thick shear wall panels (equivalent diagonal element)
# For a panel diagonal, use equivalent cross-section
# Panel thickness = 3mm, effective width = 12mm (Core Zone gap is 1.2cm)
t_panel = 0.003  # m (3mm)
w_panel = 0.012  # m (12mm effective width for 1.2cm panel)
A_panel = t_panel * w_panel  # m²
I_panel = (w_panel * t_panel**3) / 12  # m⁴ (bending about weak axis)
J_panel = 0.1406 * min(t_panel, w_panel)**4  # m⁴

print(f"\nMaterial: E = {E_KPA/1e6:.1f} GPa ({E_MPA} MPa)")
print(f"Frame Section: {b_frame*1000:.0f}mm x {b_frame*1000:.0f}mm")
print(f"  A = {A_frame*1e6:.2f} mm² = {A_frame:.2e} m²")
print(f"  I = {I_frame*1e12:.2f} mm⁴ = {I_frame:.2e} m⁴")
print(f"Panel Section: {t_panel*1000:.0f}mm x {w_panel*1000:.0f}mm (equivalent)")
print(f"  A = {A_panel*1e6:.2f} mm² = {A_panel:.2e} m²")
print(f"  I = {I_panel*1e12:.2f} mm⁴ = {I_panel:.2e} m⁴")

# Maket scale factor
# Model coordinates are in "model meters" (1m model = 1cm maket = 0.01m real)
# For 1:100 scale maket
MAKET_SCALE = 0.01  # 1 model unit = 0.01m in maket

# Load data
print("\nLoading model data...")
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')

print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# Height info
max_z_model = pos_df['z'].max()
max_z_maket = max_z_model * MAKET_SCALE  # In meters
print(f"  Model height: {max_z_model} (model units)")
print(f"  Maket height: {max_z_maket:.3f} m = {max_z_maket*100:.1f} cm")

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

# Create nodes (coordinates in maket meters)
node_map = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x = row['x'] * MAKET_SCALE  # m
    y = row['y'] * MAKET_SCALE  # m
    z = row['z'] * MAKET_SCALE  # m
    ops.node(nid, x, y, z)
    node_map[nid] = (x, y, z)

print(f"  Nodes created: {len(node_map)}")

# Fix base nodes
base_nodes = pos_df[pos_df['floor'] == 0]['node_id'].astype(int).tolist()
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)
print(f"  Base nodes fixed: {len(base_nodes)}")

# Geometric transformations
# For linear transformation, need vector perpendicular to element axis
# Use different vectors depending on element orientation
ops.geomTransf('Linear', 1, 0, 1, 0)  # For X-direction elements (local y up)
ops.geomTransf('Linear', 2, 1, 0, 0)  # For Y-direction elements (local y in X)
ops.geomTransf('Linear', 3, 0, 1, 0)  # For Z-direction elements (columns)

# Create elements
print("  Creating elements...")
elem_created = 0
elem_failed = 0
panel_elem_count = 0

# Define shear wall element types
shear_wall_types = ['shear_wall_xz', 'shear_wall_yz']

for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    etype = row['element_type']

    if ni not in node_map or nj not in node_map:
        elem_failed += 1
        continue

    xi, yi, zi = node_map[ni]
    xj, yj, zj = node_map[nj]

    # Check for zero-length elements
    length = np.sqrt((xj-xi)**2 + (yj-yi)**2 + (zj-zi)**2)
    if length < 1e-6:
        elem_failed += 1
        continue

    dx = abs(xj - xi)
    dy = abs(yj - yi)
    dz = abs(zj - zi)

    # Choose transformation based on element direction
    if dz > max(dx, dy) * 0.9:  # Primarily vertical
        transf = 3
    elif dx > dy:  # X-dominant
        transf = 1
    else:  # Y-dominant
        transf = 2

    # Use different section properties for shear wall panels
    if etype in shear_wall_types:
        A_use = A_panel
        I_use = I_panel
        J_use = J_panel
        panel_elem_count += 1
    else:
        A_use = A_frame
        I_use = I_frame
        J_use = J_frame

    try:
        ops.element('elasticBeamColumn', eid, ni, nj, A_use, E_KPA, G_KPA, J_use, I_use, I_use, transf)
        elem_created += 1
    except Exception as e:
        elem_failed += 1
        if elem_failed < 5:
            print(f"    Element {eid} failed: {e}")

print(f"  Elements created: {elem_created}")
if elem_failed > 0:
    print(f"  Elements failed: {elem_failed}")

# Add masses at key floors
# Mass in tonnes (1 kg = 0.001 tonne)
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PER_FLOOR_KG = 1.60
MASS_PER_FLOOR = MASS_PER_FLOOR_KG / 1000  # tonne
ROOF_MASS_KG = 2.22
ROOF_MASS = ROOF_MASS_KG / 1000  # tonne
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

total_mass_kg = len(MASS_FLOORS) * MASS_PER_FLOOR_KG + ROOF_MASS_KG
print(f"  Total lumped mass: {total_mass_kg:.2f} kg")

# Also add self-weight (distributed mass from elements)
# This is handled by element mass, not nodal mass
# For now, the lumped mass approach is sufficient for modal analysis

# Eigenvalue analysis
print("\nPerforming eigenvalue analysis...")
n_modes = 12

try:
    # Try different solvers
    solvers = [
        ('-genBandArpack', 'genBandArpack'),
        ('-fullGenLapack', 'fullGenLapack'),
        (None, 'default')
    ]

    eigenvalues = None
    for solver_arg, solver_name in solvers:
        try:
            if solver_arg:
                eigenvalues = ops.eigen(solver_arg, n_modes)
            else:
                eigenvalues = ops.eigen(n_modes)

            # Check if we got valid results
            valid = sum(1 for ev in eigenvalues if ev > 0)
            if valid >= 3:
                print(f"  Solver '{solver_name}' succeeded with {valid} valid modes")
                break
            else:
                print(f"  Solver '{solver_name}': only {valid} valid modes, trying next...")
                eigenvalues = None
        except Exception as e:
            print(f"  Solver '{solver_name}' failed: {e}")
            continue

    if eigenvalues is None:
        raise ValueError("All solvers failed")

    print(f"\n{'Mode':<6} {'Period (s)':<14} {'Freq (Hz)':<12} {'ω (rad/s)':<12}")
    print("-" * 46)

    periods = []
    for i, ev in enumerate(eigenvalues):
        if ev > 1e-10:  # Valid positive eigenvalue
            omega = np.sqrt(ev)
            freq = omega / (2 * np.pi)
            period = 1 / freq
            periods.append(period)
            print(f"{i+1:<6} {period:<14.6f} {freq:<12.4f} {omega:<12.4f}")
        else:
            periods.append(None)
            print(f"{i+1:<6} {'(rigid)':<14} {'-':<12} {'-':<12}")

    # Get first valid period
    valid_periods = [p for p in periods if p is not None]
    T1 = valid_periods[0] if valid_periods else None

except Exception as e:
    print(f"\nEigenvalue analysis failed: {e}")
    print("\nUsing empirical formula...")

    # Empirical period for braced frame
    # T = Ct * H^x where H in meters
    H = max_z_maket  # Height in meters
    Ct = 0.05  # For braced frames
    T1 = Ct * (H ** 0.75)
    periods = [T1]
    print(f"  Empirical T₁ = {T1:.6f} s")

# TBDY 2018 Spectrum Analysis
print("\n" + "=" * 70)
print("TBDY 2018/2019 SPECTRUM ANALYSIS")
print("=" * 70)

TA = 0.061  # s (Ascending to Plateau)
TB = 0.303  # s (Plateau to Descending)
SDS = 2.046  # g
SD1 = 0.619  # g

print(f"\nTBDY Design Spectrum Parameters:")
print(f"  SDS = {SDS} g")
print(f"  SD1 = {SD1} g")
print(f"  TA = {TA:.3f} s (Ascending → Plateau)")
print(f"  TB = {TB:.3f} s (Plateau → Descending)")

if T1 is None:
    print("\nERROR: Could not determine fundamental period")
    ops.wipe()
    sys.exit(1)

if T1 < TA:
    region = "ASCENDING"
    Sae = SDS * (0.4 + 0.6 * T1 / TA)
elif T1 <= TB:
    region = "PLATEAU"
    Sae = SDS
else:
    region = "DESCENDING"
    Sae = SD1 / T1

print(f"\n" + "-" * 50)
print(f"  FUNDAMENTAL PERIOD: T₁ = {T1:.6f} s")
print(f"                         = {T1*1000:.3f} ms")
print(f"  SPECTRUM REGION: {region}")
print(f"  SPECTRAL ACCELERATION: Sae(T₁) = {Sae:.3f} g")
print("-" * 50)

if region == "PLATEAU":
    print(f"\n  ⚠️  WARNING: Building at MAXIMUM spectral acceleration!")
    print(f"     Current: T₁ = {T1*1000:.3f} ms")
    print(f"     Target:  T < {TA*1000:.1f} ms to reach ascending region")
    req_factor = (T1 / TA) ** 2
    print(f"     Required stiffness increase: ~{req_factor:.1f}x")
    print(f"\n  Options to increase stiffness:")
    print(f"     1. Add shear wall panels (3mm balsa)")
    print(f"     2. Increase section size (but weight penalty)")
    print(f"     3. Add more bracing")

elif region == "ASCENDING":
    print(f"\n  ✓ EXCELLENT! Building in ASCENDING region!")
    print(f"     Spectral acceleration is {Sae/SDS*100:.1f}% of maximum")
    print(f"     Lower period = lower seismic forces")
    margin = (TA - T1) / TA * 100
    print(f"     Period margin to plateau: {margin:.1f}%")

else:
    print(f"\n  ℹ Building in DESCENDING region")
    print(f"     Sae is {Sae/SDS*100:.1f}% of peak (SDS)")

# Calculate expected base shear
# V = Sae(T) * W / R
# For competition: R = 1 (elastic)
W = total_mass_kg * 9.81 / 1000  # Weight in kN
V_base = Sae * W  # Base shear in kN (for R=1)
print(f"\n  Expected Base Shear (R=1): V = {V_base:.3f} kN = {V_base*1000:.1f} N")

# Save results
results = {
    'T1_s': T1,
    'T1_ms': T1 * 1000,
    'region': region,
    'Sae_g': Sae,
    'TA_s': TA,
    'TB_s': TB,
    'SDS_g': SDS,
    'SD1_g': SD1,
    'total_mass_kg': total_mass_kg,
    'base_shear_kN': V_base,
    'n_elements': elem_created,
    'n_nodes': len(node_map),
    'maket_height_m': max_z_maket
}

import json
with open(RESULTS_DIR / 'modal_analysis_v2.json', 'w') as f:
    json.dump(results, f, indent=2)

if periods:
    valid_modes = [(i+1, p) for i, p in enumerate(periods) if p is not None]
    if valid_modes:
        pd.DataFrame({
            'mode': [m[0] for m in valid_modes],
            'period_s': [m[1] for m in valid_modes],
            'frequency_hz': [1/m[1] for m in valid_modes]
        }).to_csv(RESULTS_DIR / 'modal_periods_v2.csv', index=False)

print(f"\nResults saved to: {RESULTS_DIR}")

ops.wipe()
print("\n" + "=" * 70)
print("MODAL ANALYSIS COMPLETE")
print("=" * 70)
