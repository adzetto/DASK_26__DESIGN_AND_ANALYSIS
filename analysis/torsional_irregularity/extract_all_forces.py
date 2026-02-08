#!/usr/bin/env python3
"""
Extract element forces from all three ground motions (KYH-1, KYH-2, KYH-3)
"""

import numpy as np
import os

# Material properties (scaled balsa)
E = 40800  # kN/cm² (scaled ×240)
fy_scaled = 9600  # kN/cm²

# Section properties (6mm × 6mm)
A = 0.36  # cm²
Wel = 0.0036  # cm³

# Capacities
Py = fy_scaled * A  # 3456 kN
My = fy_scaled * Wel  # 34.56 kN·cm

def analyze_ground_motion(gm_name, forces_file):
    """Analyze element forces for one ground motion"""
    print(f"\n{'='*60}")
    print(f"Analyzing {gm_name}")
    print(f"{'='*60}")

    if not os.path.exists(forces_file):
        print(f"File not found: {forces_file}")
        return None

    # Read data
    data = np.loadtxt(forces_file)
    n_steps, n_cols = data.shape
    n_elements = n_cols // 12

    print(f"  Elements: {n_elements}, Time steps: {n_steps}")

    # Analyze each element
    results = []
    for i in range(n_elements):
        elem_forces = data[:, i*12:(i+1)*12]

        # Extract forces
        Fxi = elem_forces[:, 0]
        Myi = elem_forces[:, 4]
        Mzi = elem_forces[:, 5]
        Fxj = elem_forces[:, 6]
        Myj = elem_forces[:, 10]
        Mzj = elem_forces[:, 11]

        # Axial and moment
        P = np.abs((Fxi + Fxj) / 2)
        My_max = np.maximum(np.abs(Myi), np.abs(Myj))
        Mz_max = np.maximum(np.abs(Mzi), np.abs(Mzj))
        M_max = np.sqrt(My_max**2 + Mz_max**2)

        # DCR
        DCR = P / Py + M_max / My

        max_P = np.max(P)
        max_M = np.max(M_max)
        max_DCR = np.max(DCR)

        results.append({
            'element': i+1,
            'P_max': max_P,
            'M_max': max_M,
            'DCR_max': max_DCR
        })

    # Sort by DCR
    results.sort(key=lambda x: x['DCR_max'], reverse=True)

    # Statistics
    all_dcr = [r['DCR_max'] for r in results]
    all_p = [r['P_max'] for r in results]
    all_m = [r['M_max'] for r in results]

    print(f"\n  Statistics:")
    print(f"    Max DCR: {max(all_dcr):.4f}")
    print(f"    Max P: {max(all_p):.2f} kN")
    print(f"    Max M: {max(all_m):.2f} kN·cm")
    print(f"    Mean DCR: {np.mean(all_dcr):.4f}")

    # Top 5
    print(f"\n  Top 5 Critical Elements:")
    print(f"    {'Elem':<8} {'P (kN)':<12} {'M (kN·cm)':<12} {'DCR':<10}")
    for r in results[:5]:
        print(f"    {r['element']:<8} {r['P_max']:<12.2f} {r['M_max']:<12.2f} {r['DCR_max']:<10.4f}")

    return {
        'gm_name': gm_name,
        'max_DCR': max(all_dcr),
        'max_P': max(all_p),
        'max_M': max(all_m),
        'mean_DCR': np.mean(all_dcr),
        'results': results
    }

def main():
    base_path = "analysis/torsional_irregularity/results"

    gms = [
        ('KYH-1', os.path.join(base_path, 'th_KYH1/element_forces/sample_forces.txt')),
        ('KYH-2', os.path.join(base_path, 'th_KYH2/element_forces/sample_forces.txt')),
        ('KYH-3', os.path.join(base_path, 'th_KYH3/element_forces/sample_forces.txt')),
    ]

    all_results = []
    for gm_name, filepath in gms:
        result = analyze_ground_motion(gm_name, filepath)
        if result:
            all_results.append(result)

    # Summary table
    print(f"\n{'='*60}")
    print("SUMMARY - ALL GROUND MOTIONS")
    print(f"{'='*60}")
    print(f"{'GM':<10} {'Max DCR':<12} {'Max P (kN)':<15} {'Max M (kN·cm)':<15}")
    print(f"{'-'*60}")
    for r in all_results:
        print(f"{r['gm_name']:<10} {r['max_DCR']:<12.4f} {r['max_P']:<15.2f} {r['max_M']:<15.2f}")

    # Save for plotting
    output_file = os.path.join(base_path, "force_summary_all.txt")
    with open(output_file, 'w') as f:
        f.write("# GM_name  max_DCR  max_P(kN)  max_M(kN·cm)  mean_DCR\n")
        for r in all_results:
            f.write(f"{r['gm_name']:<10} {r['max_DCR']:.6f} {r['max_P']:.4f} {r['max_M']:.4f} {r['mean_DCR']:.6f}\n")

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
