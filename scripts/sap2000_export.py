"""
SAP2000 OAPI Export Script v6
- Converts core_wall diagonals to Area Objects (Shells)
- Removes core_wall diagonals from Frames
- Uses robust API calling to handle argument count variations
- Uses dynamic dispatch to avoid type errors
"""

import sys
import os
import pandas as pd
import comtypes.client
import traceback

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# Use paths from config
DATA_DIR = config.DATA_DIR
SAP2000_DIR = config.SAP2000_DIR

# Material and section properties from config
BALSA_E = config.BALSA_E
BALSA_DENSITY = config.BALSA_DENSITY
BALSA_NU = config.BALSA_NU
FRAME_SIZE = config.FRAME_SIZE
WALL_THICK = config.WALL_THICK       

# ---------------------------------------------------------------------------
# Helper: Safe API Caller (Polymorphic)
# ---------------------------------------------------------------------------
def try_api_call(func, name, *args_lists):
    """
    Tries calling func with different argument lists until one works.
    Useful for COM methods where signatures might vary.
    """
    last_ex = None
    for i, args in enumerate(args_lists):
        try:
            # Check for Tuple return (common in comtypes)
            ret = func(*args)
            if isinstance(ret, tuple):
                if ret[0] == 0: return ret
            elif ret == 0:
                return (0, None)
            # If non-zero return, it means API fail logic
        except TypeError as e:
            last_ex = e
            continue
        except Exception as e:
            if "arguments" in str(e) or "parameters" in str(e):
                last_ex = e
                continue
            print(f"  Error invoking {name}: {e}")
            return (1, None)
            
    # print(f"  Failed to call {name}. Last error: {last_ex}")
    return (1, None)

# ---------------------------------------------------------------------------
# Load Data
# ---------------------------------------------------------------------------
print("Loading model data...")
pos_df = pd.read_csv(os.path.join(DATA_DIR, "position_matrix.csv"))
conn_df = pd.read_csv(os.path.join(DATA_DIR, "connectivity_matrix.csv"))

n_nodes = len(pos_df)
n_elements = len(conn_df)
print(f"  Nodes: {n_nodes}, Elements: {n_elements}")

# Convert to mm
pos_df['x_mm'] = pos_df['x'] * 1000
pos_df['y_mm'] = pos_df['y'] * 1000
pos_df['z_mm'] = pos_df['z'] * 1000

# ---------------------------------------------------------------------------
# Connect to SAP2000
# ---------------------------------------------------------------------------
print("\nConnecting to SAP2000...")

import time

sap_object = None
sap_model = None

# Clear any cached type libraries to force regeneration
try:
    import comtypes.gen
    # This helps when SAP2000 version changed
except:
    pass

# Try comtypes with proper interface handling
try:
    # First try to get active instance
    try:
        sap_object = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
        print("  Found running SAP2000 instance")
    except:
        # Create new instance
        print("  Starting new SAP2000 instance...")
        sap_object = comtypes.client.CreateObject("CSI.SAP2000.API.SapObject")
        ret = sap_object.ApplicationStart()
        print(f"  ApplicationStart returned: {ret}")
        time.sleep(3)  # Wait for SAP2000 to fully initialize

    # Access SapModel - try different methods
    try:
        sap_model = sap_object.SapModel
    except:
        # Try accessing via QueryInterface or different method
        print("  Direct SapModel access failed, trying alternative...")
        try:
            # Some versions need this
            sap_model = getattr(sap_object, 'SapModel')
        except:
            # Last resort - try win32com
            import win32com.client
            sap_object = win32com.client.gencache.EnsureDispatch("CSI.SAP2000.API.SapObject")
            sap_object.ApplicationStart()
            time.sleep(3)
            sap_model = sap_object.SapModel

    print("  Connected successfully")

except Exception as e:
    print(f"  Connection error: {e}")
    print("\n  Troubleshooting:")
    print("  1. Close all SAP2000 instances")
    print("  2. Open SAP2000 manually (Run as Administrator)")
    print("  3. Create a new blank model")
    print("  4. Run this script again")
    sys.exit(1)

if sap_model is None:
    print("  Could not get SapModel interface")
    sys.exit(1)

# Initialize
print("Initializing model...")
sap_model.InitializeNewModel(5) # kN_mm_C
sap_model.File.NewBlank()

# Materials
print("Defining materials...")
sap_model.PropMaterial.SetMaterial("BALSA", 6)
sap_model.PropMaterial.SetMPIsotropic("BALSA", BALSA_E, BALSA_NU, 0.0)
weight_per_vol = BALSA_DENSITY * 9.81 / 1e9
sap_model.PropMaterial.SetWeightAndMass("BALSA", 1, weight_per_vol)

# Sections
print("Defining sections...")
sap_model.PropFrame.SetRectangle("BALSA_6x6", "BALSA", FRAME_SIZE, FRAME_SIZE)
sap_model.PropArea.SetShell_1("BALSA_WALL", 1, True, "BALSA", 0.0, WALL_THICK, WALL_THICK)

# ---------------------------------------------------------------------------
# Create Joints
# ---------------------------------------------------------------------------
print(f"Creating {n_nodes} joints...")
node_coords = {} 

for idx, row in pos_df.iterrows():
    nid = int(row['node_id'])
    x, y, z = float(row['x_mm']), float(row['y_mm']), float(row['z_mm'])
    node_coords[nid] = (x, y, z)
    sap_model.PointObj.AddCartesian(x, y, z, f"N{nid}", f"N{nid}")

# ---------------------------------------------------------------------------
# Create Elements (Frames & Areas)
# ---------------------------------------------------------------------------
print("Creating elements (Frames & Areas)...")

created_areas = set()
frame_count = 0
area_count = 0
frame_fallback_count = 0

# Helper to find node by coord
def find_node(tx, ty, tz):
    for nid, (nx, ny, nz) in node_coords.items():
        if abs(nx-tx)<1.0 and abs(ny-ty)<1.0 and abs(nz-tz)<1.0:
            return nid
    return None

for idx, row in conn_df.iterrows():
    etype = row['element_type']

    if 'node_id_i' in row:
        n1, n2 = int(row['node_id_i']), int(row['node_id_j'])
    else:
        n1, n2 = int(row['node_i']), int(row['node_j'])

    elem_id = int(row['element_id'])

    # ---------------------------------------------------------
    # CASE 1: CORE WALL
    # ---------------------------------------------------------
    if etype == 'core_wall':
        p1 = node_coords[n1]
        p2 = node_coords[n2]

        # Sort by Z
        if p1[2] > p2[2]:
            p1, p2 = p2, p1
            n1, n2 = n2, n1

        x1, y1, z1 = p1
        x2, y2, z2 = p2

        n3 = None
        n4 = None

        if abs(y1 - y2) < 1.0: # Planar in XZ
            n3 = find_node(x2, y1, z1)
            n4 = find_node(x1, y2, z2)
        elif abs(x1 - x2) < 1.0: # Planar in YZ
            n3 = find_node(x1, y2, z1)
            n4 = find_node(x2, y1, z2)

        success = False
        panel_key = None
        if n3 is not None and n4 is not None:
            panel_key = tuple(sorted([n1, n2, n3, n4]))

            if panel_key not in created_areas:
                name_u = f"W{area_count}"
                prop = "BALSA_WALL"
                pts = [f"N{n1}", f"N{n3}", f"N{n2}", f"N{n4}"]

                # SAP2000 API: AddByPoint(NumberPoints, PointNames, Name, PropName, UserName)
                try:
                    ret = sap_model.AreaObj.AddByPoint(4, pts, name_u, prop, name_u)
                    # Return is [name, code] where code 0 = success
                    if ret == 0 or (isinstance(ret, (tuple, list)) and ret[-1] == 0):
                        area_count += 1
                        created_areas.add(panel_key)
                        success = True
                        if area_count % 50 == 0:
                            print(f"  Created {area_count} wall panels...")
                except Exception as e:
                    pass  # Will fall back to frame

                if not success:
                    print(f"  Warning: Failed to create wall W{area_count}")
            else:
                success = True # Already created

        # Fallback to Diagonal Frame if Area fails
        if not success and panel_key is not None and panel_key not in created_areas:
             # Create diagonal frame so model isn't empty
             name_u = f"E{elem_id}"
             prop = "BALSA_6x6"
             try:
                 # SAP2000 API: AddByPoint(Point1, Point2, Name, PropName, UserName)
                 ret = sap_model.FrameObj.AddByPoint(f"N{n1}", f"N{n2}", name_u, prop, name_u)
                 # Return is [name, code] where code 0 = success
                 if ret == 0 or (isinstance(ret, (tuple, list)) and ret[-1] == 0):
                     frame_fallback_count += 1
             except:
                 pass

    # ---------------------------------------------------------
    # CASE 2: FRAMES
    # ---------------------------------------------------------
    else:
        name_u = f"E{elem_id}"
        prop = "BALSA_6x6"

        try:
            # SAP2000 API: AddByPoint(Point1, Point2, Name, PropName, UserName)
            ret = sap_model.FrameObj.AddByPoint(f"N{n1}", f"N{n2}", name_u, prop, name_u)
            # Return is [name, code] where code 0 = success
            if ret == 0 or (isinstance(ret, (tuple, list)) and ret[-1] == 0):
                frame_count += 1
                if frame_count % 500 == 0:
                    print(f"  Created {frame_count} frames...")
        except Exception as e:
            if frame_count == 0:
                print(f"  Frame creation error: {e}")

print(f"Done. Created {frame_count} frames, {area_count} wall panels, {frame_fallback_count} fallback braces.")

# ---------------------------------------------------------------------------
# Finish
# ---------------------------------------------------------------------------
base_z = pos_df['z_mm'].min()
count_fix = 0
for idx, row in pos_df.iterrows():
    if abs(row['z_mm'] - base_z) < 1.0:
        sap_model.PointObj.SetRestraint(f"N{int(row['node_id'])}", [True]*6)
        count_fix += 1
print(f"Fixed {count_fix} base nodes.")

sap_model.LoadPatterns.Add("DEAD", 1)
sap_model.LoadPatterns.Add("EQX", 5)
sap_model.LoadPatterns.Add("EQY", 5)

sap_model.View.RefreshView(0, False)
model_path = os.path.join(SAP2000_DIR, "DASK_Building_v2.sdb")
sap_model.File.Save(model_path)
print(f"Model saved to: {model_path}")
