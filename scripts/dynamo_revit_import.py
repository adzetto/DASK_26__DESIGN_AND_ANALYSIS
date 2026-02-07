"""
================================================================================
DASK V9 MODEL - DYNAMO PYTHON NODE SCRIPT
================================================================================

Project: DASK 2025 - Twin Towers Earthquake-Resistant Building Design
Purpose: Import structural model into Revit via Dynamo

USAGE IN DYNAMO:
1. Create a new Dynamo graph in Revit
2. Add a Python Script node
3. Copy this entire script into the Python node
4. Connect a "File Path" node with the JSON file path as input
5. Run the graph

INPUT:
    IN[0] - File path to dask_v9_real_scale.json or dask_v9_model_scale.json

OUTPUT:
    OUT - Dictionary with created element IDs and statistics

REQUIRED PACKAGES:
    - Dynamo Revit nodes
    - Python Standard Library (json)

================================================================================
"""

# Dynamo imports
import clr
import json
import sys

# Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')
clr.AddReference('RevitNodes')
clr.AddReference('RevitServices')

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB.Structure import *
from RevitServices.Persistence import DocumentManager
from RevitServices.Transactions import TransactionManager

# Dynamo geometry
clr.AddReference('ProtoGeometry')
from Autodesk.DesignScript.Geometry import *

# ==============================================================================
# CONFIGURATION
# ==============================================================================

# Get current document
doc = DocumentManager.Instance.CurrentDBDocument

# Unit conversion (meters to internal units - feet)
M_TO_FEET = 3.28084

# ==============================================================================
# HELPER FUNCTIONS
# ==============================================================================

def get_or_create_level(doc, elevation_m, name):
    """
    Get existing level at elevation or create new one.

    Parameters:
        doc: Revit document
        elevation_m: Elevation in meters
        name: Level name

    Returns:
        Revit Level element
    """
    elevation_ft = elevation_m * M_TO_FEET

    # Find existing levels
    collector = FilteredElementCollector(doc).OfClass(Level)

    for level in collector:
        if abs(level.Elevation - elevation_ft) < 0.01:
            return level

    # Create new level
    TransactionManager.Instance.EnsureInTransaction(doc)
    level = Level.Create(doc, elevation_ft)
    level.Name = name
    TransactionManager.Instance.TransactionTaskDone()

    return level


def find_family_type(doc, category, type_name_contains=None):
    """
    Find a family type by category and optional name filter.

    Parameters:
        doc: Revit document
        category: BuiltInCategory enum
        type_name_contains: Optional string to search in type name

    Returns:
        FamilySymbol or None
    """
    collector = FilteredElementCollector(doc).OfClass(FamilySymbol).OfCategory(category)

    types = list(collector)

    if type_name_contains:
        for t in types:
            if type_name_contains.lower() in Element.Name.GetValue(t).lower():
                return t

    # Return first available
    return types[0] if types else None


def create_revit_line(start_xyz, end_xyz):
    """
    Create Revit Line from coordinate lists.

    Parameters:
        start_xyz: [x, y, z] in meters
        end_xyz: [x, y, z] in meters

    Returns:
        Autodesk.Revit.DB.Line
    """
    start_pt = XYZ(
        start_xyz[0] * M_TO_FEET,
        start_xyz[1] * M_TO_FEET,
        start_xyz[2] * M_TO_FEET
    )
    end_pt = XYZ(
        end_xyz[0] * M_TO_FEET,
        end_xyz[1] * M_TO_FEET,
        end_xyz[2] * M_TO_FEET
    )

    return Line.CreateBound(start_pt, end_pt)


def create_column(doc, elem_data, levels, column_type):
    """
    Create a structural column.

    Parameters:
        doc: Revit document
        elem_data: Element dictionary from JSON
        levels: Dictionary of floor -> Level
        column_type: FamilySymbol for columns

    Returns:
        ElementId of created column or None
    """
    if not column_type:
        return None

    start = elem_data['start']
    end = elem_data['end']

    # Ensure bottom to top order
    if start[2] > end[2]:
        start, end = end, start

    start_pt = XYZ(
        start[0] * M_TO_FEET,
        start[1] * M_TO_FEET,
        start[2] * M_TO_FEET
    )

    # Find base and top levels
    base_elev = start[2]
    top_elev = end[2]

    base_level = None
    top_level = None

    for floor, level in levels.items():
        level_elev = level.Elevation / M_TO_FEET

        if abs(level_elev - base_elev) < 0.1:
            base_level = level
        if abs(level_elev - top_elev) < 0.1:
            top_level = level

    if not base_level:
        base_level = list(levels.values())[0]
    if not top_level:
        top_level = list(levels.values())[-1]

    # Activate type if needed
    if not column_type.IsActive:
        column_type.Activate()
        doc.Regenerate()

    # Create column
    column = doc.Create.NewFamilyInstance(
        start_pt,
        column_type,
        base_level,
        StructuralType.Column
    )

    # Set top constraint
    param = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM)
    if param:
        param.Set(top_level.Id)

    return column.Id


def create_beam(doc, elem_data, levels, beam_type):
    """
    Create a structural beam.

    Parameters:
        doc: Revit document
        elem_data: Element dictionary from JSON
        levels: Dictionary of floor -> Level
        beam_type: FamilySymbol for beams

    Returns:
        ElementId of created beam or None
    """
    if not beam_type:
        return None

    line = create_revit_line(elem_data['start'], elem_data['end'])

    # Find level at beam elevation
    beam_elev = elem_data['start'][2]
    base_level = list(levels.values())[0]

    for floor, level in levels.items():
        level_elev = level.Elevation / M_TO_FEET
        if abs(level_elev - beam_elev) < 0.1:
            base_level = level
            break

    # Activate type if needed
    if not beam_type.IsActive:
        beam_type.Activate()
        doc.Regenerate()

    # Create beam
    beam = doc.Create.NewFamilyInstance(
        line,
        beam_type,
        base_level,
        StructuralType.Beam
    )

    return beam.Id


def create_brace(doc, elem_data, levels, brace_type):
    """
    Create a structural brace.

    Parameters:
        doc: Revit document
        elem_data: Element dictionary from JSON
        levels: Dictionary of floor -> Level
        brace_type: FamilySymbol for braces

    Returns:
        ElementId of created brace or None
    """
    if not brace_type:
        return None

    line = create_revit_line(elem_data['start'], elem_data['end'])

    # Find base level
    z_min = min(elem_data['start'][2], elem_data['end'][2])
    base_level = list(levels.values())[0]

    for floor, level in levels.items():
        level_elev = level.Elevation / M_TO_FEET
        if level_elev <= z_min:
            base_level = level

    # Activate type if needed
    if not brace_type.IsActive:
        brace_type.Activate()
        doc.Regenerate()

    # Create brace
    brace = doc.Create.NewFamilyInstance(
        line,
        brace_type,
        base_level,
        StructuralType.Brace
    )

    return brace.Id

# ==============================================================================
# MAIN IMPORT FUNCTION
# ==============================================================================

def import_dask_model(json_path):
    """
    Main function to import DASK V9 model from JSON.

    Parameters:
        json_path: Path to JSON export file

    Returns:
        Dictionary with import results
    """
    results = {
        'success': False,
        'levels_created': 0,
        'columns_created': 0,
        'beams_created': 0,
        'braces_created': 0,
        'errors': [],
        'element_ids': []
    }

    try:
        # Load JSON data
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        metadata = data.get('metadata', {})
        levels_data = data.get('levels', [])
        elements_data = data.get('elements', {})

        print("DASK V9 Import - " + metadata.get('project', 'Unknown'))
        print("Scale: " + metadata.get('scale', 'Unknown'))
        print("Elements: " + str(metadata.get('element_count', 0)))

        # Start transaction
        TransactionManager.Instance.EnsureInTransaction(doc)

        # Create levels
        levels = {}
        for level_data in levels_data:
            floor = level_data['floor']
            name = level_data['name']
            elev_m = level_data['elevation_m']

            level = get_or_create_level(doc, elev_m, name)
            levels[floor] = level
            results['levels_created'] += 1

        # Find family types
        column_type = find_family_type(
            doc,
            BuiltInCategory.OST_StructuralColumns,
            "HSS"  # Try to find HSS (Hollow Structural Section)
        )

        beam_type = find_family_type(
            doc,
            BuiltInCategory.OST_StructuralFraming,
            "W10"  # Try to find W-section
        )

        brace_type = find_family_type(
            doc,
            BuiltInCategory.OST_StructuralFraming,
            "HSS"
        )

        # Fallback to any available type
        if not column_type:
            column_type = find_family_type(doc, BuiltInCategory.OST_StructuralColumns)
        if not beam_type:
            beam_type = find_family_type(doc, BuiltInCategory.OST_StructuralFraming)
        if not brace_type:
            brace_type = beam_type

        print("Column type: " + (Element.Name.GetValue(column_type) if column_type else "None"))
        print("Beam type: " + (Element.Name.GetValue(beam_type) if beam_type else "None"))
        print("Brace type: " + (Element.Name.GetValue(brace_type) if brace_type else "None"))

        # Create elements by type
        for elem_type, elems in elements_data.items():
            for elem in elems:
                try:
                    elem_id = None

                    if elem_type == "column":
                        elem_id = create_column(doc, elem, levels, column_type)
                        if elem_id:
                            results['columns_created'] += 1

                    elif elem_type in ["beam_x", "beam_y", "bridge_beam"]:
                        elem_id = create_beam(doc, elem, levels, beam_type)
                        if elem_id:
                            results['beams_created'] += 1

                    else:
                        elem_id = create_brace(doc, elem, levels, brace_type)
                        if elem_id:
                            results['braces_created'] += 1

                    if elem_id:
                        results['element_ids'].append(elem_id)

                except Exception as ex:
                    results['errors'].append(
                        "Element {}: {}".format(elem.get('id', '?'), str(ex))
                    )

        # Commit transaction
        TransactionManager.Instance.TransactionTaskDone()

        results['success'] = True
        results['total_created'] = (
            results['columns_created'] +
            results['beams_created'] +
            results['braces_created']
        )

    except Exception as ex:
        results['errors'].append("Critical error: " + str(ex))

    return results

# ==============================================================================
# DYNAMO NODE EXECUTION
# ==============================================================================

# Get input from Dynamo
json_file_path = IN[0]

# Execute import
if json_file_path:
    result = import_dask_model(json_file_path)
    OUT = result
else:
    OUT = {"error": "No JSON file path provided. Connect a File Path node to IN[0]."}
