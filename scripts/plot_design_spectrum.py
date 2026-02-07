"""
PLOT TBDY 2018 DESIGN SPECTRUM
==============================
Visualizes the Horizontal Elastic Design Spectrum S_ae(T)
and marks the position of the Balsa Model.

Parameters (DASK/Bolu Region):
  SDS = 2.046 g
  SD1 = 0.619 g
  TA  = 0.061 s
  TB  = 0.303 s
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

# Setup
OUTPUT_DIR = Path(__file__).parent.parent / 'results' / 'visualizations'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 1. PARAMETERS
SDS = 2.046
SD1 = 0.619
TA = 0.061
TB = 0.303
TL = 6.0

# 2. DEFINE SPECTRUM FUNCTION (TBDY 2018 Eq. 2.2)
def get_Sae(T):
    if T < TA:
        # Ascending (Linear)
        return (0.4 + 0.6 * (T / TA)) * SDS
    elif T <= TB:
        # Plateau (Constant)
        return SDS
    elif T <= TL:
        # Descending (Hyperbolic)
        return SD1 / T
    else:
        # Long Period
        return SD1 * TL / (T**2)

# 3. GENERATE CURVE DATA
T_vals = np.linspace(0, 2.0, 500) # Plot up to 2.0 seconds
Sae_vals = [get_Sae(t) for t in T_vals]

# 4. MODEL DATA (Balsa V8)
T_model = 0.038
Sae_model = get_Sae(T_model)

# 5. PLOT
plt.figure(figsize=(10, 6))

# Plot Curve
plt.plot(T_vals, Sae_vals, 'b-', linewidth=2, label='TBDY 2018 Spectrum (Bolu)')

# Highlight Regions
plt.axvline(x=TA, color='k', linestyle='--', alpha=0.5)
plt.axvline(x=TB, color='k', linestyle='--', alpha=0.5)
plt.text(TA/2, SDS*1.05, 'Ascending', ha='center', fontsize=10, color='green')
plt.text((TA+TB)/2, SDS*1.05, 'Plateau (Max)', ha='center', fontsize=10, color='red')
plt.text(TB+0.5, SDS*0.5, 'Descending', ha='center', fontsize=10, color='blue')

# Mark Model Period
plt.plot(T_model, Sae_model, 'ro', markersize=10, zorder=5, label=f'Model V8 (T={T_model}s)')
plt.annotate(f'V8: {Sae_model:.2f}g\n(Ascending)', 
             xy=(T_model, Sae_model), 
             xytext=(T_model+0.2, Sae_model-0.5),
             arrowprops=dict(facecolor='black', shrink=0.05))

# Formatting
plt.title('TBDY 2018 Design Spectrum & Model Stiffness', fontsize=14)
plt.xlabel('Period T (s)', fontsize=12)
plt.ylabel('Spectral Acceleration Sae (g)', fontsize=12)
plt.grid(True, which='both', linestyle='--', alpha=0.7)
plt.legend()
plt.xlim(0, 1.5)
plt.ylim(0, SDS*1.2)

# Save
out_path = OUTPUT_DIR / 'tbdy_spectrum_check.png'
plt.savefig(out_path, dpi=300)
print(f"Plot saved to: {out_path}")
print(f"\nCalculations:")
print(f"  T = {T_model} s")
print(f"  TA = {TA} s")
print(f"  Since T < TA -> Formula: (0.4 + 0.6 * T/TA) * SDS")
print(f"  Sae = (0.4 + 0.6 * {T_model}/{TA}) * {SDS}")
print(f"  Sae = (0.4 + {0.6 * T_model/TA:.3f}) * {2.046}")
print(f"  Sae = {0.4 + 0.6 * T_model/TA:.3f} * {2.046}")
print(f"  Sae = {Sae_model:.3f} g")
