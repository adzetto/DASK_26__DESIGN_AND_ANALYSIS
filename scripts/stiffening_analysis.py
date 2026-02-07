"""
DASK 2026 Twin Towers - Stiffening Analysis
Core + Bracing only (no outrigger system)
Weight limit: 1.4 kg for 2 towers + bridges
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

print("=" * 70)
print("DASK 2026 - STIFFENING ANALYSIS (Core + Bracing)")
print("=" * 70)

# ============================================
# CURRENT MODEL STATE (from twin_towers.ipynb)
# ============================================
current_state = {
    'nodes': 796,
    'elements': 2768,
    'total_length_mm': 239459,
    'weight_limit_kg': 1.40,
    'height_mm': 1530,
    'T1_s': 0.1181,          # Fundamental period (Y-direction)
    'max_drift_mm': 369.2,
    'drift_ratio': 0.241,
    'target_drift': 0.02,    # 2% typical limit
    'target_drift_mm': 30.6,
}

# Material properties
balsa = {
    'E_MPa': 3500,
    'rho_kg_m3': 160,      # Typical balsa density
    'section_mm': 6,
    'A_mm2': 36,           # 6mm x 6mm
    'I_mm4': 108,          # (6^4)/12
}

# Calculate current weight
current_weight_kg = current_state['total_length_mm'] * balsa['A_mm2'] * balsa['rho_kg_m3'] / 1e9
current_state['weight_kg'] = current_weight_kg

print("\n--- CURRENT STATE ---")
print(f"  Total elements: {current_state['elements']}")
print(f"  Total length: {current_state['total_length_mm']:,.0f} mm")
print(f"  Current weight: {current_weight_kg:.3f} kg")
print(f"  Weight limit: {current_state['weight_limit_kg']:.2f} kg")
print(f"  Weight margin: {(current_state['weight_limit_kg'] - current_weight_kg)*1000:.0f} g")
print(f"  Building height: {current_state['height_mm']:.0f} mm")
print(f"  Fundamental period: {current_state['T1_s']:.4f} s")

# Check weight compliance
if current_weight_kg <= current_state['weight_limit_kg']:
    print(f"\n  ✓ Weight OK: {current_weight_kg:.3f} kg ≤ {current_state['weight_limit_kg']:.2f} kg")
else:
    print(f"\n  ✗ OVERWEIGHT: {current_weight_kg:.3f} kg > {current_state['weight_limit_kg']:.2f} kg")
    excess = (current_weight_kg - current_state['weight_limit_kg']) * 1000
    print(f"    Need to remove: {excess:.0f} g")

# ============================================
# DASK 2026 DESIGN SPECTRUM - Sae(T)
# TBDY 2018 Horizontal Elastic Design Spectrum
# ============================================
print("\n" + "=" * 70)
print("DASK 2026 DESIGN SPECTRUM ANALYSIS")
print("=" * 70)

# DASK 2026 Spectrum Parameters (from şartname)
# Site: Istanbul Technical University (ITU)
# Ground motion: PGA = 0.82g (maximum spectral acceleration)
SDS = 2.046    # Short period design spectral acceleration (g)
SD1 = 0.619    # 1-second design spectral acceleration (g)
TA = 0.2 * SD1 / SDS   # Corner period TA
TB = SD1 / SDS         # Corner period TB
TL = 6.0               # Long period limit

# PGA for DASK 2026
PGA = 0.82  # g

print(f"\nSpectrum Parameters (TBDY 2018):")
print(f"  SDS = {SDS:.3f} g")
print(f"  SD1 = {SD1:.3f} g")
print(f"  TA  = {TA:.3f} s")
print(f"  TB  = {TB:.3f} s")
print(f"  TL  = {TL:.1f} s")
print(f"  PGA = {PGA:.2f} g")

def Sae(T):
    """
    TBDY 2018 Horizontal Elastic Design Spectrum
    Returns: Sae(T) in units of g
    """
    if T < TA:
        return SDS * (0.4 + 0.6 * T / TA)
    elif T <= TB:
        return SDS
    elif T <= TL:
        return SD1 / T
    else:
        return SD1 * TL / (T * T)

# Generate spectrum curve
T_range = np.concatenate([
    np.linspace(0.001, TA, 20),
    np.linspace(TA, TB, 30),
    np.linspace(TB, 2.0, 100),
    np.linspace(2.0, 4.0, 50)
])
T_range = np.unique(np.sort(T_range))
Sae_values = np.array([Sae(T) for T in T_range])

# Building period and corresponding spectral acceleration
T_building = current_state['T1_s']
Sae_building = Sae(T_building)

print(f"\nBuilding Dynamic Properties:")
print(f"  Fundamental Period T1 = {T_building:.4f} s")
print(f"  Spectral Acceleration Sae(T1) = {Sae_building:.3f} g")

# Determine spectrum region
if T_building < TA:
    region = "ASCENDING BRANCH (T < TA)"
    region_desc = "Period increases → Sae increases"
elif T_building <= TB:
    region = "PLATEAU (TA ≤ T ≤ TB)"
    region_desc = "Maximum spectral acceleration (Sae = SDS)"
else:
    region = "DESCENDING BRANCH (T > TB)"
    region_desc = "Period increases → Sae decreases (velocity-controlled)"

print(f"\n  Spectrum Region: {region}")
print(f"  Implication: {region_desc}")

# ============================================
# PERIOD vs Sae(T) PLOT
# ============================================
fig, ax = plt.subplots(1, 1, figsize=(12, 7))

# Plot spectrum curve
ax.plot(T_range, Sae_values, 'b-', linewidth=2, label='TBDY 2018 Design Spectrum')

# Mark corner periods
ax.axvline(x=TA, color='gray', linestyle='--', alpha=0.5, label=f'TA = {TA:.3f}s')
ax.axvline(x=TB, color='gray', linestyle='-.', alpha=0.5, label=f'TB = {TB:.3f}s')

# Mark building period
ax.plot(T_building, Sae_building, 'ro', markersize=15, markeredgecolor='black',
        markeredgewidth=2, zorder=5, label=f'Building T1 = {T_building:.4f}s')

# Add annotation for building
ax.annotate(f'T₁ = {T_building:.4f}s\nSae = {Sae_building:.3f}g',
            xy=(T_building, Sae_building),
            xytext=(T_building + 0.15, Sae_building + 0.3),
            fontsize=12, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='red', lw=2),
            bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.8))

# Fill regions
ax.fill_between(T_range[T_range <= TA], 0, Sae_values[T_range <= TA],
                alpha=0.2, color='green', label='Ascending (T < TA)')
ax.fill_between(T_range[(T_range >= TA) & (T_range <= TB)], 0,
                Sae_values[(T_range >= TA) & (T_range <= TB)],
                alpha=0.2, color='orange', label='Plateau (TA ≤ T ≤ TB)')
ax.fill_between(T_range[T_range >= TB], 0, Sae_values[T_range >= TB],
                alpha=0.2, color='blue', label='Descending (T > TB)')

# Mark SDS and PGA
ax.axhline(y=SDS, color='orange', linestyle=':', alpha=0.7)
ax.text(3.5, SDS + 0.05, f'SDS = {SDS:.3f}g', fontsize=10, color='darkorange')

ax.axhline(y=PGA, color='red', linestyle=':', alpha=0.7)
ax.text(3.5, PGA + 0.05, f'PGA = {PGA:.2f}g', fontsize=10, color='red')

ax.set_xlabel('Period T (s)', fontsize=12)
ax.set_ylabel('Spectral Acceleration Sae(T) (g)', fontsize=12)
ax.set_title('DASK 2026 - Period vs Spectral Acceleration\nTBDY 2018 Horizontal Elastic Design Spectrum', fontsize=14)
ax.set_xlim(0, 4)
ax.set_ylim(0, max(Sae_values) * 1.15)
ax.grid(True, alpha=0.3)
ax.legend(loc='upper right', fontsize=9)

# Save plot
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', 'visualizations')
os.makedirs(output_dir, exist_ok=True)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, 'period_vs_sae_spectrum.png'), dpi=150, bbox_inches='tight')
print(f"\nSpectrum plot saved to: period_vs_sae_spectrum.png")

plt.show()

# ============================================
# STIFFENING OPTIONS (Core + Bracing only)
# ============================================
print("\n" + "=" * 70)
print("STIFFENING OPTIONS ANALYSIS (Core + Bracing Only)")
print("=" * 70)

# Stiffness ratio needed
stiffness_ratio = current_state['max_drift_mm'] / current_state['target_drift_mm']
print(f"\n  Required stiffness increase: {stiffness_ratio:.1f}x")

# Option 1: Add Y-direction braces
print("\n--- OPTION 1: ADD Y-DIRECTION BRACES ---")
y_brace_data = {
    'description': 'Add continuous X-braces on short faces (Y-direction)',
    'new_length_mm': 26 * 2 * 72 * 2,  # 26 floors, 2 bays Y, diagonal ~72mm, 2 towers
    'element_count': 26 * 2 * 2,       # 26 floors, 2 bays, 2 towers
}
y_brace_data['weight_g'] = y_brace_data['new_length_mm'] * balsa['A_mm2'] * balsa['rho_kg_m3'] / 1e6
y_brace_data['stiffness_increase'] = 1.5

print(f"  Added elements: {y_brace_data['element_count']}")
print(f"  Added length: {y_brace_data['new_length_mm']:,.0f} mm")
print(f"  Added weight: {y_brace_data['weight_g']:.1f} g")
print(f"  Est. stiffness increase: {y_brace_data['stiffness_increase']:.1f}x in Y-direction")

# Option 2: Stiffen bridges
print("\n--- OPTION 2: STIFFEN BRIDGE CONNECTIONS ---")
bridge_data = {
    'description': 'Double bridge elements at floors 6, 12, 18',
    'new_length_mm': 80 * 4 * 8,  # gap=80mm, 4 beams x 8 bridges
    'element_count': 32,
}
bridge_data['weight_g'] = bridge_data['new_length_mm'] * balsa['A_mm2'] * balsa['rho_kg_m3'] / 1e6
bridge_data['torsion_reduction'] = 0.7

print(f"  Added elements: {bridge_data['element_count']}")
print(f"  Added length: {bridge_data['new_length_mm']:,.0f} mm")
print(f"  Added weight: {bridge_data['weight_g']:.1f} g")
print(f"  Est. torsion reduction: {(1-bridge_data['torsion_reduction'])*100:.0f}%")

# Option 3: Increase section size at base
print("\n--- OPTION 3: LARGER BASE SECTION (8x8mm) ---")
base_section_data = {
    'description': 'Use 8x8mm section for ground floor columns',
    'A_new_mm2': 64,
    'I_new_mm4': 341.33,
    'columns_affected': 36,       # Base columns (18 per tower)
    'column_height_mm': 90,
}
base_section_data['old_weight_g'] = base_section_data['columns_affected'] * base_section_data['column_height_mm'] * balsa['A_mm2'] * balsa['rho_kg_m3'] / 1e6
base_section_data['new_weight_g'] = base_section_data['columns_affected'] * base_section_data['column_height_mm'] * base_section_data['A_new_mm2'] * balsa['rho_kg_m3'] / 1e6
base_section_data['weight_diff_g'] = base_section_data['new_weight_g'] - base_section_data['old_weight_g']
base_section_data['I_ratio'] = base_section_data['I_new_mm4'] / balsa['I_mm4']
base_section_data['stress_reduction'] = 1 / base_section_data['I_ratio']

print(f"  Section: 6x6mm -> 8x8mm")
print(f"  Columns affected: {base_section_data['columns_affected']}")
print(f"  Weight change: +{base_section_data['weight_diff_g']:.1f} g")
print(f"  Moment of inertia increase: {base_section_data['I_ratio']:.1f}x")
print(f"  Base stress reduction: {(1-base_section_data['stress_reduction'])*100:.0f}%")

# Option 4: Add core shear walls (braces)
print("\n--- OPTION 4: ADD CORE X-BRACES ---")
core_brace_data = {
    'description': 'Add X-pattern in core at every 3 floors',
    'floors': list(range(1, 26, 3)),
    'x_patterns_per_floor': 4,  # 2 per tower, 2 directions
}
core_brace_data['element_count'] = len(core_brace_data['floors']) * core_brace_data['x_patterns_per_floor'] * 2
core_brace_data['diagonal_mm'] = 68
core_brace_data['new_length_mm'] = core_brace_data['element_count'] * core_brace_data['diagonal_mm']
core_brace_data['weight_g'] = core_brace_data['new_length_mm'] * balsa['A_mm2'] * balsa['rho_kg_m3'] / 1e6
core_brace_data['stiffness_increase'] = 1.4

print(f"  Core X-braces at floors: {core_brace_data['floors']}")
print(f"  Added elements: {core_brace_data['element_count']}")
print(f"  Added weight: {core_brace_data['weight_g']:.1f} g")
print(f"  Est. stiffness increase: {core_brace_data['stiffness_increase']:.1f}x")

# ============================================
# WEIGHT BUDGET ANALYSIS
# ============================================
print("\n" + "=" * 70)
print("WEIGHT BUDGET ANALYSIS")
print("=" * 70)

weight_limit = current_state['weight_limit_kg'] * 1000  # g
current_weight = current_weight_kg * 1000  # g

print(f"\n  Weight limit:  {weight_limit:.0f} g")
print(f"  Current weight: {current_weight:.1f} g")
print(f"  Available:      {weight_limit - current_weight:.1f} g")

# Check if options fit in budget
print(f"\n  Option breakdown:")
options_weight = {
    'Y-braces': y_brace_data['weight_g'],
    'Bridge reinforcement': bridge_data['weight_g'],
    'Base section upgrade': base_section_data['weight_diff_g'],
    'Core X-braces': core_brace_data['weight_g'],
}

cumulative = current_weight
for option, weight in options_weight.items():
    cumulative += weight
    status = "✓" if cumulative <= weight_limit else "✗"
    print(f"    {status} +{option}: {weight:.1f}g → Total: {cumulative:.1f}g")

# ============================================
# RECOMMENDATIONS
# ============================================
print("\n" + "=" * 70)
print("RECOMMENDATIONS SUMMARY")
print("=" * 70)

# Combined strategy (within budget)
total_added_weight = (
    y_brace_data['weight_g'] +
    bridge_data['weight_g'] +
    base_section_data['weight_diff_g']
)
new_weight = current_weight + total_added_weight

print(f"\n  RECOMMENDED STIFFENING PACKAGE:")
print(f"    - Add Y-direction braces: +{y_brace_data['weight_g']:.0f} g")
print(f"    - Stiffen bridges: +{bridge_data['weight_g']:.0f} g")
print(f"    - Larger base section: +{base_section_data['weight_diff_g']:.0f} g")
print(f"    ---------------------------------")
print(f"    Total added: {total_added_weight:.0f} g")
print(f"\n  New total weight: {new_weight:.0f} g = {new_weight/1000:.3f} kg")
print(f"  Weight limit: {weight_limit:.0f} g")
print(f"  Margin: {weight_limit - new_weight:.0f} g")

# Period implication
if T_building < TA:
    position_text = f"T1 = {T_building:.4f}s falls in the ASCENDING branch (T < TA = {TA:.3f}s)"
    implication_text = "Located in region where Sae INCREASES with period"
elif T_building <= TB:
    position_text = f"T1 = {T_building:.4f}s falls in the PLATEAU region (TA < T < TB)"
    implication_text = "Located at MAXIMUM spectral acceleration (Sae = SDS)"
else:
    position_text = f"T1 = {T_building:.4f}s falls in the DESCENDING branch (T > TB = {TB:.3f}s)"
    implication_text = "Located in region where Sae DECREASES with period"

print(f"""
PERIOD vs SPECTRAL ACCELERATION ANALYSIS:
=========================================
Building Period: T1 = {T_building:.4f} s
Spectral Region: {region}

Current position on spectrum:
  - {position_text}
  - Sae(T1) = {Sae_building:.3f}g

Structural Implications:
  - Building period is relatively short for the spectrum
  - {implication_text}
  - Current Sae is {Sae_building/SDS*100:.1f}% of maximum plateau value (SDS)

Design Considerations:
  - For seismic design: short period = high accelerations but low displacements
  - The building experiences {Sae_building:.3f}g spectral acceleration
  - Base shear will be proportional to Sae(T) × building mass
""")

# Save summary data
output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results', 'data')
os.makedirs(output_dir, exist_ok=True)

summary_data = {
    'option': ['Y-braces', 'Bridges', 'Base section', 'Core braces'],
    'weight_g': [
        y_brace_data['weight_g'],
        bridge_data['weight_g'],
        base_section_data['weight_diff_g'],
        core_brace_data['weight_g']
    ],
    'effect': [
        f"{y_brace_data['stiffness_increase']:.1f}x Y-stiffness",
        f"{(1-bridge_data['torsion_reduction'])*100:.0f}% torsion reduction",
        f"{(1-base_section_data['stress_reduction'])*100:.0f}% base stress reduction",
        f"{core_brace_data['stiffness_increase']:.1f}x stiffness"
    ],
    'priority': [1, 1, 1, 2]
}

df = pd.DataFrame(summary_data)
df.to_csv(os.path.join(output_dir, 'stiffening_options.csv'), index=False)
print(f"\nSummary saved to: stiffening_options.csv")

# Save spectrum data
spectrum_df = pd.DataFrame({
    'T_s': T_range,
    'Sae_g': Sae_values
})
spectrum_df.to_csv(os.path.join(output_dir, 'design_spectrum.csv'), index=False)
print(f"Spectrum data saved to: design_spectrum.csv")

# ============================================
# WEIGHT TABLE FOR DIFFERENT BALSA DENSITIES
# ============================================
print("\n" + "=" * 70)
print("WEIGHT vs BALSA DENSITY")
print("=" * 70)

densities = [100, 120, 140, 160, 180, 200]
weights = []

for rho in densities:
    weight = current_state['total_length_mm'] * balsa['A_mm2'] * rho / 1e9
    weights.append({
        'Density (kg/m³)': rho,
        'Weight (g)': weight * 1000,
        'Weight (kg)': weight,
        'Status': '✓ OK' if weight <= current_state['weight_limit_kg'] else '✗ OVER'
    })

weight_df = pd.DataFrame(weights)
print(f"\nTotal element length: {current_state['total_length_mm']:,.0f} mm")
print(f"Section: {balsa['section_mm']:.0f}mm × {balsa['section_mm']:.0f}mm (A = {balsa['A_mm2']} mm²)")
print(f"Weight limit: {current_state['weight_limit_kg']} kg")
print()
print(weight_df.to_string(index=False))

# Maximum allowable density
max_density = current_state['weight_limit_kg'] * 1e9 / (current_state['total_length_mm'] * balsa['A_mm2'])
print(f"\nMaximum allowable balsa density: {max_density:.0f} kg/m³")
