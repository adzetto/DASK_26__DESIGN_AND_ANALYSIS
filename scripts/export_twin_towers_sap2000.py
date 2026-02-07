#!/usr/bin/env python3
"""
SAP2000 Export Script for Twin Towers Model
============================================
Exports twin towers with bridges to SAP2000 $2k text file format.
Includes:
- All nodes (joints)
- All frame elements (columns, beams, braces)
- Area elements (shear walls, core walls)
- Point masses at specified floors
- Material and section definitions
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'data')
OUTPUT_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), 'sap2000_model')

# Load model data
print("="*60)
print("SAP2000 EXPORT - TWIN TOWERS MODEL")
print("="*60)

print("\nLoading model data...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_position_matrix.csv'))
conn_df = pd.read_csv(os.path.join(DATA_DIR, 'twin_connectivity_matrix.csv'))

print(f"  Nodes: {len(pos_df)}")
print(f"  Elements: {len(conn_df)}")

# =====================================================
# MATERIAL AND SECTION PROPERTIES
# =====================================================
# Balsa wood properties
BALSA_E = 3500.0        # MPa = N/mm²
BALSA_G = BALSA_E / 2.6 # MPa
BALSA_NU = 0.3
BALSA_DENSITY = 160e-9  # kg/mm³ = 160 kg/m³

# Section dimensions (mm)
SECTION_SIZE = 6.0      # 6mm x 6mm balsa
WALL_THICKNESS = 2.0    # mm for shell elements

# Unit conversion: model is in cm, SAP2000 uses mm
SCALE = 10.0  # 1 cm = 10 mm

# Mass per floor (kg)
MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
MASS_PER_FLOOR = 1.60  # kg
MASS_ROOF = 2.22       # kg

# =====================================================
# GENERATE $2K FILE
# =====================================================
output_file = os.path.join(OUTPUT_DIR, 'Twin_Towers_Complete.s2k')
os.makedirs(OUTPUT_DIR, exist_ok=True)

print(f"\nGenerating SAP2000 $2k file...")

with open(output_file, 'w') as f:
    
    # Header
    f.write(f"; SAP2000 Text File - Twin Towers Model\n")
    f.write(f"; Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write(f"; Units: N, mm, kg\n")
    f.write(f";\n\n")
    
    # =====================================================
    # TABLE: PROGRAM CONTROL
    # =====================================================
    f.write("TABLE:  \"PROGRAM CONTROL\"\n")
    f.write("   ProgramName=SAP2000   Version=24.0.0   ProgLevel=Advanced   ")
    f.write("LicenseOS=Yes   LicenseSC=Yes   LicenseBR=Yes   LicenseHT=No   ")
    f.write('CurrUnits="N, mm, C"   ')
    f.write("SteelCode=AISC360-16   ConcrCode=ACI318-19   ")
    f.write("AlumCode=AA-ASD2000   ColdCode=AISI-ASD96   ")
    f.write("BridgeCode=AASHTO2017\n")
    f.write("\n")
    
    # =====================================================
    # TABLE: ACTIVE DEGREES OF FREEDOM
    # =====================================================
    f.write("TABLE:  \"ACTIVE DEGREES OF FREEDOM\"\n")
    f.write("   UX=Yes   UY=Yes   UZ=Yes   RX=Yes   RY=Yes   RZ=Yes\n")
    f.write("\n")
    
    # =====================================================
    # TABLE: COORDINATE SYSTEMS
    # =====================================================
    f.write("TABLE:  \"COORDINATE SYSTEMS\"\n")
    f.write('   Name=GLOBAL   Type=Cartesian   X=0   Y=0   Z=0   AboutZ=0   AboutY=0   AboutX=0\n')
    f.write("\n")
    
    # =====================================================
    # TABLE: MATERIAL PROPERTIES
    # =====================================================
    f.write("TABLE:  \"MATERIAL PROPERTIES 01 - GENERAL\"\n")
    f.write(f'   Material=BALSA   Type=Other   Grade=""   SymType=Isotropic   ')
    f.write(f'TempDepend=No   Color=Yellow\n')
    f.write("\n")
    
    f.write("TABLE:  \"MATERIAL PROPERTIES 02 - BASIC MECHANICAL PROPERTIES\"\n")
    f.write(f'   Material=BALSA   UnitWeight={BALSA_DENSITY * 9810:.6E}   ')
    f.write(f'UnitMass={BALSA_DENSITY:.6E}   E1={BALSA_E}   G12={BALSA_G}   U12={BALSA_NU}   ')
    f.write(f'A1=1.17E-05\n')
    f.write("\n")
    
    # =====================================================
    # TABLE: FRAME SECTIONS
    # =====================================================
    f.write("TABLE:  \"FRAME SECTION PROPERTIES 01 - GENERAL\"\n")
    f.write(f'   SectionName=BALSA6x6   Material=BALSA   Shape=Rectangular   ')
    f.write(f't3={SECTION_SIZE}   t2={SECTION_SIZE}   ')
    f.write(f'Area={SECTION_SIZE**2}   TorsConst={0.1406*SECTION_SIZE**4:.4f}   ')
    f.write(f'I33={SECTION_SIZE**4/12:.4f}   I22={SECTION_SIZE**4/12:.4f}   ')
    f.write(f'AS2={SECTION_SIZE**2*5/6:.4f}   AS3={SECTION_SIZE**2*5/6:.4f}   ')
    f.write(f'S33Top={SECTION_SIZE**3/6:.4f}   S33Bot={SECTION_SIZE**3/6:.4f}   ')
    f.write(f'S22Top={SECTION_SIZE**3/6:.4f}   S22Bot={SECTION_SIZE**3/6:.4f}   ')
    f.write(f'Z33={SECTION_SIZE**3/4:.4f}   Z22={SECTION_SIZE**3/4:.4f}   ')
    f.write(f'R33={SECTION_SIZE/np.sqrt(12):.4f}   R22={SECTION_SIZE/np.sqrt(12):.4f}\n')
    f.write("\n")
    
    # =====================================================
    # TABLE: AREA SECTIONS (Shell)
    # =====================================================
    f.write("TABLE:  \"AREA SECTION PROPERTIES\"\n")
    f.write(f'   Section=WALL2mm   Material=BALSA   MatAngle=0   ')
    f.write(f'AreaType=Shell   Type=Shell-Thin   DrillDOF=Yes   Thickness={WALL_THICKNESS}   ')
    f.write(f'BendThick={WALL_THICKNESS}   Color=Gray8Dark\n')
    f.write("\n")
    
    # =====================================================
    # TABLE: JOINT COORDINATES
    # =====================================================
    f.write("TABLE:  \"JOINT COORDINATES\"\n")
    
    node_map = {}  # node_id -> joint_name
    for idx, row in pos_df.iterrows():
        node_id = int(row['node_id'])
        x = row['x'] * SCALE  # cm to mm
        y = row['y'] * SCALE
        z = row['z'] * SCALE
        
        joint_name = f"J{node_id+1}"
        node_map[node_id] = joint_name
        
        f.write(f'   Joint={joint_name}   CoordSys=GLOBAL   CoordType=Cartesian   ')
        f.write(f'XorR={x:.2f}   Y={y:.2f}   Z={z:.2f}   ')
        f.write(f'SpecialJt=No   GlobalX={x:.2f}   GlobalY={y:.2f}   GlobalZ={z:.2f}\n')
    
    f.write("\n")
    
    # =====================================================
    # TABLE: JOINT RESTRAINTS (Fixed Base)
    # =====================================================
    f.write("TABLE:  \"JOINT RESTRAINT ASSIGNMENTS\"\n")
    
    base_nodes = pos_df[pos_df['z'] == 0]
    for idx, row in base_nodes.iterrows():
        node_id = int(row['node_id'])
        joint_name = node_map[node_id]
        f.write(f'   Joint={joint_name}   U1=Yes   U2=Yes   U3=Yes   R1=Yes   R2=Yes   R3=Yes\n')
    
    f.write("\n")
    
    # =====================================================
    # TABLE: JOINT ADDED MASS ASSIGNMENTS
    # =====================================================
    f.write("TABLE:  \"JOINT ADDED MASS ASSIGNMENTS\"\n")
    
    # Group nodes by floor
    floor_nodes = {}
    for idx, row in pos_df.iterrows():
        floor = int(row['floor'])
        node_id = int(row['node_id'])
        if floor not in floor_nodes:
            floor_nodes[floor] = []
        floor_nodes[floor].append(node_id)
    
    # Add mass at specified floors
    total_mass_added = 0
    for floor in MASS_FLOORS:
        if floor in floor_nodes:
            n_nodes = len(floor_nodes[floor])
            mass_per_node = MASS_PER_FLOOR / n_nodes  # kg per node
            for node_id in floor_nodes[floor]:
                joint_name = node_map[node_id]
                f.write(f'   Joint={joint_name}   CoordSys=GLOBAL   ')
                f.write(f'Mass1={mass_per_node:.6f}   Mass2={mass_per_node:.6f}   Mass3={mass_per_node:.6f}\n')
            total_mass_added += MASS_PER_FLOOR
    
    # Roof mass
    max_floor = max(floor_nodes.keys())
    if max_floor in floor_nodes:
        n_nodes = len(floor_nodes[max_floor])
        mass_per_node = MASS_ROOF / n_nodes
        for node_id in floor_nodes[max_floor]:
            joint_name = node_map[node_id]
            f.write(f'   Joint={joint_name}   CoordSys=GLOBAL   ')
            f.write(f'Mass1={mass_per_node:.6f}   Mass2={mass_per_node:.6f}   Mass3={mass_per_node:.6f}\n')
        total_mass_added += MASS_ROOF
    
    f.write("\n")
    print(f"  Added point mass: {total_mass_added:.2f} kg")
    
    # =====================================================
    # TABLE: CONNECTIVITY - FRAME
    # =====================================================
    f.write("TABLE:  \"CONNECTIVITY - FRAME\"\n")
    
    # Frame element types
    frame_types = ['column', 'beam_x', 'beam_y', 'floor_brace', 'brace_xz', 'brace_yz',
                   'core_brace_xz', 'core_brace_yz',
                   'bridge_beam', 'bridge_column', 'bridge_truss']
    
    frame_count = 0
    for idx, row in conn_df.iterrows():
        elem_type = row['element_type']
        if elem_type in frame_types:
            n1 = int(row['node_i'])
            n2 = int(row['node_j'])
            elem_id = int(row['element_id'])
            
            if n1 in node_map and n2 in node_map:
                frame_name = f"F{elem_id+1}"
                j1 = node_map[n1]
                j2 = node_map[n2]
                
                f.write(f'   Frame={frame_name}   JointI={j1}   JointJ={j2}   ')
                f.write(f'IsCurved=No   GUID=\n')
                frame_count += 1
    
    f.write("\n")
    print(f"  Frame elements: {frame_count}")
    
    # =====================================================
    # TABLE: FRAME SECTION ASSIGNMENTS
    # =====================================================
    f.write("TABLE:  \"FRAME SECTION ASSIGNMENTS\"\n")
    
    for idx, row in conn_df.iterrows():
        elem_type = row['element_type']
        if elem_type in frame_types:
            elem_id = int(row['element_id'])
            frame_name = f"F{elem_id+1}"
            f.write(f'   Frame={frame_name}   SectionType=Rectangular   AutoSelect=N.A.   ')
            f.write(f'AnalSect=BALSA6x6   DesignSect=BALSA6x6   MatProp=Default\n')
    
    f.write("\n")
    
    # =====================================================
    # TABLE: FRAME RELEASE ASSIGNMENTS (PIN ends for braces)
    # =====================================================
    f.write("TABLE:  \"FRAME RELEASE ASSIGNMENTS 1 - GENERAL\"\n")
    
    brace_types = ['floor_brace', 'brace_xz', 'brace_yz', 'core_brace_xz', 'core_brace_yz', 'bridge_truss']
    for idx, row in conn_df.iterrows():
        elem_type = row['element_type']
        if elem_type in brace_types:
            elem_id = int(row['element_id'])
            frame_name = f"F{elem_id+1}"
            # Pin both ends (moment release)
            f.write(f'   Frame={frame_name}   PI=No   V2I=No   V3I=No   TI=No   M2I=Yes   M3I=Yes   ')
            f.write(f'PJ=No   V2J=No   V3J=No   TJ=No   M2J=Yes   M3J=Yes   ')
            f.write(f'PartialFix=No\n')
    
    f.write("\n")
    
    # =====================================================
    # TABLE: CONNECTIVITY - AREA (Shell elements)
    # =====================================================
    f.write("TABLE:  \"CONNECTIVITY - AREA\"\n")
    
    # Shell element types (diagonal braces treated as shells)
    shell_types = ['shear_wall_xz', 'shear_wall_yz', 'core_wall_xz', 'core_wall_yz', 
                   'bridge_shear', 'bridge_rigid']
    
    area_count = 0
    for idx, row in conn_df.iterrows():
        elem_type = row['element_type']
        if elem_type in shell_types:
            n1 = int(row['node_i'])
            n2 = int(row['node_j'])
            elem_id = int(row['element_id'])
            
            if n1 in node_map and n2 in node_map:
                area_name = f"A{elem_id+1}"
                j1 = node_map[n1]
                j2 = node_map[n2]
                
                # For diagonal elements, we need to create a 2-point "line" shell
                # SAP2000 needs 3 or 4 points for area, so we'll export as frame with shell property
                # Alternative: Export as frame with high stiffness
                f.write(f'   Area={area_name}   NumJoints=2   Joint1={j1}   Joint2={j2}   ')
                f.write(f'GUID=\n')
                area_count += 1
    
    f.write("\n")
    print(f"  Area elements: {area_count} (diagonal shells)")
    
    # =====================================================
    # TABLE: LOAD PATTERNS
    # =====================================================
    f.write("TABLE:  \"LOAD PATTERN DEFINITIONS\"\n")
    f.write('   LoadPat=DEAD   DesignType=Dead   SelfWtMult=1\n')
    f.write('   LoadPat=MODAL   DesignType=Other   SelfWtMult=0\n')
    f.write("\n")
    
    # =====================================================
    # TABLE: MODAL CASE
    # =====================================================
    f.write("TABLE:  \"CASE - MODAL 1 - GENERAL\"\n")
    f.write('   Case=MODAL   ModeType=Eigen   MaxNumModes=12   MinNumModes=1   ')
    f.write('EigenShift=0   EigenCutoff=0   EigenTol=1E-09   AutoShift=Yes\n')
    f.write("\n")
    
    f.write("TABLE:  \"CASE - MODAL 2 - LOAD ASSIGNMENTS\"\n")
    f.write('   Case=MODAL   LoadType="Load pattern"   LoadName=DEAD   ')
    f.write('LoadSF=0   Type=Loads\n')
    f.write("\n")
    
    # =====================================================
    # END OF MODEL DEFINITION
    # =====================================================
    f.write("END TABLE DATA\n")

print(f"\n{'='*60}")
print(f"SAP2000 $2K FILE SAVED: {output_file}")
print(f"{'='*60}")

# =====================================================
# ALSO CREATE CSI S2K FILE FOR ETABS COMPATIBILITY
# =====================================================
# Create a simpler CSV version for manual import
csv_nodes = os.path.join(OUTPUT_DIR, 'twin_towers_nodes.csv')
csv_elements = os.path.join(OUTPUT_DIR, 'twin_towers_elements.csv')
csv_masses = os.path.join(OUTPUT_DIR, 'twin_towers_masses.csv')

# Nodes
nodes_export = pos_df[['node_id', 'x', 'y', 'z', 'floor', 'tower']].copy()
nodes_export['x_mm'] = nodes_export['x'] * SCALE
nodes_export['y_mm'] = nodes_export['y'] * SCALE
nodes_export['z_mm'] = nodes_export['z'] * SCALE
nodes_export.to_csv(csv_nodes, index=False)
print(f"\nNodes CSV: {csv_nodes}")

# Elements
conn_df.to_csv(csv_elements, index=False)
print(f"Elements CSV: {csv_elements}")

# Masses
mass_data = []
for floor in MASS_FLOORS:
    if floor in floor_nodes:
        n_nodes = len(floor_nodes[floor])
        mass_per_node = MASS_PER_FLOOR / n_nodes
        for node_id in floor_nodes[floor]:
            mass_data.append({
                'node_id': node_id,
                'floor': floor,
                'mass_kg': mass_per_node,
                'mass_type': 'floor'
            })

max_floor = max(floor_nodes.keys())
if max_floor in floor_nodes:
    n_nodes = len(floor_nodes[max_floor])
    mass_per_node = MASS_ROOF / n_nodes
    for node_id in floor_nodes[max_floor]:
        mass_data.append({
            'node_id': node_id,
            'floor': max_floor,
            'mass_kg': mass_per_node,
            'mass_type': 'roof'
        })

mass_df = pd.DataFrame(mass_data)
mass_df.to_csv(csv_masses, index=False)
print(f"Masses CSV: {csv_masses}")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"  Total Nodes: {len(pos_df)}")
print(f"  Total Elements: {len(conn_df)}")
print(f"  Frame Elements: {frame_count}")
print(f"  Area Elements: {area_count}")
print(f"  Total Point Mass: {total_mass_added:.2f} kg")
print(f"  Floors with mass: {MASS_FLOORS} + roof")
print(f"{'='*60}")
