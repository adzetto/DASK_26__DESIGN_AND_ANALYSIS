#!/usr/bin/env python3
"""
Damage Assessment Analysis for DASK 2026 V9 Twin Towers
Analyzes element forces from ZTAH to assess damage potential under design earthquake
"""

import numpy as np
import os

# Material properties (scaled balsa)
E = 40800  # kN/cm² (scaled ×240 from 170 MPa)
G = 15692  # kN/cm²
fy_scaled = 9600  # kN/cm² (scaled from 400 MPa steel, ×240)

# Section properties (6mm × 6mm)
A = 0.36  # cm²
Iy = Iz = 0.0108  # cm⁴
J = 0.0216  # cm⁴
Wel = 0.0036  # cm³

# Element capacities
Py = fy_scaled * A  # Yield axial force = 3456 kN
My = fy_scaled * Wel  # Yield moment = 34.56 kN·cm

def read_element_forces(filepath):
    """Read element forces from OpenSees recorder output"""
    print(f"Reading element forces from: {filepath}")
    data = np.loadtxt(filepath)
    n_steps, n_cols = data.shape
    n_elements = n_cols // 12  # 12 forces per element (6 at each node)
    print(f"  Time steps: {n_steps}")
    print(f"  Columns: {n_cols}")
    print(f"  Elements recorded: {n_elements}")
    return data, n_elements

def calculate_stress_ratios(forces, element_length=6.0):
    """
    Calculate demand-to-capacity ratios (DCR) for each element
    forces: array of shape (n_steps, 12) for one element
    Returns: max DCR over all time steps
    """
    # Extract forces at node i and node j
    # Format: Fxi, Fyi, Fzi, Mxi, Myi, Mzi, Fxj, Fyj, Fzj, Mxj, Myj, Mzj
    Fxi = forces[:, 0]
    Myi = forces[:, 4]
    Mzi = forces[:, 5]
    Fxj = forces[:, 6]
    Myj = forces[:, 10]
    Mzj = forces[:, 11]

    # Axial force (average of two nodes, usually same for elastic beam)
    P = np.abs((Fxi + Fxj) / 2)

    # Bending moments (max of two ends)
    My_max = np.maximum(np.abs(Myi), np.abs(Myj))
    Mz_max = np.maximum(np.abs(Mzi), np.abs(Mzj))
    M_max = np.sqrt(My_max**2 + Mz_max**2)

    # Interaction equation (simplified): P/Py + M/My <= 1.0
    DCR_axial = P / Py
    DCR_moment = M_max / My
    DCR_interaction = DCR_axial + DCR_moment

    # Return max DCR over all time steps
    max_DCR = np.max(DCR_interaction)
    max_P = np.max(P)
    max_M = np.max(M_max)

    return {
        'DCR_max': max_DCR,
        'P_max': max_P,
        'M_max': max_M,
        'P_ratio': max_P / Py,
        'M_ratio': max_M / My
    }

def classify_damage_state(DCR):
    """
    Classify damage state based on DCR
    Based on HAZUS/FEMA P-58 fragility concepts
    """
    if DCR < 0.25:
        return "None", "No damage"
    elif DCR < 0.50:
        return "DS1", "Slight (cosmetic)"
    elif DCR < 0.75:
        return "DS2", "Moderate (minor repair)"
    elif DCR < 1.00:
        return "DS3", "Extensive (major repair)"
    else:
        return "DS4", "Complete (replacement)"

def main():
    # KYH-1 (design earthquake) results
    base_path = "analysis/torsional_irregularity/results/th_KYH1/element_forces"
    forces_file = os.path.join(base_path, "sample_forces.txt")

    if not os.path.exists(forces_file):
        print(f"Error: {forces_file} not found")
        return

    # Read forces
    data, n_elements = read_element_forces(forces_file)

    # Analyze each element
    print(f"\n{'='*80}")
    print("DAMAGE ASSESSMENT SUMMARY (KYH-1, Design Earthquake)")
    print(f"{'='*80}")

    critical_elements = []

    for i in range(n_elements):
        # Extract forces for element i (12 columns)
        elem_forces = data[:, i*12:(i+1)*12]

        # Calculate DCR
        result = calculate_stress_ratios(elem_forces)
        dcr = result['DCR_max']

        # Classify damage
        ds_code, ds_desc = classify_damage_state(dcr)

        if dcr > 0.0:  # Report all elements with any stress
            critical_elements.append({
                'element': i+1,
                'DCR': dcr,
                'P_max': result['P_max'],
                'M_max': result['M_max'],
                'damage_state': ds_code,
                'description': ds_desc
            })

    # Sort by DCR descending
    critical_elements.sort(key=lambda x: x['DCR'], reverse=True)

    # Print top 10 critical elements
    print(f"\nTop 10 Critical Elements:")
    print(f"{'Element':<10} {'DCR':<10} {'P_max (kN)':<15} {'M_max (kN·cm)':<15} {'Damage State':<15} {'Description':<25}")
    print(f"{'-'*100}")

    for elem in critical_elements[:10]:
        print(f"{elem['element']:<10} {elem['DCR']:<10.3f} {elem['P_max']:<15.2f} "
              f"{elem['M_max']:<15.2f} {elem['damage_state']:<15} {elem['description']:<25}")

    # Statistics
    all_dcr = [elem['DCR'] for elem in critical_elements] if critical_elements else [0]

    print(f"\n{'='*80}")
    print("STATISTICS:")
    print(f"  Max DCR: {max(all_dcr):.3f}")
    print(f"  Mean DCR (critical elements): {np.mean(all_dcr):.3f}")
    print(f"  Elements with DCR > 0.5: {len(critical_elements)}")
    print(f"  Total elements analyzed: {n_elements}")
    print(f"{'='*80}")

    # Damage state distribution
    ds_count = {}
    for elem in critical_elements:
        ds = elem['damage_state']
        ds_count[ds] = ds_count.get(ds, 0) + 1

    if ds_count:
        print("\nDamage State Distribution (among critical elements):")
        for ds in ['DS1', 'DS2', 'DS3', 'DS4']:
            count = ds_count.get(ds, 0)
            if count > 0:
                print(f"  {ds}: {count} elements")

    # Save results
    output_file = os.path.join(base_path, "damage_assessment_summary.txt")
    with open(output_file, 'w') as f:
        f.write("DAMAGE ASSESSMENT SUMMARY - KYH-1 (Design Earthquake)\n")
        f.write("="*80 + "\n\n")
        f.write(f"Max DCR: {max(all_dcr):.3f}\n")
        f.write(f"Critical elements (DCR > 0.5): {len(critical_elements)}\n\n")

        f.write("Top 20 Critical Elements:\n")
        f.write(f"{'Element':<10} {'DCR':<10} {'P_max (kN)':<15} {'M_max (kN·cm)':<15} {'Damage State':<15}\n")
        f.write("-"*80 + "\n")
        for elem in critical_elements[:20]:
            f.write(f"{elem['element']:<10} {elem['DCR']:<10.3f} {elem['P_max']:<15.2f} "
                   f"{elem['M_max']:<15.2f} {elem['damage_state']:<15}\n")

    print(f"\nResults saved to: {output_file}")

if __name__ == "__main__":
    main()
