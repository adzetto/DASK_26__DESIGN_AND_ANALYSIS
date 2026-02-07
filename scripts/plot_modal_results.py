#!/usr/bin/env python3
"""
Plot Modal Analysis Results with TBDY2018 Spectrum
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Results from OpenSeesPy analysis
T1 = 0.0412  # Fundamental period (s)
modes = [
    (1, 0.0412, 24.29),
    (2, 0.0411, 24.33),
    (3, 0.0169, 59.04),
    (4, 0.0097, 102.62),
    (5, 0.0076, 130.92),
]

# TBDY2018 Parameters
SS, S1 = 1.20, 0.35
FS, F1 = 1.20, 1.50
SDS = SS * FS  # 1.44g
SD1 = S1 * F1  # 0.525g
TA = 0.2 * SD1 / SDS  # 0.0729s
TB = SD1 / SDS        # 0.3646s
TL = 6.0

# Calculate Sae for T1
if T1 < TA:
    Sae_T1 = SDS * (0.4 + 0.6 * T1 / TA)
elif T1 <= TB:
    Sae_T1 = SDS
else:
    Sae_T1 = SD1 / T1

# Generate spectrum
T_range = np.linspace(0.001, 2.0, 1000)
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

# Create figure with 2 subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# ============================================
# Plot 1: TBDY2018 Spectrum with Period
# ============================================
ax1.plot(T_range, Sae_curve, 'b-', linewidth=2.5, label='TBDY2018 Spektrum')

# Mark regions
ax1.axvline(x=TA, color='orange', linestyle='--', linewidth=2, label=f'TA = {TA:.4f}s')
ax1.axvline(x=TB, color='red', linestyle='--', linewidth=2, label=f'TB = {TB:.4f}s')
ax1.axvspan(0, TA, alpha=0.15, color='green', label='Artan Bölge')
ax1.axvspan(TA, TB, alpha=0.2, color='red', label='Plato Bölgesi')
ax1.axvspan(TB, 2.0, alpha=0.1, color='blue', label='Azalan Bölge')

# Mark T1
ax1.axvline(x=T1, color='green', linestyle='-', linewidth=3, label=f'T1 = {T1:.4f}s')
ax1.plot(T1, Sae_T1, 'go', markersize=20, markeredgecolor='black', markeredgewidth=2, zorder=10)
ax1.annotate(f'T1 = {T1:.4f}s\nSae = {Sae_T1:.3f}g',
             xy=(T1, Sae_T1), xytext=(T1 + 0.15, Sae_T1 + 0.1),
             fontsize=12, fontweight='bold',
             arrowprops=dict(arrowstyle='->', color='green', lw=2),
             bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.9))

# Mark all modes
for mode, T, f in modes:
    if T < TA:
        S = SDS * (0.4 + 0.6 * T / TA)
    elif T <= TB:
        S = SDS
    else:
        S = SD1 / T
    if mode > 1:
        ax1.plot(T, S, 's', markersize=8, color='purple', alpha=0.7)
        ax1.annotate(f'M{mode}', xy=(T, S), xytext=(T, S + 0.08), fontsize=8, ha='center')

ax1.set_xlabel('Periyot T (s)', fontsize=14)
ax1.set_ylabel('Spektral İvme Sae (g)', fontsize=14)
ax1.set_title('TBDY2018 Tasarım Spektrumu\nTwin Towers V5 - Rijit Tasarım', fontsize=16, fontweight='bold')
ax1.legend(loc='upper right', fontsize=10)
ax1.grid(True, alpha=0.3)
ax1.set_xlim(0, 1.0)
ax1.set_ylim(0, SDS * 1.2)

# Add text box
info_text = f"""Model Bilgileri:
─────────────────
Düğüm: 1906
Eleman: 10960
Perde Duvar: 5232
Test Yükü: 15.02 kg

Periyot Analizi:
─────────────────
T1 = {T1:.4f} s
T2 = 0.0411 s
Sae = {Sae_T1:.3f} g

Durum: PLATO DIŞI ✓
(Artan Bölgede)"""

ax1.text(0.98, 0.45, info_text, transform=ax1.transAxes, fontsize=10,
         verticalalignment='top', horizontalalignment='right',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9),
         fontfamily='monospace')

# ============================================
# Plot 2: Mode Periods Bar Chart
# ============================================
mode_nums = [m[0] for m in modes]
periods = [m[1] for m in modes]
freqs = [m[2] for m in modes]

colors = ['green' if T < TA else ('red' if T <= TB else 'blue') for _, T, _ in modes]

bars = ax2.bar(mode_nums, periods, color=colors, edgecolor='black', linewidth=1.5, alpha=0.8)

# Add horizontal lines for TA and TB
ax2.axhline(y=TA, color='orange', linestyle='--', linewidth=2, label=f'TA = {TA:.4f}s')
ax2.axhline(y=TB, color='red', linestyle='--', linewidth=2, label=f'TB = {TB:.4f}s')

# Add value labels on bars
for bar, T, f in zip(bars, periods, freqs):
    height = bar.get_height()
    ax2.annotate(f'{T:.4f}s\n({f:.1f}Hz)',
                xy=(bar.get_x() + bar.get_width()/2, height),
                xytext=(0, 5), textcoords="offset points",
                ha='center', va='bottom', fontsize=10, fontweight='bold')

ax2.set_xlabel('Mod Numarası', fontsize=14)
ax2.set_ylabel('Periyot T (s)', fontsize=14)
ax2.set_title('Modal Periyotlar\n(OpenSeesPy Analizi)', fontsize=16, fontweight='bold')
ax2.legend(loc='upper right', fontsize=11)
ax2.grid(True, alpha=0.3, axis='y')
ax2.set_xticks(mode_nums)
ax2.set_ylim(0, max(TB, max(periods)) * 1.3)

# Add legend for colors
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='green', edgecolor='black', label='T < TA (Artan)'),
    Patch(facecolor='red', edgecolor='black', label='TA ≤ T ≤ TB (Plato)'),
    Patch(facecolor='blue', edgecolor='black', label='T > TB (Azalan)')
]
ax2.legend(handles=legend_elements, loc='upper right', fontsize=10)

plt.tight_layout()

# Save
RESULTS_DIR = Path(__file__).parent.parent / 'results' / 'visualizations'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

output_path = RESULTS_DIR / 'modal_analysis_tbdy2018.png'
plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {output_path}")

# Also save a zoomed version
fig2, ax = plt.subplots(figsize=(12, 8))

ax.plot(T_range, Sae_curve, 'b-', linewidth=3, label='TBDY2018 Spektrum')
ax.axvline(x=TA, color='orange', linestyle='--', linewidth=2.5, label=f'TA = {TA:.4f}s')
ax.axvline(x=TB, color='red', linestyle='--', linewidth=2.5, label=f'TB = {TB:.4f}s')
ax.axvspan(0, TA, alpha=0.2, color='lightgreen')
ax.axvspan(TA, TB, alpha=0.25, color='lightcoral')

ax.axvline(x=T1, color='darkgreen', linestyle='-', linewidth=4)
ax.plot(T1, Sae_T1, 'go', markersize=25, markeredgecolor='black', markeredgewidth=3, zorder=10)

ax.annotate(f'TEMEL PERİYOT\nT1 = {T1:.4f} s\nSae = {Sae_T1:.3f} g',
            xy=(T1, Sae_T1), xytext=(0.2, 1.2),
            fontsize=14, fontweight='bold',
            arrowprops=dict(arrowstyle='->', color='darkgreen', lw=3),
            bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.95, edgecolor='green', linewidth=2))

ax.set_xlabel('Periyot T (s)', fontsize=16)
ax.set_ylabel('Spektral İvme Sae (g)', fontsize=16)
ax.set_title('TBDY2018 Tasarım Spektrumu - Twin Towers V5 Rijit\n' +
             f'Temel Periyot: T1 = {T1:.4f}s | Bölge: ARTAN (Plato Altı)',
             fontsize=18, fontweight='bold')
ax.legend(loc='upper right', fontsize=12)
ax.grid(True, alpha=0.4)
ax.set_xlim(0, 0.6)
ax.set_ylim(0, 1.6)

# Region labels
ax.text(TA/2, 0.5, 'ARTAN\nBÖLGE', fontsize=14, ha='center', va='center',
        color='darkgreen', fontweight='bold', alpha=0.8)
ax.text((TA+TB)/2, 0.5, 'PLATO\nBÖLGESİ', fontsize=14, ha='center', va='center',
        color='darkred', fontweight='bold', alpha=0.8)

plt.tight_layout()
output_path2 = RESULTS_DIR / 'modal_analysis_tbdy2018_zoom.png'
plt.savefig(output_path2, dpi=150, bbox_inches='tight', facecolor='white')
print(f"Saved: {output_path2}")

print("\nDone!")
