#!/usr/bin/env python
# coding: utf-8

# ### Building Parameters
# 
# | Component | Width (X) | Depth (Y) | Floors | Height |
# |-----------|-----------|-----------|--------|--------|
# | **Podium** | 5 bays × 8m = 40m | 2 bays × 8m = 16m | Floors 0-12 (13 floors) | 81m |
# | **Tower** | 3 bays × 8m = 24m | 2 bays × 8m = 16m | Floors 13-25 (13 floors) | 153m |
# 
# | Parameter | Value |
# |-----------|-------|
# | **Ground Floor Height** | 9.0m |
# | **Typical Floor Height** | 6.0m |
# | **Total Floors** | 26 (Floor 0 to Floor 25) |

# ---
# ## 1. Import Libraries and Setup

# In[1]:


import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)


# ---
# ## 2. Building Geometry Parameters

# In[2]:


BAY_WIDTH = 8.0

PODIUM_BAYS_X = 5
PODIUM_BAYS_Y = 2
PODIUM_FLOORS = 13

TOWER_BAYS_X = 3
TOWER_BAYS_Y = 2
TOTAL_FLOORS = 26

GROUND_FLOOR_HEIGHT = 9.0
TYPICAL_FLOOR_HEIGHT = 6.0

PODIUM_X_COORDS = np.arange(PODIUM_BAYS_X + 1) * BAY_WIDTH
TOWER_X_COORDS = np.array([8.0, 16.0, 24.0, 32.0])
Y_COORDS = np.arange(PODIUM_BAYS_Y + 1) * BAY_WIDTH

Z_COORDS = np.zeros(TOTAL_FLOORS)
Z_COORDS[0] = 0.0
Z_COORDS[1] = GROUND_FLOOR_HEIGHT
Z_COORDS[2:] = GROUND_FLOOR_HEIGHT + np.arange(1, TOTAL_FLOORS - 1) * TYPICAL_FLOOR_HEIGHT

print("PODIUM_X_COORDS:", PODIUM_X_COORDS)
print("TOWER_X_COORDS:", TOWER_X_COORDS)
print("Y_COORDS:", Y_COORDS)
print("Z_COORDS:", Z_COORDS)


# ---
# ## 3. Generate Position Matrix with Numpy

# In[3]:


# Podium nodes: floors 0-12, full grid (6x3)
podium_floors = np.arange(PODIUM_FLOORS)
podium_xx, podium_yy, podium_ff = np.meshgrid(PODIUM_X_COORDS, Y_COORDS, podium_floors, indexing='ij')
podium_zz = Z_COORDS[podium_ff]

podium_x_flat = podium_xx.flatten()
podium_y_flat = podium_yy.flatten()
podium_z_flat = podium_zz.flatten()
podium_f_flat = podium_ff.flatten()

n_podium = len(podium_x_flat)
print(f"Podium nodes: {n_podium}")

# Tower nodes: floors 13-25, centered grid (4x3)
tower_floors = np.arange(PODIUM_FLOORS, TOTAL_FLOORS)
tower_xx, tower_yy, tower_ff = np.meshgrid(TOWER_X_COORDS, Y_COORDS, tower_floors, indexing='ij')
tower_zz = Z_COORDS[tower_ff]

tower_x_flat = tower_xx.flatten()
tower_y_flat = tower_yy.flatten()
tower_z_flat = tower_zz.flatten()
tower_f_flat = tower_ff.flatten()

n_tower = len(tower_x_flat)
print(f"Tower nodes: {n_tower}")

# Chevron Center Nodes: floors 0-25 (ALL FLOORS), X=20, Front/Back faces only (Y=0,16)
# User requested chevron braces passing through the middle (full height)
chev_x_coords = np.array([20.0])
chev_y_coords = np.array([Y_COORDS[0], Y_COORDS[-1]])
chev_floors = np.arange(TOTAL_FLOORS) # Changed from tower_floors to ALL floors

chev_xx, chev_yy, chev_ff = np.meshgrid(chev_x_coords, chev_y_coords, chev_floors, indexing='ij')
chev_zz = Z_COORDS[chev_ff]

chev_x_flat = chev_xx.flatten()
chev_y_flat = chev_yy.flatten()
chev_z_flat = chev_zz.flatten()
chev_f_flat = chev_ff.flatten()
n_chev = len(chev_x_flat)
print(f"Chevron nodes: {n_chev}")

# Combine all nodes
all_x = np.concatenate([podium_x_flat, tower_x_flat, chev_x_flat])
all_y = np.concatenate([podium_y_flat, tower_y_flat, chev_y_flat])
all_z = np.concatenate([podium_z_flat, tower_z_flat, chev_z_flat])
all_floor = np.concatenate([podium_f_flat, tower_f_flat, chev_f_flat])
all_zone = np.array(['podium'] * n_podium + ['tower'] * n_tower + ['chevron_node'] * n_chev)

n_nodes = len(all_x)
node_ids = np.arange(n_nodes)

position_df = pd.DataFrame({
    'node_id': node_ids,
    'x': all_x,
    'y': all_y,
    'z': all_z,
    'floor': all_floor.astype(int),
    'zone': all_zone
})

print(f"\nTotal nodes: {n_nodes}")
print(f"Position Matrix Shape: {position_df.shape}")
print(position_df.head(20))


# In[4]:


# Create node lookup: (floor, x, y) -> node_id
node_lookup = {}
for i in range(n_nodes):
    key = (int(all_floor[i]), float(all_x[i]), float(all_y[i]))
    node_lookup[key] = i

print("Node lookup examples:")
print(f"  Floor 0, (0, 0): Node {node_lookup.get((0, 0.0, 0.0), 'N/A')}")
print(f"  Floor 12, (0, 0): Node {node_lookup.get((12, 0.0, 0.0), 'N/A')} (last podium)")
print(f"  Floor 13, (8, 0): Node {node_lookup.get((13, 8.0, 0.0), 'N/A')} (first tower)")
print(f"  Floor 13, (0, 0): Node {node_lookup.get((13, 0.0, 0.0), 'N/A')} (edge - should be N/A)")


# ---
# ## 4. Generate Connectivity with Numpy Arrays
# 
# **Bracing Strategy:**
# - Front/Back faces (Y=0, Y=16): X-brace on ALL bays, ALL floors
# - Left/Right faces: X-brace only on CORNER bays (reduced)
# - Tower center: Chevron braces (inverted V)

# In[5]:


# Helper arrays for element creation
elements_list = []

# ============================================
# BEAMS X-DIRECTION (numpy vectorized)
# ============================================
beam_x_nodes = []

# Podium beams X
for f in range(PODIUM_FLOORS):
    for y in Y_COORDS:
        for i in range(len(PODIUM_X_COORDS) - 1):
            n1 = node_lookup.get((f, PODIUM_X_COORDS[i], y))
            n2 = node_lookup.get((f, PODIUM_X_COORDS[i+1], y))
            if n1 is not None and n2 is not None:
                beam_x_nodes.append([n1, n2])

# Tower beams X
for f in range(PODIUM_FLOORS, TOTAL_FLOORS):
    for y in Y_COORDS:
        for i in range(len(TOWER_X_COORDS) - 1):
            n1 = node_lookup.get((f, TOWER_X_COORDS[i], y))
            n2 = node_lookup.get((f, TOWER_X_COORDS[i+1], y))
            if n1 is not None and n2 is not None:
                beam_x_nodes.append([n1, n2])

beam_x_arr = np.array(beam_x_nodes)
print(f"Beam X elements: {len(beam_x_arr)}")

# ============================================
# BEAMS Y-DIRECTION
# ============================================
beam_y_nodes = []

# Podium beams Y
for f in range(PODIUM_FLOORS):
    for x in PODIUM_X_COORDS:
        for i in range(len(Y_COORDS) - 1):
            n1 = node_lookup.get((f, x, Y_COORDS[i]))
            n2 = node_lookup.get((f, x, Y_COORDS[i+1]))
            if n1 is not None and n2 is not None:
                beam_y_nodes.append([n1, n2])

# Tower beams Y
for f in range(PODIUM_FLOORS, TOTAL_FLOORS):
    for x in TOWER_X_COORDS:
        for i in range(len(Y_COORDS) - 1):
            n1 = node_lookup.get((f, x, Y_COORDS[i]))
            n2 = node_lookup.get((f, x, Y_COORDS[i+1]))
            if n1 is not None and n2 is not None:
                beam_y_nodes.append([n1, n2])

beam_y_arr = np.array(beam_y_nodes)
print(f"Beam Y elements: {len(beam_y_arr)}")

# ============================================
# COLUMNS (vertical)
# ============================================
column_nodes = []

# Podium columns (floors 0-11 to 1-12)
for f in range(PODIUM_FLOORS - 1):
    for x in PODIUM_X_COORDS:
        for y in Y_COORDS:
            n1 = node_lookup.get((f, x, y))
            n2 = node_lookup.get((f+1, x, y))
            if n1 is not None and n2 is not None:
                column_nodes.append([n1, n2])

# Transition columns (floor 12 to 13) - only tower footprint
for x in TOWER_X_COORDS:
    for y in Y_COORDS:
        n1 = node_lookup.get((PODIUM_FLOORS - 1, x, y))
        n2 = node_lookup.get((PODIUM_FLOORS, x, y))
        if n1 is not None and n2 is not None:
            column_nodes.append([n1, n2])

# Tower columns (floors 13-24 to 14-25)
for f in range(PODIUM_FLOORS, TOTAL_FLOORS - 1):
    for x in TOWER_X_COORDS:
        for y in Y_COORDS:
            n1 = node_lookup.get((f, x, y))
            n2 = node_lookup.get((f+1, x, y))
            if n1 is not None and n2 is not None:
                column_nodes.append([n1, n2])

column_arr = np.array(column_nodes)
print(f"Column elements: {len(column_arr)}")


# In[6]:


# ============================================
# BRACES XZ - FRONT/BACK FACES + INTERNAL
# MEGA BRACES: Spanning 2 Floors (0->2, 2->4...)
# Skip Center Bay on Faces (for Chevron).
# ============================================
brace_xz_nodes = []

# Iterate floors with step 2
for f in range(0, TOTAL_FLOORS - 1, 2):
    f_top = f + 2
    if f_top >= TOTAL_FLOORS:
        break # Cannot do 2-story brace at very top if odd count remaining

    for y in Y_COORDS:
        # Iterate all potential bays (Podium width)
        # We check checks for node existence to handle Tower/Podium width differences automatically.
        all_x_candidates = [0.0, 8.0, 16.0, 24.0, 32.0, 40.0]

        for i in range(len(all_x_candidates) - 1):
            x1, x2 = all_x_candidates[i], all_x_candidates[i+1]

            # Check Face vs Internal
            is_face = (y == Y_COORDS[0] or y == Y_COORDS[-1])

            # Center Bay logic (16-24) - Skip for ALL Y values (core wall area)
            is_center_bay = (x1 == 16.0 and x2 == 24.0)

            # Skip Center Bay entirely (Core wall + Chevron area)
            if is_center_bay:
                continue


            # Check corner existence for 2-story bay
            n_bl = node_lookup.get((f, x1, y))
            n_br = node_lookup.get((f, x2, y))
            n_tl = node_lookup.get((f_top, x1, y))
            n_tr = node_lookup.get((f_top, x2, y))

            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                brace_xz_nodes.append([n_bl, n_tr])
                brace_xz_nodes.append([n_br, n_tl])

brace_xz_arr = np.array(brace_xz_nodes)
print(f"Brace XZ (2-story span) elements: {len(brace_xz_arr)}")


# In[7]:


# ============================================
# BRACES YZ - LEFT/RIGHT FACES (edge X only)
# MEGA BRACES: Spanning 2 Floors (0->2, 2->4...)
# ============================================
brace_yz_nodes = []

# Iterate floors with step 2
for f in range(0, TOTAL_FLOORS - 1, 2):
    f_top = f + 2
    if f_top >= TOTAL_FLOORS:
        break

    # X positions for left/right edges depend on floor zone
    # Podium: Left=0, Right=40
    # Tower: Left=8, Right=32
    # We check for node existence to handle boundary automatically.

    # Left edge candidates
    left_x_candidates = [0.0, 8.0]  # Podium=0, Tower=8
    # Right edge candidates
    right_x_candidates = [40.0, 32.0]  # Podium=40, Tower=32

    for x_list in [left_x_candidates, right_x_candidates]:
        for x in x_list:
            # Iterate Y bays
            for j in range(len(Y_COORDS) - 1):
                y1, y2 = Y_COORDS[j], Y_COORDS[j+1]

                n_bl = node_lookup.get((f, x, y1))
                n_br = node_lookup.get((f, x, y2))
                n_tl = node_lookup.get((f_top, x, y1))
                n_tr = node_lookup.get((f_top, x, y2))

                if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                    brace_yz_nodes.append([n_bl, n_tr])
                    brace_yz_nodes.append([n_br, n_tl])

brace_yz_arr = np.array(brace_yz_nodes) if brace_yz_nodes else np.array([]).reshape(0, 2)
print(f"Brace YZ (2-story span, left/right) elements: {len(brace_yz_arr)}")
print(f"\nBrace ratio (XZ:YZ) = {len(brace_xz_arr)}:{len(brace_yz_arr)} = {len(brace_xz_arr)/max(len(brace_yz_arr),1):.1f}:1")


# In[8]:


# ============================================
# CHEVRON BRACES - Center Bay (Inverted V)
# Floors 0 to Top. Front/Back faces only.
# ============================================
chevron_nodes = []

center_x_left = 16.0
center_x_right = 24.0
center_x_mid = 20.0

# Floors 0 to Top
for f in range(TOTAL_FLOORS - 1):
    for y in [Y_COORDS[0], Y_COORDS[-1]]: # Faces only
        # Inverted V: Base at floor f, Apex at floor f+1
        n_bl = node_lookup.get((f, center_x_left, y))
        n_br = node_lookup.get((f, center_x_right, y))
        n_apex = node_lookup.get((f+1, center_x_mid, y))

        if all(n is not None for n in [n_bl, n_br, n_apex]):
            chevron_nodes.append([n_bl, n_apex])
            chevron_nodes.append([n_br, n_apex])

chevron_arr = np.array(chevron_nodes) if chevron_nodes else np.array([]).reshape(0, 2)
print(f"Chevron brace elements: {len(chevron_arr)}")


# In[9]:


# ============================================
# SPACE BRACES - Podium to Tower Transition
# 3D diagonal braces transferring loads from
# wider podium (X=0,40) to narrower tower (X=8,32)
# ============================================
space_brace_nodes = []

# Transition floor: Podium top (floor 12) to Tower bottom (floor 13)
f_podium_top = PODIUM_FLOORS - 1  # 12
f_tower_bottom = PODIUM_FLOORS    # 13

# Podium outer X coords: 0, 40
# Tower inner X coords: 8, 32
# Connect each outer podium corner to corresponding inner tower corner

# Left side: X=0 (podium) -> X=8 (tower)
# Right side: X=40 (podium) -> X=32 (tower)

transitions = [
    (0.0, 8.0),   # Left outer to left inner
    (40.0, 32.0), # Right outer to right inner
]

for x_pod, x_tow in transitions:
    for y in Y_COORDS:
        # Podium top node
        n_pod = node_lookup.get((f_podium_top, x_pod, y))

        # Connect to ALL tower bottom nodes on that Y-line
        for y_tow in Y_COORDS:
            n_tow = node_lookup.get((f_tower_bottom, x_tow, y_tow))
            if n_pod is not None and n_tow is not None:
                space_brace_nodes.append([n_pod, n_tow])

# Also connect diagonally across (podium X=0 to tower X=8 across Y)
# This creates the "web" pattern shown in user's image

# Cross connections: left podium to all tower left, right podium to all tower right
for x_pod, x_tow in transitions:
    for y_pod in Y_COORDS:
        n_pod = node_lookup.get((f_podium_top, x_pod, y_pod))
        # Connect to tower nodes at same X but different Ys
        for y_tow in Y_COORDS:
            if y_pod != y_tow:  # Cross connection
                n_tow = node_lookup.get((f_tower_bottom, x_tow, y_tow))
                # Already added above, skip duplicates
                pass

space_brace_arr = np.array(space_brace_nodes) if space_brace_nodes else np.array([]).reshape(0, 2)
print(f"Space brace elements (transition): {len(space_brace_arr)}")


# In[ ]:


# ============================================
# CENTRAL CORE - Shear Walls (Perde Duvarlar)
# 4-sided core box running full height
# Using balsa panels (3mm thick)
# Core location: X=16-24, Y=0-16 (center bay)
# ============================================
core_wall_nodes = []

# Core boundary coordinates
core_x_left = 16.0
core_x_right = 24.0
core_y_front = 0.0
core_y_back = 16.0
core_y_mid = 8.0  # Internal Y grid line

# Shear walls are vertical panels connecting floor nodes
# We'll create diagonal bracing pattern on each wall face
# This simulates the panel behavior in the model

# FRONT WALL (Y=0): X from 16-24
# BACK WALL (Y=16): X from 16-24
# LEFT WALL (X=16): Y from 0-16
# RIGHT WALL (X=24): Y from 0-16

for f in range(TOTAL_FLOORS - 1):
    f_top = f + 1

    # FRONT WALL (Y=0) - X bay 16-24
    n_bl = node_lookup.get((f, core_x_left, core_y_front))
    n_br = node_lookup.get((f, core_x_right, core_y_front))
    n_tl = node_lookup.get((f_top, core_x_left, core_y_front))
    n_tr = node_lookup.get((f_top, core_x_right, core_y_front))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])  # Diagonal 1
        core_wall_nodes.append([n_br, n_tl])  # Diagonal 2

    # BACK WALL (Y=16) - X bay 16-24  
    n_bl = node_lookup.get((f, core_x_left, core_y_back))
    n_br = node_lookup.get((f, core_x_right, core_y_back))
    n_tl = node_lookup.get((f_top, core_x_left, core_y_back))
    n_tr = node_lookup.get((f_top, core_x_right, core_y_back))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])
        core_wall_nodes.append([n_br, n_tl])

    # LEFT WALL (X=16) - Y bay 0-8
    n_bl = node_lookup.get((f, core_x_left, core_y_front))
    n_br = node_lookup.get((f, core_x_left, core_y_mid))
    n_tl = node_lookup.get((f_top, core_x_left, core_y_front))
    n_tr = node_lookup.get((f_top, core_x_left, core_y_mid))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])
        core_wall_nodes.append([n_br, n_tl])

    # LEFT WALL (X=16) - Y bay 8-16
    n_bl = node_lookup.get((f, core_x_left, core_y_mid))
    n_br = node_lookup.get((f, core_x_left, core_y_back))
    n_tl = node_lookup.get((f_top, core_x_left, core_y_mid))
    n_tr = node_lookup.get((f_top, core_x_left, core_y_back))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])
        core_wall_nodes.append([n_br, n_tl])

    # RIGHT WALL (X=24) - Y bay 0-8
    n_bl = node_lookup.get((f, core_x_right, core_y_front))
    n_br = node_lookup.get((f, core_x_right, core_y_mid))
    n_tl = node_lookup.get((f_top, core_x_right, core_y_front))
    n_tr = node_lookup.get((f_top, core_x_right, core_y_mid))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])
        core_wall_nodes.append([n_br, n_tl])

    # RIGHT WALL (X=24) - Y bay 8-16
    n_bl = node_lookup.get((f, core_x_right, core_y_mid))
    n_br = node_lookup.get((f, core_x_right, core_y_back))
    n_tl = node_lookup.get((f_top, core_x_right, core_y_mid))
    n_tr = node_lookup.get((f_top, core_x_right, core_y_back))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])
        core_wall_nodes.append([n_br, n_tl])

    # INTERNAL CENTER WALL (Y=8) - X bay 16-24 (divides core in center)
    n_bl = node_lookup.get((f, core_x_left, core_y_mid))
    n_br = node_lookup.get((f, core_x_right, core_y_mid))
    n_tl = node_lookup.get((f_top, core_x_left, core_y_mid))
    n_tr = node_lookup.get((f_top, core_x_right, core_y_mid))
    if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
        core_wall_nodes.append([n_bl, n_tr])  # Diagonal 1
        core_wall_nodes.append([n_br, n_tl])  # Diagonal 2

core_wall_arr = np.array(core_wall_nodes) if core_wall_nodes else np.array([]).reshape(0, 2)
print(f"Core wall elements: {len(core_wall_arr)}")


# In[10]:


# ============================================
# FLOOR BRACES (slab diagonals)
# ============================================
brace_floor_nodes = []

# Podium floor braces
for f in range(PODIUM_FLOORS):
    for i in range(len(PODIUM_X_COORDS) - 1):
        for j in range(len(Y_COORDS) - 1):
            x1, x2 = PODIUM_X_COORDS[i], PODIUM_X_COORDS[i+1]
            y1, y2 = Y_COORDS[j], Y_COORDS[j+1]
            n_bl = node_lookup.get((f, x1, y1))
            n_br = node_lookup.get((f, x2, y1))
            n_tl = node_lookup.get((f, x1, y2))
            n_tr = node_lookup.get((f, x2, y2))
            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                brace_floor_nodes.append([n_bl, n_tr])
                brace_floor_nodes.append([n_br, n_tl])

# Tower floor braces
for f in range(PODIUM_FLOORS, TOTAL_FLOORS):
    for i in range(len(TOWER_X_COORDS) - 1):
        for j in range(len(Y_COORDS) - 1):
            x1, x2 = TOWER_X_COORDS[i], TOWER_X_COORDS[i+1]
            y1, y2 = Y_COORDS[j], Y_COORDS[j+1]
            n_bl = node_lookup.get((f, x1, y1))
            n_br = node_lookup.get((f, x2, y1))
            n_tl = node_lookup.get((f, x1, y2))
            n_tr = node_lookup.get((f, x2, y2))
            if all(n is not None for n in [n_bl, n_br, n_tl, n_tr]):
                brace_floor_nodes.append([n_bl, n_tr])
                brace_floor_nodes.append([n_br, n_tl])

brace_floor_arr = np.array(brace_floor_nodes)
print(f"Floor brace elements: {len(brace_floor_arr)}")


# In[11]:


# ============================================
# Combine all elements into connectivity DataFrame
# ============================================

# Calculate lengths using numpy
coords = position_df[['x', 'y', 'z']].values

all_elements = []
element_id = 0

element_types = [
    ('beam_x', beam_x_arr),
    ('beam_y', beam_y_arr),
    ('column', column_arr),
    ('brace_xz', brace_xz_arr),
    ('brace_yz', brace_yz_arr),
    ('chevron', chevron_arr),
    ('brace_space', space_brace_arr),
    ('core_wall', core_wall_arr),
    ('brace_floor', brace_floor_arr)
]

for etype, arr in element_types:
    if len(arr) == 0:
        continue
    for row in arr:
        n1, n2 = int(row[0]), int(row[1])
        c1, c2 = coords[n1], coords[n2]
        length = np.sqrt(np.sum((c2 - c1) ** 2))
        all_elements.append({
            'element_id': element_id,
            'node_i': n1,
            'node_j': n2,
            'element_type': etype,
            'length': round(length, 4)
        })
        element_id += 1

connectivity_df = pd.DataFrame(all_elements)

print("=" * 70)
print("CONNECTIVITY MATRIX")
print("=" * 70)
print(f"\nTotal elements: {len(connectivity_df)}")
print(f"\nElements by type:")
print(connectivity_df['element_type'].value_counts())

n_xz = len(connectivity_df[connectivity_df['element_type'] == 'brace_xz'])
n_yz = len(connectivity_df[connectivity_df['element_type'] == 'brace_yz'])
n_chevron = len(connectivity_df[connectivity_df['element_type'] == 'chevron'])
print(f"\nBrace ratio (XZ : YZ) = {n_xz} : {n_yz} = {n_xz/max(n_yz,1):.1f} : 1")
print(f"Chevron braces: {n_chevron}")


# In[12]:


# Create adjacency matrix
adjacency_matrix = np.zeros((n_nodes, n_nodes), dtype=int)

for _, row in connectivity_df.iterrows():
    i, j = int(row['node_i']), int(row['node_j'])
    adjacency_matrix[i, j] = 1
    adjacency_matrix[j, i] = 1

print(f"Adjacency Matrix Shape: {adjacency_matrix.shape}")
print(f"Total connections (edges): {np.sum(adjacency_matrix) // 2}")


# ---
# ## 5. Interactive 3D Visualization

# In[13]:


# 3D Building View
fig_3d = go.Figure()

element_styles = {
    'column':       {'color': 'blue',      'width': 3},
    'beam_x':       {'color': 'green',     'width': 2},
    'beam_y':       {'color': 'orange',    'width': 2},
    'brace_xz':     {'color': 'red',       'width': 2},
    'brace_yz':     {'color': 'purple',    'width': 2},
    'chevron':      {'color': 'cyan',      'width': 2.5},
    'brace_floor':  {'color': 'lightgray', 'width': 1},
    'brace_space':  {'color': 'black',     'width': 4},
    'core_wall':    {'color': 'brown',     'width': 3}
}

for etype, style in element_styles.items():
    elements = connectivity_df[connectivity_df['element_type'] == etype]
    if len(elements) == 0:
        continue

    x_lines, y_lines, z_lines = [], [], []
    for _, row in elements.iterrows():
        n1_coords = coords[int(row['node_i'])]
        n2_coords = coords[int(row['node_j'])]
        x_lines.extend([n1_coords[0], n2_coords[0], None])
        y_lines.extend([n1_coords[1], n2_coords[1], None])
        z_lines.extend([n1_coords[2], n2_coords[2], None])

    fig_3d.add_trace(go.Scatter3d(
        x=x_lines, y=y_lines, z=z_lines,
        mode='lines',
        name=etype.replace('_', ' ').title(),
        line=dict(color=style['color'], width=style['width']),
        hoverinfo='name'
    ))

fig_3d.add_trace(go.Scatter3d(
    x=all_x, y=all_y, z=all_z,
    mode='markers',
    name='Nodes',
    marker=dict(size=3, color=all_floor, colorscale='Viridis', opacity=0.8),
    hovertemplate='Node %{customdata}<br>X: %{x}m<br>Y: %{y}m<br>Z: %{z}m<extra></extra>',
    customdata=node_ids
))

fig_3d.update_layout(
    title='Stepped Building - 3D View',
    scene=dict(
        xaxis_title='X [m]',
        yaxis_title='Y [m]',
        zaxis_title='Z [m]',
        aspectmode='data',
        camera=dict(eye=dict(x=1.5, y=1.5, z=0.7))
    ),
    width=1000, height=800
)
# fig_3d.show()


# ---
# ## 6. Floor Plan Views

# In[14]:


# Floor 0 Plan
floor_num = 0
floor_mask = position_df['floor'] == floor_num
floor_nodes = position_df[floor_mask]
floor_node_ids = set(floor_nodes['node_id'])

floor_beams = connectivity_df[
    (connectivity_df['node_i'].isin(floor_node_ids)) & 
    (connectivity_df['node_j'].isin(floor_node_ids)) &
    (connectivity_df['element_type'].isin(['beam_x', 'beam_y']))
]

fig_floor0 = go.Figure()

for etype, color in [('beam_x', 'green'), ('beam_y', 'orange')]:
    beams = floor_beams[floor_beams['element_type'] == etype]
    for _, row in beams.iterrows():
        c1, c2 = coords[int(row['node_i'])], coords[int(row['node_j'])]
        fig_floor0.add_trace(go.Scatter(
            x=[c1[0], c2[0]], y=[c1[1], c2[1]],
            mode='lines', line=dict(color=color, width=4),
            showlegend=False, hoverinfo='skip'
        ))

fig_floor0.add_trace(go.Scatter(
    x=floor_nodes['x'], y=floor_nodes['y'],
    mode='markers+text',
    marker=dict(size=15, color='blue', symbol='square'),
    text=[f"({int(r['x'])},{int(r['y'])})" for _, r in floor_nodes.iterrows()],
    textposition='top center', name='Columns'
))

fig_floor0.update_layout(
    title=f'Floor {floor_num} Plan (Podium) | Z = {Z_COORDS[floor_num]}m',
    xaxis_title='X [m]', yaxis_title='Y [m]',
    xaxis=dict(scaleanchor='y', range=[-5, 45]),
    yaxis=dict(range=[-5, 21]),
    width=900, height=500, showlegend=False
)
# fig_floor0.show()


# In[15]:


# Floor 15 Plan (Tower)
floor_num = 15
floor_mask = position_df['floor'] == floor_num
floor_nodes = position_df[floor_mask]
floor_node_ids = set(floor_nodes['node_id'])

floor_beams = connectivity_df[
    (connectivity_df['node_i'].isin(floor_node_ids)) & 
    (connectivity_df['node_j'].isin(floor_node_ids)) &
    (connectivity_df['element_type'].isin(['beam_x', 'beam_y']))
]

fig_floor15 = go.Figure()

for etype, color in [('beam_x', 'green'), ('beam_y', 'orange')]:
    beams = floor_beams[floor_beams['element_type'] == etype]
    for _, row in beams.iterrows():
        c1, c2 = coords[int(row['node_i'])], coords[int(row['node_j'])]
        fig_floor15.add_trace(go.Scatter(
            x=[c1[0], c2[0]], y=[c1[1], c2[1]],
            mode='lines', line=dict(color=color, width=4),
            showlegend=False, hoverinfo='skip'
        ))

fig_floor15.add_trace(go.Scatter(
    x=floor_nodes['x'], y=floor_nodes['y'],
    mode='markers+text',
    marker=dict(size=15, color='blue', symbol='square'),
    text=[f"({int(r['x'])},{int(r['y'])})" for _, r in floor_nodes.iterrows()],
    textposition='top center', name='Columns'
))

fig_floor15.update_layout(
    title=f'Floor {floor_num} Plan (Tower) | Z = {Z_COORDS[floor_num]}m',
    xaxis_title='X [m]', yaxis_title='Y [m]',
    xaxis=dict(scaleanchor='y', range=[-5, 45]),
    yaxis=dict(range=[-5, 21]),
    width=900, height=500, showlegend=False
)
# fig_floor15.show()


# ---
# ## 7. Front Elevation View (X-Z Plane at Y=0)

# In[16]:


# Front Elevation - Y=0 face
front_mask = position_df['y'] == 0
front_nodes = position_df[front_mask]
front_node_ids = set(front_nodes['node_id'])

front_elements = connectivity_df[
    (connectivity_df['node_i'].isin(front_node_ids)) & 
    (connectivity_df['node_j'].isin(front_node_ids))
]

fig_front = go.Figure()

styles_front = {
    'column': ('blue', 3),
    'beam_x': ('black', 2),
    'brace_xz': ('red', 2),
    'chevron': ('blue', 2.5)
}

for etype, (color, width) in styles_front.items():
    elements = front_elements[front_elements['element_type'] == etype]
    for _, row in elements.iterrows():
        c1, c2 = coords[int(row['node_i'])], coords[int(row['node_j'])]
        fig_front.add_trace(go.Scatter(
            x=[c1[0], c2[0]], y=[c1[2], c2[2]],
            mode='lines', line=dict(color=color, width=width),
            showlegend=False, hoverinfo='skip'
        ))

fig_front.add_trace(go.Scatter(
    x=front_nodes['x'], y=front_nodes['z'],
    mode='markers', marker=dict(size=5, color='green'),
    showlegend=False
))

# Annotations
podium_top = Z_COORDS[PODIUM_FLOORS - 1]
total_height = Z_COORDS[-1]

fig_front.add_annotation(x=20, y=-8, text="40m (Podium)", showarrow=False, font=dict(size=12))
fig_front.add_annotation(x=20, y=total_height+8, text="24m (Tower)", showarrow=False, font=dict(size=12))
fig_front.add_hline(y=podium_top, line_dash="dash", line_color="gray", annotation_text="Podium Top")

fig_front.update_layout(
    title=f'Front Elevation (Y=0) | Height: {total_height:.0f}m',
    xaxis_title='X [m]', yaxis_title='Z [m]',
    xaxis=dict(range=[-10, 50]),
    yaxis=dict(range=[-15, total_height+20], scaleanchor='x'),
    width=700, height=900
)
# fig_front.show()


# ---
# ## 8. Side Elevation View (Y-Z Plane)

# In[17]:


# Side Elevations (Left and Right)
# Left: Podium X=0, Tower X=8
# Right: Podium X=48, Tower X=40

from plotly.subplots import make_subplots

fig_sides = make_subplots(rows=1, cols=2, subplot_titles=['Left Elevation', 'Right Elevation'])

sides = [
    {'name': 'Left', 'podium_x': 0, 'tower_x': 8, 'col': 1},
    {'name': 'Right', 'podium_x': 48, 'tower_x': 40, 'col': 2}
]

styles_side = {
    'column': ('blue', 4),
    'beam_y': ('green', 3),
    'brace_yz': ('red', 2),
    'chevron': ('magenta', 2),
    'brace_xz': ('black', 1)  # Space braces might show as lines?
}

for side in sides:
    # Filter nodes on this face
    podium_mask = (position_df['x'] == side['podium_x']) & (position_df['zone'] == 'podium')
    tower_mask = (position_df['x'] == side['tower_x']) & (position_df['zone'] == 'tower')
    # Also include chevron nodes if they are on face? Chevrons are at X=20, so not on side faces.

    side_nodes = position_df[podium_mask | tower_mask]
    side_node_ids = set(side_nodes['node_id'])

    # Filter elements
    side_elements = []
    for _, row in connectivity_df.iterrows():
        if row['node_i'] in side_node_ids and row['node_j'] in side_node_ids:
            side_elements.append(row)
    side_elements = pd.DataFrame(side_elements) if side_elements else pd.DataFrame(columns=connectivity_df.columns)

    if len(side_elements) > 0:
        for etype, (color, width) in styles_side.items():
            elements = side_elements[side_elements['element_type'] == etype]
            for _, row in elements.iterrows():
                c1 = coords[int(row['node_i'])]
                c2 = coords[int(row['node_j'])]
                fig_sides.add_trace(go.Scatter(
                    x=[c1[1], c2[1]], y=[c1[2], c2[2]],
                    mode='lines', line=dict(color=color, width=width),
                    showlegend=False, hoverinfo='skip'
                ), row=1, col=side['col'])

    # Add markers
    fig_sides.add_trace(go.Scatter(
        x=side_nodes['y'], y=side_nodes['z'],
        mode='markers', marker=dict(size=4, color='green'),
        showlegend=False
    ), row=1, col=side['col'])

    fig_sides.add_hline(y=podium_top, line_dash="dash", line_color="gray", row=1, col=side['col'])

fig_sides.update_layout(
    title='Side Elevations (Left & Right)',
    width=900, height=800,
    xaxis_title='Y [m]', yaxis_title='Z [m]'
)
# fig_sides.show()



# ---
# ## 9. Statistics Summary

# In[18]:


print("=" * 70)
print("BUILDING STRUCTURAL SUMMARY")
print("=" * 70)

print(f"\nGEOMETRY:")
print(f"   Podium:  {PODIUM_X_COORDS[-1]:.0f}m x {Y_COORDS[-1]:.0f}m x {Z_COORDS[PODIUM_FLOORS-1]:.0f}m")
print(f"   Tower:   {TOWER_X_COORDS[-1]-TOWER_X_COORDS[0]:.0f}m x {Y_COORDS[-1]:.0f}m | Total: {Z_COORDS[-1]:.0f}m")

print(f"\nNODES: {n_nodes}")
print(f"   Podium: {n_podium} | Tower: {n_tower}")

print(f"\nELEMENTS:")
for etype, count in connectivity_df['element_type'].value_counts().items():
    print(f"   {etype:15s}: {count:5d}")
print(f"   {'TOTAL':15s}: {len(connectivity_df):5d}")

print(f"\nBRACE RATIO:")
print(f"   Front/Back (XZ): {n_xz}")
print(f"   Left/Right (YZ): {n_yz}")
print(f"   Ratio: {n_xz/max(n_yz,1):.1f} : 1")


# In[19]:


# Statistics visualization
fig_stats = make_subplots(
    rows=1, cols=2,
    subplot_titles=['Element Count', 'Length Distribution'],
    specs=[[{'type': 'pie'}, {'type': 'box'}]]
)

counts = connectivity_df['element_type'].value_counts()
fig_stats.add_trace(
    go.Pie(labels=[e.replace('_', ' ').title() for e in counts.index], values=counts.values, hole=0.4),
    row=1, col=1
)

for etype in connectivity_df['element_type'].unique():
    lengths = connectivity_df[connectivity_df['element_type'] == etype]['length']
    fig_stats.add_trace(
        go.Box(y=lengths, name=etype.replace('_', ' ').title()),
        row=1, col=2
    )

fig_stats.update_layout(title='Element Statistics', height=400, width=1000, showlegend=False)
# fig_stats.show()


# ---
# ## 10. Export Data

# In[20]:


position_df.to_csv('position_matrix.csv', index=False)
connectivity_df.to_csv('connectivity_matrix.csv', index=False)
np.savetxt('adjacency_matrix.csv', adjacency_matrix, delimiter=',', fmt='%d')

np.savez('building_data.npz',
         adjacency_matrix=adjacency_matrix,
         coords=coords,
         podium_x=PODIUM_X_COORDS,
         tower_x=TOWER_X_COORDS,
         y_coords=Y_COORDS,
         z_coords=Z_COORDS)

print("Exported:")
print("  - position_matrix.csv")
print("  - connectivity_matrix.csv")
print("  - adjacency_matrix.csv")
print("  - building_data.npz")

