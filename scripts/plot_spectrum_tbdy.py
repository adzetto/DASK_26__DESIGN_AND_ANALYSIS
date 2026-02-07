#!/usr/bin/env python3
"""
TBDY2018 Design Spectrum - Period vs Sae(T) Plot
Shows current T1 position on the spectrum
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# =====================================================
# TBDY2018 SPECTRUM PARAMETERS
# =====================================================
# These are typical values - adjust based on your site
SDS = 1.0  # Short period design spectral acceleration (g)
SD1 = 0.5  # 1-second design spectral acceleration (g)

# Characteristic periods
TA = 0.2 * SD1 / SDS  # = 0.1s for SDS=1, SD1=0.5
TB = SD1 / SDS        # = 0.5s for SDS=1, SD1=0.5

# For DASK model (from modal analysis)
TA = 0.0729  # seconds
TB = 0.3646  # seconds
SDS = 1.556  # g (calculated to match Sae at plateau)

# Current model period
T1_CURRENT = 0.0608  # seconds (from modal analysis)

# =====================================================
# SPECTRUM FUNCTION
# =====================================================
def sae_tbdy2018(T, TA, TB, SDS):
    """
    TBDY2018 Elastic Design Spectrum
    
    T < TA:       Sae = (0.4 + 0.6*T/TA) * SDS  (ascending)
    TA <= T <= TB: Sae = SDS                     (plateau)
    T > TB:        Sae = SDS * TB / T            (descending)
    """
    if T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        return SDS
    else:
        return SDS * TB / T

# =====================================================
# GENERATE SPECTRUM DATA
# =====================================================
T_range = np.linspace(0.001, 1.0, 1000)
Sae_values = [sae_tbdy2018(T, TA, TB, SDS) for T in T_range]

# Calculate Sae at T1
Sae_T1 = sae_tbdy2018(T1_CURRENT, TA, TB, SDS)

# =====================================================
# PLOTTING
# =====================================================
fig, ax = plt.subplots(figsize=(12, 7))

# Fill regions with different colors
# Ascending region (T < TA)
T_asc = T_range[T_range < TA]
Sae_asc = [sae_tbdy2018(T, TA, TB, SDS) for T in T_asc]
ax.fill_between(T_asc, 0, Sae_asc, alpha=0.3, color='green', label='Ascending (T < TA)')

# Plateau region (TA <= T <= TB)
T_plat = T_range[(T_range >= TA) & (T_range <= TB)]
Sae_plat = [sae_tbdy2018(T, TA, TB, SDS) for T in T_plat]
ax.fill_between(T_plat, 0, Sae_plat, alpha=0.3, color='red', label='Plateau (TA ≤ T ≤ TB)')

# Descending region (T > TB)
T_desc = T_range[T_range > TB]
Sae_desc = [sae_tbdy2018(T, TA, TB, SDS) for T in T_desc]
ax.fill_between(T_desc, 0, Sae_desc, alpha=0.3, color='blue', label='Descending (T > TB)')

# Main spectrum curve
ax.plot(T_range, Sae_values, 'k-', linewidth=2.5, label='TBDY2018 Spectrum')

# Mark TA and TB
ax.axvline(x=TA, color='green', linestyle='--', linewidth=1.5, alpha=0.7)
ax.axvline(x=TB, color='red', linestyle='--', linewidth=1.5, alpha=0.7)

# Annotate TA and TB
ax.annotate(f'TA = {TA:.4f}s', xy=(TA, SDS*1.05), fontsize=11, ha='center', color='green', fontweight='bold')
ax.annotate(f'TB = {TB:.4f}s', xy=(TB, SDS*1.05), fontsize=11, ha='center', color='red', fontweight='bold')

# Mark current T1 position
ax.plot(T1_CURRENT, Sae_T1, 'ro', markersize=15, markeredgecolor='black', markeredgewidth=2, zorder=5)
ax.annotate(f'T1 = {T1_CURRENT:.4f}s\nSae = {Sae_T1:.3f}g', 
            xy=(T1_CURRENT, Sae_T1), 
            xytext=(T1_CURRENT + 0.08, Sae_T1 + 0.15),
            fontsize=12, fontweight='bold', color='red',
            arrowprops=dict(arrowstyle='->', color='red', lw=2))

# Horizontal line showing plateau level
ax.axhline(y=SDS, color='gray', linestyle=':', linewidth=1, alpha=0.5)
ax.annotate(f'SDS = {SDS:.3f}g', xy=(0.85, SDS), fontsize=10, va='bottom', color='gray')

# Labels and title
ax.set_xlabel('Period T (s)', fontsize=14, fontweight='bold')
ax.set_ylabel('Spectral Acceleration Sae(T) (g)', fontsize=14, fontweight='bold')
ax.set_title('TBDY2018 Elastic Design Spectrum\nTwin Towers Model - Current Period Position', 
             fontsize=16, fontweight='bold')

# Grid
ax.grid(True, alpha=0.3, linestyle='-')
ax.set_xlim(0, 0.8)
ax.set_ylim(0, max(Sae_values) * 1.15)

# Legend
ax.legend(loc='upper right', fontsize=11, framealpha=0.9)

# Add info box
info_text = f"""Model Parameters:
T1 = {T1_CURRENT:.4f}s (Fundamental Period)
TA = {TA:.4f}s
TB = {TB:.4f}s

Status: {'ASCENDING (T < TA) ✓' if T1_CURRENT < TA else 'PLATEAU (TA ≤ T ≤ TB) ✗' if T1_CURRENT <= TB else 'DESCENDING (T > TB)'}
Sae(T1) = {Sae_T1:.3f}g"""

props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.55, 0.65, info_text, transform=ax.transAxes, fontsize=11,
        verticalalignment='top', bbox=props, family='monospace')

plt.tight_layout()

# Save figure
output_path = '/mnt/c/Users/lenovo/Desktop/DASK_NEW/results/visualizations/tbdy2018_spectrum.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"\n{'='*60}")
print(f"SPECTRUM PLOT SAVED: {output_path}")
print(f"{'='*60}")

# Also save as PDF
pdf_path = '/mnt/c/Users/lenovo/Desktop/DASK_NEW/results/visualizations/tbdy2018_spectrum.pdf'
plt.savefig(pdf_path, format='pdf', bbox_inches='tight', facecolor='white')
print(f"PDF SAVED: {pdf_path}")

plt.show()

# Print summary
print(f"\n{'='*60}")
print("TBDY2018 SPECTRUM ANALYSIS")
print(f"{'='*60}")
print(f"TA = {TA:.4f}s (Ascending → Plateau transition)")
print(f"TB = {TB:.4f}s (Plateau → Descending transition)")
print(f"SDS = {SDS:.3f}g (Plateau level)")
print(f"\nCurrent Model:")
print(f"  T1 = {T1_CURRENT:.4f}s")
print(f"  Sae(T1) = {Sae_T1:.3f}g")
print(f"\nPosition: ", end="")
if T1_CURRENT < TA:
    print("ASCENDING REGION (T < TA) ✓")
    print("  → Lower Sae, good for weight optimization")
    margin = (TA - T1_CURRENT) / TA * 100
    print(f"  → Margin to TA: {(TA - T1_CURRENT)*1000:.1f}ms ({margin:.1f}%)")
elif T1_CURRENT <= TB:
    print("PLATEAU REGION (TA ≤ T ≤ TB) ✗")
    print("  → Maximum Sae - NOT RECOMMENDED")
else:
    print("DESCENDING REGION (T > TB)")
    print("  → Decreasing Sae with increasing period")
print(f"{'='*60}")
