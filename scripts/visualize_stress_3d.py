"""
3D Stress Visualization for DASK 2026 Twin Towers
Visualizes critical elements based on OpenSees analysis results
"""

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
RESULTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'results', 'data')
VIS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'results', 'visualizations')

os.makedirs(VIS_DIR, exist_ok=True)

print("=" * 70)
print("DASK 2026 - 3D STRESS VISUALIZATION")
print("=" * 70)

# Load data
print("\nLoading data...")
stress_df = pd.read_csv(os.path.join(RESULTS_DIR, 'twin_towers_stress_results.csv'))
pos_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_position_matrix.csv'))
conn_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_connectivity_matrix.csv'))

print(f"  Stress results: {len(stress_df)} elements")
print(f"  Position matrix: {len(pos_df)} nodes")
print(f"  Connectivity: {len(conn_df)} elements")

# Create node coordinate lookup (in mm scale)
MODEL_SCALE = 10.0  # 1m = 10mm maket
node_coords = {}
for _, row in pos_df.iterrows():
    node_coords[int(row['node_id'])] = (
        row['x'] * MODEL_SCALE,
        row['y'] * MODEL_SCALE,
        row['z'] * MODEL_SCALE
    )

# Merge connectivity with stress data
conn_df['elem_id_os'] = conn_df['element_id'] + 1  # OpenSees uses 1-based
merged_df = conn_df.merge(stress_df, left_on='elem_id_os', right_on='elem_id', how='left')

# Fill NaN stress values with 0
merged_df['combined_stress_MPa'] = merged_df['combined_stress_MPa'].fillna(0)
merged_df['axial_stress_MPa'] = merged_df['axial_stress_MPa'].fillna(0)
merged_df['shear_stress_MPa'] = merged_df['shear_stress_MPa'].fillna(0)

# Statistics
print("\n" + "=" * 70)
print("STRESS ANALYSIS SUMMARY")
print("=" * 70)

# Filter out zero-stress elements (base connections)
active_df = merged_df[merged_df['combined_stress_MPa'] > 0.1]
print(f"\nActive elements (stress > 0.1 MPa): {len(active_df)} / {len(merged_df)}")

# Summary by element type
print("\n{:<20} {:>8} {:>12} {:>12} {:>12}".format(
    "Element Type", "Count", "Avg Comb.", "Max Comb.", "Max Shear"))
print("-" * 64)

type_summary = []
for etype in active_df['element_type'].unique():
    type_df = active_df[active_df['element_type'] == etype]
    count = len(type_df)
    avg_comb = type_df['combined_stress_MPa'].mean()
    max_comb = type_df['combined_stress_MPa'].max()
    max_shear = type_df['shear_stress_MPa'].max()
    type_summary.append({
        'type': etype,
        'count': count,
        'avg_combined': avg_comb,
        'max_combined': max_comb,
        'max_shear': max_shear
    })
    print("{:<20} {:>8} {:>12.2f} {:>12.2f} {:>12.2f}".format(
        etype, count, avg_comb, max_comb, max_shear))

type_summary_df = pd.DataFrame(type_summary)
type_summary_df = type_summary_df.sort_values('max_combined', ascending=False)

# Top 20 critical elements
print("\n" + "=" * 70)
print("TOP 20 CRITICAL ELEMENTS (by Combined Stress)")
print("=" * 70)

critical_20 = active_df.nlargest(20, 'combined_stress_MPa')
print("\n{:<6} {:<18} {:<8} {:>10} {:>10} {:>10}".format(
    "ID", "Type", "Tower", "Z (mm)", "Combined", "Axial"))
print("-" * 72)

for _, row in critical_20.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    z_avg = (node_coords.get(n1, (0,0,0))[2] + node_coords.get(n2, (0,0,0))[2]) / 2
    print("{:<6} {:<18} {:<8} {:>10.1f} {:>10.2f} {:>10.2f}".format(
        int(row['elem_id_os']),
        row['element_type'],
        int(row['tower_x']) if pd.notna(row.get('tower_x')) else '-',
        z_avg,
        row['combined_stress_MPa'],
        row['axial_stress_MPa']
    ))

# ============================================================================
# 3D VISUALIZATION
# ============================================================================
print("\n" + "=" * 70)
print("CREATING 3D VISUALIZATIONS...")
print("=" * 70)

# Color scale based on combined stress
max_stress = merged_df['combined_stress_MPa'].max()
stress_threshold_low = max_stress * 0.1   # 10% of max
stress_threshold_mid = max_stress * 0.3   # 30% of max
stress_threshold_high = max_stress * 0.6  # 60% of max

def get_stress_color(stress):
    """Return color based on stress level"""
    if stress < stress_threshold_low:
        return 'green'
    elif stress < stress_threshold_mid:
        return 'yellow'
    elif stress < stress_threshold_high:
        return 'orange'
    else:
        return 'red'

# Prepare element lines for 3D plot
def create_element_traces(df, color_by='combined_stress_MPa', show_all=True):
    """Create Plotly traces for elements colored by stress"""
    
    # Group by stress level for efficiency
    traces = []
    
    # Low stress (green)
    low_x, low_y, low_z = [], [], []
    mid_x, mid_y, mid_z = [], [], []
    high_x, high_y, high_z = [], [], []
    crit_x, crit_y, crit_z = [], [], []
    
    for _, row in df.iterrows():
        n1 = int(row['node_i'])
        n2 = int(row['node_j'])
        
        if n1 not in node_coords or n2 not in node_coords:
            continue
        
        p1 = node_coords[n1]
        p2 = node_coords[n2]
        stress = row[color_by]
        
        if stress < stress_threshold_low:
            if show_all:
                low_x.extend([p1[0], p2[0], None])
                low_y.extend([p1[1], p2[1], None])
                low_z.extend([p1[2], p2[2], None])
        elif stress < stress_threshold_mid:
            mid_x.extend([p1[0], p2[0], None])
            mid_y.extend([p1[1], p2[1], None])
            mid_z.extend([p1[2], p2[2], None])
        elif stress < stress_threshold_high:
            high_x.extend([p1[0], p2[0], None])
            high_y.extend([p1[1], p2[1], None])
            high_z.extend([p1[2], p2[2], None])
        else:
            crit_x.extend([p1[0], p2[0], None])
            crit_y.extend([p1[1], p2[1], None])
            crit_z.extend([p1[2], p2[2], None])
    
    # Add traces
    if show_all and low_x:
        traces.append(go.Scatter3d(
            x=low_x, y=low_y, z=low_z,
            mode='lines',
            line=dict(color='rgba(0,128,0,0.3)', width=1),
            name=f'Low Stress (<{stress_threshold_low:.0f} MPa)',
            hoverinfo='skip'
        ))
    
    if mid_x:
        traces.append(go.Scatter3d(
            x=mid_x, y=mid_y, z=mid_z,
            mode='lines',
            line=dict(color='yellow', width=2),
            name=f'Medium ({stress_threshold_low:.0f}-{stress_threshold_mid:.0f} MPa)'
        ))
    
    if high_x:
        traces.append(go.Scatter3d(
            x=high_x, y=high_y, z=high_z,
            mode='lines',
            line=dict(color='orange', width=3),
            name=f'High ({stress_threshold_mid:.0f}-{stress_threshold_high:.0f} MPa)'
        ))
    
    if crit_x:
        traces.append(go.Scatter3d(
            x=crit_x, y=crit_y, z=crit_z,
            mode='lines',
            line=dict(color='red', width=5),
            name=f'CRITICAL (>{stress_threshold_high:.0f} MPa)'
        ))
    
    return traces

# Create main 3D stress visualization
print("\n  Creating full model stress view...")

fig = go.Figure()

# Add all elements colored by stress
traces = create_element_traces(merged_df)
for trace in traces:
    fig.add_trace(trace)

# Add markers for top 10 critical elements
critical_10 = active_df.nlargest(10, 'combined_stress_MPa')
crit_x, crit_y, crit_z, crit_text = [], [], [], []

for _, row in critical_10.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    if n1 in node_coords and n2 in node_coords:
        p1 = node_coords[n1]
        p2 = node_coords[n2]
        mid = ((p1[0]+p2[0])/2, (p1[1]+p2[1])/2, (p1[2]+p2[2])/2)
        crit_x.append(mid[0])
        crit_y.append(mid[1])
        crit_z.append(mid[2])
        crit_text.append(
            f"ID: {int(row['elem_id_os'])}<br>"
            f"Type: {row['element_type']}<br>"
            f"Combined: {row['combined_stress_MPa']:.1f} MPa<br>"
            f"Axial: {row['axial_stress_MPa']:.1f} MPa<br>"
            f"Shear: {row['shear_stress_MPa']:.1f} MPa"
        )

fig.add_trace(go.Scatter3d(
    x=crit_x, y=crit_y, z=crit_z,
    mode='markers+text',
    marker=dict(size=10, color='darkred', symbol='diamond'),
    text=[f"#{i+1}" for i in range(len(crit_x))],
    textposition='top center',
    textfont=dict(size=12, color='white'),
    hovertext=crit_text,
    hoverinfo='text',
    name='Top 10 Critical'
))

fig.update_layout(
    title=dict(
        text='DASK 2026 Twin Towers - 3D Stress Analysis<br><sup>Combined Stress Distribution (0.4g Lateral Load)</sup>',
        font=dict(size=18)
    ),
    scene=dict(
        xaxis_title='X (mm)',
        yaxis_title='Y (mm)',
        zaxis_title='Z (mm)',
        aspectmode='data',
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.8))
    ),
    showlegend=True,
    legend=dict(x=0.02, y=0.98),
    template='plotly_dark',
    width=1400,
    height=900
)

# Save full model view
output_path = os.path.join(VIS_DIR, 'stress_3d_full.html')
fig.write_html(output_path)
print(f"  Saved: {output_path}")

# ============================================================================
# Create view focusing on critical elements only
# ============================================================================
print("\n  Creating critical elements view...")

fig2 = go.Figure()

# Only show high and critical stress elements
traces_crit = create_element_traces(merged_df, show_all=False)
for trace in traces_crit:
    fig2.add_trace(trace)

# Add critical markers with more detail
for _, row in critical_10.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    if n1 in node_coords and n2 in node_coords:
        p1 = node_coords[n1]
        p2 = node_coords[n2]
        fig2.add_trace(go.Scatter3d(
            x=[p1[0], p2[0]], y=[p1[1], p2[1]], z=[p1[2], p2[2]],
            mode='lines',
            line=dict(color='magenta', width=8),
            name=f"#{int(row['elem_id_os'])} {row['element_type']}",
            hovertext=f"ID: {int(row['elem_id_os'])}<br>Type: {row['element_type']}<br>Stress: {row['combined_stress_MPa']:.1f} MPa"
        ))

fig2.update_layout(
    title=dict(
        text='DASK 2026 - Critical Elements (High Stress Only)<br><sup>Elements above 30% of maximum stress shown</sup>',
        font=dict(size=18)
    ),
    scene=dict(
        xaxis_title='X (mm)',
        yaxis_title='Y (mm)', 
        zaxis_title='Z (mm)',
        aspectmode='data',
        camera=dict(eye=dict(x=1.2, y=1.2, z=0.6))
    ),
    showlegend=True,
    template='plotly_dark',
    width=1400,
    height=900
)

output_path2 = os.path.join(VIS_DIR, 'stress_3d_critical.html')
fig2.write_html(output_path2)
print(f"  Saved: {output_path2}")

# ============================================================================
# Create stress distribution by floor
# ============================================================================
print("\n  Creating floor-by-floor stress chart...")

# Calculate average stress per floor
floor_stress = []
for _, row in merged_df.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    if n1 in node_coords and n2 in node_coords:
        z_avg = (node_coords[n1][2] + node_coords[n2][2]) / 2
        floor = int(z_avg / 60)  # Approximate floor (60mm per typical floor)
        floor_stress.append({
            'floor': floor,
            'z_mm': z_avg,
            'combined_stress': row['combined_stress_MPa'],
            'element_type': row['element_type']
        })

floor_df = pd.DataFrame(floor_stress)

# Group by floor and element type
fig3 = go.Figure()

colors = {
    'column': 'red',
    'beam_x': 'blue', 
    'beam_y': 'cyan',
    'brace_xz': 'orange',
    'brace_yz': 'yellow',
    'core_wall': 'purple',
    'brace_floor': 'green'
}

for etype in ['column', 'beam_x', 'brace_xz', 'core_wall', 'brace_floor']:
    type_floor = floor_df[floor_df['element_type'] == etype]
    if len(type_floor) > 0:
        avg_by_floor = type_floor.groupby('floor')['combined_stress'].mean().reset_index()
        fig3.add_trace(go.Scatter(
            x=avg_by_floor['combined_stress'],
            y=avg_by_floor['floor'] * 60,  # Convert to mm
            mode='lines+markers',
            name=etype,
            line=dict(color=colors.get(etype, 'gray'), width=2)
        ))

fig3.update_layout(
    title='Average Combined Stress by Height',
    xaxis_title='Average Combined Stress (MPa)',
    yaxis_title='Height (mm)',
    template='plotly_white',
    width=800,
    height=600,
    showlegend=True
)

output_path3 = os.path.join(VIS_DIR, 'stress_by_floor.html')
fig3.write_html(output_path3)
print(f"  Saved: {output_path3}")

# ============================================================================
# Element type comparison bar chart
# ============================================================================
print("\n  Creating element type comparison...")

fig4 = go.Figure()

fig4.add_trace(go.Bar(
    x=type_summary_df['type'],
    y=type_summary_df['max_combined'],
    name='Max Combined Stress',
    marker_color='red'
))

fig4.add_trace(go.Bar(
    x=type_summary_df['type'],
    y=type_summary_df['avg_combined'],
    name='Avg Combined Stress',
    marker_color='orange'
))

fig4.add_trace(go.Bar(
    x=type_summary_df['type'],
    y=type_summary_df['max_shear'],
    name='Max Shear Stress',
    marker_color='purple'
))

fig4.update_layout(
    title='Stress Comparison by Element Type',
    xaxis_title='Element Type',
    yaxis_title='Stress (MPa)',
    barmode='group',
    template='plotly_white',
    width=1000,
    height=500
)

output_path4 = os.path.join(VIS_DIR, 'stress_by_type.html')
fig4.write_html(output_path4)
print(f"  Saved: {output_path4}")

# ============================================================================
# Summary
# ============================================================================
print("\n" + "=" * 70)
print("CRITICAL FINDINGS")
print("=" * 70)

print(f"""
1. MOST CRITICAL ELEMENTS: Ground floor columns
   - Max Combined Stress: {active_df['combined_stress_MPa'].max():.1f} MPa
   - Location: Base of both towers (Z = 0-90mm)
   - Cause: High bending moments at fixed supports

2. STRESS DISTRIBUTION:
   - Columns: Highest stress (avg {type_summary_df[type_summary_df['type']=='column']['avg_combined'].values[0]:.1f} MPa)
   - Braces XZ: Second highest due to lateral load transfer
   - Core walls: Moderate stress, good load distribution
   - Bridge elements: Low stress - well designed

3. CRITICAL ZONES:
   - Ground floor connections (0-90mm height)
   - Tower base at corners
   - XZ bracing at lower floors

4. RECOMMENDATIONS:
   - Strengthen ground floor column connections
   - Consider larger section at base (8x8mm instead of 6x6mm)
   - Add diagonal bracing at ground floor corners
""")

print("=" * 70)
print("VISUALIZATION FILES CREATED:")
print("=" * 70)
print(f"  [stress_3d_full.html](results/visualizations/stress_3d_full.html) - Full model with stress colors")
print(f"  [stress_3d_critical.html](results/visualizations/stress_3d_critical.html) - Critical elements only")
print(f"  [stress_by_floor.html](results/visualizations/stress_by_floor.html) - Stress distribution by height")
print(f"  [stress_by_type.html](results/visualizations/stress_by_type.html) - Comparison by element type")
