"""
Export data for LaTeX/TikZ figures
DASK 2025 Project Proposal
"""

import os
import csv
import numpy as np
import pandas as pd

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")
TEX_DATA_DIR = os.path.join(BASE_DIR, "tex", "data")

os.makedirs(TEX_DATA_DIR, exist_ok=True)

# ==============================================================================
# 1. AFAD DD-2 DESIGN SPECTRUM DATA
# ==============================================================================

def export_spectrum_data():
    """Export TBDY 2018 design spectrum for TikZ pgfplots"""

    # AFAD DD-2 parameters for Afyon Dinar (from analysis)
    SS = 0.877  # Short period spectral acceleration
    S1 = 0.243  # 1-second spectral acceleration
    FS = 1.149  # Site coefficient for short period
    F1 = 2.114  # Site coefficient for 1-second

    SDS = SS * FS  # Design spectral acceleration at short period
    SD1 = S1 * F1  # Design spectral acceleration at 1-second

    TA = 0.2 * SD1 / SDS  # Period at start of constant acceleration
    TB = SD1 / SDS        # Period at end of constant acceleration
    TL = 6.0              # Long period transition

    print(f"Spectrum Parameters:")
    print(f"  SDS = {SDS:.3f}g, SD1 = {SD1:.3f}g")
    print(f"  TA = {TA:.3f}s, TB = {TB:.3f}s, TL = {TL:.1f}s")

    # Generate spectrum points
    periods = []
    accelerations = []

    # Ascending region (0 to TA)
    for T in np.linspace(0, TA, 20):
        Sae = (0.4 + 0.6 * T / TA) * SDS if TA > 0 else SDS
        periods.append(T)
        accelerations.append(Sae)

    # Constant region (TA to TB)
    for T in np.linspace(TA, TB, 30):
        Sae = SDS
        periods.append(T)
        accelerations.append(Sae)

    # Descending region (TB to TL)
    for T in np.linspace(TB, TL, 50):
        Sae = SD1 / T
        periods.append(T)
        accelerations.append(Sae)

    # Long period region (TL to 10s)
    for T in np.linspace(TL, 10, 20):
        Sae = SD1 * TL / (T * T)
        periods.append(T)
        accelerations.append(Sae)

    # Write TSV file
    output_path = os.path.join(TEX_DATA_DIR, "afad_spectrum_dd2.tsv")
    with open(output_path, 'w') as f:
        f.write("T\tSae\n")
        for T, Sae in zip(periods, accelerations):
            f.write(f"{T:.4f}\t{Sae:.4f}\n")

    print(f"  Exported: {output_path}")

    # Also export key points for annotation
    key_points_path = os.path.join(TEX_DATA_DIR, "spectrum_key_points.tsv")
    with open(key_points_path, 'w') as f:
        f.write("name\tT\tSae\n")
        f.write(f"T1\t0.0479\t{(0.4 + 0.6 * 0.0479 / TA) * SDS:.4f}\n")  # Building period
        f.write(f"TA\t{TA:.4f}\t{SDS:.4f}\n")
        f.write(f"TB\t{TB:.4f}\t{SDS:.4f}\n")
        f.write(f"TL\t{TL:.4f}\t{SD1 * TL / (TL * TL):.4f}\n")

    print(f"  Exported: {key_points_path}")

    return SDS, SD1, TA, TB

# ==============================================================================
# 2. STRUCTURAL GEOMETRY DATA (Single Tower)
# ==============================================================================

def export_structure_data():
    """Export structural geometry for TikZ drawing"""

    # Load position and connectivity data
    pos_file = os.path.join(DATA_DIR, "twin_position_matrix_v9.csv")
    conn_file = os.path.join(DATA_DIR, "twin_connectivity_matrix_v9.csv")

    nodes_df = pd.read_csv(pos_file)
    elements_df = pd.read_csv(conn_file)

    # Filter for Tower 1 only (tower == '1' as string)
    tower1_nodes = nodes_df[nodes_df['tower'].astype(str) == '1'].copy()

    # Get unique floors for Tower 1
    floors = sorted(tower1_nodes['floor'].unique())
    print(f"Tower 1: {len(tower1_nodes)} nodes, {len(floors)} floors")

    # Export nodes for Tower 1 (XZ view - front elevation)
    # We'll use x and z coordinates, averaging y for each x position
    nodes_xz_path = os.path.join(TEX_DATA_DIR, "tower1_nodes_xz.tsv")

    # Get unique x positions
    x_positions = sorted(tower1_nodes['x'].unique())
    z_positions = sorted(tower1_nodes['z'].unique())

    with open(nodes_xz_path, 'w') as f:
        f.write("node_id\tx\tz\tfloor\n")
        for _, row in tower1_nodes.iterrows():
            # Only include nodes at y=0 or y=16 (outer edges)
            if row['y'] in [0.0, 16.0]:
                f.write(f"{int(row['node_id'])}\t{row['x']:.1f}\t{row['z']:.1f}\t{int(row['floor'])}\n")

    print(f"  Exported: {nodes_xz_path}")

    # Export elements for Tower 1
    # Filter elements belonging to tower1
    tower1_node_ids = set(tower1_nodes['node_id'].values)

    # Create node lookup
    node_lookup = {int(row['node_id']): row for _, row in nodes_df.iterrows()}

    # Categorize elements
    columns = []
    beams = []
    braces = []

    for _, elem in elements_df.iterrows():
        ni = int(elem['node_i'])
        nj = int(elem['node_j'])

        # Check if both nodes are in tower 1
        if ni not in tower1_node_ids or nj not in tower1_node_ids:
            continue

        node_i = node_lookup[ni]
        node_j = node_lookup[nj]

        elem_type = elem['element_type']

        # For XZ view, we need elements in the XZ plane (same y or averaged)
        # Filter for y=0 or y=16 (front and back faces)
        yi, yj = node_i['y'], node_j['y']

        if elem_type == 'column':
            # Columns are vertical - include all
            columns.append({
                'x1': node_i['x'], 'z1': node_i['z'],
                'x2': node_j['x'], 'z2': node_j['z'],
                'floor': min(node_i['floor'], node_j['floor'])
            })
        elif elem_type in ['beam_x']:
            # X-direction beams - include if at front face (y=0)
            if yi == 0 and yj == 0:
                beams.append({
                    'x1': node_i['x'], 'z1': node_i['z'],
                    'x2': node_j['x'], 'z2': node_j['z'],
                    'floor': node_i['floor']
                })
        elif elem_type in ['brace_xz', 'shear_wall_xz']:
            # XZ braces - include if at front face
            if yi == 0 and yj == 0:
                braces.append({
                    'x1': node_i['x'], 'z1': node_i['z'],
                    'x2': node_j['x'], 'z2': node_j['z'],
                    'type': elem_type,
                    'floor': min(node_i['floor'], node_j['floor'])
                })

    # Export columns
    columns_path = os.path.join(TEX_DATA_DIR, "tower1_columns.tsv")
    with open(columns_path, 'w') as f:
        f.write("x1\tz1\tx2\tz2\tfloor\n")
        for col in columns:
            f.write(f"{col['x1']:.1f}\t{col['z1']:.1f}\t{col['x2']:.1f}\t{col['z2']:.1f}\t{col['floor']}\n")
    print(f"  Exported: {columns_path} ({len(columns)} columns)")

    # Export beams
    beams_path = os.path.join(TEX_DATA_DIR, "tower1_beams.tsv")
    with open(beams_path, 'w') as f:
        f.write("x1\tz1\tx2\tz2\tfloor\n")
        for beam in beams:
            f.write(f"{beam['x1']:.1f}\t{beam['z1']:.1f}\t{beam['x2']:.1f}\t{beam['z2']:.1f}\t{beam['floor']}\n")
    print(f"  Exported: {beams_path} ({len(beams)} beams)")

    # Export braces
    braces_path = os.path.join(TEX_DATA_DIR, "tower1_braces.tsv")
    with open(braces_path, 'w') as f:
        f.write("x1\tz1\tx2\tz2\ttype\tfloor\n")
        for brace in braces:
            f.write(f"{brace['x1']:.1f}\t{brace['z1']:.1f}\t{brace['x2']:.1f}\t{brace['z2']:.1f}\t{brace['type']}\t{brace['floor']}\n")
    print(f"  Exported: {braces_path} ({len(braces)} braces)")

    return len(columns), len(beams), len(braces)

# ==============================================================================
# 3. MODAL ANALYSIS RESULTS
# ==============================================================================

def export_modal_data():
    """Export modal analysis results"""

    # Modal results from V9 analysis
    modal_data = [
        {'mode': 1, 'period': 0.0479, 'frequency': 20.88, 'direction': 'X-Translation'},
        {'mode': 2, 'period': 0.0478, 'frequency': 20.92, 'direction': 'Y-Translation'},
        {'mode': 3, 'period': 0.0478, 'frequency': 20.92, 'direction': 'Torsion'},
        {'mode': 4, 'period': 0.0162, 'frequency': 61.73, 'direction': 'X-2nd mode'},
        {'mode': 5, 'period': 0.0161, 'frequency': 62.11, 'direction': 'Y-2nd mode'},
    ]

    modal_path = os.path.join(TEX_DATA_DIR, "modal_results.tsv")
    with open(modal_path, 'w') as f:
        f.write("mode\tperiod\tfrequency\tdirection\n")
        for m in modal_data:
            f.write(f"{m['mode']}\t{m['period']:.4f}\t{m['frequency']:.2f}\t{m['direction']}\n")

    print(f"  Exported: {modal_path}")

# ==============================================================================
# 4. IRREGULARITY CHECK RESULTS
# ==============================================================================

def export_irregularity_data():
    """Export torsional irregularity check results"""

    # From V9 analysis
    torsion_data = [
        {'floor': 1, 'delta_max': 0.0023, 'delta_avg': 0.0021, 'eta_bi': 1.112},
        {'floor': 5, 'delta_max': 0.0232, 'delta_avg': 0.0231, 'eta_bi': 1.003},
        {'floor': 10, 'delta_max': 0.0639, 'delta_avg': 0.0635, 'eta_bi': 1.005},
        {'floor': 15, 'delta_max': 0.1076, 'delta_avg': 0.1072, 'eta_bi': 1.002},
        {'floor': 20, 'delta_max': 0.1420, 'delta_avg': 0.1419, 'eta_bi': 1.000},
        {'floor': 25, 'delta_max': 0.1670, 'delta_avg': 0.1668, 'eta_bi': 1.001},
    ]

    torsion_path = os.path.join(TEX_DATA_DIR, "torsion_check.tsv")
    with open(torsion_path, 'w') as f:
        f.write("floor\tdelta_max\tdelta_avg\teta_bi\n")
        for t in torsion_data:
            f.write(f"{t['floor']}\t{t['delta_max']:.4f}\t{t['delta_avg']:.4f}\t{t['eta_bi']:.3f}\n")

    print(f"  Exported: {torsion_path}")

# ==============================================================================
# 5. DRIFT RESULTS
# ==============================================================================

def export_drift_data():
    """Export interstory drift results"""

    drift_data = [
        {'floor': 5, 'drift_ratio': 0.000318},
        {'floor': 10, 'drift_ratio': 0.000589},
        {'floor': 15, 'drift_ratio': 0.000591},
        {'floor': 20, 'drift_ratio': 0.000596},
        {'floor': 25, 'drift_ratio': 0.001168},
    ]

    drift_path = os.path.join(TEX_DATA_DIR, "drift_results.tsv")
    with open(drift_path, 'w') as f:
        f.write("floor\tdrift_ratio\n")
        for d in drift_data:
            f.write(f"{d['floor']}\t{d['drift_ratio']:.6f}\n")

    print(f"  Exported: {drift_path}")

# ==============================================================================
# MAIN
# ==============================================================================

if __name__ == "__main__":
    print("="*60)
    print("DASK V9 - LaTeX Data Export")
    print("="*60)

    print("\n[1] Exporting AFAD DD-2 spectrum data...")
    export_spectrum_data()

    print("\n[2] Exporting structural geometry...")
    export_structure_data()

    print("\n[3] Exporting modal analysis results...")
    export_modal_data()

    print("\n[4] Exporting irregularity check results...")
    export_irregularity_data()

    print("\n[5] Exporting drift results...")
    export_drift_data()

    print("\n" + "="*60)
    print("Export complete! Data files in: tex/data/")
    print("="*60)
