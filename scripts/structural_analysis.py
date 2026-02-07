#!/usr/bin/env python3
"""
STRUCTURAL ANALYSIS - Period, Stiffness & Seismic Risk
=======================================================
TBDY2018 compliance check for twin towers model.

Analysis includes:
1. Fundamental period estimation (Rayleigh method)
2. TBDY2018 design spectrum comparison
3. Plateau region check
4. Stiffness analysis
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

print("=" * 70)
print("STRUCTURAL ANALYSIS - TBDY2018 Compliance")
print("=" * 70)

# ============================================
# LOAD MODEL DATA
# ============================================
DATA_DIR = Path(__file__).parent.parent / 'data'

conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
npz = np.load(DATA_DIR / 'twin_building_data.npz')

coords = npz['coords']
z_coords = npz['z_coords']

n_nodes = len(pos_df)
n_elements = len(conn_df)

print(f"Model: {n_nodes} nodes, {n_elements} elements")
print(f"Height: {z_coords[-1]:.1f}m ({len(z_coords)} floors)")

# ============================================
# MATERIAL & SECTION PROPERTIES (Balsa 6x6mm)
# ============================================
# Scale 1:100, so model dimensions in cm = real dimensions in m
E_BALSA = 3500e6  # Pa (3.5 GPa for balsa)
RHO_BALSA = 160   # kg/m³

# Section: 6x6mm = 0.006 x 0.006 m (model scale)
# At 1:100 scale, this represents 0.6 x 0.6 m in real scale
b = 0.006  # m (model)
h = 0.006  # m (model)
A = b * h  # m² = 36e-6 m²
I = b * h**3 / 12  # m⁴ = 1.08e-10 m⁴

print(f"\nSection Properties (6x6mm balsa):")
print(f"  Area: {A*1e6:.1f} mm²")
print(f"  Moment of Inertia: {I*1e12:.4f} mm⁴")
print(f"  E: {E_BALSA/1e9:.1f} GPa")

# ============================================
# BUILDING PARAMETERS
# ============================================
# Total building dimensions (model scale = real scale at 1:100)
max_x = coords[:, 0].max()
max_y = coords[:, 1].max()
max_z = coords[:, 2].max()

print(f"\nBuilding Dimensions:")
print(f"  X: {max_x:.1f}m")
print(f"  Y: {max_y:.1f}m")
print(f"  Height: {max_z:.1f}m")

# ============================================
# MASS CALCULATION
# ============================================
# Calculate total mass from element lengths
total_length = conn_df['length'].sum()  # meters (model scale)
total_mass = total_length * A * RHO_BALSA  # kg

# For seismic analysis, we need to distribute mass to floors
# Simplified: assume uniform mass distribution
n_floors = len(z_coords)
mass_per_floor = total_mass / n_floors

print(f"\nMass Distribution:")
print(f"  Total element length: {total_length:.1f}m")
print(f"  Total mass: {total_mass:.3f} kg")
print(f"  Mass per floor: {mass_per_floor*1000:.2f} g")

# ============================================
# STIFFNESS ANALYSIS
# ============================================
# Simplified lateral stiffness estimation
# Using cantilever beam analogy for each tower

# Count columns
columns = conn_df[conn_df['element_type'] == 'column']
n_columns = len(columns)

# Average column length (floor height)
avg_floor_height = (z_coords[-1] - z_coords[0]) / (n_floors - 1)

# Lateral stiffness of single column (fixed-fixed): k = 12EI/L³
k_column = 12 * E_BALSA * I / (avg_floor_height ** 3)

# Total lateral stiffness (parallel columns)
# Columns per floor per tower
columns_per_floor = n_columns / (n_floors - 1) / 2  # divide by floors and 2 towers

# Simplified frame stiffness (considering bracing contribution)
# Bracing increases stiffness significantly
bracing_elements = conn_df[conn_df['element_type'].str.contains('brace|shear|wall', case=False)]
n_bracing = len(bracing_elements)

# Bracing stiffness contribution (simplified)
# Each brace adds axial stiffness: k = EA*cos²θ/L
avg_brace_length = bracing_elements['length'].mean() if len(bracing_elements) > 0 else avg_floor_height * 1.4
k_brace = E_BALSA * A / avg_brace_length * 0.5  # cos²(45°) ≈ 0.5

# Total lateral stiffness per floor
k_lateral_floor = columns_per_floor * k_column + (n_bracing / (n_floors - 1)) * k_brace

print(f"\nStiffness Analysis:")
print(f"  Columns: {n_columns} total, {columns_per_floor:.0f} per floor")
print(f"  Bracing elements: {n_bracing}")
print(f"  Column stiffness: {k_column:.2e} N/m")
print(f"  Brace stiffness: {k_brace:.2e} N/m")
print(f"  Total lateral stiffness/floor: {k_lateral_floor:.2e} N/m")

# ============================================
# PERIOD ESTIMATION
# ============================================
# Method 1: Empirical formula (TBDY2018 Eq. 4.7)
# T = Ct * H^0.75
# For steel frames: Ct = 0.0724
# For concrete frames: Ct = 0.0488
# For braced frames: Ct = 0.0488
Ct = 0.05  # Conservative for balsa frame
H = max_z  # Building height in meters

T_empirical = Ct * (H ** 0.75)

# Method 2: Rayleigh method (simplified)
# T = 2π * sqrt(Σmi*δi² / Σfi*δi)
# For uniform mass and linear deflection: T ≈ 2π * sqrt(M*H³ / (3*EI_eff))

# Effective moment of inertia (considering all columns and bracing)
n_cols_x = len([x for x in np.unique(coords[:, 0])])  # grid lines in X
n_cols_y = len(np.unique(coords[:, 1]))  # grid lines in Y

# Effective building stiffness (simplified shear building model)
# K_eff = sum of story stiffnesses
K_eff = k_lateral_floor * (n_floors - 1) / n_floors  # average

# Fundamental period: T = 2π * sqrt(M/K)
# For MDOF, use participation factor ≈ 0.7
M_eff = total_mass * 0.7  # Effective modal mass
T_rayleigh = 2 * np.pi * np.sqrt(M_eff / K_eff)

# Method 3: Dunkerley's method (lower bound)
# For tall buildings: T ≈ 0.1 * N (N = number of stories)
T_dunkerley = 0.1 * n_floors

# Method 4: Based on building type (TBDY2018 Table 4.1)
# For dual systems (frame + shear wall): T = 0.07 * H^0.75
T_dual = 0.07 * (H ** 0.75)

print(f"\nPeriod Estimation:")
print(f"  Empirical (Ct*H^0.75): T = {T_empirical:.3f} s")
print(f"  Rayleigh method: T = {T_rayleigh:.3f} s")
print(f"  Dunkerley (0.1*N): T = {T_dunkerley:.3f} s")
print(f"  Dual system: T = {T_dual:.3f} s")

# Use average of methods for design
T_design = (T_empirical + T_dual) / 2
print(f"\n  >>> DESIGN PERIOD: T = {T_design:.3f} s <<<")

# ============================================
# TBDY2018 DESIGN SPECTRUM
# ============================================
# Assume seismic parameters for high seismic zone (e.g., Istanbul)
# Soil class: ZC (medium soil)

print("\n" + "=" * 70)
print("TBDY2018 DESIGN SPECTRUM ANALYSIS")
print("=" * 70)

# Short period spectral acceleration coefficient
SS = 1.20  # g (typical for Zone 1)
S1 = 0.35  # g (typical for Zone 1)

# Soil amplification factors for ZC
FS = 1.20  # Short period
F1 = 1.50  # 1-second period

# Design spectral accelerations
SDS = SS * FS  # Short period design spectral acceleration
SD1 = S1 * F1  # 1-second design spectral acceleration

# Corner periods
TA = 0.2 * SD1 / SDS
TB = SD1 / SDS
TL = 6.0  # Long period transition

print(f"\nSeismic Parameters (Zone 1, Soil ZC):")
print(f"  SS = {SS:.2f}g, S1 = {S1:.2f}g")
print(f"  FS = {FS:.2f}, F1 = {F1:.2f}")
print(f"  SDS = {SDS:.3f}g")
print(f"  SD1 = {SD1:.3f}g")
print(f"\nSpectrum Corner Periods:")
print(f"  TA = {TA:.3f} s")
print(f"  TB = {TB:.3f} s")
print(f"  TL = {TL:.1f} s")

# ============================================
# PLATEAU REGION CHECK
# ============================================
print(f"\n" + "-" * 50)
print("PLATEAU REGION CHECK")
print("-" * 50)

if T_design < TA:
    region = "ASCENDING (T < TA)"
    Sae = SDS * (0.4 + 0.6 * T_design / TA)
    in_plateau = False
elif T_design <= TB:
    region = "PLATEAU (TA ≤ T ≤ TB)"
    Sae = SDS
    in_plateau = True
elif T_design <= TL:
    region = "DESCENDING (TB < T ≤ TL)"
    Sae = SD1 / T_design
    in_plateau = False
else:
    region = "LONG PERIOD (T > TL)"
    Sae = SD1 * TL / (T_design ** 2)
    in_plateau = False

print(f"\n  Design Period: T = {T_design:.3f} s")
print(f"  Plateau Range: {TA:.3f} s ≤ T ≤ {TB:.3f} s")
print(f"\n  >>> REGION: {region} <<<")
print(f"  Spectral Acceleration: Sae = {Sae:.3f}g")

if in_plateau:
    print(f"\n  ⚠️  WARNING: Structure is in PLATEAU region!")
    print(f"      This means MAXIMUM spectral acceleration.")
    print(f"      Consider INCREASING stiffness to reduce period below TA={TA:.3f}s")
    print(f"      Or DECREASING stiffness to increase period above TB={TB:.3f}s")
else:
    print(f"\n  ✓ Structure is OUTSIDE plateau region.")

# ============================================
# SEISMIC FORCE CALCULATION
# ============================================
print(f"\n" + "-" * 50)
print("SEISMIC FORCE ANALYSIS")
print("-" * 50)

# Base shear coefficient
# V = (SDS * I * W) / R for short period structures
# V = (SD1 * I * W) / (T * R) for longer period structures

I_factor = 1.5  # Importance factor (Category III)
R = 4.0  # Response modification factor (special moment frame)

if T_design <= TB:
    Cs = SDS / R
else:
    Cs = SD1 / (T_design * R)

# Minimum Cs
Cs_min = 0.044 * SDS * I_factor
Cs = max(Cs, Cs_min)

# Weight (use actual model weight)
W = total_mass * 9.81  # N

# Base shear
V_base = Cs * I_factor * W

print(f"\n  Importance Factor: I = {I_factor}")
print(f"  Response Modification: R = {R}")
print(f"  Seismic Coefficient: Cs = {Cs:.4f}")
print(f"  Building Weight: W = {W:.2f} N ({total_mass*1000:.1f} g)")
print(f"\n  >>> BASE SHEAR: V = {V_base:.2f} N <<<")

# ============================================
# STIFFNESS RECOMMENDATIONS
# ============================================
print(f"\n" + "=" * 70)
print("RECOMMENDATIONS")
print("=" * 70)

# Target period to exit plateau
if in_plateau:
    # Option 1: Increase stiffness (reduce period)
    T_target_stiff = TA * 0.8  # 20% below TA
    K_required_stiff = M_eff * (2 * np.pi / T_target_stiff) ** 2
    stiffness_increase = K_required_stiff / K_eff

    # Option 2: Decrease stiffness (increase period)
    T_target_flex = TB * 1.3  # 30% above TB
    K_required_flex = M_eff * (2 * np.pi / T_target_flex) ** 2
    stiffness_decrease = K_required_flex / K_eff

    print(f"\nTo EXIT plateau region:")
    print(f"\n  Option 1: INCREASE STIFFNESS (Stiffer structure)")
    print(f"    Target period: T < {T_target_stiff:.3f} s")
    print(f"    Required stiffness increase: {stiffness_increase:.1f}x")
    print(f"    Methods: Add more bracing, thicker sections, shear walls")

    print(f"\n  Option 2: DECREASE STIFFNESS (More flexible)")
    print(f"    Target period: T > {T_target_flex:.3f} s")
    print(f"    Required stiffness decrease: {stiffness_decrease:.2f}x")
    print(f"    Methods: Remove bracing, reduce sections (NOT recommended)")

    print(f"\n  >>> RECOMMENDATION: Option 1 - Add stiffness <<<")
else:
    if T_design < TA:
        print(f"\n  ✓ Structure is STIFFER than plateau region")
        print(f"    Spectral acceleration increases with period in this range")
        print(f"    Current design is efficient")
    else:
        print(f"\n  ✓ Structure is MORE FLEXIBLE than plateau region")
        print(f"    Spectral acceleration decreases with period")
        print(f"    Seismic forces are reduced")

# ============================================
# PLOT SPECTRUM
# ============================================
print(f"\nGenerating spectrum plot...")

RESULTS_DIR = Path(__file__).parent.parent / 'results' / 'visualizations'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Generate spectrum curve
T_range = np.linspace(0.01, 4.0, 500)
Sae_curve = []

for T in T_range:
    if T < TA:
        Sae_curve.append(SDS * (0.4 + 0.6 * T / TA))
    elif T <= TB:
        Sae_curve.append(SDS)
    elif T <= TL:
        Sae_curve.append(SD1 / T)
    else:
        Sae_curve.append(SD1 * TL / (T ** 2))

plt.figure(figsize=(12, 8))
plt.plot(T_range, Sae_curve, 'b-', linewidth=2, label='TBDY2018 Design Spectrum')

# Mark regions
plt.axvline(x=TA, color='orange', linestyle='--', alpha=0.7, label=f'TA = {TA:.3f}s')
plt.axvline(x=TB, color='red', linestyle='--', alpha=0.7, label=f'TB = {TB:.3f}s')
plt.axvspan(TA, TB, alpha=0.2, color='red', label='Plateau Region')

# Mark design period
plt.axvline(x=T_design, color='green', linestyle='-', linewidth=2, label=f'T_design = {T_design:.3f}s')
plt.plot(T_design, Sae, 'go', markersize=15, markeredgecolor='black', markeredgewidth=2)

# Mark all estimated periods
periods = {
    'Empirical': T_empirical,
    'Rayleigh': T_rayleigh,
    'Dual': T_dual
}
for name, T_val in periods.items():
    if 0 < T_val < 4:
        plt.axvline(x=T_val, color='gray', linestyle=':', alpha=0.5)
        plt.text(T_val, SDS * 1.05, name, rotation=90, fontsize=8, alpha=0.7)

plt.xlabel('Period T (s)', fontsize=12)
plt.ylabel('Spectral Acceleration Sae (g)', fontsize=12)
plt.title('TBDY2018 Design Spectrum - Twin Towers Analysis\n' +
          f'Zone 1, Soil ZC | T = {T_design:.3f}s | Sae = {Sae:.3f}g', fontsize=14)
plt.legend(loc='upper right', fontsize=10)
plt.grid(True, alpha=0.3)
plt.xlim(0, 4)
plt.ylim(0, SDS * 1.3)

# Add text box with results
textstr = f'Design Period: T = {T_design:.3f} s\n'
textstr += f'Region: {region}\n'
textstr += f'Sae = {Sae:.3f}g\n'
textstr += f'Base Shear: V = {V_base:.2f} N'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
plt.text(0.98, 0.5, textstr, transform=plt.gca().transAxes, fontsize=11,
         verticalalignment='center', horizontalalignment='right', bbox=props)

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'period_vs_sae_spectrum.png', dpi=150)
print(f"Spectrum plot saved: {RESULTS_DIR / 'period_vs_sae_spectrum.png'}")

# ============================================
# SAVE RESULTS
# ============================================
results = {
    'Parameter': [
        'Building Height (m)', 'Number of Floors', 'Total Mass (kg)',
        'T_empirical (s)', 'T_rayleigh (s)', 'T_dual (s)', 'T_design (s)',
        'SS (g)', 'S1 (g)', 'SDS (g)', 'SD1 (g)',
        'TA (s)', 'TB (s)',
        'Spectral Region', 'Sae (g)', 'In Plateau',
        'Base Shear (N)', 'Seismic Coefficient Cs'
    ],
    'Value': [
        f'{max_z:.1f}', f'{n_floors}', f'{total_mass:.3f}',
        f'{T_empirical:.3f}', f'{T_rayleigh:.3f}', f'{T_dual:.3f}', f'{T_design:.3f}',
        f'{SS:.2f}', f'{S1:.2f}', f'{SDS:.3f}', f'{SD1:.3f}',
        f'{TA:.3f}', f'{TB:.3f}',
        region, f'{Sae:.3f}', 'YES' if in_plateau else 'NO',
        f'{V_base:.2f}', f'{Cs:.4f}'
    ]
}

results_df = pd.DataFrame(results)
results_path = Path(__file__).parent.parent / 'results' / 'data' / 'seismic_analysis.csv'
results_path.parent.mkdir(parents=True, exist_ok=True)
results_df.to_csv(results_path, index=False)
print(f"\nResults saved: {results_path}")

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")
