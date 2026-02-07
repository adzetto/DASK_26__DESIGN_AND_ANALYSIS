"""
DASK 2026 Twin Towers - Plotly 3D Visualization
Interactive HTML visualization with element type filtering
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
RESULTS_DIR = SCRIPT_DIR.parent / 'results' / 'visualizations'
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = RESULTS_DIR / "twin_towers_3d_interactive.html"

print("=" * 70)
print("TWIN TOWERS PLOTLY VISUALIZATION")
print("=" * 70)

# Load data
print("\nLoading data...")
pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
npz = np.load(DATA_DIR / 'twin_building_data.npz')

coords = npz['coords']
z_coords = npz['z_coords']

print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# Node lookup
node_xyz = {int(r['node_id']): (r['x'], r['y'], r['z']) for _, r in pos_df.iterrows()}

# Color scheme for element types
COLORS = {
    'column': '#0066CC',           # Blue
    'beam_x': '#00AA00',           # Green
    'beam_y': '#FF8800',           # Orange
    'brace_xz': '#FF0000',         # Red - diagonal braces XZ
    'brace_yz': '#FF00FF',         # Magenta - diagonal braces YZ
    'brace_floor': '#888888',      # Gray
    'floor_brace': '#888888',      # Gray
    'brace_space': '#666666',      # Dark gray
    'core_wall': '#8B4513',        # Brown
    'core_wall_yz': '#8B4513',     # Brown - core YZ
    'core_wall_xz': '#A0522D',     # Sienna - core XZ
    'shear_wall_xz': '#1E90FF',    # Dodger blue - will be plate
    'shear_wall_yz': '#00CED1',    # Dark turquoise - will be plate
    'bridge_beam': '#9400D3',      # Violet
    'bridge_column': '#4B0082',    # Indigo
    'bridge_brace_top': '#FF69B4', # Hot pink
    'bridge_brace_bot': '#FF1493', # Deep pink
    'bridge_truss_side': '#DA70D6',# Orchid
    'bridge_brace_face': '#C71585',# Medium violet red
    'bridge_shear_yz': '#00CED1',  # Dark turquoise (coupled shear wall)
    'bridge_shear': '#00CED1',     # Dark turquoise
    'bridge_rigid': '#FFD700',     # Gold
    'bridge_truss': '#FF6347',     # Tomato
}

# Line widths
WIDTHS = {
    'column': 4,
    'beam_x': 2,
    'beam_y': 2,
    'brace_xz': 1.5,
    'brace_yz': 1.5,
    'brace_floor': 1,
    'brace_space': 2,
    'core_wall': 3,
    'bridge_beam': 3,
    'bridge_column': 3,
    'bridge_brace_top': 2,
    'bridge_brace_bot': 2,
    'bridge_truss_side': 2,
    'bridge_brace_face': 2,
    'bridge_shear_yz': 3,
}

# Create traces for each element type
print("\nCreating visualization...")
fig = go.Figure()

element_types = conn_df['element_type'].unique()
print(f"  Element types: {len(element_types)}")

# Separate shear walls for plate rendering
shear_wall_types = ['shear_wall_xz', 'shear_wall_yz']

# First, render shear walls as plates (Mesh3d)
for sw_type in shear_wall_types:
    if sw_type not in element_types:
        continue
    
    sw_df = conn_df[conn_df['element_type'] == sw_type]
    
    # Group diagonal pairs into quads
    # Each shear wall panel has 2 diagonals - we need to find the 4 corner nodes
    processed_panels = set()
    panel_vertices_x = []
    panel_vertices_y = []
    panel_vertices_z = []
    panel_i = []
    panel_j = []
    panel_k = []
    vertex_count = 0
    
    for _, row in sw_df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 not in node_xyz or n2 not in node_xyz:
            continue
        
        p1, p2 = node_xyz[n1], node_xyz[n2]
        
        # Create a thin quad plate for each diagonal
        # Offset slightly for visibility
        mid_x = (p1[0] + p2[0]) / 2
        mid_y = (p1[1] + p2[1]) / 2
        mid_z = (p1[2] + p2[2]) / 2
        
        # Add vertices for a thin strip along the diagonal
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        dz = p2[2] - p1[2]
        length = (dx**2 + dy**2 + dz**2) ** 0.5
        
        # Perpendicular offset for strip width
        if sw_type == 'shear_wall_xz':
            # XZ plane - offset in Y
            offset = 0.3
            v1 = (p1[0], p1[1] - offset, p1[2])
            v2 = (p1[0], p1[1] + offset, p1[2])
            v3 = (p2[0], p2[1] + offset, p2[2])
            v4 = (p2[0], p2[1] - offset, p2[2])
        else:
            # YZ plane - offset in X
            offset = 0.3
            v1 = (p1[0] - offset, p1[1], p1[2])
            v2 = (p1[0] + offset, p1[1], p1[2])
            v3 = (p2[0] + offset, p2[1], p2[2])
            v4 = (p2[0] - offset, p2[1], p2[2])
        
        # Add to mesh
        base = vertex_count
        panel_vertices_x.extend([v1[0], v2[0], v3[0], v4[0]])
        panel_vertices_y.extend([v1[1], v2[1], v3[1], v4[1]])
        panel_vertices_z.extend([v1[2], v2[2], v3[2], v4[2]])
        
        # Two triangles per quad
        panel_i.extend([base, base])
        panel_j.extend([base+1, base+2])
        panel_k.extend([base+2, base+3])
        
        vertex_count += 4
    
    if vertex_count > 0:
        color = COLORS.get(sw_type, '#1E90FF')
        fig.add_trace(go.Mesh3d(
            x=panel_vertices_x,
            y=panel_vertices_y,
            z=panel_vertices_z,
            i=panel_i,
            j=panel_j,
            k=panel_k,
            color=color,
            opacity=0.6,
            name=f"{sw_type} (plate) ({len(sw_df)})",
            hoverinfo='name',
            flatshading=True
        ))
        print(f"    {sw_type}: {len(sw_df)} elements (as plates)")

# Then render other elements as lines
for etype in sorted(element_types):
    if etype in shear_wall_types:
        continue  # Already rendered as plates
    
    elem_df = conn_df[conn_df['element_type'] == etype]

    x_lines = []
    y_lines = []
    z_lines = []

    for _, row in elem_df.iterrows():
        n1, n2 = int(row['node_i']), int(row['node_j'])
        if n1 in node_xyz and n2 in node_xyz:
            p1, p2 = node_xyz[n1], node_xyz[n2]
            x_lines.extend([p1[0], p2[0], None])
            y_lines.extend([p1[1], p2[1], None])
            z_lines.extend([p1[2], p2[2], None])

    color = COLORS.get(etype, '#999999')
    width = WIDTHS.get(etype, 2)

    # Determine visibility (show main structure, hide some minor elements by default)
    visible = True
    if etype in ['brace_floor', 'brace_space']:
        visible = 'legendonly'

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
        text="<b>DASK 2026 Twin Towers</b><br>" +
             f"<sup>Elements: {len(conn_df)} | Nodes: {len(pos_df)} | " +
             f"Weight: 1.166 kg | Period: T₁ ≈ 0.12s</sup>",
        x=0.5,
        font=dict(size=18)
    ),
    scene=dict(
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        zaxis_title='Z (m)',
        aspectmode='data',
        camera=dict(
            eye=dict(x=1.5, y=1.5, z=0.8)
        ),
        xaxis=dict(range=[-5, max_x + 5]),
        yaxis=dict(range=[-5, max_y + 5]),
        zaxis=dict(range=[0, max_z + 10]),
    ),
    legend=dict(
        title="Element Types (click to toggle)",
        yanchor="top",
        y=0.99,
        xanchor="left",
        x=0.01,
        bgcolor="rgba(255,255,255,0.8)"
    ),
    margin=dict(l=0, r=0, t=80, b=0),
    template='plotly_white'
)

# Add annotations for key features
annotations = [
    dict(x=20, y=8, z=75, text="Podium Top (F12)", showarrow=True, arrowhead=2),
    dict(x=20, y=20, z=50, text="Bridge Zone", showarrow=True, arrowhead=2),
    dict(x=20, y=0, z=153, text="Tower 1 Roof", showarrow=True, arrowhead=2),
    dict(x=20, y=40, z=153, text="Tower 2 Roof", showarrow=True, arrowhead=2),
]

# Add floor level indicators
floor_z_levels = [0, 33, 69, 75, 105, 141, 153]  # Key floor levels
floor_names = ['Ground', 'Bridge 1 (F5)', 'Bridge 2 (F11)', 'Podium Top (F12)',
               'Bridge 3 (F17)', 'Bridge 4 (F23)', 'Roof (F25)']

# Save
fig.write_html(OUTPUT_FILE, include_plotlyjs='cdn')

print(f"\n{'=' * 70}")
print(f"HTML SAVED: {OUTPUT_FILE}")
print("=" * 70)
print("""
Features:
  - Click legend items to show/hide element types
  - Drag to rotate, scroll to zoom
  - Double-click to reset view
  - Hover over elements to see type
""")

# Also create a simpler view with just structure outline
print("\nCreating simplified view...")

fig2 = go.Figure()

# Add all elements as one trace for quick overview
x_all, y_all, z_all = [], [], []
for _, row in conn_df.iterrows():
    n1, n2 = int(row['node_i']), int(row['node_j'])
    if n1 in node_xyz and n2 in node_xyz:
        p1, p2 = node_xyz[n1], node_xyz[n2]
        x_all.extend([p1[0], p2[0], None])
        y_all.extend([p1[1], p2[1], None])
        z_all.extend([p1[2], p2[2], None])

fig2.add_trace(go.Scatter3d(
    x=x_all, y=y_all, z=z_all,
    mode='lines',
    name='All Elements',
    line=dict(color='#333333', width=1),
    hoverinfo='skip'
))

# Highlight bridges
bridge_df = conn_df[conn_df['tower'] == 'bridge']
x_br, y_br, z_br = [], [], []
for _, row in bridge_df.iterrows():
    n1, n2 = int(row['node_i']), int(row['node_j'])
    if n1 in node_xyz and n2 in node_xyz:
        p1, p2 = node_xyz[n1], node_xyz[n2]
        x_br.extend([p1[0], p2[0], None])
        y_br.extend([p1[1], p2[1], None])
        z_br.extend([p1[2], p2[2], None])

fig2.add_trace(go.Scatter3d(
    x=x_br, y=y_br, z=z_br,
    mode='lines',
    name=f'Bridges ({len(bridge_df)} elem)',
    line=dict(color='#FF0000', width=4),
))

# Highlight bracing
brace_df = conn_df[conn_df['element_type'].str.contains('brace')]
x_brace, y_brace, z_brace = [], [], []
for _, row in brace_df.iterrows():
    n1, n2 = int(row['node_i']), int(row['node_j'])
    if n1 in node_xyz and n2 in node_xyz:
        p1, p2 = node_xyz[n1], node_xyz[n2]
        x_brace.extend([p1[0], p2[0], None])
        y_brace.extend([p1[1], p2[1], None])
        z_brace.extend([p1[2], p2[2], None])

fig2.add_trace(go.Scatter3d(
    x=x_brace, y=y_brace, z=z_brace,
    mode='lines',
    name=f'Bracing ({len(brace_df)} elem)',
    line=dict(color='#00AA00', width=2),
    visible='legendonly'
))

fig2.update_layout(
    title=dict(
        text="<b>DASK 2026 Twin Towers - Overview</b><br>" +
             "<sup>7.2cm - 1.6cm - 7.2cm column layout | Coupled Shear Wall Bridges</sup>",
        x=0.5,
        font=dict(size=18)
    ),
    scene=dict(
        xaxis_title='X (m)',
        yaxis_title='Y (m)',
        zaxis_title='Z (m)',
        aspectmode='data',
        camera=dict(eye=dict(x=1.8, y=1.8, z=0.6))
    ),
    legend=dict(
        yanchor="top", y=0.99,
        xanchor="left", x=0.01
    ),
    template='plotly_white'
)

OUTPUT_FILE2 = RESULTS_DIR / "twin_towers_overview.html"
fig2.write_html(OUTPUT_FILE2, include_plotlyjs='cdn')
print(f"Overview saved: {OUTPUT_FILE2}")

# Weight summary
print(f"""
MODEL SUMMARY:
==============
  Tower Layout: 7.2 - 1.6 - 7.2 cm (X direction)
  Total Elements: {len(conn_df)}

  Bridges: 4 total
    - F5-F6 (Z=33-39m)
    - F11-F12 (Z=69-75m)
    - F17-F18 (Z=105-111m)
    - F23-F25 (Z=141-153m, double height)

  Bridge Elements: {len(bridge_df)}
    - Each bridge has coupled shear wall bracing (YZ plane)
    - Provides Y-direction resistance between towers

  Weight: 1.166 kg (Limit: 1.4 kg, Margin: +234g)
""")
