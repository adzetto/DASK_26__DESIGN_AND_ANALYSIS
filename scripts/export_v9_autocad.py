"""
EXPORT MODEL V9 TO AUTOCAD DXF
==============================
Creates a comprehensive DXF file with:
- Separate layers for each element type
- Color coding by element type
- 3D wireframe model
- Plan views at key levels
- Annotations
"""

import numpy as np
import pandas as pd
import ezdxf
from ezdxf import colors
from pathlib import Path

print("=" * 70)
print("EXPORTING MODEL V9 TO AUTOCAD DXF")
print("=" * 70)

# Load V9 model data
DATA_DIR = Path(__file__).parent.parent / 'data'
EXPORTS_DIR = Path(__file__).parent.parent / 'exports'

pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix_v9.csv')
conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix_v9.csv')

print(f"Nodes: {len(pos_df)}")
print(f"Elements: {len(conn_df)}")

# Create coordinate lookup
coords = {}
for _, row in pos_df.iterrows():
    coords[int(row['node_id'])] = (row['x'], row['y'], row['z'])

# Create DXF document
doc = ezdxf.new('R2010', setup=True)
msp = doc.modelspace()

# Define layer colors (AutoCAD Color Index)
LAYER_COLORS = {
    'column': colors.CYAN,           # 4 - Cyan
    'beam_x': colors.GREEN,          # 3 - Green
    'beam_y': colors.YELLOW,         # 2 - Yellow
    'brace_xz': colors.MAGENTA,      # 6 - Magenta
    'brace_yz': colors.RED,          # 1 - Red
    'shear_wall_xz': colors.WHITE,   # 7 - White
    'floor_brace': colors.BLUE,      # 5 - Blue
    'bridge_beam': 30,               # Orange
    'bridge_column': 30,
    'bridge_truss': 40,              # Light orange
    'bridge_rigid': 50,              # Yellow-green
}

# Create layers
print("\nCreating layers...")
for layer_name, color in LAYER_COLORS.items():
    doc.layers.add(layer_name, color=color)

# Add annotation layer
doc.layers.add('annotations', color=colors.WHITE)
doc.layers.add('dimensions', color=colors.CYAN)
doc.layers.add('floor_levels', color=colors.GREEN)

# Draw 3D elements
print("Drawing 3D elements...")
element_counts = {}

for _, row in conn_df.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    etype = row['element_type']
    
    if n1 not in coords or n2 not in coords:
        continue
    
    p1 = coords[n1]
    p2 = coords[n2]
    
    layer = etype if etype in LAYER_COLORS else 'column'
    
    msp.add_line(p1, p2, dxfattribs={'layer': layer})
    
    element_counts[etype] = element_counts.get(etype, 0) + 1

print("\nElement counts:")
for etype, count in sorted(element_counts.items()):
    print(f"  {etype}: {count}")

# Add floor level annotations
print("\nAdding floor annotations...")
floor_levels = sorted(pos_df['z'].unique())
max_x = pos_df['x'].max()
max_y = pos_df['y'].max()

for i, z in enumerate(floor_levels):
    # Add text annotation for each floor
    if i == 0:
        label = f"GROUND (z={z:.1f})"
    elif i == len(floor_levels) - 1:
        label = f"ROOF (z={z:.1f})"
    else:
        label = f"F{i} (z={z:.1f})"
    
    # Place annotation outside the building
    msp.add_text(
        label,
        dxfattribs={
            'layer': 'floor_levels',
            'height': 1.5,
            'insert': (max_x + 5, max_y / 2, z)
        }
    )

# Add title block
print("Adding title block...")
title_text = [
    "DASK 2026 TWIN TOWERS",
    "MODEL V9 - STIFFENED",
    "Scale: 1:50",
    f"Elements: {len(conn_df)}",
    f"Height: {pos_df['z'].max():.1f} cm",
    "Date: 2026-02-04"
]

title_y = -10
for line in title_text:
    msp.add_text(
        line,
        dxfattribs={
            'layer': 'annotations',
            'height': 2.0,
            'insert': (0, title_y, 0)
        }
    )
    title_y -= 3

# Add dimension lines for building footprint
print("Adding dimensions...")
min_x = pos_df['x'].min()
min_y = pos_df['y'].min()

# X dimension
msp.add_line(
    (min_x, min_y - 5, 0),
    (max_x, min_y - 5, 0),
    dxfattribs={'layer': 'dimensions'}
)
msp.add_text(
    f"{max_x - min_x:.1f} cm",
    dxfattribs={
        'layer': 'dimensions',
        'height': 1.5,
        'insert': ((min_x + max_x) / 2, min_y - 7, 0)
    }
)

# Y dimension
msp.add_line(
    (min_x - 5, min_y, 0),
    (min_x - 5, max_y, 0),
    dxfattribs={'layer': 'dimensions'}
)
msp.add_text(
    f"{max_y - min_y:.1f} cm",
    dxfattribs={
        'layer': 'dimensions',
        'height': 1.5,
        'insert': (min_x - 10, (min_y + max_y) / 2, 0),
        'rotation': 90
    }
)

# Save main DXF file
output_file = EXPORTS_DIR / 'twin_towers_v9_autocad.dxf'
doc.saveas(output_file)
print(f"\nSaved: {output_file}")

# Create plan view DXF (XY projection at ground level)
print("\nCreating plan view...")
doc_plan = ezdxf.new('R2010', setup=True)
msp_plan = doc_plan.modelspace()

for layer_name, color in LAYER_COLORS.items():
    doc_plan.layers.add(layer_name, color=color)

# Draw ground floor elements only
ground_z = 0
z_tol = 0.5

for _, row in conn_df.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    etype = row['element_type']
    
    if n1 not in coords or n2 not in coords:
        continue
    
    p1 = coords[n1]
    p2 = coords[n2]
    
    # Only include ground floor elements
    if abs(p1[2] - ground_z) < z_tol or abs(p2[2] - ground_z) < z_tol:
        if etype in ['column', 'beam_x', 'beam_y']:
            layer = etype if etype in LAYER_COLORS else 'column'
            # Project to XY plane
            msp_plan.add_line((p1[0], p1[1]), (p2[0], p2[1]), dxfattribs={'layer': layer})

# Add node markers at ground level
doc_plan.layers.add('nodes', color=colors.RED)
for _, row in pos_df[pos_df['z'] == 0].iterrows():
    x, y = row['x'], row['y']
    msp_plan.add_circle((x, y), radius=0.3, dxfattribs={'layer': 'nodes'})

plan_file = EXPORTS_DIR / 'twin_towers_v9_plan.dxf'
doc_plan.saveas(plan_file)
print(f"Saved: {plan_file}")

# Create elevation view DXF (XZ projection)
print("\nCreating elevation view...")
doc_elev = ezdxf.new('R2010', setup=True)
msp_elev = doc_elev.modelspace()

for layer_name, color in LAYER_COLORS.items():
    doc_elev.layers.add(layer_name, color=color)

# Draw elements projected to XZ plane (front elevation)
y_front = pos_df['y'].min()  # Front face
y_tol = 0.5

for _, row in conn_df.iterrows():
    n1 = int(row['node_i'])
    n2 = int(row['node_j'])
    etype = row['element_type']
    
    if n1 not in coords or n2 not in coords:
        continue
    
    p1 = coords[n1]
    p2 = coords[n2]
    
    # Include elements on front face
    if abs(p1[1] - y_front) < y_tol or abs(p2[1] - y_front) < y_tol:
        layer = etype if etype in LAYER_COLORS else 'column'
        # Project to XZ plane
        msp_elev.add_line((p1[0], p1[2]), (p2[0], p2[2]), dxfattribs={'layer': layer})

elev_file = EXPORTS_DIR / 'twin_towers_v9_elevation.dxf'
doc_elev.saveas(elev_file)
print(f"Saved: {elev_file}")

print("\n" + "=" * 70)
print("AUTOCAD EXPORT COMPLETE")
print("=" * 70)
print(f"\nFiles created:")
print(f"  1. {output_file.name} - Full 3D model with layers")
print(f"  2. {plan_file.name} - Ground floor plan view")
print(f"  3. {elev_file.name} - Front elevation view")
print(f"\nLayer color coding:")
for layer, color in LAYER_COLORS.items():
    print(f"  {layer}: Color {color}")
