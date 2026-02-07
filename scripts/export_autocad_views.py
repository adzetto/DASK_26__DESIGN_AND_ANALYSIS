#!/usr/bin/env python3
"""
Export AutoCAD Views with Hatched Shear Walls
Creates DXF files for: Front, Back, Left, Right, Top views
"""

import numpy as np
import pandas as pd
import ezdxf
from ezdxf.enums import TextEntityAlignment
import os

# =====================================================
# CONSTANTS
# =====================================================
X_COORDS = [0, 3, 11, 14.4, 15.6, 19, 27, 30]  # cm
Y_COORDS_T1 = [0, 4, 7.4, 8.6, 12, 16]  # Tower 1
Y_COORDS_T2 = [24, 28, 31.4, 32.6, 36, 40]  # Tower 2
TOTAL_FLOORS = 27
FLOOR_HEIGHT = 60  # mm (6m / 100 = 60mm at 1:100 scale)
GROUND_HEIGHT = 90  # mm (9m / 100)
TOTAL_HEIGHT = GROUND_HEIGHT + (TOTAL_FLOORS - 1) * FLOOR_HEIGHT  # 1590mm = 159m

# Scale: 1cm model = 10mm drawing (1:10 for plan, 1:100 for elevation)
SCALE_PLAN = 10  # 1cm -> 10mm
SCALE_ELEV = 1   # 1m -> 1mm (compact for elevation)

# Colors
COLOR_SHEARWALL = 8  # Gray
COLOR_COLUMN = 7     # White
COLOR_BRACE = 30     # Orange
COLOR_BEAM = 5       # Blue
COLOR_CORE = 42      # Brown
COLOR_HATCH = 8      # Gray

def get_floor_z(floor):
    """Get Z coordinate for floor (in mm at 1:100)"""
    if floor == 0:
        return 0
    return GROUND_HEIGHT + (floor - 1) * FLOOR_HEIGHT

def create_hatch_pattern(msp, points, color=8, pattern='ANSI31'):
    """Create hatch pattern for shear wall indication"""
    hatch = msp.add_hatch(color=color)
    hatch.paths.add_polyline_path(points, is_closed=True)
    hatch.set_pattern_fill(pattern, scale=2.0)
    return hatch

# =====================================================
# TOP VIEW (FLOOR PLAN)
# =====================================================
def create_top_view():
    """Create floor plan view (top view)"""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    # Create layers
    doc.layers.add('OUTLINE', color=7)
    doc.layers.add('SHEARWALL', color=8)
    doc.layers.add('COLUMN', color=7)
    doc.layers.add('BRACE', color=30)
    doc.layers.add('CORE', color=42)
    doc.layers.add('DIM', color=2)
    doc.layers.add('TEXT', color=7)
    doc.layers.add('HATCH', color=8)
    
    for tower_num, y_coords in enumerate([Y_COORDS_T1, Y_COORDS_T2], 1):
        y_offset = 0 if tower_num == 1 else 240  # mm
        
        # Tower outline
        outline = [
            (0, y_offset),
            (300, y_offset),
            (300, y_offset + 160),
            (0, y_offset + 160),
            (0, y_offset)
        ]
        msp.add_lwpolyline(outline, dxfattribs={'layer': 'OUTLINE', 'lineweight': 50})
        
        # Shear walls with hatch
        # Front wall (Y=0)
        sw_front = [(0, y_offset), (300, y_offset), (300, y_offset + 5), (0, y_offset + 5)]
        create_hatch_pattern(msp, sw_front, pattern='ANSI31')
        msp.add_lwpolyline(sw_front + [(0, y_offset)], dxfattribs={'layer': 'SHEARWALL'})
        
        # Back wall (Y=16)
        sw_back = [(0, y_offset + 155), (300, y_offset + 155), (300, y_offset + 160), (0, y_offset + 160)]
        create_hatch_pattern(msp, sw_back, pattern='ANSI31')
        msp.add_lwpolyline(sw_back + [(0, y_offset + 155)], dxfattribs={'layer': 'SHEARWALL'})
        
        # Left wall (X=0)
        sw_left = [(0, y_offset), (5, y_offset), (5, y_offset + 160), (0, y_offset + 160)]
        create_hatch_pattern(msp, sw_left, pattern='ANSI32')
        msp.add_lwpolyline(sw_left + [(0, y_offset)], dxfattribs={'layer': 'SHEARWALL'})
        
        # Right wall (X=30)
        sw_right = [(295, y_offset), (300, y_offset), (300, y_offset + 160), (295, y_offset + 160)]
        create_hatch_pattern(msp, sw_right, pattern='ANSI32')
        msp.add_lwpolyline(sw_right + [(295, y_offset)], dxfattribs={'layer': 'SHEARWALL'})
        
        # Core zone (hatched differently)
        core = [(144, y_offset + 74), (156, y_offset + 74), (156, y_offset + 86), (144, y_offset + 86)]
        create_hatch_pattern(msp, core, color=42, pattern='ANSI37')
        msp.add_lwpolyline(core + [(144, y_offset + 74)], dxfattribs={'layer': 'CORE', 'lineweight': 35})
        
        # Column grid points
        for x in X_COORDS:
            for y_local in [0, 4, 7.4, 8.6, 12, 16]:
                cx = x * SCALE_PLAN
                cy = y_offset + y_local * SCALE_PLAN
                msp.add_circle((cx, cy), 3, dxfattribs={'layer': 'COLUMN'})
        
        # Floor braces (X pattern)
        for i in range(len(X_COORDS) - 1):
            for j in range(len(Y_COORDS_T1) - 1):
                x1 = X_COORDS[i] * SCALE_PLAN
                x2 = X_COORDS[i + 1] * SCALE_PLAN
                y1 = y_offset + [0, 4, 7.4, 8.6, 12][j] * SCALE_PLAN
                y2 = y_offset + [4, 7.4, 8.6, 12, 16][j] * SCALE_PLAN
                
                # Skip core zone and very small panels
                panel_w = X_COORDS[i + 1] - X_COORDS[i]
                panel_h = [4, 3.4, 1.2, 3.4, 4][j]
                
                if panel_w > 2 and panel_h > 2:
                    msp.add_line((x1, y1), (x2, y2), dxfattribs={'layer': 'BRACE', 'color': 30})
                    msp.add_line((x2, y1), (x1, y2), dxfattribs={'layer': 'BRACE', 'color': 30})
        
        # Tower label
        label = f"TOWER {tower_num}"
        msp.add_text(label, height=15, dxfattribs={'layer': 'TEXT'}).set_placement(
            (150, y_offset + 80), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Bridge zone indication
    bridge_rect = [(110, 160), (190, 160), (190, 240), (110, 240)]
    msp.add_lwpolyline(bridge_rect + [(110, 160)], dxfattribs={'layer': 'OUTLINE', 'color': 1, 'linetype': 'DASHED'})
    msp.add_text("BRIDGE ZONE", height=10, dxfattribs={'layer': 'TEXT', 'color': 1}).set_placement(
        (150, 200), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Dimensions - using lines and text instead of dimension entities
    # X direction
    y_dim = -20
    for i in range(len(X_COORDS) - 1):
        x1 = X_COORDS[i] * SCALE_PLAN
        x2 = X_COORDS[i + 1] * SCALE_PLAN
        dim_val = X_COORDS[i + 1] - X_COORDS[i]
        # Draw dimension line
        msp.add_line((x1, y_dim), (x2, y_dim), dxfattribs={'layer': 'DIM'})
        msp.add_line((x1, y_dim - 3), (x1, y_dim + 3), dxfattribs={'layer': 'DIM'})
        msp.add_line((x2, y_dim - 3), (x2, y_dim + 3), dxfattribs={'layer': 'DIM'})
        msp.add_text(f"{dim_val}", height=5, dxfattribs={'layer': 'DIM'}).set_placement(
            ((x1 + x2) / 2, y_dim - 8), align=TextEntityAlignment.MIDDLE_CENTER)
    
    # Total width
    msp.add_text("30 cm", height=8, dxfattribs={'layer': 'DIM'}).set_placement(
        (150, -40), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_line((0, -35), (300, -35), dxfattribs={'layer': 'DIM'})
    msp.add_line((0, -38), (0, -32), dxfattribs={'layer': 'DIM'})
    msp.add_line((300, -38), (300, -32), dxfattribs={'layer': 'DIM'})
    
    # Title
    msp.add_text("TOP VIEW - TYPICAL FLOOR PLAN", height=12, dxfattribs={'layer': 'TEXT'}).set_placement(
        (150, -60), align=TextEntityAlignment.MIDDLE_CENTER)
    
    return doc

# =====================================================
# FRONT/BACK VIEW (XZ Plane)
# =====================================================
def create_front_view():
    """Create front elevation view (XZ plane, Y=0)"""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    doc.layers.add('OUTLINE', color=7)
    doc.layers.add('SHEARWALL', color=8)
    doc.layers.add('BRACE', color=30)
    doc.layers.add('FLOOR', color=9)
    doc.layers.add('TEXT', color=7)
    doc.layers.add('HATCH', color=8)
    
    # Scale for elevation: 1m = 10mm
    scale = 10
    
    # Building outline
    msp.add_lwpolyline([
        (0, 0), (300, 0), (300, 1590), (0, 1590), (0, 0)
    ], dxfattribs={'layer': 'OUTLINE', 'lineweight': 50})
    
    # Floor lines
    for floor in range(TOTAL_FLOORS + 1):
        z = get_floor_z(floor)
        msp.add_line((0, z), (300, z), dxfattribs={'layer': 'FLOOR', 'color': 9})
    
    # Core shear wall (X = 14.4 to 15.6) - hatched
    core_sw = [(144, 0), (156, 0), (156, 1590), (144, 1590)]
    create_hatch_pattern(msp, core_sw, pattern='ANSI31')
    msp.add_lwpolyline(core_sw + [(144, 0)], dxfattribs={'layer': 'SHEARWALL', 'lineweight': 35})
    
    # DAMA bracing pattern
    for floor in range(1, TOTAL_FLOORS):
        z_bot = get_floor_z(floor)
        z_top = get_floor_z(floor + 1)
        
        for i, (x1, x2) in enumerate([(30, 110), (190, 270)]):
            # DAMA pattern
            if (floor + i) % 2 == 0:
                msp.add_line((x1, z_bot), (x2, z_top), dxfattribs={'layer': 'BRACE'})
            else:
                msp.add_line((x2, z_bot), (x1, z_top), dxfattribs={'layer': 'BRACE'})
    
    # Ground floor shading
    ground = [(0, 0), (300, 0), (300, 90), (0, 90)]
    create_hatch_pattern(msp, ground, color=9, pattern='SOLID')
    
    # Labels
    msp.add_text("FRONT ELEVATION", height=15, dxfattribs={'layer': 'TEXT'}).set_placement(
        (150, -30), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("30 cm", height=10, dxfattribs={'layer': 'TEXT'}).set_placement(
        (150, -50), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("159 m", height=10, dxfattribs={'layer': 'TEXT'}).set_placement(
        (-30, 795), align=TextEntityAlignment.MIDDLE_CENTER)
    
    return doc

# =====================================================
# SIDE VIEW (YZ Plane)
# =====================================================
def create_side_view():
    """Create side elevation view (YZ plane, X=0)"""
    doc = ezdxf.new('R2010')
    msp = doc.modelspace()
    
    doc.layers.add('OUTLINE', color=7)
    doc.layers.add('SHEARWALL', color=8)
    doc.layers.add('BRACE', color=30)
    doc.layers.add('FLOOR', color=9)
    doc.layers.add('BRIDGE', color=1)
    doc.layers.add('TEXT', color=7)
    doc.layers.add('HATCH', color=8)
    
    # Tower 1 (Y = 0 to 16)
    msp.add_lwpolyline([
        (0, 0), (160, 0), (160, 1590), (0, 1590), (0, 0)
    ], dxfattribs={'layer': 'OUTLINE', 'lineweight': 50})
    
    # Tower 2 (Y = 24 to 40)
    msp.add_lwpolyline([
        (240, 0), (400, 0), (400, 1590), (240, 1590), (240, 0)
    ], dxfattribs={'layer': 'OUTLINE', 'lineweight': 50})
    
    # Gap indication
    msp.add_line((160, 0), (160, 1590), dxfattribs={'layer': 'OUTLINE', 'linetype': 'DASHED'})
    msp.add_line((240, 0), (240, 1590), dxfattribs={'layer': 'OUTLINE', 'linetype': 'DASHED'})
    
    # Floor lines
    for floor in range(TOTAL_FLOORS + 1):
        z = get_floor_z(floor)
        msp.add_line((0, z), (160, z), dxfattribs={'layer': 'FLOOR', 'color': 9})
        msp.add_line((240, z), (400, z), dxfattribs={'layer': 'FLOOR', 'color': 9})
    
    # Bridge zones
    bridge_floors = [(5, 6), (11, 12), (17, 18), (23, 25)]
    for bf1, bf2 in bridge_floors:
        z1 = get_floor_z(bf1)
        z2 = get_floor_z(bf2)
        bridge_rect = [(160, z1), (240, z1), (240, z2), (160, z2)]
        create_hatch_pattern(msp, bridge_rect, color=1, pattern='ANSI33')
        msp.add_lwpolyline(bridge_rect + [(160, z1)], dxfattribs={'layer': 'BRIDGE', 'color': 1})
    
    # Mega-braces (every 4 floors)
    mega_floors = [0, 4, 8, 12, 16, 20, 24]
    for floor in mega_floors:
        if floor > 0 and floor < TOTAL_FLOORS - 1:
            z_bot = get_floor_z(floor)
            z_top = get_floor_z(floor + 1)
            # Tower 1
            msp.add_line((0, z_bot), (40, z_top), dxfattribs={'layer': 'BRACE'})
            msp.add_line((40, z_bot), (0, z_top), dxfattribs={'layer': 'BRACE'})
            msp.add_line((120, z_bot), (160, z_top), dxfattribs={'layer': 'BRACE'})
            msp.add_line((160, z_bot), (120, z_top), dxfattribs={'layer': 'BRACE'})
            # Tower 2
            msp.add_line((240, z_bot), (280, z_top), dxfattribs={'layer': 'BRACE'})
            msp.add_line((280, z_bot), (240, z_top), dxfattribs={'layer': 'BRACE'})
            msp.add_line((360, z_bot), (400, z_top), dxfattribs={'layer': 'BRACE'})
            msp.add_line((400, z_bot), (360, z_top), dxfattribs={'layer': 'BRACE'})
    
    # Core shear walls (hatched) - at center of each tower
    core1 = [(74, 0), (86, 0), (86, 1590), (74, 1590)]
    core2 = [(314, 0), (326, 0), (326, 1590), (314, 1590)]
    create_hatch_pattern(msp, core1, pattern='ANSI31')
    create_hatch_pattern(msp, core2, pattern='ANSI31')
    msp.add_lwpolyline(core1 + [(74, 0)], dxfattribs={'layer': 'SHEARWALL', 'lineweight': 35})
    msp.add_lwpolyline(core2 + [(314, 0)], dxfattribs={'layer': 'SHEARWALL', 'lineweight': 35})
    
    # Ground floor
    ground1 = [(0, 0), (160, 0), (160, 90), (0, 90)]
    ground2 = [(240, 0), (400, 0), (400, 90), (240, 90)]
    create_hatch_pattern(msp, ground1, color=9, pattern='SOLID')
    create_hatch_pattern(msp, ground2, color=9, pattern='SOLID')
    
    # Labels
    msp.add_text("SIDE ELEVATION", height=15, dxfattribs={'layer': 'TEXT'}).set_placement(
        (200, -30), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("TOWER 1", height=12, dxfattribs={'layer': 'TEXT'}).set_placement(
        (80, 1620), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("8 cm GAP", height=10, dxfattribs={'layer': 'TEXT'}).set_placement(
        (200, 1620), align=TextEntityAlignment.MIDDLE_CENTER)
    msp.add_text("TOWER 2", height=12, dxfattribs={'layer': 'TEXT'}).set_placement(
        (320, 1620), align=TextEntityAlignment.MIDDLE_CENTER)
    
    return doc

# =====================================================
# MAIN EXECUTION
# =====================================================
if __name__ == "__main__":
    output_dir = "/mnt/c/Users/lenovo/Desktop/DASK_NEW/exports"
    
    print("="*60)
    print("EXPORTING AUTOCAD VIEWS")
    print("="*60)
    
    # Top View
    print("\nCreating TOP VIEW...")
    doc_top = create_top_view()
    top_path = os.path.join(output_dir, "twin_towers_top_view.dxf")
    doc_top.saveas(top_path)
    print(f"  Saved: {top_path}")
    
    # Front View
    print("\nCreating FRONT VIEW...")
    doc_front = create_front_view()
    front_path = os.path.join(output_dir, "twin_towers_front_view.dxf")
    doc_front.saveas(front_path)
    print(f"  Saved: {front_path}")
    
    # Back View (same as front, different label)
    print("\nCreating BACK VIEW...")
    doc_back = create_front_view()
    # Update label
    for entity in doc_back.modelspace():
        if entity.dxftype() == 'TEXT' and 'FRONT' in entity.dxf.text:
            entity.dxf.text = entity.dxf.text.replace('FRONT', 'BACK')
    back_path = os.path.join(output_dir, "twin_towers_back_view.dxf")
    doc_back.saveas(back_path)
    print(f"  Saved: {back_path}")
    
    # Side Views (Left and Right)
    print("\nCreating SIDE VIEWS (LEFT & RIGHT)...")
    doc_left = create_side_view()
    left_path = os.path.join(output_dir, "twin_towers_left_view.dxf")
    doc_left.saveas(left_path)
    print(f"  Saved: {left_path}")
    
    doc_right = create_side_view()
    for entity in doc_right.modelspace():
        if entity.dxftype() == 'TEXT' and 'SIDE' in entity.dxf.text:
            entity.dxf.text = entity.dxf.text.replace('SIDE', 'RIGHT SIDE')
    right_path = os.path.join(output_dir, "twin_towers_right_view.dxf")
    doc_right.saveas(right_path)
    print(f"  Saved: {right_path}")
    
    print("\n" + "="*60)
    print("ALL VIEWS EXPORTED SUCCESSFULLY")
    print("="*60)
    
    # Summary
    print("\nExported files:")
    print(f"  1. {top_path}")
    print(f"  2. {front_path}")
    print(f"  3. {back_path}")
    print(f"  4. {left_path}")
    print(f"  5. {right_path}")
