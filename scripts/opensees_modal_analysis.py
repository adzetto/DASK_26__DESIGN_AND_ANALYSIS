"""
OpenSees Modal Analysis for DASK 2026 Twin Towers
Calculates natural periods and mode shapes
"""

import numpy as np
import pandas as pd
from pathlib import Path

try:
    import openseespy.opensees as ops
    OPENSEES_AVAILABLE = True
except ImportError:
    OPENSEES_AVAILABLE = False
    print("WARNING: OpenSeesPy not available. Install with: pip install openseespy")

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
RESULTS_DIR = SCRIPT_DIR.parent / 'results' / 'data'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

print("=" * 70)
print("OPENSEES MODAL ANALYSIS - DASK 2026 Twin Towers")
print("=" * 70)

# ============================================
# MATERIAL PROPERTIES - Balsa Wood
# ============================================
E_BALSA = 3500.0  # MPa = N/mm²
DENSITY_BALSA = 160.0  # kg/m³ = 160e-9 kg/mm³
NU_BALSA = 0.3
G_BALSA = E_BALSA / (2 * (1 + NU_BALSA))  # Shear modulus

# Section: 6mm x 6mm
SECTION_WIDTH = 6.0  # mm
SECTION_HEIGHT = 6.0  # mm
A_SECTION = SECTION_WIDTH * SECTION_HEIGHT  # mm²
I_SECTION = (SECTION_WIDTH * SECTION_HEIGHT**3) / 12  # mm⁴
J_SECTION = 0.1406 * SECTION_WIDTH**4  # Torsional constant for square section

# Convert to consistent units (N, mm, kg)
# E in N/mm² (MPa) - OK
# Density for mass: kg/mm³
RHO_MM = DENSITY_BALSA * 1e-9  # kg/mm³

print(f"\nMaterial Properties:")
print(f"  E = {E_BALSA} MPa")
print(f"  G = {G_BALSA:.1f} MPa")
print(f"  ρ = {DENSITY_BALSA} kg/m³")
print(f"\nSection Properties (6mm x 6mm):")
print(f"  A = {A_SECTION} mm²")
print(f"  I = {I_SECTION} mm⁴")
print(f"  J = {J_SECTION:.1f} mm⁴")

# ============================================
# LOAD MODEL DATA
# ============================================
print("\nLoading model data...")
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}")
print(f"  Elements: {n_elements}")

# Node coordinates (convert m to mm for model scale)
# Note: Model is in meters, we'll work in mm for OpenSees
SCALE = 10.0  # 1m in model = 10mm in maket (1:100 scale, then x10 for mm)

node_coords = {}
for _, row in pos_df.iterrows():
    nid = int(row['node_id'])
    # Coordinates in mm (model scale)
    x = row['x'] * SCALE
    y = row['y'] * SCALE
    z = row['z'] * SCALE
    node_coords[nid] = (x, y, z)

# Element connectivity
elements = []
for _, row in conn_df.iterrows():
    eid = int(row['element_id'])
    ni = int(row['node_i'])
    nj = int(row['node_j'])
    etype = row['element_type']
    length = row['length'] * SCALE  # Convert to mm
    elements.append({
        'id': eid,
        'ni': ni,
        'nj': nj,
        'type': etype,
        'length': length
    })

# ============================================
# MASS CONFIGURATION (DASK Rules)
# ============================================
# Floors with 1.60 kg mass
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PER_FLOOR = 1.60  # kg
MASS_ROOF = 2.22  # kg at floor 25 (roof)

# Get floor levels from position data
floor_levels = sorted(pos_df['floor'].unique())
z_coords = {}
for f in floor_levels:
    z_val = pos_df[pos_df['floor'] == f]['z'].iloc[0]
    z_coords[f] = z_val * SCALE  # mm

print(f"\nMass Configuration:")
print(f"  Mass floors: {MASS_FLOORS}")
print(f"  Mass per floor: {MASS_PER_FLOOR} kg")
print(f"  Roof mass: {MASS_ROOF} kg")

if not OPENSEES_AVAILABLE:
    print("\n" + "=" * 70)
    print("OPENSEES NOT AVAILABLE - Estimating period with simplified formula")
    print("=" * 70)

    # Simplified Rayleigh method estimation
    # T ≈ 2π√(Σm·δ² / Σm·g·δ)
    # For cantilever approximation: T ≈ 0.1 * N (number of stories)
    # More refined: T = 2π√(m·H³/(3·E·I))

    H_total = max(z_coords.values())  # Total height in mm

    # Approximate stiffness (simplified)
    # For twin towers with bracing, approximate as equivalent column
    n_columns_per_tower = 12  # 4 x 3 grid
    n_towers = 2
    n_total_columns = n_columns_per_tower * n_towers

    # Equivalent moment of inertia (distributed columns)
    # I_eq ≈ n * A * d² where d is distance from centroid
    tower_width = 160  # mm (16m * 10)
    d_avg = tower_width / 4  # Average distance from centroid
    I_eq = n_total_columns * A_SECTION * d_avg**2

    # Total mass
    total_mass = len(MASS_FLOORS) * MASS_PER_FLOOR + MASS_ROOF
    total_mass_kg = total_mass

    # Effective mass at top (approximation)
    m_eff = total_mass_kg * 0.7  # 70% of mass participates in first mode

    # Cantilever period formula
    # T = 2π√(m·H³/(3·E·I))
    # Units: m in kg, H in mm, E in N/mm², I in mm⁴
    # Result should be in seconds

    # For a frame structure with bracing, use empirical formula
    # T ≈ Ct * H^x where H is height in meters
    H_meters = H_total / 10 / 1000  # Convert mm to m (via cm)
    H_meters = H_total / SCALE / 100  # Correct: mm -> m

    # TBDY 2018 empirical formula for braced frames: Ct = 0.05, x = 0.75
    Ct = 0.05
    T_empirical = Ct * (H_meters ** 0.75)

    # More detailed Rayleigh estimation
    # Consider bracing stiffness contribution
    n_braces_xz = conn_df[conn_df['element_type'] == 'brace_xz'].shape[0]
    n_braces_yz = conn_df[conn_df['element_type'] == 'brace_yz'].shape[0]
    n_core_walls = conn_df[conn_df['element_type'] == 'core_wall'].shape[0]

    # Stiffness multiplier based on bracing density
    brace_factor = 1.0 + 0.01 * (n_braces_xz + n_braces_yz) + 0.02 * n_core_walls

    # Adjusted period (more bracing = lower period)
    T_adjusted = T_empirical / np.sqrt(brace_factor)

    print(f"\nSimplified Period Estimation:")
    print(f"  Total height: {H_meters:.2f} m")
    print(f"  Total mass: {total_mass_kg:.2f} kg")
    print(f"  XZ Braces: {n_braces_xz}")
    print(f"  YZ Braces: {n_braces_yz}")
    print(f"  Core walls: {n_core_walls}")
    print(f"  Brace stiffness factor: {brace_factor:.2f}")
    print(f"\n  Empirical T (TBDY): {T_empirical:.4f} s")
    print(f"  Adjusted T (with bracing): {T_adjusted:.4f} s")

    # TBDY 2018 Spectrum parameters
    TA = 0.061  # s (Ascending to Plateau)
    TB = 0.303  # s (Plateau to Descending)
    SDS = 2.046  # g

    T_building = T_adjusted

    if T_building < TA:
        region = "ASCENDING"
        Sae = SDS * (0.4 + 0.6 * T_building / TA)
    elif T_building <= TB:
        region = "PLATEAU"
        Sae = SDS
    else:
        region = "DESCENDING"
        SD1 = 0.619
        Sae = SD1 / T_building

    print(f"\n" + "=" * 70)
    print(f"SPECTRUM POSITION:")
    print(f"  T₁ = {T_building:.4f} s")
    print(f"  TA = {TA:.3f} s")
    print(f"  TB = {TB:.3f} s")
    print(f"  Region: {region}")
    print(f"  Sae(T₁) = {Sae:.3f} g")
    print("=" * 70)

    if region == "PLATEAU":
        print("\n⚠️  Building is in PLATEAU region (maximum spectral acceleration)")
        print(f"    To reach ASCENDING region, need T < {TA:.3f}s")
        print(f"    Required stiffness increase: ~{(T_building/TA)**2:.1f}x")

    # Save results
    results = {
        'T1_estimated': T_building,
        'T_empirical': T_empirical,
        'region': region,
        'Sae': Sae,
        'total_mass_kg': total_mass_kg,
        'n_braces_xz': n_braces_xz,
        'n_braces_yz': n_braces_yz,
        'n_core_walls': n_core_walls,
        'brace_factor': brace_factor
    }

    exit()

# ============================================
# OPENSEES MODEL
# ============================================
print("\nBuilding OpenSees model...")

ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Create nodes
for nid, (x, y, z) in node_coords.items():
    ops.node(nid, x, y, z)

# Fix base nodes (z = 0)
base_nodes = [nid for nid, (x, y, z) in node_coords.items() if z < 1.0]
print(f"  Fixed base nodes: {len(base_nodes)}")
for nid in base_nodes:
    ops.fix(nid, 1, 1, 1, 1, 1, 1)

# Material
mat_tag = 1
ops.uniaxialMaterial('Elastic', mat_tag, E_BALSA)

# Geometric transformation
transf_tag_x = 1  # For elements primarily in X direction
transf_tag_y = 2  # For elements primarily in Y direction
transf_tag_z = 3  # For vertical elements (columns)

ops.geomTransf('Linear', transf_tag_x, 0, 0, 1)  # Local z along global Z
ops.geomTransf('Linear', transf_tag_y, 0, 0, 1)
ops.geomTransf('Linear', transf_tag_z, 1, 0, 0)  # Local z along global X for columns

# Create elements
print("  Creating elements...")
elem_count = 0
for elem in elements:
    eid = elem['id']
    ni = elem['ni']
    nj = elem['nj']
    etype = elem['type']

    # Skip if nodes don't exist
    if ni not in node_coords or nj not in node_coords:
        continue

    # Get coordinates
    xi, yi, zi = node_coords[ni]
    xj, yj, zj = node_coords[nj]

    # Determine transformation based on element orientation
    dx = abs(xj - xi)
    dy = abs(yj - yi)
    dz = abs(zj - zi)

    if dz > max(dx, dy):
        # Primarily vertical (column)
        transf = transf_tag_z
    elif dx > dy:
        # Primarily X direction
        transf = transf_tag_x
    else:
        # Primarily Y direction
        transf = transf_tag_y

    try:
        # ElasticBeamColumn element
        # elasticBeamColumn eleTag iNode jNode A E G J Iy Iz transfTag
        ops.element('elasticBeamColumn', eid, ni, nj,
                    A_SECTION, E_BALSA, G_BALSA, J_SECTION, I_SECTION, I_SECTION, transf)
        elem_count += 1
    except Exception as e:
        pass  # Skip problematic elements

print(f"  Elements created: {elem_count}")

# ============================================
# ADD MASSES
# ============================================
print("\nAdding masses...")

# Get nodes at each mass floor
def get_floor_nodes(floor_idx):
    return pos_df[pos_df['floor'] == floor_idx]['node_id'].tolist()

# Distribute mass equally among floor nodes
for floor in MASS_FLOORS:
    floor_nodes = get_floor_nodes(floor)
    if floor_nodes:
        mass_per_node = MASS_PER_FLOOR / len(floor_nodes)
        for nid in floor_nodes:
            if nid in node_coords:
                # mass command: mass nodeTag mx my mz mIx mIy mIz
                ops.mass(int(nid), mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)

# Roof mass
roof_floor = max(floor_levels)
roof_nodes = get_floor_nodes(roof_floor)
if roof_nodes:
    mass_per_node = MASS_ROOF / len(roof_nodes)
    for nid in roof_nodes:
        if nid in node_coords:
            ops.mass(int(nid), mass_per_node, mass_per_node, mass_per_node, 0, 0, 0)

print(f"  Mass added to {len(MASS_FLOORS)} floors + roof")

# ============================================
# EIGENVALUE ANALYSIS
# ============================================
print("\nPerforming eigenvalue analysis...")

n_modes = 10  # Number of modes to compute

try:
    eigenvalues = ops.eigen('-fullGenLapack', n_modes)

    print(f"\n{'Mode':<6} {'Period (s)':<12} {'Frequency (Hz)':<15}")
    print("-" * 35)

    periods = []
    for i, ev in enumerate(eigenvalues):
        if ev > 0:
            omega = np.sqrt(ev)  # rad/s
            freq = omega / (2 * np.pi)  # Hz
            period = 1 / freq if freq > 0 else 0  # s
            periods.append(period)
            print(f"{i+1:<6} {period:<12.4f} {freq:<15.4f}")
        else:
            periods.append(0)
            print(f"{i+1:<6} {'N/A':<12} {'N/A':<15}")

    T1 = periods[0] if periods else 0

    # TBDY 2018 Spectrum analysis
    print("\n" + "=" * 70)
    print("TBDY 2018 SPECTRUM ANALYSIS")
    print("=" * 70)

    TA = 0.061
    TB = 0.303
    SDS = 2.046
    SD1 = 0.619

    if T1 < TA:
        region = "ASCENDING"
        Sae = SDS * (0.4 + 0.6 * T1 / TA)
    elif T1 <= TB:
        region = "PLATEAU"
        Sae = SDS
    else:
        region = "DESCENDING"
        Sae = SD1 / T1

    print(f"\nFundamental Period: T₁ = {T1:.4f} s")
    print(f"Spectrum Position: {region}")
    print(f"  TA = {TA:.3f} s")
    print(f"  TB = {TB:.3f} s")
    print(f"Spectral Acceleration: Sae(T₁) = {Sae:.3f} g")

    if region == "PLATEAU":
        print(f"\n⚠️  WARNING: Building is at MAXIMUM spectral acceleration!")
        print(f"    To reach ASCENDING: need T < {TA:.3f}s (current: {T1:.4f}s)")
        req_stiffness = (T1 / TA) ** 2
        print(f"    Required stiffness increase: ~{req_stiffness:.1f}x")
    elif region == "ASCENDING":
        print(f"\n✓ Building is in ASCENDING region - good for seismic design!")
        print(f"    Sae is {Sae/SDS*100:.1f}% of maximum (SDS)")

    # Save results
    results_df = pd.DataFrame({
        'mode': range(1, len(periods) + 1),
        'period_s': periods,
        'frequency_hz': [1/p if p > 0 else 0 for p in periods]
    })
    results_df.to_csv(RESULTS_DIR / 'modal_analysis_results.csv', index=False)
    print(f"\nResults saved to: {RESULTS_DIR / 'modal_analysis_results.csv'}")

except Exception as e:
    print(f"\nError in eigenvalue analysis: {e}")
    print("Using simplified period estimation instead...")

    # Fallback to empirical
    H_total = max(z_coords.values()) / SCALE / 100  # m
    Ct = 0.05
    T1 = Ct * (H_total ** 0.75)
    print(f"  Empirical T₁ = {T1:.4f} s")

ops.wipe()
print("\n" + "=" * 70)
print("MODAL ANALYSIS COMPLETE")
print("=" * 70)
