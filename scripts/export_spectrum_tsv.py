#!/usr/bin/env python3
"""
Export TBDY2018 Spectrum Data to TSV for pgfplots
"""

import numpy as np
import os

# =====================================================
# TBDY2018 SPECTRUM PARAMETERS
# =====================================================
TA = 0.0729  # seconds
TB = 0.3646  # seconds
SDS = 1.556  # g

def sae_tbdy2018(T, TA, TB, SDS):
    """TBDY2018 Elastic Design Spectrum"""
    if T < TA:
        return (0.4 + 0.6 * T / TA) * SDS
    elif T <= TB:
        return SDS
    else:
        return SDS * TB / T

# =====================================================
# GENERATE AND EXPORT DATA
# =====================================================
print("="*60)
print("EXPORTING TBDY2018 SPECTRUM TO TSV")
print("="*60)

# Generate data points
T_values = np.concatenate([
    np.linspace(0.001, TA, 50),      # Ascending region (dense)
    np.linspace(TA, TB, 30),          # Plateau region
    np.linspace(TB, 1.0, 50)          # Descending region
])
T_values = np.unique(T_values)  # Remove duplicates
T_values = np.sort(T_values)

Sae_values = [sae_tbdy2018(T, TA, TB, SDS) for T in T_values]

# Export to TSV
output_path = "/mnt/c/Users/lenovo/Desktop/DASK_NEW/results/data/tbdy2018_spectrum.tsv"
os.makedirs(os.path.dirname(output_path), exist_ok=True)

with open(output_path, 'w') as f:
    f.write("T\tSae\n")
    for T, Sae in zip(T_values, Sae_values):
        f.write(f"{T:.6f}\t{Sae:.6f}\n")

print(f"\nData exported to: {output_path}")
print(f"Total points: {len(T_values)}")

# Also create a CSV version
csv_path = output_path.replace('.tsv', '.csv')
with open(csv_path, 'w') as f:
    f.write("T,Sae\n")
    for T, Sae in zip(T_values, Sae_values):
        f.write(f"{T:.6f},{Sae:.6f}\n")
print(f"CSV version: {csv_path}")

# Summary
print("\n" + "="*60)
print("SPECTRUM PARAMETERS")
print("="*60)
print(f"TA = {TA:.4f} s")
print(f"TB = {TB:.4f} s")
print(f"SDS = {SDS:.3f} g")
print(f"\nRegions:")
print(f"  Ascending:  T < {TA:.4f}s  -> Sae = (0.4 + 0.6*T/TA) * SDS")
print(f"  Plateau:    {TA:.4f}s <= T <= {TB:.4f}s  -> Sae = SDS = {SDS:.3f}g")
print(f"  Descending: T > {TB:.4f}s  -> Sae = SDS * TB / T")

# Current model info
T1 = 0.0608
Sae_T1 = sae_tbdy2018(T1, TA, TB, SDS)
print(f"\nCurrent Model:")
print(f"  T1 = {T1:.4f} s")
print(f"  Sae(T1) = {Sae_T1:.3f} g")
print(f"  Region: {'ASCENDING' if T1 < TA else 'PLATEAU' if T1 <= TB else 'DESCENDING'}")
print("="*60)
