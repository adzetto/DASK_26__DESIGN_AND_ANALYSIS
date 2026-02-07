"""
Stress Analysis and Visualization Script
- Analyzes member stresses under earthquake loading
- Creates interactive Plotly visualizations
- Identifies critical elements
"""

import os
import sys
import numpy as np
import pandas as pd
import openseespy.opensees as ops
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import time
import re

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Use paths from config
DATA_DIR = config.DATA_DIR
AT2_FILE = config.EARTHQUAKE_FILE
RESULTS_DATA_DIR = config.RESULTS_DATA_DIR
RESULTS_VIS_DIR = config.RESULTS_VIS_DIR

# Material and section properties from config
BALSA_E = config.BALSA_E
BALSA_DENSITY = config.BALSA_DENSITY
BALSA_NU = config.BALSA_NU
BALSA_G = config.BALSA_G
FRAME_SIZE = config.FRAME_SIZE
WALL_THICK = config.WALL_THICK
FRAME_A = config.FRAME_A
FRAME_I = config.FRAME_I
FRAME_c = config.FRAME_c

# Strength values
BALSA_TENSION_STRENGTH = config.BALSA_TENSION_STRENGTH
BALSA_COMPRESSION_STRENGTH = config.BALSA_COMPRESSION_STRENGTH
BALSA_SHEAR_STRENGTH = config.BALSA_SHEAR_STRENGTH

# DASK Mass configuration
MASS_FLOORS_1_60 = config.MASS_FLOORS_1_60
MASS_FLOOR_ROOF = config.MASS_FLOOR_ROOF
MASS_1_60_KG = config.MASS_1_60_KG
MASS_ROOF_KG = config.MASS_ROOF_KG
MASS_CONVERSION = config.MASS_CONVERSION_OPENSEES

# ---------------------------------------------------------------------------
# Parse AT2 file
# ---------------------------------------------------------------------------
def parse_at2(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    header_line = lines[3]
    npts_match = re.search(r'NPTS\s*=\s*(\d+)', header_line)
    dt_match = re.search(r'DT\s*=\s*([.\d]+)', header_line)
    npts = int(npts_match.group(1)) if npts_match else None
    dt = float(dt_match.group(1)) if dt_match else None
    acc_values = []
    for line in lines[4:]:
        for val in line.split():
            try:
                acc_values.append(float(val))
            except:
                continue
    return np.arange(npts) * dt, np.array(acc_values[:npts]), dt, npts

# ---------------------------------------------------------------------------
# Main Script
# ---------------------------------------------------------------------------
print("=" * 70)
print("STRESS ANALYSIS AND VISUALIZATION")
print("=" * 70)

# Load model data
print("\nLoading model data...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, "position_matrix.csv"))
conn_df = pd.read_csv(os.path.join(DATA_DIR, "connectivity_matrix.csv"))

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")

# Convert to mm
pos_df['x_mm'] = pos_df['x'] * 1000
pos_df['y_mm'] = pos_df['y'] * 1000
pos_df['z_mm'] = pos_df['z'] * 1000

# Load earthquake data
print(f"\nLoading earthquake: {AT2_FILE}")
time_arr, acc_g, dt, npts = parse_at2(AT2_FILE)
pga = np.max(np.abs(acc_g))
print(f"  PGA: {pga:.4f}g")

# ---------------------------------------------------------------------------
# Build OpenSees Model
# ---------------------------------------------------------------------------
print("\n--- BUILDING OPENSEES MODEL ---")
ops.wipe()
ops.model('basic', '-ndm', 3, '-ndf', 6)

# Coordinate transformations
ops.geomTransf('Linear', 1, 0, 1, 0)   # Vertical elements
ops.geomTransf('Linear', 2, 0, 0, 1)   # Y-direction elements
ops.geomTransf('Linear', 3, 0, 1, 0)   # X-direction elements

# Create nodes
node_coords = {}
for idx, row in pos_df.iterrows():
    nid = int(row['node_id']) + 1
    x, y, z = float(row['x_mm']), float(row['y_mm']), float(row['z_mm'])
    node_coords[int(row['node_id'])] = (x, y, z)
    ops.node(nid, x, y, z)

# Fix base nodes
base_z = pos_df['z_mm'].min()
for idx, row in pos_df.iterrows():
    if abs(row['z_mm'] - base_z) < 1.0:
        nid = int(row['node_id']) + 1
        ops.fix(nid, 1, 1, 1, 1, 1, 1)

# Create material for shells
ops.nDMaterial('ElasticIsotropic', 100, BALSA_E, BALSA_NU)
ops.section('PlateFiber', 200, 100, WALL_THICK)

# Helper functions
def find_node_id(tx, ty, tz):
    for nid, (nx, ny, nz) in node_coords.items():
        if abs(nx-tx) < 1.0 and abs(ny-ty) < 1.0 and abs(nz-tz) < 1.0:
            return nid
    return None

# Store element data for stress analysis
element_data = []
created_panels = set()
frame_count = 0
shell_count = 0

print("Creating elements...")

for idx, row in conn_df.iterrows():
    etype = row['element_type']

    if 'node_id_i' in row:
        n1, n2 = int(row['node_id_i']), int(row['node_id_j'])
    else:
        n1, n2 = int(row['node_i']), int(row['node_j'])

    elem_id = int(row['element_id']) + 1
    p1 = node_coords[n1]
    p2 = node_coords[n2]

    # Element length
    L = np.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2 + (p2[2]-p1[2])**2)

    # Determine transformation
    dz = abs(p2[2] - p1[2])
    dx = abs(p2[0] - p1[0])
    dy = abs(p2[1] - p1[1])

    if dz > max(dx, dy):
        transf_tag = 1
        orientation = 'vertical'
    elif dx > dy:
        transf_tag = 3
        orientation = 'x-direction'
    else:
        transf_tag = 2
        orientation = 'y-direction'

    if etype == 'core_wall':
        # Try to create shell, fall back to frame
        if p1[2] > p2[2]:
            p1, p2 = p2, p1
            n1, n2 = n2, n1

        x1, y1, z1 = p1
        x2, y2, z2 = p2

        n3, n4 = None, None
        if abs(y1 - y2) < 1.0:
            n3 = find_node_id(x2, y1, z1)
            n4 = find_node_id(x1, y2, z2)
        elif abs(x1 - x2) < 1.0:
            n3 = find_node_id(x1, y2, z1)
            n4 = find_node_id(x2, y1, z2)

        if n3 is not None and n4 is not None:
            panel_key = tuple(sorted([n1, n2, n3, n4]))
            if panel_key not in created_panels:
                try:
                    ops.element('ShellMITC4', elem_id, n1+1, n3+1, n2+1, n4+1, 200)
                    created_panels.add(panel_key)
                    shell_count += 1
                    element_data.append({
                        'elem_id': elem_id, 'type': 'shell', 'n1': n1, 'n2': n2,
                        'x1': p1[0], 'y1': p1[1], 'z1': p1[2],
                        'x2': p2[0], 'y2': p2[1], 'z2': p2[2],
                        'length': L, 'orientation': 'wall', 'element_type': etype
                    })
                    continue
                except:
                    pass

        # Fall back to frame
        try:
            ops.element('elasticBeamColumn', elem_id, n1+1, n2+1,
                       FRAME_A, BALSA_E, BALSA_G, FRAME_I*0.1406*36/108, FRAME_I, FRAME_I,
                       transf_tag)
            frame_count += 1
            element_data.append({
                'elem_id': elem_id, 'type': 'frame', 'n1': n1, 'n2': n2,
                'x1': p1[0], 'y1': p1[1], 'z1': p1[2],
                'x2': p2[0], 'y2': p2[1], 'z2': p2[2],
                'length': L, 'orientation': orientation, 'element_type': etype
            })
        except:
            pass
    else:
        # Regular frame element
        try:
            ops.element('elasticBeamColumn', elem_id, n1+1, n2+1,
                       FRAME_A, BALSA_E, BALSA_G, FRAME_I*0.1406*36/108, FRAME_I, FRAME_I,
                       transf_tag)
            frame_count += 1
            element_data.append({
                'elem_id': elem_id, 'type': 'frame', 'n1': n1, 'n2': n2,
                'x1': p1[0], 'y1': p1[1], 'z1': p1[2],
                'x2': p2[0], 'y2': p2[1], 'z2': p2[2],
                'length': L, 'orientation': orientation, 'element_type': etype
            })
        except:
            pass

print(f"Created {frame_count} frames, {shell_count} shells")
elem_df = pd.DataFrame(element_data)

# ---------------------------------------------------------------------------
# Add Masses
# ---------------------------------------------------------------------------
print("\n--- ADDING MASSES ---")
floor_nodes = {}
for idx, row in pos_df.iterrows():
    floor = int(row['floor'])
    if floor not in floor_nodes:
        floor_nodes[floor] = []
    floor_nodes[floor].append(int(row['node_id']))

for floor in MASS_FLOORS_1_60:
    if floor in floor_nodes:
        n_nodes_floor = len(floor_nodes[floor])
        mass_per_node = (MASS_1_60_KG / n_nodes_floor) * MASS_CONVERSION
        for node_id in floor_nodes[floor]:
            ops.mass(node_id + 1, mass_per_node, mass_per_node, 0.0, 0.0, 0.0, 0.0)

if MASS_FLOOR_ROOF in floor_nodes:
    n_nodes_floor = len(floor_nodes[MASS_FLOOR_ROOF])
    mass_per_node = (MASS_ROOF_KG / n_nodes_floor) * MASS_CONVERSION
    for node_id in floor_nodes[MASS_FLOOR_ROOF]:
        ops.mass(node_id + 1, mass_per_node, mass_per_node, 0.0, 0.0, 0.0, 0.0)

# ---------------------------------------------------------------------------
# Static Analysis under Gravity + Lateral Load
# ---------------------------------------------------------------------------
print("\n--- STATIC ANALYSIS (Gravity + Lateral) ---")

# Create load pattern for lateral load (simplified earthquake equivalent)
ops.timeSeries('Linear', 1)
ops.pattern('Plain', 1, 1)

# Apply lateral loads at mass floors (equivalent static method)
# F = 0.4 * W * g (simplified seismic coefficient)
seismic_coef = 0.4 * 9810  # mm/s² (0.4g)

for floor in MASS_FLOORS_1_60 + [MASS_FLOOR_ROOF]:
    if floor in floor_nodes:
        mass_kg = MASS_1_60_KG if floor != MASS_FLOOR_ROOF else MASS_ROOF_KG
        force_per_node = (mass_kg * seismic_coef) / len(floor_nodes[floor]) * MASS_CONVERSION
        for node_id in floor_nodes[floor]:
            # Apply force in Y direction (weaker direction)
            ops.load(node_id + 1, 0.0, force_per_node, 0.0, 0.0, 0.0, 0.0)

# Analysis
ops.system('BandGeneral')
ops.numberer('RCM')
ops.constraints('Plain')
ops.integrator('LoadControl', 1.0)
ops.algorithm('Newton')
ops.analysis('Static')

print("  Running static analysis...")
ops.analyze(1)
print("  Completed")

# ---------------------------------------------------------------------------
# Extract Element Forces and Calculate Stresses
# ---------------------------------------------------------------------------
print("\n--- EXTRACTING ELEMENT FORCES ---")

stress_results = []

for elem in element_data:
    if elem['type'] != 'frame':
        continue

    elem_id = elem['elem_id']

    try:
        # Get element forces: [N1, Vy1, Vz1, T1, My1, Mz1, N2, Vy2, Vz2, T2, My2, Mz2]
        forces = ops.eleForce(elem_id)

        if len(forces) >= 12:
            # Forces at node i
            N1 = forces[0]    # Axial force (N)
            Vy1 = forces[1]   # Shear Y
            Vz1 = forces[2]   # Shear Z
            My1 = forces[4]   # Moment about Y (N-mm)
            Mz1 = forces[5]   # Moment about Z (N-mm)

            # Forces at node j
            N2 = forces[6]
            Vy2 = forces[7]
            Vz2 = forces[8]
            My2 = forces[10]
            Mz2 = forces[11]

            # Maximum forces along element
            N_max = max(abs(N1), abs(N2))
            V_max = max(abs(Vy1), abs(Vy2), abs(Vz1), abs(Vz2))
            M_max = max(abs(My1), abs(My2), abs(Mz1), abs(Mz2))

            # Calculate stresses
            # Axial stress: σ_a = N / A
            sigma_axial = N_max / FRAME_A  # MPa (N/mm² since N in N, A in mm²)

            # Bending stress: σ_b = M * c / I
            sigma_bending = M_max * FRAME_c / FRAME_I  # MPa

            # Shear stress: τ = V * Q / (I * t) ≈ 1.5 * V / A for rectangular section
            tau_shear = 1.5 * V_max / FRAME_A  # MPa

            # Combined stress (von Mises approximation for uniaxial + bending)
            sigma_combined = sigma_axial + sigma_bending

            # Utilization ratio (compared to allowable stress)
            if N1 < 0:  # Compression
                utilization = sigma_combined / BALSA_COMPRESSION_STRENGTH
            else:  # Tension
                utilization = sigma_combined / BALSA_TENSION_STRENGTH

            shear_utilization = tau_shear / BALSA_SHEAR_STRENGTH

            stress_results.append({
                'elem_id': elem_id,
                'n1': elem['n1'],
                'n2': elem['n2'],
                'x_mid': (elem['x1'] + elem['x2']) / 2,
                'y_mid': (elem['y1'] + elem['y2']) / 2,
                'z_mid': (elem['z1'] + elem['z2']) / 2,
                'x1': elem['x1'], 'y1': elem['y1'], 'z1': elem['z1'],
                'x2': elem['x2'], 'y2': elem['y2'], 'z2': elem['z2'],
                'length': elem['length'],
                'orientation': elem['orientation'],
                'element_type': elem['element_type'],
                'N_max': N_max,
                'V_max': V_max,
                'M_max': M_max,
                'sigma_axial': sigma_axial,
                'sigma_bending': sigma_bending,
                'sigma_combined': sigma_combined,
                'tau_shear': tau_shear,
                'utilization': utilization,
                'shear_utilization': shear_utilization
            })

    except Exception as e:
        pass

stress_df = pd.DataFrame(stress_results)
print(f"  Analyzed {len(stress_df)} frame elements")

# ---------------------------------------------------------------------------
# Identify Critical Elements
# ---------------------------------------------------------------------------
print("\n--- IDENTIFYING CRITICAL ELEMENTS ---")

# Sort by utilization ratio
stress_df_sorted = stress_df.sort_values('utilization', ascending=False)

# Top 20 critical elements
n_critical = 20
critical_elements = stress_df_sorted.head(n_critical)

print(f"\n  Top {n_critical} Critical Elements (by stress utilization):")
print(f"  {'Elem':<8} {'Type':<12} {'σ_axial':<10} {'σ_bend':<10} {'σ_comb':<10} {'Util':<8} {'Z (mm)':<10}")
print(f"  {'-'*70}")

for idx, row in critical_elements.iterrows():
    print(f"  {row['elem_id']:<8} {row['orientation']:<12} {row['sigma_axial']:<10.3f} "
          f"{row['sigma_bending']:<10.3f} {row['sigma_combined']:<10.3f} "
          f"{row['utilization']:<8.2%} {row['z_mid']:<10.0f}")

# Statistics
print(f"\n  Stress Statistics:")
print(f"    Max combined stress: {stress_df['sigma_combined'].max():.3f} MPa")
print(f"    Mean combined stress: {stress_df['sigma_combined'].mean():.3f} MPa")
print(f"    Max utilization: {stress_df['utilization'].max():.2%}")
print(f"    Elements > 50% utilization: {len(stress_df[stress_df['utilization'] > 0.5])}")
print(f"    Elements > 80% utilization: {len(stress_df[stress_df['utilization'] > 0.8])}")
print(f"    Elements > 100% (overstressed): {len(stress_df[stress_df['utilization'] > 1.0])}")

# Save results
stress_df.to_csv(os.path.join(RESULTS_DATA_DIR, "stress_results.csv"), index=False)
print(f"\n  Results saved to stress_results.csv")

# ---------------------------------------------------------------------------
# PLOTLY VISUALIZATIONS
# ---------------------------------------------------------------------------
print("\n--- CREATING VISUALIZATIONS ---")

# 1. 3D Building Stress Visualization
print("  Creating 3D stress visualization...")

# Normalize stress for color mapping
max_stress = stress_df['sigma_combined'].max()
stress_df['stress_normalized'] = stress_df['sigma_combined'] / max_stress

# Create figure
fig1 = go.Figure()

# Add all frame elements as lines colored by stress
for idx, row in stress_df.iterrows():
    # Color based on utilization
    util = row['utilization']
    if util > 1.0:
        color = 'red'
        width = 4
    elif util > 0.8:
        color = 'orange'
        width = 3
    elif util > 0.5:
        color = 'yellow'
        width = 2
    else:
        color = 'green'
        width = 1

    fig1.add_trace(go.Scatter3d(
        x=[row['x1'], row['x2']],
        y=[row['y1'], row['y2']],
        z=[row['z1'], row['z2']],
        mode='lines',
        line=dict(color=color, width=width),
        hovertemplate=(
            f"Element: {row['elem_id']}<br>"
            f"Type: {row['orientation']}<br>"
            f"σ_combined: {row['sigma_combined']:.3f} MPa<br>"
            f"Utilization: {row['utilization']:.1%}<br>"
            f"<extra></extra>"
        ),
        showlegend=False
    ))

# Add legend entries
for label, color in [('Overstressed (>100%)', 'red'), ('High (>80%)', 'orange'),
                     ('Medium (>50%)', 'yellow'), ('Low (<50%)', 'green')]:
    fig1.add_trace(go.Scatter3d(
        x=[None], y=[None], z=[None],
        mode='lines',
        line=dict(color=color, width=3),
        name=label
    ))

# Highlight critical elements with markers
fig1.add_trace(go.Scatter3d(
    x=critical_elements['x_mid'],
    y=critical_elements['y_mid'],
    z=critical_elements['z_mid'],
    mode='markers',
    marker=dict(size=8, color='red', symbol='diamond'),
    name='Critical Elements',
    hovertemplate=(
        "Element: %{customdata[0]}<br>"
        "σ_combined: %{customdata[1]:.3f} MPa<br>"
        "Utilization: %{customdata[2]:.1%}<br>"
        "<extra></extra>"
    ),
    customdata=critical_elements[['elem_id', 'sigma_combined', 'utilization']].values
))

fig1.update_layout(
    title='3D Building Stress Visualization - DASK Model',
    scene=dict(
        xaxis_title='X (mm)',
        yaxis_title='Y (mm)',
        zaxis_title='Z (mm)',
        aspectmode='data'
    ),
    legend=dict(x=0.02, y=0.98),
    width=1200,
    height=800
)

fig1.write_html(os.path.join(RESULTS_VIS_DIR, "stress_3d_view.html"))
print("    Saved: stress_3d_view.html")

# 2. Stress Distribution by Height
print("  Creating stress distribution plots...")

fig2 = make_subplots(
    rows=2, cols=2,
    subplot_titles=(
        'Combined Stress vs Height',
        'Stress Utilization Distribution',
        'Critical Elements by Floor',
        'Stress by Element Type'
    )
)

# Plot 2a: Stress vs Height
fig2.add_trace(
    go.Scatter(
        x=stress_df['sigma_combined'],
        y=stress_df['z_mid'],
        mode='markers',
        marker=dict(
            size=5,
            color=stress_df['utilization'],
            colorscale='RdYlGn_r',
            showscale=True,
            colorbar=dict(title='Utilization', x=0.45)
        ),
        hovertemplate="σ: %{x:.3f} MPa<br>Z: %{y:.0f} mm<extra></extra>"
    ),
    row=1, col=1
)

# Plot 2b: Utilization Histogram
fig2.add_trace(
    go.Histogram(
        x=stress_df['utilization'] * 100,
        nbinsx=30,
        marker_color='steelblue',
        name='Elements'
    ),
    row=1, col=2
)

# Add vertical lines for thresholds
for thresh, color, name in [(50, 'yellow', '50%'), (80, 'orange', '80%'), (100, 'red', '100%')]:
    fig2.add_vline(x=thresh, line_dash="dash", line_color=color, row=1, col=2)

# Plot 2c: Critical elements by floor (Z level)
# Bin by floor height (approximately every 6000mm)
stress_df['floor_bin'] = (stress_df['z_mid'] / 6000).astype(int)
critical_by_floor = stress_df[stress_df['utilization'] > 0.5].groupby('floor_bin').size()

fig2.add_trace(
    go.Bar(
        x=[f"Floor {i}" for i in critical_by_floor.index],
        y=critical_by_floor.values,
        marker_color='coral',
        name='High Stress Elements'
    ),
    row=2, col=1
)

# Plot 2d: Stress by orientation
stress_by_type = stress_df.groupby('orientation')['sigma_combined'].agg(['mean', 'max'])
fig2.add_trace(
    go.Bar(
        x=stress_by_type.index,
        y=stress_by_type['mean'],
        name='Mean Stress',
        marker_color='steelblue'
    ),
    row=2, col=2
)
fig2.add_trace(
    go.Bar(
        x=stress_by_type.index,
        y=stress_by_type['max'],
        name='Max Stress',
        marker_color='indianred'
    ),
    row=2, col=2
)

fig2.update_xaxes(title_text="Combined Stress (MPa)", row=1, col=1)
fig2.update_yaxes(title_text="Height Z (mm)", row=1, col=1)
fig2.update_xaxes(title_text="Utilization (%)", row=1, col=2)
fig2.update_yaxes(title_text="Number of Elements", row=1, col=2)
fig2.update_xaxes(title_text="Floor Level", row=2, col=1)
fig2.update_yaxes(title_text="Count", row=2, col=1)
fig2.update_xaxes(title_text="Element Orientation", row=2, col=2)
fig2.update_yaxes(title_text="Stress (MPa)", row=2, col=2)

fig2.update_layout(
    title='Stress Analysis Summary - DASK Building',
    height=800,
    width=1200,
    showlegend=True
)

fig2.write_html(os.path.join(RESULTS_VIS_DIR, "stress_analysis_charts.html"))
print("    Saved: stress_analysis_charts.html")

# 3. Critical Elements Detail View
print("  Creating critical elements detail view...")

fig3 = go.Figure()

# Add all elements in gray
for idx, row in stress_df.iterrows():
    fig3.add_trace(go.Scatter3d(
        x=[row['x1'], row['x2']],
        y=[row['y1'], row['y2']],
        z=[row['z1'], row['z2']],
        mode='lines',
        line=dict(color='lightgray', width=1),
        showlegend=False,
        hoverinfo='skip'
    ))

# Highlight critical elements with stress color scale
critical_50 = stress_df[stress_df['utilization'] > 0.5].copy()
critical_50['color_val'] = critical_50['utilization'].clip(upper=1.5)

for idx, row in critical_50.iterrows():
    color = f'rgb({int(255*min(row["utilization"], 1))}, {int(255*max(0, 1-row["utilization"]))}, 0)'
    fig3.add_trace(go.Scatter3d(
        x=[row['x1'], row['x2']],
        y=[row['y1'], row['y2']],
        z=[row['z1'], row['z2']],
        mode='lines',
        line=dict(color=color, width=4),
        showlegend=False,
        hovertemplate=(
            f"Element: {row['elem_id']}<br>"
            f"σ_axial: {row['sigma_axial']:.3f} MPa<br>"
            f"σ_bending: {row['sigma_bending']:.3f} MPa<br>"
            f"σ_combined: {row['sigma_combined']:.3f} MPa<br>"
            f"Utilization: {row['utilization']:.1%}<br>"
            f"<extra></extra>"
        )
    ))

fig3.update_layout(
    title='Critical Elements Highlighted (>50% Utilization)',
    scene=dict(
        xaxis_title='X (mm)',
        yaxis_title='Y (mm)',
        zaxis_title='Z (mm)',
        aspectmode='data'
    ),
    width=1200,
    height=800
)

fig3.write_html(os.path.join(RESULTS_VIS_DIR, "critical_elements_3d.html"))
print("    Saved: critical_elements_3d.html")

# 4. Force Distribution Visualization
print("  Creating force distribution visualization...")

fig4 = make_subplots(
    rows=1, cols=3,
    subplot_titles=('Axial Force Distribution', 'Shear Force Distribution', 'Moment Distribution')
)

fig4.add_trace(
    go.Histogram(x=stress_df['N_max'], nbinsx=30, marker_color='steelblue', name='Axial (N)'),
    row=1, col=1
)
fig4.add_trace(
    go.Histogram(x=stress_df['V_max'], nbinsx=30, marker_color='coral', name='Shear (N)'),
    row=1, col=2
)
fig4.add_trace(
    go.Histogram(x=stress_df['M_max'], nbinsx=30, marker_color='mediumseagreen', name='Moment (N-mm)'),
    row=1, col=3
)

fig4.update_xaxes(title_text="Axial Force (N)", row=1, col=1)
fig4.update_xaxes(title_text="Shear Force (N)", row=1, col=2)
fig4.update_xaxes(title_text="Moment (N-mm)", row=1, col=3)

fig4.update_layout(
    title='Internal Force Distributions',
    height=400,
    width=1200,
    showlegend=False
)

fig4.write_html(os.path.join(RESULTS_VIS_DIR, "force_distribution.html"))
print("    Saved: force_distribution.html")

# ---------------------------------------------------------------------------
# Summary Report
# ---------------------------------------------------------------------------
print("\n" + "=" * 70)
print("STRESS ANALYSIS SUMMARY")
print("=" * 70)

print(f"""
Model Configuration:
  - Frame section: {FRAME_SIZE}mm x {FRAME_SIZE}mm
  - Material: Balsa wood (E={BALSA_E} MPa)
  - Allowable tension: {BALSA_TENSION_STRENGTH} MPa
  - Allowable compression: {BALSA_COMPRESSION_STRENGTH} MPa

Loading:
  - Equivalent static lateral load (0.4g seismic)
  - Applied at mass floors

Results:
  - Total frame elements analyzed: {len(stress_df)}
  - Maximum combined stress: {stress_df['sigma_combined'].max():.3f} MPa
  - Maximum utilization ratio: {stress_df['utilization'].max():.2%}
  - Overstressed elements (>100%): {len(stress_df[stress_df['utilization'] > 1.0])}
  - High stress elements (>80%): {len(stress_df[stress_df['utilization'] > 0.8])}
  - Medium stress elements (>50%): {len(stress_df[stress_df['utilization'] > 0.5])}

Critical Locations:
  - Most stressed elements are at Z = {critical_elements['z_mid'].mean():.0f} mm (avg)
  - Primary failure mode: {'Compression' if stress_df.loc[stress_df['utilization'].idxmax(), 'N_max'] < 0 else 'Tension'}

Output Files:
  - stress_results.csv (detailed stress data)
  - stress_3d_view.html (interactive 3D visualization)
  - stress_analysis_charts.html (stress distribution charts)
  - critical_elements_3d.html (critical elements highlighted)
  - force_distribution.html (internal force histograms)
""")

ops.wipe()
print("\nAnalysis complete!")
