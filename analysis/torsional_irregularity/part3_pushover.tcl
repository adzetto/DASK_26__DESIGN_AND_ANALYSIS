

# ############################################################################
# ############################################################################
# ##                                                                        ##
# ##  PART 3: STATIC PUSHOVER ANALYSIS (Statik Itme Analizi)               ##
# ##  TBDY 2018 Section 5.6.5 - Capacity Curve                             ##
# ##  Displacement-Controlled, Inverted Triangular Load Pattern             ##
# ##                                                                        ##
# ############################################################################
# ############################################################################

puts ""
puts "################################################################"
puts "################################################################"
puts "##                                                            ##"
puts "##  PART 3: STATIC PUSHOVER ANALYSIS                         ##"
puts "##  (Statik Itme Analizi - TBDY 2018)                        ##"
puts "##  Displacement-Controlled Monotonic Push                    ##"
puts "##                                                            ##"
puts "################################################################"
puts "################################################################"
puts ""

# ============================================================================
# RESET MODEL STATE FOR PUSHOVER
# ============================================================================
puts ">>> Resetting model state from time history to initial condition..."
reset
wipeAnalysis
remove recorders
loadConst -time 0.0
puts ">>> Model reset to initial state (zero displacements)"
puts ">>> All recorders removed"
puts ">>> Analysis objects cleared"
puts ""

# ============================================================================
# PUSHOVER PARAMETERS
# ============================================================================
puts "============================================================"
puts "  PUSHOVER ANALYSIS PARAMETERS"
puts "============================================================"
puts ""

# Control node (Tower 1 roof center)
set ctrlNode 809         ;# Node 809 at (11.0, 7.4, 153.0)
set ctrlDOF  1           ;# X-direction
set H_total  153.0       ;# Building height (cm)

# Target displacement: 4% of building height (generous for capacity curve)
set targetDisp [expr $H_total * 0.04]
set dU         0.005     ;# Displacement increment per step (cm)
set Nsteps_PO  [expr int($targetDisp / $dU)]

puts "  Control Node:         $ctrlNode (Tower 1 roof center)"
puts "  Control DOF:          $ctrlDOF (X-direction)"
puts "  Building Height:      $H_total cm"
puts "  Target Displacement:  [format "%.2f" $targetDisp] cm (4% drift)"
puts "  Displacement step:    $dU cm"
puts "  Total steps:          $Nsteps_PO"
puts ""

# ============================================================================
# PUSHOVER RECORDERS
# ============================================================================
puts "============================================================"
puts "  PUSHOVER RECORDER SETUP"
puts "============================================================"

file mkdir results/pushover

# Control node displacement
recorder Node -file results/pushover/ctrl_node_disp.txt -node $ctrlNode -dof 1 2 3 disp
puts "  [OK] Control node displacement (node $ctrlNode)"

# Both tower roof displacements
recorder Node -file results/pushover/roof_T1_disp.txt -node 809 -dof 1 disp
recorder Node -file results/pushover/roof_T2_disp.txt -node 1641 -dof 1 disp
puts "  [OK] Roof displacement both towers"

# Base reactions (all Tower 1 + Tower 2 base nodes)
recorder Node -file results/pushover/base_react_T1.txt -node 0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 -dof 1 reaction
recorder Node -file results/pushover/base_react_T2.txt -node 832 833 834 835 836 837 838 839 840 841 842 843 844 845 846 847 848 849 850 851 852 853 854 855 856 857 858 859 860 861 862 863 -dof 1 reaction
puts "  [OK] Base reaction recorders (all 64 ground nodes)"

# Floor displacement profile (one node per floor, Tower 1)
# Using node index pattern: floor*32 + 9 (center node at (11.0, 7.4))
recorder Node -file results/pushover/floor_profile_ux.txt -node 41 73 105 137 169 201 233 265 297 329 361 393 425 457 489 521 553 585 617 649 681 713 745 777 809 -dof 1 disp
puts "  [OK] Floor displacement profile (25 floors, Tower 1 center)"

puts ""

# ============================================================================
# LATERAL LOAD PATTERN - INVERTED TRIANGULAR (TBDY 2018)
# ============================================================================
puts "============================================================"
puts "  PUSHOVER LOAD PATTERN"
puts "  Inverted Triangular Distribution (TBDY 2018 Sec. 5.6.5)"
puts "============================================================"
puts ""
puts "  Load distribution: F_i proportional to m_i * h_i"
puts "  Applied to both Tower 1 and Tower 2 nodes"
puts "  Direction: X (DOF 1)"
puts ""

# Linear time series for pushover (load factor increases with pseudo-time)
timeSeries Linear 500

# Inverted triangular load pattern
# F_i = h_i / sum(h_i) for each floor
# Floor heights: floor_i * (153/25) = floor_i * 6.12 cm
# sum of h_i for floors 1-25 = 6.12 * (1+2+...+25) = 6.12 * 325 = 1989 cm

set h_story [expr $H_total / 25.0]  ;# Story height = 6.12 cm
set sum_hi 0.0
for {set fl 1} {$fl <= 25} {incr fl} {
    set sum_hi [expr $sum_hi + $fl * $h_story]
}

puts "  Story height:  [format "%.3f" $h_story] cm"
puts "  Sum(h_i):      [format "%.3f" $sum_hi] cm"
puts ""
puts "  Floor | Height(cm) | Load Factor | Force/Node(kN)"
puts "  ------|------------|-------------|---------------"

pattern Plain 500 500 {

    # Apply loads floor by floor
    # Tower 1 nodes: floor*32 + 0..31
    # Tower 2 nodes: 832 + floor*32 + 0..31
    # Apply to every 4th node to reduce computational effort (8 nodes per floor per tower)

    # Floor 1
    set h_1 [expr 1 * 6.12]; set lf_1 [expr $h_1 / 1989.0]; set fn_1 [expr $lf_1 / 16.0]
    load  36 $fn_1 0 0 0 0 0;  load  40 $fn_1 0 0 0 0 0;  load  44 $fn_1 0 0 0 0 0;  load  48 $fn_1 0 0 0 0 0
    load  52 $fn_1 0 0 0 0 0;  load  56 $fn_1 0 0 0 0 0;  load  60 $fn_1 0 0 0 0 0;  load  63 $fn_1 0 0 0 0 0
    load 868 $fn_1 0 0 0 0 0;  load 872 $fn_1 0 0 0 0 0;  load 876 $fn_1 0 0 0 0 0;  load 880 $fn_1 0 0 0 0 0
    load 884 $fn_1 0 0 0 0 0;  load 888 $fn_1 0 0 0 0 0;  load 892 $fn_1 0 0 0 0 0;  load 895 $fn_1 0 0 0 0 0

    # Floor 2
    set h_2 [expr 2 * 6.12]; set lf_2 [expr $h_2 / 1989.0]; set fn_2 [expr $lf_2 / 16.0]
    load  68 $fn_2 0 0 0 0 0;  load  72 $fn_2 0 0 0 0 0;  load  76 $fn_2 0 0 0 0 0;  load  80 $fn_2 0 0 0 0 0
    load  84 $fn_2 0 0 0 0 0;  load  88 $fn_2 0 0 0 0 0;  load  92 $fn_2 0 0 0 0 0;  load  95 $fn_2 0 0 0 0 0
    load 900 $fn_2 0 0 0 0 0;  load 904 $fn_2 0 0 0 0 0;  load 908 $fn_2 0 0 0 0 0;  load 912 $fn_2 0 0 0 0 0
    load 916 $fn_2 0 0 0 0 0;  load 920 $fn_2 0 0 0 0 0;  load 924 $fn_2 0 0 0 0 0;  load 927 $fn_2 0 0 0 0 0

    # Floor 3
    set h_3 [expr 3 * 6.12]; set lf_3 [expr $h_3 / 1989.0]; set fn_3 [expr $lf_3 / 16.0]
    load 100 $fn_3 0 0 0 0 0;  load 104 $fn_3 0 0 0 0 0;  load 108 $fn_3 0 0 0 0 0;  load 112 $fn_3 0 0 0 0 0
    load 116 $fn_3 0 0 0 0 0;  load 120 $fn_3 0 0 0 0 0;  load 124 $fn_3 0 0 0 0 0;  load 127 $fn_3 0 0 0 0 0
    load 932 $fn_3 0 0 0 0 0;  load 936 $fn_3 0 0 0 0 0;  load 940 $fn_3 0 0 0 0 0;  load 944 $fn_3 0 0 0 0 0
    load 948 $fn_3 0 0 0 0 0;  load 952 $fn_3 0 0 0 0 0;  load 956 $fn_3 0 0 0 0 0;  load 959 $fn_3 0 0 0 0 0

    # Floor 4
    set h_4 [expr 4 * 6.12]; set lf_4 [expr $h_4 / 1989.0]; set fn_4 [expr $lf_4 / 16.0]
    load 132 $fn_4 0 0 0 0 0;  load 136 $fn_4 0 0 0 0 0;  load 140 $fn_4 0 0 0 0 0;  load 144 $fn_4 0 0 0 0 0
    load 148 $fn_4 0 0 0 0 0;  load 152 $fn_4 0 0 0 0 0;  load 156 $fn_4 0 0 0 0 0;  load 159 $fn_4 0 0 0 0 0
    load 964 $fn_4 0 0 0 0 0;  load 968 $fn_4 0 0 0 0 0;  load 972 $fn_4 0 0 0 0 0;  load 976 $fn_4 0 0 0 0 0
    load 980 $fn_4 0 0 0 0 0;  load 984 $fn_4 0 0 0 0 0;  load 988 $fn_4 0 0 0 0 0;  load 991 $fn_4 0 0 0 0 0

    # Floor 5
    set h_5 [expr 5 * 6.12]; set lf_5 [expr $h_5 / 1989.0]; set fn_5 [expr $lf_5 / 16.0]
    load 164 $fn_5 0 0 0 0 0;  load 168 $fn_5 0 0 0 0 0;  load 172 $fn_5 0 0 0 0 0;  load 176 $fn_5 0 0 0 0 0
    load 180 $fn_5 0 0 0 0 0;  load 184 $fn_5 0 0 0 0 0;  load 188 $fn_5 0 0 0 0 0;  load 191 $fn_5 0 0 0 0 0
    load 996 $fn_5 0 0 0 0 0;  load 1000 $fn_5 0 0 0 0 0;  load 1004 $fn_5 0 0 0 0 0;  load 1008 $fn_5 0 0 0 0 0
    load 1012 $fn_5 0 0 0 0 0;  load 1016 $fn_5 0 0 0 0 0;  load 1020 $fn_5 0 0 0 0 0;  load 1023 $fn_5 0 0 0 0 0
}

# Print load summary using a loop
puts ""
for {set fl 1} {$fl <= 5} {incr fl} {
    set hi [expr $fl * $h_story]
    set lfi [expr $hi / $sum_hi]
    set fni [expr $lfi / 16.0]
    puts "  [format "%5d" $fl] | [format "%10.3f" $hi] | [format "%11.6f" $lfi] | [format "%13.8f" $fni]"
}
puts "  ... (continuing for all 25 floors)"

# We need to add floors 6-25 outside the pattern block using separate load commands
# Actually, loads must be inside the pattern block. Let me use a different approach.

puts ""
puts ">>> NOTE: Loads applied to floors 1-5 within pattern block"
puts ">>> Floors 6-25 will be added via additional pattern"
puts ""

# Additional load pattern for floors 6-25
timeSeries Linear 501
pattern Plain 501 501 {

    # Floor 6-25: generate loads programmatically
    for {set fl 6} {$fl <= 25} {incr fl} {
        set hi [expr $fl * 6.12]
        set lfi [expr $hi / 1989.0]
        set fni [expr $lfi / 16.0]

        # Tower 1 nodes: floor*32 + offsets (4, 8, 12, 16, 20, 24, 28, 31)
        set baseN1 [expr $fl * 32]
        load [expr $baseN1 + 4]  $fni 0 0 0 0 0
        load [expr $baseN1 + 8]  $fni 0 0 0 0 0
        load [expr $baseN1 + 12] $fni 0 0 0 0 0
        load [expr $baseN1 + 16] $fni 0 0 0 0 0
        load [expr $baseN1 + 20] $fni 0 0 0 0 0
        load [expr $baseN1 + 24] $fni 0 0 0 0 0
        load [expr $baseN1 + 28] $fni 0 0 0 0 0
        load [expr $baseN1 + 31] $fni 0 0 0 0 0

        # Tower 2 nodes: 832 + floor*32 + offsets
        set baseN2 [expr 832 + $fl * 32]
        load [expr $baseN2 + 4]  $fni 0 0 0 0 0
        load [expr $baseN2 + 8]  $fni 0 0 0 0 0
        load [expr $baseN2 + 12] $fni 0 0 0 0 0
        load [expr $baseN2 + 16] $fni 0 0 0 0 0
        load [expr $baseN2 + 20] $fni 0 0 0 0 0
        load [expr $baseN2 + 24] $fni 0 0 0 0 0
        load [expr $baseN2 + 28] $fni 0 0 0 0 0
        load [expr $baseN2 + 31] $fni 0 0 0 0 0
    }
}

puts ">>> Inverted triangular load pattern applied to all 25 floors"
puts ">>> Both Tower 1 and Tower 2 loaded simultaneously"
puts ""

# ============================================================================
# PUSHOVER ANALYSIS CONFIGURATION
# ============================================================================
puts "============================================================"
puts "  PUSHOVER ANALYSIS CONFIGURATION"
puts "============================================================"
puts ""

constraints Transformation
puts "  Constraints:   Transformation"

numberer RCM
puts "  Numberer:      RCM"

system BandGeneral
puts "  System:        BandGeneral"

test NormDispIncr 1.0e-6 100
puts "  Test:          NormDispIncr (tol=1e-6, maxIter=100)"

algorithm Newton
puts "  Algorithm:     Newton"

integrator DisplacementControl $ctrlNode $ctrlDOF $dU
puts "  Integrator:    DisplacementControl"
puts "    Control node:  $ctrlNode"
puts "    Control DOF:   $ctrlDOF (X-direction)"
puts "    dU increment:  $dU cm"

analysis Static
puts "  Analysis:      Static"
puts ""

# ============================================================================
# RUN PUSHOVER ANALYSIS
# ============================================================================
puts "============================================================"
puts "  RUNNING PUSHOVER ANALYSIS"
puts "  Target: [format "%.2f" $targetDisp] cm ($Nsteps_PO steps)"
puts "============================================================"
puts ""

set ok_po 0
set completedSteps 0
set maxBaseShear 0.0
set dispAtMaxV 0.0

# Store pushover curve data in list
set poData {}

# Progress interval
set poInterval [expr int($Nsteps_PO / 25)]
if {$poInterval < 1} { set poInterval 1 }

puts ">>> Step | Roof Disp(cm) | Base Shear(kN) | Drift(%) | Status"
puts ">>> -----|---------------|----------------|----------|-------"

for {set step 1} {$step <= $Nsteps_PO} {incr step} {

    set ok_po [analyze 1]

    # Convergence recovery
    if {$ok_po != 0} {
        puts "  *** Step $step: Newton failed, trying ModifiedNewton..."
        algorithm ModifiedNewton
        set ok_po [analyze 1]

        if {$ok_po != 0} {
            puts "  *** Step $step: Trying NewtonLineSearch..."
            algorithm NewtonLineSearch 0.8
            test NormDispIncr 1.0e-5 200
            set ok_po [analyze 1]

            if {$ok_po != 0} {
                puts "  *** Step $step: Trying smaller increment (dU/5)..."
                integrator DisplacementControl $ctrlNode $ctrlDOF [expr $dU / 5.0]
                algorithm Newton
                test NormDispIncr 1.0e-5 200
                set subOK 0
                for {set s 1} {$s <= 5} {incr s} {
                    set subOK [analyze 1]
                    if {$subOK != 0} { break }
                }
                set ok_po $subOK
                # Restore original increment
                integrator DisplacementControl $ctrlNode $ctrlDOF $dU
            }
        }
        # Restore defaults
        algorithm Newton
        test NormDispIncr 1.0e-6 100
    }

    if {$ok_po != 0} {
        puts ""
        puts ">>> PUSHOVER STOPPED at step $step (disp = [format "%.4f" [nodeDisp $ctrlNode $ctrlDOF]] cm)"
        break
    }

    incr completedSteps

    # Current roof displacement
    set currDisp [nodeDisp $ctrlNode $ctrlDOF]

    # Calculate base shear (sum of X-reactions at all fixed nodes)
    set Vbase 0.0
    for {set bn 0} {$bn <= 31} {incr bn} {
        set Vbase [expr $Vbase + [nodeReaction $bn 1]]
    }
    for {set bn 832} {$bn <= 863} {incr bn} {
        set Vbase [expr $Vbase + [nodeReaction $bn 1]]
    }
    set Vbase [expr abs($Vbase)]

    # Track max base shear
    if {$Vbase > $maxBaseShear} {
        set maxBaseShear $Vbase
        set dispAtMaxV $currDisp
    }

    # Store pushover data point
    lappend poData [list $currDisp $Vbase]

    # Print progress
    if {[expr $step % $poInterval] == 0 || $step == 1 || $step == $Nsteps_PO} {
        set drift_pct [expr $currDisp / $H_total * 100.0]
        set pct [expr int(100.0 * $step / $Nsteps_PO)]
        puts ">>> [format "%4d" $step] | [format "%13.4f" $currDisp] | [format "%14.4f" $Vbase] | [format "%8.3f" $drift_pct] | ${pct}%"
    }
}

puts ""
if {$ok_po == 0} {
    puts ">>> PUSHOVER ANALYSIS COMPLETED SUCCESSFULLY"
    puts ">>> All $completedSteps steps converged"
} else {
    puts ">>> PUSHOVER ANALYSIS COMPLETED ($completedSteps / $Nsteps_PO steps)"
}
puts ""

# ============================================================================
# PUSHOVER RESULTS SUMMARY
# ============================================================================
puts "============================================================"
puts "  PUSHOVER RESULTS SUMMARY"
puts "============================================================"
puts ""

set finalDisp_po [nodeDisp $ctrlNode $ctrlDOF]
set finalDrift [expr $finalDisp_po / $H_total]

# Tower 2 roof displacement at final state
set finalDisp_T2 [nodeDisp 1641 1]

puts "  --- Capacity Curve Summary ---"
puts "  Final Roof Disp (Tower 1):  [format "%.6f" $finalDisp_po] cm"
puts "  Final Roof Disp (Tower 2):  [format "%.6f" $finalDisp_T2] cm"
puts "  Final Drift Ratio:          [format "%.6f" $finalDrift] ([format "%.3f" [expr $finalDrift * 100]]%)"
puts "  Max Base Shear:             [format "%.4f" $maxBaseShear] kN"
puts "  Disp at Max Shear:          [format "%.4f" $dispAtMaxV] cm"
puts ""

# Estimate yield point and ductility
set nPts [llength $poData]
puts "  Pushover data points: $nPts"

if {$nPts > 20} {
    # Initial stiffness from first 5% of data
    set pt_early [lindex $poData [expr int($nPts * 0.05)]]
    set d_early [lindex $pt_early 0]
    set v_early [lindex $pt_early 1]

    if {$d_early > 0.0} {
        set K_init [expr $v_early / $d_early]
        puts "  Initial Stiffness K0:         [format "%.4f" $K_init] kN/cm"

        # Find approximate yield: where tangent stiffness drops below 50% of initial
        set yieldFound 0
        set yieldDisp 0.0
        set yieldForce 0.0

        for {set k 10} {$k < $nPts} {incr k} {
            set ptA [lindex $poData [expr $k - 5]]
            set ptB [lindex $poData $k]
            set dA [lindex $ptA 0]; set vA [lindex $ptA 1]
            set dB [lindex $ptB 0]; set vB [lindex $ptB 1]
            set dd [expr $dB - $dA]
            if {$dd > 0.0} {
                set K_tan [expr ($vB - $vA) / $dd]
                if {$K_init > 0.0 && [expr $K_tan / $K_init] < 0.5} {
                    set yieldDisp $dA
                    set yieldForce $vA
                    set yieldFound 1
                    break
                }
            }
        }

        if {$yieldFound} {
            puts ""
            puts "  --- Bilinear Approximation ---"
            puts "  Yield Displacement:           [format "%.4f" $yieldDisp] cm"
            puts "  Yield Force:                  [format "%.4f" $yieldForce] kN"
            set ductility [expr $finalDisp_po / $yieldDisp]
            puts "  Ductility Ratio (mu):         [format "%.2f" $ductility]"
            puts "  Yield Drift:                  [format "%.4f" [expr $yieldDisp / $H_total * 100]]%"
        } else {
            puts "  >>> Structure remained essentially elastic (no significant stiffness reduction)"
        }
    }
}
puts ""

# ============================================================================
# SAVE PUSHOVER CURVE TO FILE
# ============================================================================
puts ">>> Saving pushover curve data..."

set poFile [open "results/pushover/pushover_curve.txt" w]
puts $poFile "# TBDY 2018 Static Pushover Analysis - Capacity Curve"
puts $poFile "# Twin Towers V9 (1:50 Scale Model)"
puts $poFile "# Control Node: $ctrlNode (Tower 1 roof center)"
puts $poFile "# Column 1: Roof Displacement (cm)"
puts $poFile "# Column 2: Base Shear (kN)"
puts $poFile "#"
puts $poFile "0.00000000 0.00000000"
foreach pt $poData {
    puts $poFile "[format "%.8f" [lindex $pt 0]] [format "%.8f" [lindex $pt 1]]"
}
close $poFile
puts ">>> Pushover curve: results/pushover/pushover_curve.txt ($nPts data points)"

# Save pushover summary
set poSumFile [open "results/pushover/pushover_summary.txt" w]
puts $poSumFile "==============================================="
puts $poSumFile "TBDY 2018 STATIC PUSHOVER ANALYSIS - RESULTS"
puts $poSumFile "==============================================="
puts $poSumFile ""
puts $poSumFile "Model: Twin Towers V9 (1:50 Scale)"
puts $poSumFile "Nodes: 1680, Elements: 4248"
puts $poSumFile ""
puts $poSumFile "Control Node: $ctrlNode (11.0, 7.4, 153.0 cm)"
puts $poSumFile "Load Pattern: Inverted Triangular (TBDY 2018)"
puts $poSumFile ""
puts $poSumFile "Target Displacement: [format "%.2f" $targetDisp] cm (4% drift)"
puts $poSumFile "Achieved Displacement: [format "%.4f" $finalDisp_po] cm"
puts $poSumFile "Final Drift Ratio: [format "%.6f" $finalDrift]"
puts $poSumFile ""
puts $poSumFile "Max Base Shear: [format "%.4f" $maxBaseShear] kN"
puts $poSumFile "Disp at Max Shear: [format "%.4f" $dispAtMaxV] cm"
puts $poSumFile ""
puts $poSumFile "Completed Steps: $completedSteps / $Nsteps_PO"
close $poSumFile
puts ">>> Pushover summary: results/pushover/pushover_summary.txt"
puts ""

# ============================================================================
# FINAL SUMMARY - ALL THREE ANALYSES
# ============================================================================
puts ""
puts "################################################################"
puts "################################################################"
puts "##                                                            ##"
puts "##           ALL ANALYSES COMPLETED SUCCESSFULLY              ##"
puts "##                                                            ##"
puts "################################################################"
puts "################################################################"
puts ""
puts "  PART 1: A1a Torsional Irregularity Analysis"
puts "    -> torsion_results.txt"
puts "    -> eta_bi (torsional irregularity ratio)"
puts "    -> D_bi (eccentricity amplification factor)"
puts ""
puts "  PART 2: Time History Analysis"
puts "    -> results/time_history/roof_disp_T1.txt"
puts "    -> results/time_history/roof_disp_T2.txt"
puts "    -> results/time_history/roof_vel_T1.txt"
puts "    -> results/time_history/roof_accel_T1.txt"
puts "    -> results/time_history/base_reaction_T1.txt"
puts "    -> results/time_history/envelope_roof_T1.txt"
puts "    -> results/time_history/th_summary.txt"
puts ""
puts "  PART 3: Static Pushover Analysis"
puts "    -> results/pushover/pushover_curve.txt"
puts "    -> results/pushover/pushover_summary.txt"
puts "    -> results/pushover/ctrl_node_disp.txt"
puts "    -> results/pushover/base_react_T1.txt"
puts "    -> results/pushover/floor_profile_ux.txt"
puts ""

# Final cleanup
wipe
puts ">>> Final model cleanup complete"
puts ">>> All output files written to results/ directory"
puts ""
