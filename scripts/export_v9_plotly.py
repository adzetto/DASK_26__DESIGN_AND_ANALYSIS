"""
DASK 2026 Twin Towers V9 - Plotly 3D HTML Export
Interactive visualization with element type filtering
"""

import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
RESULTS_DIR = SCRIPT_DIR.parent / 'results' / 'visualizations'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "twin_towers_v9_3d.html"

print("=" * 70)
print("TWIN TOWERS V9 - PLOTLY 3D EXPORT")
print("=" * 70)

# Load V9 data
print("\nLoading V9 data...")
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix_v9.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix_v9.csv')

print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# Node lookup
node_xyz = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos_df.iterrows()}

# Color scheme
COLORS = {
    'column': '#0066CC',
    'beam_x': '#00AA00',
    'beam_y': '#FF8800',
    'brace_xz': '#FF0000',
    'brace_yz': '#FF00FF',
    'floor_brace': '#888888',
    'shear_wall_xz': '#1E90FF',
    'shear_wall_yz': '#00CED1',
    'bridge_beam': '#9400D3',
    'bridge_column': '#4B0082',
    'bridge_truss': '#FF6347',
    'bridge_rigid': '#FFD700',
}

WIDTHS = {
    'column': 4,
    'beam_x': 2,
    'beam_y': 2,
    'brace_xz': 1.5,
    'brace_yz': 1.5,
    'floor_brace': 1,
    'shear_wall_xz': 3,
    'shear_wall_yz': 3,
    'bridge_beam': 3,
    'bridge_column': 3,
    'bridge_truss': 2,
    'bridge_rigid': 2,
}

# Create figure
print("\nCreating visualization...")
fig = go.Figure()

element_types = conn_df['element_type'].unique()
print(f"  Element types: {list(element_types)}")

# Render shear walls as plates (Mesh3d)
shear_wall_types = [t for t in element_types if 'shear_wall' in t]

for sw_type in shear_wall_types:
    sw_df = conn_df[conn_df['element_type'] == sw_type]

    panel_vx, panel_vy, panel_vz = [], [], []
    panel_i, panel_j, panel_k = [], [], []
    vertex_count = 0

    for _, row in sw_df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            continue

        p1, p2 = node_xyz[n1], node_xyz[n2]
        offset = 0.3

        if 'xz' in sw_type:
            v1 = (p1[0], p1[1] - offset, p1[2])
            v2 = (p1[0], p1[1] + offset, p1[2])
            v3 = (p2[0], p2[1] + offset, p2[2])
            v4 = (p2[0], p2[1] - offset, p2[2])
        else:
            v1 = (p1[0] - offset, p1[1], p1[2])
            v2 = (p1[0] + offset, p1[1], p1[2])
            v3 = (p2[0] + offset, p2[1], p2[2])
            v4 = (p2[0] - offset, p2[1], p2[2])

        base = vertex_count
        panel_vx.extend([v1[0], v2[0], v3[0], v4[0]])
        panel_vy.extend([v1[1], v2[1], v3[1], v4[1]])
        panel_vz.extend([v1[2], v2[2], v3[2], v4[2]])
        panel_i.extend([base, base])
        panel_j.extend([base + 1, base + 2])
        panel_k.extend([base + 2, base + 3])
        vertex_count += 4

    if vertex_count > 0:
        color = COLORS.get(sw_type, '#1E90FF')
        fig.add_trace(go.Mesh3d(
            x=panel_vx, y=panel_vy, z=panel_vz,
            i=panel_i, j=panel_j, k=panel_k,
            color=color, opacity=0.6,
            name=f"{sw_type} ({len(sw_df)})",
            hoverinfo='name', flatshading=True
        ))
        print(f"    {sw_type}: {len(sw_df)} elements (plates)")

# Render other elements as lines
for etype in sorted(element_types):
    if 'shear_wall' in etype:
        continue

    elem_df = conn_df[conn_df['element_type'] == etype]
    x_lines, y_lines, z_lines = [], [], []

    for _, row in elem_df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 in node_xyz and n2 in node_xyz:
            p1, p2 = node_xyz[n1], node_xyz[n2]
            x_lines.extend([p1[0], p2[0], None])
            y_lines.extend([p1[1], p2[1], None])
            z_lines.extend([p1[2], p2[2], None])

    color = COLORS.get(etype, '#999999')
    width = WIDTHS.get(etype, 2)
    visible = 'legendonly' if etype == 'floor_brace' else True

    fig.add_trace(go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        name=f"{etype} ({len(elem_df)})",
        line=dict(color=color, width=width),
        visible=visible,
        hoverinfo='name'
    ))
    print(f"    {etype}: {len(elem_df)} elements")

# Layout
max_x = pos_df['x'].max()
max_y = pos_df['y'].max()
max_z = pos_df['z'].max()

fig.update_layout(
    title=dict(
        text="<b>DASK 2026 Twin Towers - V9 (Stiffened)</b><br>"
             f"<sup>Elements: {len(conn_df)} | Nodes: {len(pos_df)} | "
             "Minimal weight bracing config</sup>",
        x=0.5,
        font=dict(size=18)
    ),
    scene=dict(
        xaxis_title='X (cm)',
        yaxis_title='Y (cm)',
        zaxis_title='Z (cm)',
        aspectmode='data',
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.8)),
        xaxis=dict(range=[-5, max_x + 5]),
        yaxis=dict(range=[-5, max_y + 5]),
        zaxis=dict(range=[0, max_z + 10]),
    ),
    legend=dict(
        title="Element Types (click to toggle)",
        yanchor="top", y=0.99,
        xanchor="left", x=0.01,
        bgcolor="rgba(255,255,255,0.8)"
    ),
    margin=dict(l=0, r=0, t=80, b=0),
    template='plotly_white'
)

# Save
fig.write_html(OUTPUT_FILE, include_plotlyjs='cdn')

print(f"\n{'=' * 70}")
print(f"HTML SAVED: {OUTPUT_FILE}")
print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")
print(f"  Element types: {len(element_types)}")
print("=" * 70)
