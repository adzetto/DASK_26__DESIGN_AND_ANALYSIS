#!/usr/bin/env python3
"""
STRUCTURAL ANALYSIS V2 - Rigidity-Based Period Calculation
===========================================================
Better period estimation for heavily braced structures.
"""

import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

print("=" * 70)
print("STRUCTURAL ANALYSIS V2 - Rigidity-Based")
print("=" * 70)

# Load data
DATA_DIR = Path(__file__).parent.parent / 'data'
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
npz = np.load(DATA_DIR / 'twin_building_data.npz')

coords = npz['coords']
z_coords = npz['z_coords']

n_nodes = len(pos_df)
n_elements = len(conn_df)
n_floors = len(z_coords)
H = z_coords[-1]

print(f"Model: {n_nodes} nodes, {n_elements} elements")
print(f"Height: {H:.1f}m ({n_floors} floors)")

# ============================================
# MATERIAL PROPERTIES
# ============================================
E_BALSA = 3.5e9  # Pa
RHO_BALSA = 160  # kg/m³
b = h = 0.006  # m (6mm)
A = b * h
I = b * h**3 / 12

# ============================================
# ELEMENT ANALYSIS
# ============================================
# Count by type
elem_counts = conn_df['element_type'].value_counts()
print(f"\nElement Distribution:")
for etype, count in elem_counts.items():
    print(f"  {etype}: {count}")

# Categorize elements
columns = conn_df[conn_df['element_type'] == 'column']
bracing = conn_df[conn_df['element_type'].str.contains('shear|wall|core|brace', case=False)]
beams = conn_df[conn_df['element_type'].str.contains('beam', case=False)]

n_columns = len(columns)
n_bracing = len(bracing)
n_beams = len(beams)

print(f"\nStructural Elements:")
print(f"  Columns: {n_columns}")
print(f"  Bracing/Walls: {n_bracing}")
print(f"  Beams: {n_beams}")

# ============================================
# MASS CALCULATION
# ============================================
total_length = conn_df['length'].sum()
total_mass = total_length * A * RHO_BALSA

print(f"\nMass:")
print(f"  Total length: {total_length:.1f}m")
print(f"  Total mass: {total_mass:.3f} kg")

# ============================================
# STIFFNESS CALCULATION - Detailed
# ============================================
print(f"\n{'='*50}")
print("STIFFNESS ANALYSIS")
print(f"{'='*50}")

avg_floor_height = H / (n_floors - 1)
print(f"Average floor height: {avg_floor_height:.2f}m")

# Column stiffness (fixed-fixed bending)
k_col_bending = 12 * E_BALSA * I / (avg_floor_height ** 3)
print(f"\nColumn bending stiffness: {k_col_bending:.2e} N/m")

# Bracing stiffness (axial)
avg_brace_length = bracing['length'].mean() if len(bracing) > 0 else avg_floor_height * 1.4
k_brace_axial = E_BALSA * A / avg_brace_length
# Horizontal component (assume 45° average angle)
k_brace_horiz = k_brace_axial * 0.5  # cos²(45°)
print(f"Brace axial stiffness: {k_brace_axial:.2e} N/m")
print(f"Brace horizontal component: {k_brace_horiz:.2e} N/m")

# Per-floor stiffness
cols_per_floor = n_columns / (n_floors - 1)
braces_per_floor = n_bracing / (n_floors - 1)

k_floor_cols = cols_per_floor * k_col_bending
k_floor_braces = braces_per_floor * k_brace_horiz
k_floor_total = k_floor_cols + k_floor_braces

print(f"\nPer-floor stiffness:")
print(f"  From columns ({cols_per_floor:.0f}/floor): {k_floor_cols:.2e} N/m")
print(f"  From bracing ({braces_per_floor:.0f}/floor): {k_floor_braces:.2e} N/m")
print(f"  TOTAL: {k_floor_total:.2e} N/m")

# ============================================
# PERIOD CALCULATION - Multiple Methods
# ============================================
print(f"\n{'='*50}")
print("PERIOD ESTIMATION")
print(f"{'='*50}")

# Method 1: Single DOF approximation
# T = 2π√(M/K) where K is effective building stiffness
# For shear building: K_eff ≈ k_floor / n_floors (roughly)
K_eff = k_floor_total * (n_floors - 1) / n_floors
M_eff = total_mass * 0.7  # Modal mass participation ~70%
T_sdof = 2 * np.pi * np.sqrt(M_eff / K_eff)
print(f"\n1. SDOF Approximation:")
print(f"   K_eff = {K_eff:.2e} N/m")
print(f"   M_eff = {M_eff:.3f} kg")
print(f"   T = {T_sdof:.4f} s")

# Method 2: Rayleigh method with linear mode shape
# δ(z) = z/H (linear), f(z) = m*g*z/H
# T = 2π√(Σm*δ²/Σf*δ)
# For uniform mass: T ≈ 2π√(M*H/(3*K))
T_rayleigh = 2 * np.pi * np.sqrt(total_mass * H / (3 * K_eff))
print(f"\n2. Rayleigh (linear mode):")
print(f"   T = {T_rayleigh:.4f} s")

# Method 3: Empirical for braced frames
# T = 0.0488 * H^0.75 (for braced frames)
T_braced = 0.0488 * (H ** 0.75)
print(f"\n3. Empirical (braced frame):")
print(f"   T = {T_braced:.4f} s")

# Method 4: For heavily braced/shear wall buildings
# T = 0.05 * H / √D where D is building width in direction of motion
D_x = 30.0  # m
D_y = 16.0  # m per tower
T_shearwall_x = 0.05 * H / np.sqrt(D_x)
T_shearwall_y = 0.05 * H / np.sqrt(D_y)
print(f"\n4. Shear wall formula:")
print(f"   T_x = {T_shearwall_x:.4f} s (X-direction)")
print(f"   T_y = {T_shearwall_y:.4f} s (Y-direction)")

# Method 5: Based on bracing ratio
# More bracing = stiffer = lower period
bracing_ratio = n_bracing / n_elements
stiffness_factor = 1 + bracing_ratio * 10  # Empirical multiplier
T_adjusted = T_braced / np.sqrt(stiffness_factor)
print(f"\n5. Bracing-adjusted:")
print(f"   Bracing ratio: {bracing_ratio:.1%}")
print(f"   Stiffness factor: {stiffness_factor:.2f}x")
print(f"   T = {T_adjusted:.4f} s")

# DESIGN PERIOD - weighted average for rigid structure
# Weight towards Rayleigh and shear wall formulas for heavily braced
T_design = (T_rayleigh + T_shearwall_x + T_sdof) / 3
print(f"\n>>> DESIGN PERIOD: T = {T_design:.4f} s <<<")

# ============================================
# TBDY2018 SPECTRUM
# ============================================
print(f"\n{'='*50}")
print("TBDY2018 SPECTRUM CHECK")
print(f"{'='*50}")

SS, S1 = 1.20, 0.35
FS, F1 = 1.20, 1.50
SDS = SS * FS
SD1 = S1 * F1
TA = 0.2 * SD1 / SDS
TB = SD1 / SDS
TL = 6.0

print(f"SDS = {SDS:.3f}g, SD1 = {SD1:.3f}g")
print(f"TA = {TA:.4f}s, TB = {TB:.4f}s")

# Determine region
if T_design < TA:
    region = "ASCENDING (T < TA)"
    Sae = SDS * (0.4 + 0.6 * T_design / TA)
    in_plateau = False
    status = "STIFFER than plateau - MAXIMUM spectral acceleration zone"
elif T_design <= TB:
    region = "PLATEAU (TA ≤ T ≤ TB)"
    Sae = SDS
    in_plateau = True
    status = "IN PLATEAU - Maximum spectral acceleration"
else:
    region = "DESCENDING (T > TB)"
    Sae = SD1 / T_design
    in_plateau = False
    status = "Descending - Lower spectral acceleration"

print(f"\nDesign Period: T = {T_design:.4f} s")
print(f"Plateau Range: {TA:.4f}s to {TB:.4f}s")
print(f"\n>>> REGION: {region} <<<")
print(f">>> Sae = {Sae:.3f}g <<<")
print(f"\nStatus: {status}")

# ============================================
# COMPARISON TABLE
# ============================================
print(f"\n{'='*50}")
print("PERIOD COMPARISON")
print(f"{'='*50}")
print(f"{'Method':<30} {'Period (s)':<12} {'vs TA':<10} {'vs TB':<10}")
print("-" * 62)

periods = [
    ("SDOF Approximation", T_sdof),
    ("Rayleigh", T_rayleigh),
    ("Empirical (braced)", T_braced),
    ("Shear wall (X)", T_shearwall_x),
    ("Shear wall (Y)", T_shearwall_y),
    ("Bracing-adjusted", T_adjusted),
    ("DESIGN (average)", T_design),
]

for name, T in periods:
    vs_ta = "< TA" if T < TA else (">= TA" if T < TB else "> TB")
    vs_tb = "< TB" if T < TB else ">= TB"
    marker = "★" if T < TA else ("●" if T <= TB else "○")
    print(f"{name:<30} {T:<12.4f} {vs_ta:<10} {vs_tb:<10} {marker}")

print("\nLegend: ★ = Below plateau, ● = In plateau, ○ = Above plateau")

# ============================================
# RIGIDITY ASSESSMENT
# ============================================
print(f"\n{'='*50}")
print("RIGIDITY ASSESSMENT")
print(f"{'='*50}")

# Drift check (simplified)
# Δ/H = V / (K * H)
I_factor = 1.5
R = 4.0
W = total_mass * 9.81
V_base = Sae * I_factor * W / R

drift_ratio = V_base / (K_eff * H)
print(f"Base shear: V = {V_base:.2f} N")
print(f"Effective stiffness: K = {K_eff:.2e} N/m")
print(f"Approximate drift ratio: Δ/H = {drift_ratio:.6f} ({drift_ratio*100:.4f}%)")

# TBDY2018 drift limit
drift_limit = 0.008  # 0.8% for importance class II
print(f"TBDY2018 drift limit: {drift_limit*100:.1f}%")
if drift_ratio < drift_limit:
    print(f"✓ Drift is within limits")
else:
    print(f"✗ Drift exceeds limit!")

# Rigidity score
rigidity_score = (n_bracing / n_elements) * 100
print(f"\nRigidity Score: {rigidity_score:.1f}%")
print(f"  (Percentage of elements that are bracing/shear walls)")

if rigidity_score > 50:
    print(f"  → VERY RIGID structure")
elif rigidity_score > 30:
    print(f"  → RIGID structure")
elif rigidity_score > 15:
    print(f"  → MODERATELY RIGID structure")
else:
    print(f"  → FLEXIBLE structure")

# ============================================
# PLOT
# ============================================
RESULTS_DIR = Path(__file__).parent.parent / 'results' / 'visualizations'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

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

plt.figure(figsize=(14, 8))
plt.plot(T_range, Sae_curve, 'b-', linewidth=2.5, label='TBDY2018 Spectrum')

# Regions
plt.axvline(x=TA, color='orange', linestyle='--', alpha=0.8, linewidth=1.5, label=f'TA = {TA:.4f}s')
plt.axvline(x=TB, color='red', linestyle='--', alpha=0.8, linewidth=1.5, label=f'TB = {TB:.4f}s')
plt.axvspan(TA, TB, alpha=0.15, color='red', label='Plateau Region')
plt.axvspan(0, TA, alpha=0.1, color='orange', label='Ascending Region')

# Mark all period estimates
colors = ['green', 'purple', 'brown', 'cyan', 'magenta', 'olive']
for i, (name, T) in enumerate(periods[:-1]):  # Skip design period for now
    if T < TA:
        S = SDS * (0.4 + 0.6 * T / TA)
    elif T <= TB:
        S = SDS
    else:
        S = SD1 / T if T <= TL else SD1 * TL / (T ** 2)
    plt.plot(T, S, 'o', color=colors[i % len(colors)], markersize=8, alpha=0.7)
    plt.annotate(name.split()[0], (T, S), textcoords="offset points",
                xytext=(5, 5), fontsize=8, alpha=0.8)

# Design period
plt.axvline(x=T_design, color='green', linestyle='-', linewidth=3, label=f'T_design = {T_design:.4f}s')
plt.plot(T_design, Sae, 'go', markersize=15, markeredgecolor='black', markeredgewidth=2, zorder=10)

plt.xlabel('Period T (s)', fontsize=12)
plt.ylabel('Spectral Acceleration Sae (g)', fontsize=12)
plt.title(f'TBDY2018 Spectrum - Rigid Twin Towers (V5)\n' +
          f'T = {T_design:.4f}s | Sae = {Sae:.3f}g | Region: {region}', fontsize=14)
plt.legend(loc='upper right', fontsize=9)
plt.grid(True, alpha=0.3)
plt.xlim(0, 2.0)  # Zoom in to see detail
plt.ylim(0, SDS * 1.3)

# Info box
info = f"Rigidity Score: {rigidity_score:.1f}%\n"
info += f"Bracing Elements: {n_bracing}\n"
info += f"Total Elements: {n_elements}\n"
info += f"Base Shear: {V_base:.1f} N"
props = dict(boxstyle='round', facecolor='lightgreen', alpha=0.8)
plt.text(0.98, 0.6, info, transform=plt.gca().transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right', bbox=props)

plt.tight_layout()
plt.savefig(RESULTS_DIR / 'period_vs_sae_spectrum.png', dpi=150)
print(f"\nPlot saved: {RESULTS_DIR / 'period_vs_sae_spectrum.png'}")

print(f"\n{'='*70}")
print("ANALYSIS COMPLETE")
print(f"{'='*70}")
