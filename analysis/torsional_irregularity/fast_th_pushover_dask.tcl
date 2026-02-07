# ============================================================================
# FAST TIME HISTORY + PUSHOVER ANALYSIS - DASK 2026 Ground Motions
# Calibrated Stick Model for Twin Towers V9 (1:50 Scale)
# TBDY 2018 - Istanbul DD-2 ZD Soil
# Ground Motions: KYH-1 (PGA=0.335g), KYH-2 (PGA=1.243g), KYH-3 (PGA=1.896g)
# ============================================================================

puts "################################################################"
puts "##  FAST TIME HISTORY + PUSHOVER ANALYSIS                    ##"
puts "##  Calibrated Stick Model - Twin Towers V9 (1:50)           ##"
puts "##  TBDY 2018 - DASK 2026 Ground Motions (KYH-1/2/3)        ##"
puts "################################################################"
puts ""

wipe

# ============================================================================
# GROUND MOTION SELECTION
# Change gmID to "KYH1", "KYH2", or "KYH3" to select different records
# ============================================================================
set gmID "KYH1"

# PGA values (g):
#   KYH1 = 0.335 g
#   KYH2 = 1.243 g
#   KYH3 = 1.896 g
set gmFile "C:/Users/lenovo/Desktop/DASK_NEW/ground_motion_dask/${gmID}.txt"
set dt_gm  0.001   ;# s (all three records)
set npts_gm 32233  ;# all three records

puts ">>> Selected ground motion: $gmID"
puts ">>> File: $gmFile"
puts ""

# ============================================================================
# MODEL PARAMETERS (from detailed V9 model)
# ============================================================================
puts "============================================================"
puts "  MODEL PARAMETERS"
puts "============================================================"

set g         981.0        ;# cm/s2
set numFloors 25
set H_story   6.12         ;# cm per story (153/25)
set H_total   153.0        ;# cm total height

set E_mat     170.0        ;# kN/cm2
set G_mat     65.385       ;# kN/cm2

set massPerFloor 0.000813  ;# kN*s2/cm (= 0.798 kg / 981)
set totalMass    [expr $massPerFloor * $numFloors]

set A_col    [expr 2.0 * 32 * 0.36]
set Iz_col   10000.0
set Iy_col   $Iz_col
set J_col    [expr 2.0 * 32 * 0.0182 * 50.0]

set SDS 1.008;  set SD1 0.514;  set TA 0.102;  set TB 0.51

puts "  Floors:        $numFloors"
puts "  H_story:       $H_story cm"
puts "  H_total:       $H_total cm"
puts "  Mass/floor:    [format "%.6f" $massPerFloor] kN*s2/cm ([format "%.3f" [expr $massPerFloor * $g]] kg)"
puts "  Total mass:    [format "%.6f" $totalMass] kN*s2/cm ([format "%.2f" [expr $totalMass * $g]] kg)"
puts "  A_col (eff):   [format "%.4f" $A_col] cm2"
puts "  Iz_col (eff):  [format "%.4f" $Iz_col] cm4"
puts "  E:             $E_mat kN/cm2"
puts ""

# ============================================================================
# BUILD STICK MODEL
# ============================================================================
puts "============================================================"
puts "  BUILDING STICK MODEL (25-DOF)"
puts "============================================================"

model BasicBuilder -ndm 3 -ndf 6
puts ">>> 3D model created (6 DOF/node)"

puts ""
puts "  Node |   X   |   Y   |   Z(cm)  | Description"
puts "  -----|-------|-------|----------|------------------"
for {set i 0} {$i <= $numFloors} {incr i} {
    set z [expr $i * $H_story]
    node $i 0.0 0.0 $z
    if {$i == 0} {
        puts "  [format "%4d" $i] |  0.00 |  0.00 | [format "%8.2f" $z] | Base (FIXED)"
    } else {
        puts "  [format "%4d" $i] |  0.00 |  0.00 | [format "%8.2f" $z] | Floor $i"
    }
}
puts ""
puts ">>> [expr $numFloors + 1] nodes created"

fix 0 1 1 1 1 1 1
puts ">>> Node 0 fixed in all 6 DOF"

puts ""
puts "  Assigning lumped masses..."
for {set i 1} {$i <= $numFloors} {incr i} {
    set m $massPerFloor
    if {$i == 6 || $i == 7 || $i == 12 || $i == 13 || $i == 18 || $i == 19 || $i == 25} {
        set m [expr $massPerFloor * 1.3]
    }
    mass $i $m $m [expr $m * 0.5] 0.0 0.0 0.0
}
puts ">>> Lumped masses assigned to floors 1-$numFloors"
puts ""

geomTransf Linear 1 0 1 0
puts ">>> Linear geometric transformation (Tag=1)"

puts ""
puts "  Elem | Node_i | Node_j | A(cm2) | Iz(cm4) | StiffFactor"
puts "  -----|--------|--------|--------|---------|------------"
for {set i 1} {$i <= $numFloors} {incr i} {
    set ni [expr $i - 1]
    set nj $i
    set sf 1.0
    if {$i > 15} { set sf 0.80 }
    if {$i > 20} { set sf 0.65 }
    set Iz_eff [expr $Iz_col * $sf]
    set Iy_eff [expr $Iy_col * $sf]
    element elasticBeamColumn $i $ni $nj $A_col $E_mat $G_mat $J_col $Iy_eff $Iz_eff 1
    puts "  [format "%4d" $i] | [format "%6d" $ni] | [format "%6d" $nj] | [format "%6.2f" $A_col] | [format "%7.4f" $Iz_eff] | [format "%5.2f" $sf]"
}
puts ""
puts ">>> $numFloors elastic beam-column elements created"
puts ""

# ============================================================================
# EIGENVALUE ANALYSIS
# ============================================================================
puts "============================================================"
puts "  EIGENVALUE ANALYSIS"
puts "============================================================"

set nModes 5
set eigenVals [eigen $nModes]
puts ""
puts "  Mode | Period (s) | Freq (Hz) | omega (rad/s)"
puts "  -----|------------|-----------|-------------"
set T1 0.0
set omega1 0.0
for {set i 0} {$i < $nModes} {incr i} {
    set lam [lindex $eigenVals $i]
    set w [expr sqrt($lam)]
    set T [expr 2.0 * 3.14159265 / $w]
    set f [expr 1.0 / $T]
    puts "  [format "%4d" [expr $i+1]] | [format "%10.4f" $T] | [format "%9.4f" $f] | [format "%11.4f" $w]"
    if {$i == 0} { set T1 $T; set omega1 $w }
}
puts ""
puts ">>> Fundamental Period T1 = [format "%.4f" $T1] s"

set modeShape {}
for {set i 1} {$i <= $numFloors} {incr i} {
    set phi [nodeEigenvector $i 1 1]
    lappend modeShape $phi
}
set phiRoof [lindex $modeShape end]
set modeShapeNorm {}
foreach phi $modeShape {
    if {$phiRoof != 0.0} {
        lappend modeShapeNorm [expr $phi / $phiRoof]
    } else {
        lappend modeShapeNorm $phi
    }
}
puts ">>> First mode shape extracted and normalized to roof"
puts ""

# ############################################################################
#   PART A: TIME HISTORY ANALYSIS
# ############################################################################
puts ""
puts "################################################################"
puts "##  TIME HISTORY ANALYSIS                                    ##"
puts "##  DASK 2026 Ground Motion: $gmID                           ##"
puts "################################################################"
puts ""

# ============================================================================
# READ TAB-SEPARATED GROUND MOTION FILE
# ============================================================================
puts "============================================================"
puts "  READING GROUND MOTION ($gmID)"
puts "============================================================"

puts "  File:     $gmFile"
puts "  Format:   Tab-separated (Time, Accel [g])"
puts "  NPTS:     $npts_gm"
puts "  DT:       $dt_gm s"
puts "  Duration: [format "%.1f" [expr $npts_gm * $dt_gm]] s"
puts ""

if {![file exists $gmFile]} {
    puts "*** FATAL: Ground motion file not found: $gmFile"
    puts "*** Check path: $gmFile"
    return
}

set gmData {}
set fp [open $gmFile r]
set lineNum 0
while {[gets $fp line] >= 0} {
    incr lineNum
    if {$lineNum <= 1} { continue }
    set fields [split $line "\t"]
    if {[llength $fields] >= 2} {
        set val [string trim [lindex $fields 1]]
        if {$val ne "" && ![catch {expr double($val)} numVal]} {
            lappend gmData $numVal
        }
    }
}
close $fp

set nRead [llength $gmData]
puts ">>> Parsed $nRead acceleration values"

set pga 0.0
foreach val $gmData {
    if {[expr abs($val)] > $pga} { set pga [expr abs($val)] }
}
puts ">>> PGA = [format "%.5f" $pga] g = [format "%.4f" [expr $pga * $g]] cm/s2"
puts ""

# Write single-column file (convert g to cm/s2)
file mkdir ground_motion
set tempGM "ground_motion/${gmID}_single_col.txt"
set fpOut [open $tempGM w]
foreach val $gmData {
    puts $fpOut [format "%.8f" [expr $val * $g]]
}
close $fpOut
puts ">>> Converted to single-column cm/s2: $tempGM"
puts ""

# ============================================================================
# RAYLEIGH DAMPING
# ============================================================================
puts "============================================================"
puts "  RAYLEIGH DAMPING (5%)"
puts "============================================================"

set xi 0.05
set omega3 [expr $omega1 * 3.0]
set a0 [expr 2.0 * $xi * $omega1 * $omega3 / ($omega1 + $omega3)]
set a1 [expr 2.0 * $xi / ($omega1 + $omega3)]

rayleigh $a0 $a1 0.0 0.0
puts "  xi = ${xi}, omega1 = [format "%.4f" $omega1], omega3 = [format "%.4f" $omega3]"
puts "  a0 = [format "%.6f" $a0], a1 = [format "%.6f" $a1]"
puts ">>> Rayleigh damping applied"
puts ""

# ============================================================================
# RECORDERS
# ============================================================================
puts "============================================================"
puts "  TIME HISTORY RECORDERS"
puts "============================================================"

file mkdir results
file mkdir results/time_history

recorder Node -file results/time_history/roof_disp.txt      -node $numFloors -dof 1 2 3 disp
recorder Node -file results/time_history/roof_vel.txt        -node $numFloors -dof 1 2 3 vel
recorder Node -file results/time_history/roof_accel.txt      -node $numFloors -dof 1 2 3 accel
recorder Node -file results/time_history/mid_disp.txt        -node 13 -dof 1 2 3 disp
recorder Node -file results/time_history/base_reaction.txt   -node 0 -dof 1 2 3 reaction
recorder EnvelopeNode -file results/time_history/envelope_roof.txt -node $numFloors -dof 1 2 3 disp
recorder Node -file results/time_history/all_floor_ux.txt -node 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 -dof 1 disp
recorder Drift -file results/time_history/drift_s05.txt -iNode  4 -jNode  5 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_s10.txt -iNode  9 -jNode 10 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_s15.txt -iNode 14 -jNode 15 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_s20.txt -iNode 19 -jNode 20 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_s25.txt -iNode 24 -jNode 25 -dof 1 -perpDirn 3

puts "  (OK) Roof disp/vel/accel, mid-height, base reaction, envelope"
puts "  (OK) All floor X-displacements, interstory drifts (5,10,15,20,25)"
puts ""

# ============================================================================
# GROUND MOTION EXCITATION
# ============================================================================
puts "============================================================"
puts "  APPLYING GROUND MOTION ($gmID)"
puts "============================================================"

set tsTH 10
timeSeries Path $tsTH -dt $dt_gm -filePath $tempGM -factor 1.0
pattern UniformExcitation 10 1 -accel $tsTH

puts ">>> TimeSeries Path (Tag=$tsTH, dt=$dt_gm, factor=1.0)"
puts ">>> UniformExcitation Pattern 10, direction=1 (X)"
puts ""

# ============================================================================
# TRANSIENT ANALYSIS
# ============================================================================
puts "============================================================"
puts "  TRANSIENT ANALYSIS SETUP"
puts "============================================================"

# Use dt_analysis = 0.005s (5x ground motion dt, still fine for T1 ~ 0.3-0.5s)
set dt_a 0.005
set duration_gm [expr $nRead * $dt_gm]
set Nsteps_TH [expr int($duration_gm / $dt_a)]

constraints Transformation
numberer RCM
system BandSPD
test NormDispIncr 1.0e-6 25
algorithm Newton
integrator Newmark 0.5 0.25
analysis Transient

puts "  dt_analysis:  $dt_a s (ground motion dt: $dt_gm s)"
puts "  Total steps:  $Nsteps_TH"
puts "  Duration:     [format "%.1f" $duration_gm] s"
puts ""

# ============================================================================
# RUN TIME HISTORY
# ============================================================================
puts "============================================================"
puts "  RUNNING TIME HISTORY ($gmID, PGA=[format "%.3f" $pga] g)"
puts "============================================================"
puts ""

set ok 0
set maxUx 0.0
set maxUy 0.0
set progInt [expr $Nsteps_TH / 10]
if {$progInt < 1} { set progInt 1 }

puts " Step   |  Time(s)  |  Roof Ux(cm)  |  Roof Uy(cm)  | Status"
puts "--------|-----------|---------------|---------------|-------"

for {set i 1} {$i <= $Nsteps_TH} {incr i} {
    set ok [analyze 1 $dt_a]
    if {$ok != 0} {
        algorithm ModifiedNewton
        test NormDispIncr 1.0e-5 50
        set ok [analyze 1 $dt_a]
        algorithm Newton
        test NormDispIncr 1.0e-6 25
        if {$ok != 0} {
            puts " [format "%6d" $i] | FAILED - trying substeps..."
            set dt_sub [expr $dt_a / 5.0]
            for {set j 1} {$j <= 5} {incr j} {
                set ok [analyze 1 $dt_sub]
                if {$ok != 0} { break }
            }
            if {$ok != 0} {
                puts "*** STOPPED at step $i / $Nsteps_TH"
                break
            }
        }
    }
    if {[expr $i % $progInt] == 0 || $i == $Nsteps_TH} {
        set ux [nodeDisp $numFloors 1]
        set uy [nodeDisp $numFloors 2]
        if {[expr abs($ux)] > $maxUx} { set maxUx [expr abs($ux)] }
        if {[expr abs($uy)] > $maxUy} { set maxUy [expr abs($uy)] }
        set pct [expr int(100.0 * $i / $Nsteps_TH)]
        puts " [format "%6d" $i] | [format "%8.3f" [expr $i * $dt_a]] | [format "%13.6f" $ux] | [format "%13.6f" $uy] | ${pct}%"
    }
}

puts ""
if {$ok == 0} {
    puts ">>> TIME HISTORY COMPLETED SUCCESSFULLY ($Nsteps_TH steps)"
} else {
    puts ">>> TIME HISTORY STOPPED (convergence issue)"
}
puts ""

# ============================================================================
# TIME HISTORY RESULTS
# ============================================================================
puts "============================================================"
puts "  TIME HISTORY RESULTS ($gmID)"
puts "============================================================"
puts ""

set finalUx [nodeDisp $numFloors 1]
set finalUy [nodeDisp $numFloors 2]
set driftX [expr $maxUx / $H_total]

puts "  T1:                         [format "%.4f" $T1] s"
puts "  PGA ($gmID):                [format "%.5f" $pga] g"
puts ""
puts "  Max Roof Ux:                [format "%.6f" $maxUx] cm"
puts "  Max Roof Uy:                [format "%.6f" $maxUy] cm"
puts "  Final Roof Ux:              [format "%.6f" $finalUx] cm"
puts "  Roof Drift Ratio (X):       [format "%.6f" $driftX] ([format "%.3f" [expr $driftX * 100]]%)"
puts ""

if {$driftX > 0.02} {
    puts "  >>> WARNING: Exceeds TBDY 2018 collapse prevention limit (2%)"
} elseif {$driftX > 0.008} {
    puts "  >>> Exceeds serviceability, within collapse prevention"
} else {
    puts "  >>> WITHIN serviceability limits - OK"
}

set Vbase [expr abs([nodeReaction 0 1])]
puts ""
puts "  Base Shear (X):             [format "%.4f" $Vbase] kN"
set Cs [expr $Vbase / ($totalMass * $g)]
puts "  Base Shear Coeff Cs:        [format "%.4f" $Cs]"
puts ""

set thFile [open "results/time_history/th_summary_${gmID}.txt" w]
puts $thFile "TBDY 2018 Time History Analysis Results"
puts $thFile "======================================="
puts $thFile "Model: Calibrated Stick Model (Twin Towers V9 1:50)"
puts $thFile "Ground Motion: DASK 2026 $gmID"
puts $thFile "PGA = [format "%.5f" $pga] g"
puts $thFile "T1 = [format "%.4f" $T1] s"
puts $thFile ""
puts $thFile "Max Roof Ux = [format "%.6f" $maxUx] cm"
puts $thFile "Max Roof Uy = [format "%.6f" $maxUy] cm"
puts $thFile "Drift Ratio X = [format "%.6f" $driftX]"
puts $thFile "Base Shear = [format "%.4f" $Vbase] kN"
close $thFile
puts ">>> Results saved to results/time_history/th_summary_${gmID}.txt"
puts ""


# ############################################################################
#   PART B: STATIC PUSHOVER ANALYSIS
# ############################################################################
puts ""
puts "################################################################"
puts "##  STATIC PUSHOVER ANALYSIS                                 ##"
puts "##  Displacement-Controlled, Mode 1 Load Pattern             ##"
puts "################################################################"
puts ""

reset
wipeAnalysis
remove recorders
loadConst -time 0.0
puts ">>> Model reset for pushover (zero state)"
puts ""

# ============================================================================
# PUSHOVER RECORDERS
# ============================================================================
puts "============================================================"
puts "  PUSHOVER RECORDERS"
puts "============================================================"

file mkdir results/pushover

recorder Node -file results/pushover/roof_disp.txt    -node $numFloors -dof 1 disp
recorder Node -file results/pushover/base_shear.txt   -node 0 -dof 1 reaction
recorder Node -file results/pushover/all_floor_ux.txt  -node 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 -dof 1 disp

puts "  (OK) Roof displacement, base shear, all floor X-displacements"
puts ""

# ============================================================================
# PUSHOVER LOAD PATTERN (Mode-1 proportional)
# ============================================================================
puts "============================================================"
puts "  PUSHOVER LOAD PATTERN (Mode-1 Shape)"
puts "============================================================"
puts ""

timeSeries Linear 20
pattern Plain 20 20 {
    for {set i 1} {$i <= 25} {incr i} {
        set phi_i [lindex $modeShapeNorm [expr $i - 1]]
        set m_i $massPerFloor
        if {$i == 6 || $i == 7 || $i == 12 || $i == 13 || $i == 18 || $i == 19 || $i == 25} {
            set m_i [expr $massPerFloor * 1.3]
        }
        set F_i [expr $m_i * $phi_i * $g]
        load $i $F_i 0.0 0.0 0.0 0.0 0.0
    }
}

puts "  Floor | phi_i  | Force(kN)"
puts "  ------|--------|----------"
for {set i 1} {$i <= 25} {incr i} {
    set phi_i [lindex $modeShapeNorm [expr $i - 1]]
    set m_i $massPerFloor
    if {$i == 6 || $i == 7 || $i == 12 || $i == 13 || $i == 18 || $i == 19 || $i == 25} {
        set m_i [expr $massPerFloor * 1.3]
    }
    set F_i [expr $m_i * $phi_i * $g]
    puts "  [format "%5d" $i] | [format "%6.4f" $phi_i] | [format "%8.6f" $F_i]"
}
puts ""

# ============================================================================
# PUSHOVER ANALYSIS SETUP
# ============================================================================
puts "============================================================"
puts "  PUSHOVER ANALYSIS SETUP"
puts "============================================================"

set ctrlNode $numFloors
set ctrlDOF  1
set targetDisp [expr $H_total * 0.04]
set dU 0.01
set Nsteps_PO [expr int($targetDisp / $dU)]

constraints Transformation
numberer RCM
system BandSPD
test NormDispIncr 1.0e-6 50
algorithm Newton
integrator DisplacementControl $ctrlNode $ctrlDOF $dU
analysis Static

puts "  Control node:   $ctrlNode (roof)"
puts "  Target disp:    [format "%.2f" $targetDisp] cm (4% drift)"
puts "  Step size:      $dU cm"
puts "  Total steps:    $Nsteps_PO"
puts ""

# ============================================================================
# RUN PUSHOVER
# ============================================================================
puts "============================================================"
puts "  RUNNING PUSHOVER ANALYSIS..."
puts "============================================================"
puts ""

set ok_po 0
set completed 0
set maxV 0.0
set dispAtMaxV 0.0
set poData {}

set poInt [expr $Nsteps_PO / 20]
if {$poInt < 1} { set poInt 1 }

puts " Step   | Roof Disp(cm) | Base Shear(kN) | Drift(%) | Status"
puts "--------|---------------|----------------|----------|-------"

for {set i 1} {$i <= $Nsteps_PO} {incr i} {
    set ok_po [analyze 1]
    if {$ok_po != 0} {
        algorithm ModifiedNewton
        test NormDispIncr 1.0e-5 100
        set ok_po [analyze 1]
        if {$ok_po != 0} {
            algorithm NewtonLineSearch 0.8
            set ok_po [analyze 1]
            if {$ok_po != 0} {
                integrator DisplacementControl $ctrlNode $ctrlDOF [expr $dU/5.0]
                algorithm Newton; test NormDispIncr 1.0e-5 100
                for {set j 1} {$j <= 5} {incr j} {
                    set ok_po [analyze 1]
                    if {$ok_po != 0} { break }
                }
                integrator DisplacementControl $ctrlNode $ctrlDOF $dU
            }
        }
        algorithm Newton; test NormDispIncr 1.0e-6 50
        if {$ok_po != 0} {
            puts "*** STOPPED at step $i"
            break
        }
    }
    incr completed

    set d [nodeDisp $ctrlNode $ctrlDOF]
    set V [expr abs([nodeReaction 0 1])]
    lappend poData [list $d $V]
    if {$V > $maxV} { set maxV $V; set dispAtMaxV $d }

    if {[expr $i % $poInt] == 0 || $i == 1 || $i == $Nsteps_PO} {
        set dr [expr $d / $H_total * 100.0]
        set pct [expr int(100.0 * $i / $Nsteps_PO)]
        puts " [format "%6d" $i] | [format "%13.4f" $d] | [format "%14.4f" $V] | [format "%8.3f" $dr] | ${pct}%"
    }
}

puts ""
if {$ok_po == 0} {
    puts ">>> PUSHOVER COMPLETED SUCCESSFULLY ($completed steps)"
} else {
    puts ">>> PUSHOVER STOPPED ($completed / $Nsteps_PO steps)"
}
puts ""

# ============================================================================
# PUSHOVER RESULTS
# ============================================================================
puts "============================================================"
puts "  PUSHOVER RESULTS"
puts "============================================================"
puts ""

set finalD [nodeDisp $ctrlNode $ctrlDOF]
set finalDrift [expr $finalD / $H_total]

puts "  Final Roof Disp:        [format "%.4f" $finalD] cm"
puts "  Final Drift Ratio:      [format "%.6f" $finalDrift] ([format "%.3f" [expr $finalDrift * 100]]%)"
puts "  Max Base Shear:         [format "%.4f" $maxV] kN"
puts "  Disp at Max Shear:      [format "%.4f" $dispAtMaxV] cm"
puts ""

set nPts [llength $poData]
if {$nPts > 20} {
    set pt_e [lindex $poData [expr int($nPts * 0.05)]]
    set d_e [lindex $pt_e 0]; set v_e [lindex $pt_e 1]
    if {$d_e > 0} {
        set K0 [expr $v_e / $d_e]
        puts "  Initial Stiffness K0:   [format "%.4f" $K0] kN/cm"
        set yieldD 0.0; set yieldV 0.0; set found 0
        for {set k 10} {$k < $nPts} {incr k} {
            set pA [lindex $poData [expr $k - 5]]
            set pB [lindex $poData $k]
            set dA [lindex $pA 0]; set vA [lindex $pA 1]
            set dB [lindex $pB 0]; set vB [lindex $pB 1]
            set dd [expr $dB - $dA]
            if {$dd > 0} {
                set Kt [expr ($vB - $vA) / $dd]
                if {$K0 > 0 && [expr $Kt / $K0] < 0.5} {
                    set yieldD $dA; set yieldV $vA; set found 1; break
                }
            }
        }
        if {$found} {
            puts "  Yield Displacement:     [format "%.4f" $yieldD] cm"
            puts "  Yield Force:            [format "%.4f" $yieldV] kN"
            puts "  Ductility (mu):         [format "%.2f" [expr $finalD / $yieldD]]"
        } else {
            puts "  >>> Structure remained elastic (no yield detected)"
        }
    }
}
puts ""

# ============================================================================
# SAVE PUSHOVER CURVE
# ============================================================================
set poFile [open "results/pushover/pushover_curve.txt" w]
puts $poFile "# Pushover Curve - Twin Towers V9 Stick Model"
puts $poFile "# Col1: Roof Displacement (cm)  Col2: Base Shear (kN)"
puts $poFile "0.00000000 0.00000000"
foreach pt $poData {
    puts $poFile "[format "%.8f" [lindex $pt 0]] [format "%.8f" [lindex $pt 1]]"
}
close $poFile
puts ">>> Pushover curve: results/pushover/pushover_curve.txt"

set poSum [open "results/pushover/pushover_summary.txt" w]
puts $poSum "TBDY 2018 Pushover Analysis Results"
puts $poSum "===================================="
puts $poSum "Model: Calibrated Stick Model (Twin Towers V9 1:50)"
puts $poSum "T1 = [format "%.4f" $T1] s"
puts $poSum "Final Disp = [format "%.4f" $finalD] cm"
puts $poSum "Drift = [format "%.6f" $finalDrift]"
puts $poSum "Max Base Shear = [format "%.4f" $maxV] kN"
puts $poSum "Disp at Max V = [format "%.4f" $dispAtMaxV] cm"
puts $poSum "Steps completed: $completed / $Nsteps_PO"
close $poSum
puts ">>> Pushover summary: results/pushover/pushover_summary.txt"
puts ""

# ============================================================================
# FINAL SUMMARY
# ============================================================================
puts ""
puts "################################################################"
puts "##  ALL ANALYSES COMPLETED                                   ##"
puts "################################################################"
puts ""
puts "  Time History ($gmID, PGA=[format "%.3f" $pga]g):"
puts "    Max Roof Ux = [format "%.6f" $maxUx] cm"
puts "    Drift = [format "%.4f" [expr $driftX * 100]]%"
puts "    Base Shear = [format "%.4f" $Vbase] kN"
puts ""
puts "  Pushover:"
puts "    Max Base Shear = [format "%.4f" $maxV] kN"
puts "    Final Disp = [format "%.4f" $finalD] cm"
puts "    Drift = [format "%.4f" [expr $finalDrift * 100]]%"
puts ""
puts "  Output files:"
puts "    results/time_history/th_summary_${gmID}.txt"
puts "    results/pushover/pushover_curve.txt"
puts "    results/pushover/pushover_summary.txt"
puts ""

wipe
puts ">>> Done."
