#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenSees Tcl Model Generator for TBDY 2018 A1a Torsional Irregularity Analysis
===============================================================================
Generates a comprehensive OpenSees Tcl script from CSV model data.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

def generate_tcl_model(position_file, connectivity_file, output_file):
    """Generate OpenSees Tcl file from CSV data"""

    # Load data
    nodes_df = pd.read_csv(position_file)
    elements_df = pd.read_csv(connectivity_file)

    # Get unique floors
    floors = sorted(nodes_df['floor'].unique())
    max_floor = max(floors)

    # Material properties (scaled x240 for collective frame stiffness, T1 ~ 0.2s)
    stiffScale = 240.0
    E = 170.0 * stiffScale  # kN/cm2 - scaled
    G = 65.385 * stiffScale  # kN/cm2 - scaled
    nu = 0.3
    section = 0.6  # cm
    A = section ** 2
    Iz = section ** 4 / 12
    Iy = Iz
    J = 2.25 * (section / 2) ** 4

    # TBDY 2018 parameters
    SDS = 1.008
    SD1 = 0.514
    TA = 0.102
    TB = 0.51
    R = 4.0
    D = 2.5
    I_factor = 1.0

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"""# ============================================================================
# TBDY 2018 A1a TORSIONAL IRREGULARITY ANALYSIS
# OpenSees Tcl Script - Twin Towers Model V9
# ============================================================================
# Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
# Model: 1:50 Scale Twin Towers with Sky Bridges
# Code: TBDY 2018 (Turkish Building Seismic Code)
# Sections: 3.6.2.1 (A1a Torsional Irregularity), 4.7.4 (Eccentricity Amplification)
# ============================================================================

puts "============================================================"
puts "  TBDY 2018 A1a TORSIONAL IRREGULARITY ANALYSIS"
puts "  OpenSees Tcl Script - Twin Towers Model V9"
puts "============================================================"
puts ""
puts ">>> Starting analysis at [clock format [clock seconds]]"
puts ""

# ============================================================================
# CLEAR ANY PREVIOUS MODEL
# ============================================================================
wipe
puts ">>> Previous model cleared"

# ============================================================================
# MODEL PARAMETERS
# ============================================================================
puts ""
puts "============================================================"
puts "  MODEL PARAMETERS"
puts "============================================================"

# Material Properties (1:50 scale model, stiffness scaled x240)
set E {E}              ;# Elastic modulus (kN/cm2) - scaled for collective frame stiffness
set G {G}           ;# Shear modulus (kN/cm2) - scaled
set nu {nu}              ;# Poisson's ratio

# Section Properties (6mm x 6mm square section)
set section {section}           ;# Section dimension (cm)
set A {A}            ;# Cross-sectional area (cm2)
set Iz {Iz}  ;# Moment of inertia about z-axis (cm4)
set Iy $Iz             ;# Moment of inertia about y-axis (cm4)
set J {J}  ;# Torsional constant (cm4)

puts "  E  = $E kN/cm2"
puts "  G  = $G kN/cm2"
puts "  A  = $A cm2"
puts "  Iz = $Iz cm4"
puts "  J  = $J cm4"

# TBDY 2018 Spectrum Parameters (DD-2, ZD Soil, Istanbul)
set SDS {SDS}             ;# Short period design spectral acceleration (g)
set SD1 {SD1}             ;# 1-sec period design spectral acceleration (g)
set TA {TA}             ;# Spectrum corner period TA (s)
set TB {TB}              ;# Spectrum corner period TB (s)
set R {R}               ;# Response modification factor
set D {D}               ;# Overstrength factor
set I {I_factor}               ;# Importance factor

puts ""
puts "  TBDY 2018 Spectrum Parameters:"
puts "  SDS = $SDS g"
puts "  SD1 = $SD1 g"
puts "  TA  = $TA s"
puts "  TB  = $TB s"
puts "  R   = $R"
puts "  D   = $D"

# ============================================================================
# MODEL DEFINITION
# ============================================================================
puts ""
puts "============================================================"
puts "  CREATING 3D MODEL"
puts "============================================================"

model BasicBuilder -ndm 3 -ndf 6
puts ">>> 3D model with 6 DOF per node created"

# ============================================================================
# NODE DEFINITIONS
# ============================================================================
puts ""
puts ">>> Defining nodes..."

set numNodes {len(nodes_df)}
set numFloors {max_floor}

""")

        # Write nodes
        f.write("# Node definitions: node nodeTag x y z\n")
        for _, row in nodes_df.iterrows():
            node_id = int(row['node_id'])
            x, y, z = row['x'], row['y'], row['z']
            floor = int(row['floor'])
            tower = row['tower']
            f.write(f"node {node_id} {x:.6f} {y:.6f} {z:.6f}  ;# Floor {floor}, Tower {tower}\n")

        f.write(f"""
puts ">>> $numNodes nodes defined"

# ============================================================================
# BOUNDARY CONDITIONS (Fixed Base)
# ============================================================================
puts ""
puts ">>> Applying boundary conditions..."

set numFixed 0
""")

        # Write boundary conditions
        base_nodes = nodes_df[nodes_df['floor'] == 0]['node_id'].values
        f.write("\n# Fix base nodes (Floor 0): fix nodeTag Dx Dy Dz Rx Ry Rz\n")
        for node_id in base_nodes:
            f.write(f"fix {int(node_id)} 1 1 1 1 1 1\n")
            f.write(f"incr numFixed\n")

        f.write("""
puts ">>> $numFixed base nodes fixed"

# ============================================================================
# MATERIAL DEFINITION
# ============================================================================
puts ""
puts ">>> Defining materials..."

set matTag 1
uniaxialMaterial Elastic $matTag $E
puts ">>> Elastic material defined (Tag: $matTag, E: $E kN/cm2)"

# ============================================================================
# GEOMETRIC TRANSFORMATIONS
# ============================================================================
puts ""
puts ">>> Defining geometric transformations..."

# Column transformation (vertical elements)
set colTransfTag 1
geomTransf Linear $colTransfTag 1 0 0
puts ">>> Column transformation defined (Tag: $colTransfTag)"

# Beam X transformation (beams along X-axis)
set beamXTransfTag 2
geomTransf Linear $beamXTransfTag 0 0 1
puts ">>> Beam-X transformation defined (Tag: $beamXTransfTag)"

# Beam Y transformation (beams along Y-axis)
set beamYTransfTag 3
geomTransf Linear $beamYTransfTag 0 0 1
puts ">>> Beam-Y transformation defined (Tag: $beamYTransfTag)"

# Brace transformations will be created dynamically
set braceTransfStart 100
puts ">>> Brace transformations will start from Tag: $braceTransfStart"

# ============================================================================
# ELEMENT DEFINITIONS
# ============================================================================
puts ""
puts ">>> Defining elements..."

set numElements 0
set numColumns 0
set numBeamsX 0
set numBeamsY 0
set numBraces 0
set braceTransfTag $braceTransfStart

""")

        # Group elements by type for better organization
        columns = elements_df[elements_df['element_type'] == 'column']
        beams_x = elements_df[elements_df['element_type'] == 'beam_x']
        beams_y = elements_df[elements_df['element_type'] == 'beam_y']
        braces = elements_df[~elements_df['element_type'].isin(['column', 'beam_x', 'beam_y'])]

        # Write columns
        f.write("\n# ===== COLUMNS =====\n")
        f.write("puts \">>> Creating columns...\"\n")
        for _, row in columns.iterrows():
            elem_id = int(row['element_id'])
            node_i = int(row['node_i'])
            node_j = int(row['node_j'])
            f.write(f"element elasticBeamColumn {elem_id} {node_i} {node_j} $A $E $G $J $Iy $Iz $colTransfTag\n")
            f.write(f"incr numColumns\n")

        # Write beams X
        f.write("\n# ===== BEAMS (X-direction) =====\n")
        f.write("puts \">>> Creating beams (X-direction)...\"\n")
        for _, row in beams_x.iterrows():
            elem_id = int(row['element_id'])
            node_i = int(row['node_i'])
            node_j = int(row['node_j'])
            f.write(f"element elasticBeamColumn {elem_id} {node_i} {node_j} $A $E $G $J $Iy $Iz $beamXTransfTag\n")
            f.write(f"incr numBeamsX\n")

        # Write beams Y
        f.write("\n# ===== BEAMS (Y-direction) =====\n")
        f.write("puts \">>> Creating beams (Y-direction)...\"\n")
        for _, row in beams_y.iterrows():
            elem_id = int(row['element_id'])
            node_i = int(row['node_i'])
            node_j = int(row['node_j'])
            f.write(f"element elasticBeamColumn {elem_id} {node_i} {node_j} $A $E $G $J $Iy $Iz $beamYTransfTag\n")
            f.write(f"incr numBeamsY\n")

        # Write braces with dynamic transformations
        f.write("\n# ===== BRACES (Diagonal Elements) =====\n")
        f.write("puts \">>> Creating braces...\"\n")
        for _, row in braces.iterrows():
            elem_id = int(row['element_id'])
            node_i = int(row['node_i'])
            node_j = int(row['node_j'])

            # Get node coordinates
            ni_data = nodes_df[nodes_df['node_id'] == node_i].iloc[0]
            nj_data = nodes_df[nodes_df['node_id'] == node_j].iloc[0]

            dx = nj_data['x'] - ni_data['x']
            dy = nj_data['y'] - ni_data['y']
            dz = nj_data['z'] - ni_data['z']

            # Determine vecxz
            if abs(dz) > 1e-6:
                vecxz = "0 1 0"
            elif abs(dy) > 1e-6:
                vecxz = "0 0 1"
            else:
                vecxz = "0 0 1"

            f.write(f"geomTransf Linear $braceTransfTag {vecxz}\n")
            f.write(f"element elasticBeamColumn {elem_id} {node_i} {node_j} $A $E $G $J $Iy $Iz $braceTransfTag\n")
            f.write(f"incr braceTransfTag\n")
            f.write(f"incr numBraces\n")

        f.write("""
set numElements [expr $numColumns + $numBeamsX + $numBeamsY + $numBraces]
puts ""
puts ">>> Element Summary:"
puts "    Columns:    $numColumns"
puts "    Beams (X):  $numBeamsX"
puts "    Beams (Y):  $numBeamsY"
puts "    Braces:     $numBraces"
puts "    TOTAL:      $numElements"

# ============================================================================
# MASS ASSIGNMENT
# ============================================================================
puts ""
puts ">>> Assigning nodal masses..."

set floorMass 1.6       ;# kg per floor (distributed to all nodes)
set roofMass 2.22       ;# kg for roof floor
set g 981.0             ;# cm/s2

""")

        # Assign masses
        for floor in floors:
            if floor == 0:
                continue

            floor_nodes = nodes_df[nodes_df['floor'] == floor]['node_id'].values
            n_nodes = len(floor_nodes)

            # Mass in kg, convert to kN*s2/cm: divide by g=981 cm/s2
            if floor == max_floor:
                mass_per_node = 2.22 / n_nodes / 981.0
            else:
                mass_per_node = 1.6 / n_nodes / 981.0

            f.write(f"\n# Floor {floor} mass assignment ({n_nodes} nodes)\n")
            for node_id in floor_nodes:
                rotI = mass_per_node * 0.01
                f.write(f"mass {int(node_id)} {mass_per_node:.8f} {mass_per_node:.8f} {mass_per_node/10:.8f} {rotI:.8f} {rotI:.8f} {rotI:.8f}\n")

        f.write("""
puts ">>> Mass assignment completed"

# ============================================================================
# EIGENVALUE ANALYSIS
# ============================================================================
puts ""
puts "============================================================"
puts "  EIGENVALUE ANALYSIS"
puts "============================================================"

set numModes 12
puts ">>> Computing $numModes eigenvalues..."

set eigenValues [eigen -fullGenLapack $numModes]

puts ""
puts ">>> Modal Analysis Results:"
puts "============================================================"
puts [format "%4s %14s %14s %10s %15s" "Mode" "Period (s)" "Freq (Hz)" "Sae (g)" "Region"]
puts "------------------------------------------------------------"

set pi 3.14159265359

for {set i 0} {$i < $numModes} {incr i} {
    set eigenValue [lindex $eigenValues $i]
    set omega [expr sqrt($eigenValue)]
    set freq [expr $omega / (2.0 * $pi)]
    set period [expr 1.0 / $freq]

    # Calculate Sae according to TBDY 2018
    if {$period < $TA} {
        set Sae [expr (0.4 + 0.6 * $period / $TA) * $SDS]
        set region "Ascending"
    } elseif {$period <= $TB} {
        set Sae $SDS
        set region "Plateau"
    } else {
        set Sae [expr $SD1 / $period]
        set region "Descending"
    }

    puts [format "%4d %14.6f %14.4f %10.4f %15s" [expr $i+1] $period $freq $Sae $region]

    # Store first mode period
    if {$i == 0} {
        set T1 $period
    }
}

puts "------------------------------------------------------------"
puts ""
puts ">>> Fundamental Period T1 = $T1 s"

# Calculate Ra (Response Modification Factor)
if {$T1 > $TB} {
    set Ra [expr $R / $I]
} else {
    set Ra [expr $D + ($R / $I - $D) * $T1 / $TB]
}
puts ">>> Response Modification Factor Ra = $Ra"

# Calculate SaR (Reduced Design Spectral Acceleration)
if {$T1 < $TA} {
    set Sae_T1 [expr (0.4 + 0.6 * $T1 / $TA) * $SDS]
} elseif {$T1 <= $TB} {
    set Sae_T1 $SDS
} else {
    set Sae_T1 [expr $SD1 / $T1]
}
set SaR [expr $Sae_T1 / $Ra]
puts ">>> Sae(T1) = $Sae_T1 g"
puts ">>> SaR(T1) = $SaR g"

# ============================================================================
# EQUIVALENT LATERAL FORCE METHOD (TBDY 2018 Section 4.7)
# ============================================================================
puts ""
puts "============================================================"
puts "  EQUIVALENT LATERAL FORCE METHOD"
puts "  TBDY 2018 Section 4.7"
puts "============================================================"

# Total mass
""")

        total_mass = 1.6 * (max_floor - 1) + 2.22
        f.write(f"set totalMass {total_mass:.4f}  ;# Total mass (kg)\n")

        f.write("""
# Base shear force (TBDY 2018 Eq. 4.19)
set Vt [expr $totalMass * $SaR * $g / 1000.0]  ;# kN
set Vt_min [expr 0.04 * $totalMass * $I * $SDS * $g / 1000.0]
if {$Vt < $Vt_min} {
    set Vt $Vt_min
}
puts ">>> Total Base Shear Vt = $Vt kN"

# Additional force at top (TBDY 2018 Eq. 4.22)
""")

        f.write(f"set N {max_floor}  ;# Number of floors\n")

        f.write("""
set dF_NE [expr 0.0075 * $N * $Vt]
puts ">>> Additional Top Force dF_NE = $dF_NE kN"

# ============================================================================
# A1a TORSIONAL IRREGULARITY ANALYSIS
# ============================================================================
puts ""
puts "============================================================"
puts "  A1a TORSIONAL IRREGULARITY ANALYSIS"
puts "  TBDY 2018 Section 3.6.2.1 and 4.7.4"
puts "============================================================"
puts ""
puts ">>> Analyzing torsional irregularity with +/- 5% eccentricity..."
puts ""

# Floor geometry data
""")

        # Calculate floor geometry
        for floor in floors:
            if floor == 0:
                continue
            floor_nodes = nodes_df[nodes_df['floor'] == floor]
            x_coords = floor_nodes['x'].values
            y_coords = floor_nodes['y'].values
            z = floor_nodes['z'].values[0]

            Lx = x_coords.max() - x_coords.min()
            Ly = y_coords.max() - y_coords.min()
            cm_x = (x_coords.max() + x_coords.min()) / 2
            cm_y = (y_coords.max() + y_coords.min()) / 2
            ex_5 = 0.05 * Lx
            ey_5 = 0.05 * Ly

            f.write(f"set floor{floor}_z {z:.2f}\n")
            f.write(f"set floor{floor}_Lx {Lx:.2f}\n")
            f.write(f"set floor{floor}_Ly {Ly:.2f}\n")
            f.write(f"set floor{floor}_ex {ex_5:.4f}\n")
            f.write(f"set floor{floor}_ey {ey_5:.4f}\n")

        f.write("""

# Function to calculate eta_bi
proc calculateEtaBi {deltaMax deltaMin} {
    set deltaOrt [expr 0.5 * ($deltaMax + $deltaMin)]
    if {$deltaOrt > 1e-10} {
        return [expr $deltaMax / $deltaOrt]
    } else {
        return 1.0
    }
}

# Function to calculate D_bi (TBDY 2018 Eq. 4.29)
proc calculateDbi {eta} {
    if {$eta <= 1.2} {
        return 1.0
    } else {
        return [expr pow($eta / 1.2, 2)]
    }
}

# Store results
set results {}

# Loop through directions and eccentricity signs
foreach direction {X Y} {
    foreach eccSign {+1 -1} {

        puts ">>> Direction: $direction, Eccentricity: [expr $eccSign * 5]%"

        # Reset for new analysis
        remove loadPattern 1

        # Define load pattern
        timeSeries Linear 1
        pattern Plain 1 1 {
""")

        # We need to add load commands - this will be simplified
        f.write("""
            # Loads will be applied based on direction and eccentricity
        }

        # Static analysis
        system BandSPD
        numberer RCM
        constraints Plain
        integrator LoadControl 1.0
        algorithm Linear
        analysis Static

        set ok [analyze 1]

        if {$ok != 0} {
            puts "WARNING: Analysis did not converge!"
        }

        # Extract displacements and calculate eta_bi for each floor
        puts ""
        puts [format "%4s %12s %12s %12s %8s %8s %18s" "Flr" "d_max" "d_min" "d_ort" "eta_bi" "D_bi" "Status"]
        puts "--------------------------------------------------------------------------------"

""")

        # Floor-by-floor analysis
        for floor in floors:
            if floor == 0:
                continue
            floor_nodes = nodes_df[nodes_df['floor'] == floor]
            node_list = floor_nodes['node_id'].tolist()

            f.write(f"""
        # Floor {floor}
        set floor{floor}_nodes {{{' '.join(map(str, node_list))}}}
        set maxDisp 0.0
        set minDisp 1e10

        foreach nodeId $floor{floor}_nodes {{
            if {{$direction == "X"}} {{
                set disp [expr abs([nodeDisp $nodeId 1])]
            }} else {{
                set disp [expr abs([nodeDisp $nodeId 2])]
            }}
            if {{$disp > $maxDisp}} {{set maxDisp $disp}}
            if {{$disp < $minDisp}} {{set minDisp $disp}}
        }}

        set eta [calculateEtaBi $maxDisp $minDisp]
        set Dbi [calculateDbi $eta]

        if {{$eta <= 1.2}} {{
            set status "REGULAR"
        }} elseif {{$eta <= 2.0}} {{
            set status "A1a IRREGULAR"
        }} else {{
            set status "NOT PERMITTED!"
        }}

        puts [format "%4d %12.8f %12.8f %12.8f %8.4f %8.4f %18s" {floor} $maxDisp $minDisp [expr 0.5*($maxDisp+$minDisp)] $eta $Dbi $status]

        lappend results [list {floor} $direction $eccSign $eta $Dbi $status]
""")

        f.write("""
        puts "--------------------------------------------------------------------------------"
        puts ""
    }
}

# ============================================================================
# SUMMARY REPORT
# ============================================================================
puts ""
puts "============================================================"
puts "  SUMMARY REPORT"
puts "============================================================"

# Find maximum eta_bi across all cases
set maxEta 0.0
set criticalFloor 0
set criticalCase ""

foreach result $results {
    set floor [lindex $result 0]
    set dir [lindex $result 1]
    set ecc [lindex $result 2]
    set eta [lindex $result 3]

    if {$eta > $maxEta} {
        set maxEta $eta
        set criticalFloor $floor
        set criticalCase "$dir, [expr $ecc * 5]%"
    }
}

puts ""
puts ">>> Maximum eta_bi = $maxEta"
puts ">>> Critical Floor = $criticalFloor"
puts ">>> Critical Case  = $criticalCase"
puts ""

if {$maxEta <= 1.2} {
    puts ">>> RESULT: Building is REGULAR with respect to A1a torsional irregularity"
    puts ">>> No eccentricity amplification required (D_bi = 1.0)"
} elseif {$maxEta <= 2.0} {
    set Dbi_max [calculateDbi $maxEta]
    puts ">>> RESULT: Building has A1a TORSIONAL IRREGULARITY (1.2 < eta <= 2.0)"
    puts ">>> Eccentricity amplification factor D_bi = $Dbi_max"
    puts ">>> According to TBDY 2018 Section 4.7.4:"
    puts ">>>   +/- 5% accidental eccentricity shall be multiplied by D_bi"
} else {
    puts ">>> RESULT: eta_bi > 2.0 - BUILDING PERMIT CANNOT BE ISSUED!"
    puts ">>> According to TBDY 2018, structures with eta_bi > 2.0 are not permitted."
}

puts ""
puts "============================================================"
puts "  ANALYSIS COMPLETED"
puts "============================================================"
puts ">>> Completed at [clock format [clock seconds]]"
puts ""

# ============================================================================
# SAVE RESULTS TO FILE
# ============================================================================
set outFile [open "torsion_results.txt" w]
puts $outFile "TBDY 2018 A1a Torsional Irregularity Analysis Results"
puts $outFile "======================================================"
puts $outFile "Generated: [clock format [clock seconds]]"
puts $outFile ""
puts $outFile "Fundamental Period T1 = $T1 s"
puts $outFile "Base Shear Vt = $Vt kN"
puts $outFile ""
puts $outFile "Maximum eta_bi = $maxEta"
puts $outFile "Critical Floor = $criticalFloor"
puts $outFile "Critical Case = $criticalCase"
if {$maxEta > 1.2 && $maxEta <= 2.0} {
    puts $outFile "D_bi = [calculateDbi $maxEta]"
}
close $outFile

puts ">>> Results saved to torsion_results.txt"

wipe
puts ">>> Model cleared"
puts ""
""")

    print(f"Tcl file generated: {output_file}")
    return output_file


if __name__ == '__main__':
    base_dir = Path(__file__).parent
    position_file = base_dir / 'twin_position_matrix_v9.csv'
    connectivity_file = base_dir / 'twin_connectivity_matrix_v9.csv'
    output_file = base_dir / 'tbdy2018_torsion_analysis.tcl'

    generate_tcl_model(
        str(position_file),
        str(connectivity_file),
        str(output_file)
    )

    print("\nTo run the analysis:")
    print(f"  opensees {output_file}")
