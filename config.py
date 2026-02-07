"""
DASK Project Configuration
Central configuration file for all paths and constants
"""

import os

# Base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Directory paths
SCRIPTS_DIR = os.path.join(BASE_DIR, "scripts")
DATA_DIR = os.path.join(BASE_DIR, "data")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
RESULTS_DATA_DIR = os.path.join(RESULTS_DIR, "data")
RESULTS_VIS_DIR = os.path.join(RESULTS_DIR, "visualizations")
SAP2000_DIR = os.path.join(BASE_DIR, "sap2000_model")
NOTEBOOKS_DIR = os.path.join(BASE_DIR, "notebooks")
EXPORTS_DIR = os.path.join(BASE_DIR, "exports")
GROUND_MOTION_DIR = os.path.join(BASE_DIR, "ground_motion")

# Data files
POSITION_MATRIX = os.path.join(DATA_DIR, "position_matrix.csv")
CONNECTIVITY_MATRIX = os.path.join(DATA_DIR, "connectivity_matrix.csv")
ADJACENCY_MATRIX = os.path.join(DATA_DIR, "adjacency_matrix.csv")
BUILDING_DATA_NPZ = os.path.join(DATA_DIR, "building_data.npz")

# Ground motion files
EARTHQUAKE_FILE = os.path.join(GROUND_MOTION_DIR, "BOL090.AT2")

# SAP2000 model files
SAP2000_MODEL = os.path.join(SAP2000_DIR, "DASK_Building_v2.sdb")

# Result files
EARTHQUAKE_RESULTS_SAP = os.path.join(RESULTS_DATA_DIR, "earthquake_results.csv")
EARTHQUAKE_RESULTS_OPS = os.path.join(RESULTS_DATA_DIR, "earthquake_results_opensees.csv")
STRESS_RESULTS = os.path.join(RESULTS_DATA_DIR, "stress_results.csv")

# Visualization files
STRESS_3D_VIEW = os.path.join(RESULTS_VIS_DIR, "stress_3d_view.html")
STRESS_CHARTS = os.path.join(RESULTS_VIS_DIR, "stress_analysis_charts.html")
CRITICAL_ELEMENTS_3D = os.path.join(RESULTS_VIS_DIR, "critical_elements_3d.html")
FORCE_DISTRIBUTION = os.path.join(RESULTS_VIS_DIR, "force_distribution.html")

# Material Properties - Balsa Wood
BALSA_E = 3500.0          # MPa (Young's modulus)
BALSA_DENSITY = 160.0     # kg/m³
BALSA_NU = 0.3            # Poisson's ratio
BALSA_G = BALSA_E / (2 * (1 + BALSA_NU))  # Shear modulus

# Balsa Strength
BALSA_TENSION_STRENGTH = 15.0      # MPa
BALSA_COMPRESSION_STRENGTH = 12.0  # MPa
BALSA_SHEAR_STRENGTH = 2.5         # MPa

# Section Dimensions (mm) - DASK Competition Specs
FRAME_SIZE = 6.0          # 6mm x 6mm balsa frames
WALL_THICK = 3.0          # 3mm balsa panels

# Frame Section Properties
FRAME_A = FRAME_SIZE ** 2                    # mm² (area)
FRAME_I = (FRAME_SIZE ** 4) / 12             # mm⁴ (moment of inertia)
FRAME_J = 0.1406 * FRAME_SIZE ** 4           # mm⁴ (torsional constant)
FRAME_c = FRAME_SIZE / 2                     # mm (distance to extreme fiber)

# DASK Mass Configuration
MASS_FLOORS_1_60 = [3, 6, 9, 12, 15, 18, 21, 24]  # Floors with 1.60 kg
MASS_FLOOR_ROOF = 25                              # Roof floor
MASS_1_60_KG = 1.60                               # kg per floor
MASS_ROOF_KG = 2.22                               # kg at roof

# Unit conversions
MASS_CONVERSION_OPENSEES = 1e-3   # kg to N·s²/mm for OpenSeesPy
MASS_CONVERSION_SAP2000 = 1e-6    # kg to kN·s²/mm for SAP2000

def ensure_dirs():
    """Create all directories if they don't exist"""
    dirs = [SCRIPTS_DIR, DATA_DIR, RESULTS_DIR, RESULTS_DATA_DIR,
            RESULTS_VIS_DIR, SAP2000_DIR, NOTEBOOKS_DIR, EXPORTS_DIR]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

if __name__ == "__main__":
    print("DASK Project Configuration")
    print("=" * 50)
    print(f"Base Directory: {BASE_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Results Directory: {RESULTS_DIR}")
    print(f"SAP2000 Directory: {SAP2000_DIR}")
    print(f"Ground Motion: {GROUND_MOTION_DIR}")
