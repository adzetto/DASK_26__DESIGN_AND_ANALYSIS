"""
================================================================================
DASK V9 MODEL - REVIT API EXPORT SCRIPT
================================================================================

Project: DASK 2025 - Twin Towers Earthquake-Resistant Building Design
Model Version: V9 (Final)
Date: February 2026
Author: Structural Engineering Team

Description:
    This script exports the V9 twin towers structural model to Autodesk Revit
    using the Revit Python API. The script is designed to be executed within
    the Revit Python Shell (RPS), pyRevit, or Dynamo Python node.

Model Specifications:
    - Scale: 1:50 (Model dimensions in cm, Real structure in m)
    - Height: 153 cm model (76.5 m real)
    - Floors: 26 (ground + 25 upper floors)
    - Elements: 4,248 structural members
    - Material: Balsa wood 6mm x 6mm sections
    - Weight: 1.386 kg (< 1.4 kg competition limit)

Coordinate System:
    - Model Origin: (0, 0, 0) at Tower 1 base
    - X-axis: Building length (0-30 cm)
    - Y-axis: Building width (0-40 cm, includes both towers)
    - Z-axis: Building height (0-153 cm)

References:
    - TBDY 2018 (Turkish Seismic Design Code)
    - AFAD DD-2 Design Spectrum
    - Autodesk Revit API Documentation 2024
    - IronPython 2.7 / CPython 3.x compatibility

================================================================================
"""

import os
import sys
import csv
import math
from collections import defaultdict
from typing import Dict, List, Tuple, Optional, NamedTuple
from dataclasses import dataclass
from enum import Enum

# ==============================================================================
# CONFIGURATION CONSTANTS
# ==============================================================================

# File paths (relative to script directory)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(BASE_DIR, "data")

POSITION_FILE = os.path.join(DATA_DIR, "twin_position_matrix_v9.csv")
CONNECTIVITY_FILE = os.path.join(DATA_DIR, "twin_connectivity_matrix_v9.csv")

# Scale factors
MODEL_SCALE = 50  # 1:50 scale model
CM_TO_MM = 10.0   # Convert cm to mm
MM_TO_FT = 1.0 / 304.8  # Revit uses internal units (feet)
CM_TO_FT = CM_TO_MM * MM_TO_FT  # Direct cm to feet conversion

# Real-world dimensions (for full-scale export option)
REAL_SCALE_FACTOR = MODEL_SCALE * CM_TO_FT  # cm (model) -> feet (real)

# Section properties (model scale)
SECTION_WIDTH_MM = 6.0   # mm
SECTION_HEIGHT_MM = 6.0  # mm
SECTION_WIDTH_FT = SECTION_WIDTH_MM * MM_TO_FT
SECTION_HEIGHT_FT = SECTION_HEIGHT_MM * MM_TO_FT

# Material properties (Balsa wood)
MATERIAL_NAME = "Balsa_Wood_6mm"
YOUNGS_MODULUS_MPA = 3500.0  # MPa
DENSITY_KG_M3 = 160.0        # kg/m³

# Floor elevations (model scale in cm)
FLOOR_ELEVATIONS = {
    0: 0.0,    # Ground floor
    1: 9.0,    # First floor (9 cm from ground)
}
# Floors 2-25: each 6 cm apart
for i in range(2, 26):
    FLOOR_ELEVATIONS[i] = 9.0 + (i - 1) * 6.0

# ==============================================================================
# DATA STRUCTURES
# ==============================================================================

class ElementType(Enum):
    """Structural element types in the model"""
    COLUMN = "column"
    BEAM_X = "beam_x"
    BEAM_Y = "beam_y"
    BRACE_XZ = "brace_xz"
    BRACE_YZ = "brace_yz"
    SHEAR_WALL_XZ = "shear_wall_xz"
    FLOOR_BRACE = "floor_brace"
    BRIDGE_BEAM = "bridge_beam"
    BRIDGE_BRACE = "bridge_brace"
    OUTRIGGER = "outrigger"
    BELT_TRUSS = "belt_truss"
    CORNER_BRACE = "corner_brace"

@dataclass
class Node:
    """Structural node (joint) definition"""
    id: int
    x: float  # cm
    y: float  # cm
    z: float  # cm
    floor: int
    zone: str
    tower: str  # "1", "2", or "bridge"

    def to_feet(self, scale_to_real: bool = False) -> Tuple[float, float, float]:
        """Convert coordinates to Revit internal units (feet)"""
        factor = REAL_SCALE_FACTOR if scale_to_real else CM_TO_FT
        return (self.x * factor, self.y * factor, self.z * factor)

    def to_xyz_tuple(self) -> Tuple[float, float, float]:
        """Return raw coordinates as tuple"""
        return (self.x, self.y, self.z)

@dataclass
class Element:
    """Structural element (member) definition"""
    id: int
    node_i: int
    node_j: int
    element_type: str
    tower: str
    connection: str  # "rigid" or "pin"
    length: float    # cm

    def get_revit_category(self) -> str:
        """Map element type to Revit structural category"""
        type_mapping = {
            "column": "StructuralColumns",
            "beam_x": "StructuralFraming",
            "beam_y": "StructuralFraming",
            "brace_xz": "StructuralFraming",
            "brace_yz": "StructuralFraming",
            "shear_wall_xz": "StructuralFraming",
            "floor_brace": "StructuralFraming",
            "bridge_beam": "StructuralFraming",
            "bridge_brace": "StructuralFraming",
            "outrigger": "StructuralFraming",
            "belt_truss": "StructuralFraming",
            "corner_brace": "StructuralFraming",
        }
        return type_mapping.get(self.element_type, "StructuralFraming")

    def get_structural_usage(self) -> str:
        """Determine Revit structural usage"""
        if self.element_type == "column":
            return "Column"
        elif "beam" in self.element_type:
            return "Girder"
        elif "brace" in self.element_type or "shear_wall" in self.element_type:
            return "Brace"
        elif "truss" in self.element_type or "outrigger" in self.element_type:
            return "Joist"
        else:
            return "Other"

# ==============================================================================
# DATA LOADING FUNCTIONS
# ==============================================================================

def load_nodes(filepath: str) -> Dict[int, Node]:
    """
    Load node definitions from CSV file.

    Args:
        filepath: Path to position matrix CSV file

    Returns:
        Dictionary mapping node_id to Node objects

    File Format:
        node_id,x,y,z,floor,zone,tower
        0,0.0,0.0,0.0,0,tower,1
        ...
    """
    nodes = {}

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Position matrix not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tower_val = row['tower']
            # Handle both numeric and string tower values
            if tower_val.isdigit():
                tower_str = tower_val
            else:
                tower_str = tower_val  # "bridge" or other string

            node = Node(
                id=int(row['node_id']),
                x=float(row['x']),
                y=float(row['y']),
                z=float(row['z']),
                floor=int(row['floor']),
                zone=row['zone'],
                tower=tower_str
            )
            nodes[node.id] = node

    print(f"[INFO] Loaded {len(nodes)} nodes from {os.path.basename(filepath)}")
    return nodes

def load_elements(filepath: str) -> List[Element]:
    """
    Load element definitions from CSV file.

    Args:
        filepath: Path to connectivity matrix CSV file

    Returns:
        List of Element objects

    File Format:
        element_id,node_i,node_j,element_type,tower,connection,length
        0,0,32,column,tower1,rigid,9.0
        ...
    """
    elements = []

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Connectivity matrix not found: {filepath}")

    with open(filepath, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            element = Element(
                id=int(row['element_id']),
                node_i=int(row['node_i']),
                node_j=int(row['node_j']),
                element_type=row['element_type'],
                tower=row['tower'],
                connection=row['connection'],
                length=float(row['length'])
            )
            elements.append(element)

    print(f"[INFO] Loaded {len(elements)} elements from {os.path.basename(filepath)}")
    return elements

def analyze_model(nodes: Dict[int, Node], elements: List[Element]) -> dict:
    """
    Analyze the structural model and return statistics.

    Returns:
        Dictionary with model statistics
    """
    stats = {
        'total_nodes': len(nodes),
        'total_elements': len(elements),
        'element_types': defaultdict(int),
        'floors': set(),
        'towers': set(),
        'bounding_box': {
            'x_min': float('inf'), 'x_max': float('-inf'),
            'y_min': float('inf'), 'y_max': float('-inf'),
            'z_min': float('inf'), 'z_max': float('-inf'),
        }
    }

    for node in nodes.values():
        stats['floors'].add(node.floor)
        stats['towers'].add(node.tower)
        stats['bounding_box']['x_min'] = min(stats['bounding_box']['x_min'], node.x)
        stats['bounding_box']['x_max'] = max(stats['bounding_box']['x_max'], node.x)
        stats['bounding_box']['y_min'] = min(stats['bounding_box']['y_min'], node.y)
        stats['bounding_box']['y_max'] = max(stats['bounding_box']['y_max'], node.y)
        stats['bounding_box']['z_min'] = min(stats['bounding_box']['z_min'], node.z)
        stats['bounding_box']['z_max'] = max(stats['bounding_box']['z_max'], node.z)

    for element in elements:
        stats['element_types'][element.element_type] += 1

    return stats

# ==============================================================================
# REVIT API INTERFACE (Abstract Base)
# ==============================================================================

class RevitExporter:
    """
    Abstract base class for Revit API export.

    This class defines the interface for creating Revit elements.
    Implementations are provided for different Revit API access methods:
    - RevitPythonShell (IronPython)
    - pyRevit
    - Dynamo Python node
    - External command (C# wrapper)

    Note: The actual Revit API calls require running inside Revit.
    This script provides the data preparation and can generate
    intermediate files (JSON/XML) for import via Dynamo.
    """

    def __init__(self, nodes: Dict[int, Node], elements: List[Element]):
        self.nodes = nodes
        self.elements = elements
        self.scale_to_real = True  # Export at full scale (1:1)
        self._created_levels = {}
        self._created_elements = []

    def set_scale(self, scale_to_real: bool):
        """Set whether to scale model to real dimensions"""
        self.scale_to_real = scale_to_real

    def create_levels(self) -> dict:
        """Create Revit levels for each floor"""
        raise NotImplementedError("Subclass must implement create_levels")

    def create_material(self) -> object:
        """Create Balsa wood material definition"""
        raise NotImplementedError("Subclass must implement create_material")

    def create_section(self) -> object:
        """Create 6x6mm structural section family"""
        raise NotImplementedError("Subclass must implement create_section")

    def create_column(self, element: Element) -> object:
        """Create a structural column"""
        raise NotImplementedError("Subclass must implement create_column")

    def create_beam(self, element: Element) -> object:
        """Create a structural beam/brace"""
        raise NotImplementedError("Subclass must implement create_beam")

    def export_all(self) -> dict:
        """Export entire model to Revit"""
        raise NotImplementedError("Subclass must implement export_all")

# ==============================================================================
# DYNAMO/JSON EXPORT (External Method)
# ==============================================================================

def export_to_dynamo_json(nodes: Dict[int, Node], elements: List[Element],
                          output_path: str, scale_to_real: bool = True) -> str:
    """
    Export model data to JSON format for Dynamo import.

    This method creates a JSON file that can be read by a Dynamo
    graph to create the structural model in Revit.

    Args:
        nodes: Dictionary of Node objects
        elements: List of Element objects
        output_path: Path to output JSON file
        scale_to_real: If True, scale to real dimensions (76.5m height)

    Returns:
        Path to created JSON file

    JSON Structure:
    {
        "metadata": {...},
        "levels": [...],
        "nodes": [...],
        "elements": {...}
    }
    """
    import json

    # Determine scale factor
    scale_factor = MODEL_SCALE if scale_to_real else 1.0

    # Prepare metadata
    metadata = {
        "project": "DASK 2025 Twin Towers",
        "version": "V9",
        "scale": f"1:{MODEL_SCALE}" if not scale_to_real else "1:1 (Real Scale)",
        "units": "meters" if scale_to_real else "centimeters",
        "element_count": len(elements),
        "node_count": len(nodes),
        "material": {
            "name": MATERIAL_NAME,
            "youngs_modulus_mpa": YOUNGS_MODULUS_MPA,
            "density_kg_m3": DENSITY_KG_M3
        },
        "section": {
            "width_mm": SECTION_WIDTH_MM * (scale_factor if scale_to_real else 1),
            "height_mm": SECTION_HEIGHT_MM * (scale_factor if scale_to_real else 1)
        }
    }

    # Prepare levels
    levels = []
    for floor, elevation_cm in FLOOR_ELEVATIONS.items():
        if scale_to_real:
            elevation_m = elevation_cm * scale_factor / 100.0  # cm to m
        else:
            elevation_m = elevation_cm / 100.0
        levels.append({
            "floor": floor,
            "name": f"Level_{floor:02d}",
            "elevation_m": round(elevation_m, 3)
        })

    # Prepare nodes
    nodes_list = []
    for node_id, node in nodes.items():
        if scale_to_real:
            # Convert cm to m and scale
            x_m = node.x * scale_factor / 100.0
            y_m = node.y * scale_factor / 100.0
            z_m = node.z * scale_factor / 100.0
        else:
            # Just convert cm to m (model scale)
            x_m = node.x / 100.0
            y_m = node.y / 100.0
            z_m = node.z / 100.0

        nodes_list.append({
            "id": node_id,
            "x": round(x_m, 4),
            "y": round(y_m, 4),
            "z": round(z_m, 4),
            "floor": node.floor,
            "tower": node.tower
        })

    # Prepare elements grouped by type
    elements_by_type = defaultdict(list)
    for elem in elements:
        node_i = nodes[elem.node_i]
        node_j = nodes[elem.node_j]

        if scale_to_real:
            start = [
                round(node_i.x * scale_factor / 100.0, 4),
                round(node_i.y * scale_factor / 100.0, 4),
                round(node_i.z * scale_factor / 100.0, 4)
            ]
            end = [
                round(node_j.x * scale_factor / 100.0, 4),
                round(node_j.y * scale_factor / 100.0, 4),
                round(node_j.z * scale_factor / 100.0, 4)
            ]
            length_m = elem.length * scale_factor / 100.0
        else:
            start = [
                round(node_i.x / 100.0, 4),
                round(node_i.y / 100.0, 4),
                round(node_i.z / 100.0, 4)
            ]
            end = [
                round(node_j.x / 100.0, 4),
                round(node_j.y / 100.0, 4),
                round(node_j.z / 100.0, 4)
            ]
            length_m = elem.length / 100.0

        elem_data = {
            "id": elem.id,
            "node_i": elem.node_i,
            "node_j": elem.node_j,
            "start": start,
            "end": end,
            "length_m": round(length_m, 4),
            "connection": elem.connection,
            "tower": elem.tower,
            "revit_category": elem.get_revit_category(),
            "structural_usage": elem.get_structural_usage()
        }
        elements_by_type[elem.element_type].append(elem_data)

    # Combine all data
    export_data = {
        "metadata": metadata,
        "levels": levels,
        "nodes": nodes_list,
        "elements": dict(elements_by_type)
    }

    # Write JSON file
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Exported Dynamo JSON to: {output_path}")
    return output_path

# ==============================================================================
# REVIT PYTHON SHELL IMPLEMENTATION
# ==============================================================================

def generate_rps_script(nodes: Dict[int, Node], elements: List[Element],
                       output_path: str, scale_to_real: bool = True) -> str:
    """
    Generate a Revit Python Shell (RPS) script for model creation.

    This function creates a self-contained IronPython script that can be
    executed directly in Revit Python Shell to create the structural model.

    Args:
        nodes: Dictionary of Node objects
        elements: List of Element objects
        output_path: Path to output .py script file
        scale_to_real: If True, scale to real dimensions

    Returns:
        Path to generated script file
    """
    scale_factor = MODEL_SCALE if scale_to_real else 1.0

    # Calculate section dimensions for real scale
    if scale_to_real:
        section_mm = SECTION_WIDTH_MM * scale_factor  # 6mm * 50 = 300mm = 30cm
        section_str = f"{section_mm:.0f}mm x {section_mm:.0f}mm"
    else:
        section_str = f"{SECTION_WIDTH_MM:.0f}mm x {SECTION_HEIGHT_MM:.0f}mm"

    script_content = f'''# -*- coding: utf-8 -*-
"""
================================================================================
DASK V9 Twin Towers - Revit Python Shell Import Script
================================================================================

Generated: February 2026
Model Version: V9 (Final)
Scale: {"1:1 (Real Scale - 76.5m height)" if scale_to_real else "1:50 (Model Scale - 153cm height)"}
Section: {section_str}

USAGE:
1. Open Revit with a structural template
2. Open Revit Python Shell (RPS) or pyRevit Python console
3. Copy and paste this entire script
4. Press Execute/Run

REQUIREMENTS:
- Revit 2020 or later
- Revit Python Shell or pyRevit
- Structural template with appropriate family types

================================================================================
"""

# Standard library imports
import clr
import math
from collections import defaultdict

# Revit API imports
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import *
from Autodesk.Revit.UI import *

# Get current document
doc = __revit__.ActiveUIDocument.Document
uidoc = __revit__.ActiveUIDocument

# ==============================================================================
# CONFIGURATION
# ==============================================================================

SCALE_TO_REAL = {scale_to_real}
MODEL_SCALE = {MODEL_SCALE}
SCALE_FACTOR = MODEL_SCALE if SCALE_TO_REAL else 1.0

# Unit conversion (cm to internal units - feet)
CM_TO_FEET = 0.0328084
SCALE_CM_TO_FEET = CM_TO_FEET * SCALE_FACTOR

# Section size (for family selection)
SECTION_SIZE_MM = {SECTION_WIDTH_MM} * SCALE_FACTOR  # {section_str}

# ==============================================================================
# NODE DATA (Embedded from twin_position_matrix_v9.csv)
# ==============================================================================

NODES = {{
'''

    # Embed node data
    for node_id, node in sorted(nodes.items()):
        script_content += f"    {node_id}: ({node.x}, {node.y}, {node.z}, {node.floor}, '{node.tower}'),\n"

    script_content += '''}

# ==============================================================================
# ELEMENT DATA (Embedded from twin_connectivity_matrix_v9.csv)
# ==============================================================================

ELEMENTS = [
'''

    # Embed element data
    for elem in elements:
        script_content += f'    ({elem.id}, {elem.node_i}, {elem.node_j}, "{elem.element_type}", "{elem.tower}", "{elem.connection}", {elem.length}),\n'

    script_content += ''']

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_or_create_level(elevation_ft, name):
    """Get existing level or create new one at specified elevation"""
    # Find existing levels
    levels = FilteredElementCollector(doc).OfClass(Level).ToElements()

    for level in levels:
        if abs(level.Elevation - elevation_ft) < 0.01:  # Tolerance: ~3mm
            return level

    # Create new level
    level = Level.Create(doc, elevation_ft)
    level.Name = name
    return level

def find_framing_type(type_name_contains=None):
    """Find a structural framing family type"""
    collector = FilteredElementCollector(doc)
    framing_types = collector.OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_StructuralFraming).ToElements()

    if type_name_contains:
        for ft in framing_types:
            if type_name_contains.lower() in Element.Name.GetValue(ft).lower():
                if not ft.IsActive:
                    ft.Activate()
                return ft

    # Return first available
    if framing_types:
        ft = framing_types[0]
        if not ft.IsActive:
            ft.Activate()
        return ft

    return None

def find_column_type(type_name_contains=None):
    """Find a structural column family type"""
    collector = FilteredElementCollector(doc)
    column_types = collector.OfClass(FamilySymbol).OfCategory(BuiltInCategory.OST_StructuralColumns).ToElements()

    if type_name_contains:
        for ct in column_types:
            if type_name_contains.lower() in Element.Name.GetValue(ct).lower():
                if not ct.IsActive:
                    ct.Activate()
                return ct

    # Return first available
    if column_types:
        ct = column_types[0]
        if not ct.IsActive:
            ct.Activate()
        return ct

    return None

def create_line(start_xyz, end_xyz):
    """Create a Revit Line from two coordinate tuples"""
    x1, y1, z1 = start_xyz
    x2, y2, z2 = end_xyz

    # Convert to Revit internal units (feet)
    start_pt = XYZ(x1 * SCALE_CM_TO_FEET, y1 * SCALE_CM_TO_FEET, z1 * SCALE_CM_TO_FEET)
    end_pt = XYZ(x2 * SCALE_CM_TO_FEET, y2 * SCALE_CM_TO_FEET, z2 * SCALE_CM_TO_FEET)

    return Line.CreateBound(start_pt, end_pt)

# ==============================================================================
# MAIN EXPORT FUNCTION
# ==============================================================================

def export_model():
    """Main function to create the structural model in Revit"""

    print("=" * 60)
    print("DASK V9 Twin Towers - Revit Import")
    print("=" * 60)

    # Statistics
    stats = defaultdict(int)
    created_elements = []
    errors = []

    # Start transaction
    t = Transaction(doc, "Import DASK V9 Model")
    t.Start()

    try:
        # Create levels
        print("\\n[1/4] Creating levels...")
        levels = {{}}
        floor_elevations = {{0: 0.0, 1: 9.0}}
        for i in range(2, 26):
            floor_elevations[i] = 9.0 + (i - 1) * 6.0

        for floor, elev_cm in floor_elevations.items():
            elev_ft = elev_cm * SCALE_CM_TO_FEET
            elev_m = elev_cm * SCALE_FACTOR / 100.0  # Convert to real meters
            level_name = "Floor_{{:02d}}".format(floor)
            levels[floor] = get_or_create_level(elev_ft, level_name)
            print("  Created level: {{}} at {{:.2f}} m".format(level_name, elev_m))

        # Get family types
        print("\\n[2/4] Loading family types...")
        column_type = find_column_type("W10" if SCALE_TO_REAL else "HSS")
        beam_type = find_framing_type("W10" if SCALE_TO_REAL else "HSS")
        brace_type = find_framing_type("HSS" if SCALE_TO_REAL else "L")

        if not column_type:
            print("  WARNING: No column type found, using generic")
        if not beam_type:
            print("  WARNING: No beam type found, using generic")

        print("  Column type: {{}}".format(Element.Name.GetValue(column_type) if column_type else "None"))
        print("  Beam type: {{}}".format(Element.Name.GetValue(beam_type) if beam_type else "None"))
        print("  Brace type: {{}}".format(Element.Name.GetValue(brace_type) if brace_type else "None"))

        # Create structural elements
        print("\\n[3/4] Creating structural elements...")

        for elem_data in ELEMENTS:
            elem_id, node_i, node_j, elem_type, tower, connection, length = elem_data

            # Get node coordinates
            ni = NODES[node_i]
            nj = NODES[node_j]

            start_xyz = (ni[0], ni[1], ni[2])
            end_xyz = (nj[0], nj[1], nj[2])

            try:
                # Create geometry line
                line = create_line(start_xyz, end_xyz)

                # Determine base level
                floor_i = ni[3]
                floor_j = nj[3]
                base_floor = min(floor_i, floor_j)
                base_level = levels.get(base_floor, levels[0])

                if elem_type == "column":
                    # Create structural column
                    if column_type:
                        # Get start and end points
                        start_pt = line.GetEndPoint(0)
                        end_pt = line.GetEndPoint(1)

                        # Ensure bottom to top order
                        if start_pt.Z > end_pt.Z:
                            start_pt, end_pt = end_pt, start_pt

                        # Find top level
                        top_floor = max(floor_i, floor_j)
                        top_level = levels.get(top_floor, levels[25])

                        # Create column
                        column = doc.Create.NewFamilyInstance(
                            start_pt,
                            column_type,
                            base_level,
                            StructuralType.Column
                        )

                        # Set top constraint
                        column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM).Set(top_level.Id)

                        created_elements.append(column.Id)
                        stats['columns'] += 1

                elif elem_type in ["beam_x", "beam_y", "bridge_beam"]:
                    # Create structural beam
                    if beam_type:
                        beam = doc.Create.NewFamilyInstance(
                            line,
                            beam_type,
                            base_level,
                            StructuralType.Beam
                        )
                        created_elements.append(beam.Id)
                        stats['beams'] += 1

                else:
                    # Create brace
                    framing_type = brace_type if brace_type else beam_type
                    if framing_type:
                        brace = doc.Create.NewFamilyInstance(
                            line,
                            framing_type,
                            base_level,
                            StructuralType.Brace
                        )
                        created_elements.append(brace.Id)
                        stats['braces'] += 1

            except Exception as ex:
                errors.append("Element {{}}: {{}}".format(elem_id, str(ex)))

        # Commit transaction
        t.Commit()

        # Print summary
        print("\\n[4/4] Import complete!")
        print("=" * 60)
        print("SUMMARY:")
        print("  Columns created: {{}}".format(stats['columns']))
        print("  Beams created: {{}}".format(stats['beams']))
        print("  Braces created: {{}}".format(stats['braces']))
        print("  Total elements: {{}}".format(len(created_elements)))
        print("  Errors: {{}}".format(len(errors)))

        if errors:
            print("\\nERRORS (first 10):")
            for err in errors[:10]:
                print("  " + err)

        print("=" * 60)

    except Exception as ex:
        t.RollBack()
        print("CRITICAL ERROR: {{}}".format(str(ex)))
        raise

# ==============================================================================
# EXECUTE
# ==============================================================================

if __name__ == "__main__":
    export_model()
'''

    # Fix escaped braces from template (convert {{ to { and }} to })
    # This is needed because some parts of the template use regular strings
    # instead of f-strings, so the brace escaping doesn't get processed
    script_content = script_content.replace('{{', '{').replace('}}', '}')

    # Write script file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(script_content)

    print(f"[INFO] Generated RPS script: {output_path}")
    return output_path

# ==============================================================================
# IFC EXPORT (Alternative Method)
# ==============================================================================

def export_to_ifc(nodes: Dict[int, Node], elements: List[Element],
                  output_path: str, scale_to_real: bool = True) -> str:
    """
    Export model to IFC format for Revit import.

    IFC (Industry Foundation Classes) is a neutral file format supported
    by Revit and other BIM software. This method creates a minimal IFC
    file containing the structural frame.

    Note: This is a simplified IFC exporter. For production use,
    consider using IfcOpenShell library.

    Args:
        nodes: Dictionary of Node objects
        elements: List of Element objects
        output_path: Path to output .ifc file
        scale_to_real: If True, scale to real dimensions

    Returns:
        Path to created IFC file
    """
    from datetime import datetime

    scale_factor = MODEL_SCALE if scale_to_real else 1.0
    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # IFC header
    ifc_content = f'''ISO-10303-21;
HEADER;
FILE_DESCRIPTION(('DASK V9 Twin Towers Structural Model'),'2;1');
FILE_NAME('{os.path.basename(output_path)}','{timestamp}',('DASK Team'),('Structural Engineering'),'','','');
FILE_SCHEMA(('IFC4'));
ENDSEC;
DATA;
/* Project Setup */
#1=IFCPROJECT('2aG1X$P0T5Y9s3Nh4MnQqR',#2,'DASK_V9_Twin_Towers',$,$,$,$,(#10),#9);
#2=IFCOWNERHISTORY(#3,#6,$,.ADDED.,{int(datetime.now().timestamp())},$,$,$);
#3=IFCPERSONANDORGANIZATION(#4,#5,$);
#4=IFCPERSON($,'DASK','Team',$,$,$,$,$);
#5=IFCORGANIZATION($,'DASK_Project','DASK 2025',$,$);
#6=IFCAPPLICATION(#5,'1.0','DASK_Export','DASK');
#7=IFCDIRECTION((1.,0.,0.));
#8=IFCDIRECTION((0.,0.,1.));
#9=IFCUNITASSIGNMENT((#20,#21,#22));
#10=IFCGEOMETRICREPRESENTATIONCONTEXT($,'Model',3,1.E-05,#11,$);
#11=IFCAXIS2PLACEMENT3D(#12,$,$);
#12=IFCCARTESIANPOINT((0.,0.,0.));
/* Units - Meters */
#20=IFCSIUNIT(*,.LENGTHUNIT.,$,.METRE.);
#21=IFCSIUNIT(*,.AREAUNIT.,$,.SQUARE_METRE.);
#22=IFCSIUNIT(*,.VOLUMEUNIT.,$,.CUBIC_METRE.);
/* Site and Building */
#30=IFCSITE('3bH2Y$Q1U6Z0t4Pi5NoPrS',#2,'Site',$,$,#31,$,$,.ELEMENT.,$,$,$,$,$);
#31=IFCLOCALPLACEMENT($,#11);
#40=IFCBUILDING('4cI3Z$R2V7A1u5Qj6OpQsT',#2,'DASK_Twin_Towers',$,$,#41,$,$,.ELEMENT.,$,$,$);
#41=IFCLOCALPLACEMENT(#31,#11);
#42=IFCRELAGGREGATES('5dJ4A$S3W8B2v6Rk7PqRtU',#2,$,$,#1,(#30));
#43=IFCRELAGGREGATES('6eK5B$T4X9C3w7Sl8QrSuV',#2,$,$,#30,(#40));
/* Building Storeys */
'''

    # Create building storeys (floors)
    storey_ids = {}
    storey_start_id = 100
    for floor, elev_cm in FLOOR_ELEVATIONS.items():
        storey_id = storey_start_id + floor
        elev_m = elev_cm * scale_factor / 100.0
        storey_name = f"Floor_{floor:02d}"
        ifc_content += f'#{storey_id}=IFCBUILDINGSTOREY(\'{floor}eL6C$U5Y0D4x8Tm9RsTvW\',#2,\'{storey_name}\',$,$,#41,$,$,.ELEMENT.,{elev_m});\n'
        storey_ids[floor] = storey_id

    # Aggregate storeys to building
    storey_refs = ','.join([f'#{sid}' for sid in storey_ids.values()])
    ifc_content += f'#199=IFCRELAGGREGATES(\'7fM7D$V6Z1E5y9Un0StUwX\',#2,$,$,#40,({storey_refs}));\n'

    # Section profile (6mm x 6mm scaled)
    section_m = SECTION_WIDTH_MM * scale_factor / 1000.0
    ifc_content += f'''/* Section Profile */
#200=IFCRECTANGLEPROFILEDEF(.AREA.,'6x6_Section',#11,{section_m},{section_m});
/* Material */
#210=IFCMATERIAL('Balsa_Wood',$,$);
'''

    # Create structural members
    element_start_id = 1000
    for elem in elements:
        elem_ifc_id = element_start_id + elem.id
        node_i = nodes[elem.node_i]
        node_j = nodes[elem.node_j]

        # Scale coordinates
        x1 = node_i.x * scale_factor / 100.0
        y1 = node_i.y * scale_factor / 100.0
        z1 = node_i.z * scale_factor / 100.0
        x2 = node_j.x * scale_factor / 100.0
        y2 = node_j.y * scale_factor / 100.0
        z2 = node_j.z * scale_factor / 100.0

        # Determine element type
        if elem.element_type == "column":
            ifc_type = "IFCCOLUMN"
        elif "beam" in elem.element_type:
            ifc_type = "IFCBEAM"
        else:
            ifc_type = "IFCMEMBER"

        # Create points and line
        pt1_id = elem_ifc_id * 10 + 1
        pt2_id = elem_ifc_id * 10 + 2
        line_id = elem_ifc_id * 10 + 3
        shape_id = elem_ifc_id * 10 + 4

        ifc_content += f'''/* Element {elem.id}: {elem.element_type} */
#{pt1_id}=IFCCARTESIANPOINT(({x1},{y1},{z1}));
#{pt2_id}=IFCCARTESIANPOINT(({x2},{y2},{z2}));
#{line_id}=IFCPOLYLINE((#{pt1_id},#{pt2_id}));
#{elem_ifc_id}={ifc_type}('{elem.id}gN8E$W7A2F6z0Vo1TuVxY',#2,'E{elem.id}',$,$,#41,#{shape_id},$,$);
'''

    # Close IFC file
    ifc_content += '''ENDSEC;
END-ISO-10303-21;
'''

    # Write file
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(ifc_content)

    print(f"[INFO] Exported IFC file: {output_path}")
    return output_path

# ==============================================================================
# SAT/STEP EXPORT (Geometry Only)
# ==============================================================================

def export_geometry_sat(nodes: Dict[int, Node], elements: List[Element],
                        output_path: str, scale_to_real: bool = True) -> str:
    """
    Export model geometry to SAT (ACIS) format.

    SAT files can be imported into Revit as In-Place masses or
    imported geometry. This is useful for visualization but
    doesn't preserve structural properties.

    Args:
        nodes: Dictionary of Node objects
        elements: List of Element objects
        output_path: Path to output .sat file
        scale_to_real: If True, scale to real dimensions

    Returns:
        Path to created SAT file
    """
    # Note: SAT format is complex. Here we create a simplified ASCII version
    # that defines line segments as wire bodies.

    scale_factor = MODEL_SCALE if scale_to_real else 1.0

    sat_content = '''700 0 1 0
16 DASK_V9_Export 13 ACIS 33.0 NT 24 Sat Feb 04 12:00:00 2026
1 9.9999999999999995e-007 1e-010
body $-1 -1 $-1 $1 $-1 $-1 #
'''

    # Create wire body for each element
    for i, elem in enumerate(elements):
        node_i = nodes[elem.node_i]
        node_j = nodes[elem.node_j]

        x1 = node_i.x * scale_factor / 100.0  # Convert to meters
        y1 = node_i.y * scale_factor / 100.0
        z1 = node_i.z * scale_factor / 100.0
        x2 = node_j.x * scale_factor / 100.0
        y2 = node_j.y * scale_factor / 100.0
        z2 = node_j.z * scale_factor / 100.0

        # Add straight line segment
        sat_content += f'straight-curve $-1 {x1} {y1} {z1} {x2-x1} {y2-y1} {z2-z1} I I #\n'

    sat_content += 'End-of-ACIS-data\n'

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(sat_content)

    print(f"[INFO] Exported SAT geometry: {output_path}")
    return output_path

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================

def main():
    """Main execution function"""
    print("=" * 70)
    print("DASK V9 MODEL - REVIT API EXPORT")
    print("=" * 70)

    # Load model data
    print("\n[1] Loading model data...")
    nodes = load_nodes(POSITION_FILE)
    elements = load_elements(CONNECTIVITY_FILE)

    # Analyze model
    print("\n[2] Analyzing model...")
    stats = analyze_model(nodes, elements)
    print(f"    Total nodes: {stats['total_nodes']}")
    print(f"    Total elements: {stats['total_elements']}")
    print(f"    Floors: {min(stats['floors'])} - {max(stats['floors'])}")
    print(f"    Towers: {stats['towers']}")
    print(f"    Bounding box: X[{stats['bounding_box']['x_min']:.1f}, {stats['bounding_box']['x_max']:.1f}] cm")
    print(f"                  Y[{stats['bounding_box']['y_min']:.1f}, {stats['bounding_box']['y_max']:.1f}] cm")
    print(f"                  Z[{stats['bounding_box']['z_min']:.1f}, {stats['bounding_box']['z_max']:.1f}] cm")
    print("\n    Element types:")
    for elem_type, count in sorted(stats['element_types'].items()):
        print(f"      {elem_type}: {count}")

    # Create output directory
    export_dir = os.path.join(BASE_DIR, "exports", "revit")
    os.makedirs(export_dir, exist_ok=True)

    # Generate exports (both model scale and real scale)
    print("\n[3] Generating export files...")

    # Dynamo JSON (Real Scale)
    json_path_real = os.path.join(export_dir, "dask_v9_real_scale.json")
    export_to_dynamo_json(nodes, elements, json_path_real, scale_to_real=True)

    # Dynamo JSON (Model Scale)
    json_path_model = os.path.join(export_dir, "dask_v9_model_scale.json")
    export_to_dynamo_json(nodes, elements, json_path_model, scale_to_real=False)

    # Revit Python Shell script (Real Scale)
    rps_path_real = os.path.join(export_dir, "dask_v9_revit_import_real.py")
    generate_rps_script(nodes, elements, rps_path_real, scale_to_real=True)

    # Revit Python Shell script (Model Scale)
    rps_path_model = os.path.join(export_dir, "dask_v9_revit_import_model.py")
    generate_rps_script(nodes, elements, rps_path_model, scale_to_real=False)

    # IFC Export (Real Scale)
    ifc_path = os.path.join(export_dir, "dask_v9_real_scale.ifc")
    export_to_ifc(nodes, elements, ifc_path, scale_to_real=True)

    print("\n[4] Export complete!")
    print("=" * 70)
    print("GENERATED FILES:")
    print(f"  1. Dynamo JSON (Real Scale):  {json_path_real}")
    print(f"  2. Dynamo JSON (Model Scale): {json_path_model}")
    print(f"  3. RPS Script (Real Scale):   {rps_path_real}")
    print(f"  4. RPS Script (Model Scale):  {rps_path_model}")
    print(f"  5. IFC File (Real Scale):     {ifc_path}")
    print("=" * 70)
    print("\nIMPORT OPTIONS:")
    print("  Option A: Run RPS script in Revit Python Shell")
    print("  Option B: Use Dynamo graph with JSON file")
    print("  Option C: Import IFC file directly into Revit")
    print("=" * 70)

if __name__ == "__main__":
    main()
