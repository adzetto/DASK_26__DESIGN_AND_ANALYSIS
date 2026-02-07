"""Analyze Model V8 Element Distribution"""
import pandas as pd
import numpy as np

conn_df = pd.read_csv('data/twin_connectivity_matrix.csv')
pos_df = pd.read_csv('data/twin_position_matrix.csv')

print("=" * 70)
print("MODEL V8 ELEMENT ANALYSIS")
print("=" * 70)

print(f"\nTotal Elements: {len(conn_df)}")
print(f"Total Nodes: {len(pos_df)}")

print("\n" + "-" * 40)
print("ELEMENT TYPE DISTRIBUTION:")
print("-" * 40)
for etype, count in conn_df['element_type'].value_counts().items():
    total_length = conn_df[conn_df['element_type'] == etype]['length'].sum()
    print(f"  {etype:<20}: {count:4d} elements, {total_length:8.1f} cm total")

print("\n" + "-" * 40)
print("BY TOWER:")
print("-" * 40)
for tower, count in conn_df['tower'].value_counts().items():
    print(f"  {tower:<20}: {count:4d} elements")

# Analyze bracing distribution
print("\n" + "-" * 40)
print("BRACING ANALYSIS:")
print("-" * 40)

brace_types = ['brace_xz', 'brace_yz', 'floor_brace', 'shear_wall_xz']
for bt in brace_types:
    df = conn_df[conn_df['element_type'] == bt]
    if len(df) > 0:
        print(f"\n  {bt}:")
        print(f"    Count: {len(df)}")
        print(f"    Total Length: {df['length'].sum():.1f} cm")

# Analyze by floor
print("\n" + "-" * 40)
print("VERTICAL BRACING BY FLOOR (XZ Plane):")
print("-" * 40)

# Get floor levels
z_levels = sorted(pos_df['z'].unique())

for etype in ['shear_wall_xz', 'brace_xz']:
    df = conn_df[conn_df['element_type'] == etype]
    if len(df) > 0:
        print(f"\n  {etype}:")
        # For each element, find which floor it spans
        floor_counts = {}
        for _, row in df.iterrows():
            ni, nj = int(row['node_i']), int(row['node_j'])
            if ni in pos_df['node_id'].values and nj in pos_df['node_id'].values:
                z1 = pos_df[pos_df['node_id'] == ni]['z'].values[0]
                z2 = pos_df[pos_df['node_id'] == nj]['z'].values[0]
                floor = min(z1, z2)
                floor_counts[floor] = floor_counts.get(floor, 0) + 1

        for z in sorted(floor_counts.keys())[:10]:  # First 10 floors
            print(f"    z={z:6.1f} cm: {floor_counts[z]:3d} braces")

# Weight estimate
print("\n" + "-" * 40)
print("WEIGHT ESTIMATE:")
print("-" * 40)

BALSA_DENSITY = 160  # kg/m^3
SECTION_AREA = 36    # mm^2 = 0.36 cm^2

# Frame elements
frame_types = ['column', 'beam_x', 'beam_y', 'brace_xz', 'brace_yz', 'floor_brace',
               'bridge_beam', 'bridge_column', 'bridge_truss', 'bridge_rigid']
frame_df = conn_df[conn_df['element_type'].isin(frame_types)]
frame_length_cm = frame_df['length'].sum()
frame_weight = frame_length_cm * (SECTION_AREA / 100) * (BALSA_DENSITY / 1e6)

print(f"  Frame Length: {frame_length_cm:.1f} cm")
print(f"  Frame Weight: {frame_weight:.3f} kg")

# Shear walls (assuming 3mm thickness)
shear_df = conn_df[conn_df['element_type'].str.contains('shear')]
if len(shear_df) > 0:
    # Estimate panel area (diagonal length * height)
    panel_weight = 0
    for _, row in shear_df.iterrows():
        ni, nj = int(row['node_i']), int(row['node_j'])
        if ni in pos_df['node_id'].values and nj in pos_df['node_id'].values:
            z1 = pos_df[pos_df['node_id'] == ni]['z'].values[0]
            z2 = pos_df[pos_df['node_id'] == nj]['z'].values[0]
            h = abs(z2 - z1)
            w = 3.4  # Panel width
            vol = w * h * 0.3  # 3mm thickness
            panel_weight += vol * BALSA_DENSITY / 1e6
    panel_weight = panel_weight / 2  # 2 diagonals per panel
    print(f"  Panel Weight: {panel_weight:.3f} kg")
else:
    panel_weight = 0

total_weight = frame_weight + panel_weight
print(f"\n  TOTAL WEIGHT: {total_weight:.3f} kg")
print(f"  Weight Limit: 1.400 kg")
print(f"  Margin: {1.400 - total_weight:.3f} kg")

# Stiffness analysis needed
print("\n" + "-" * 40)
print("STIFFNESS REQUIREMENTS FOR ASCENDING REGION:")
print("-" * 40)

T1_current = 0.200  # Current T1
TA_DD2 = 0.102      # DD-2 ascending region boundary
TA_DD4 = 0.083      # DD-4 ascending region boundary (most demanding)

for target_name, target_T in [("DD-2 (TA=0.102s)", 0.095), ("DD-4 (TA=0.083s)", 0.075)]:
    stiffness_ratio = (T1_current / target_T) ** 2
    print(f"\n  Target: {target_name}")
    print(f"    Current T1: {T1_current:.3f} s")
    print(f"    Target T1: {target_T:.3f} s")
    print(f"    Required Stiffness Increase: {stiffness_ratio:.1f}x")
    print(f"    (T proportional to 1/sqrt(K))")
