
puts ""
puts "################################################################"
puts "################################################################"
puts "##                                                            ##"
puts "##  PART 2: TIME HISTORY ANALYSIS - DASK 2026 Ground Motions ##"
puts "##  TBDY 2018 Section 5.6                                     ##"
puts "##  Ground Motions: KYH-1, KYH-2, KYH-3 (dt=0.001s)         ##"
puts "##                                                            ##"
puts "################################################################"
puts "################################################################"
puts ""

# ============================================================================
# RESET ANALYSIS - KEEP MODEL, CLEAR ANALYSIS OBJECTS
# ============================================================================
puts ">>> Clearing previous analysis objects (model preserved)..."
wipeAnalysis
loadConst -time 0.0
puts ">>> Analysis reset complete. Model with 1680 nodes, 4248 elements intact."
puts ">>> Load constant applied, pseudo-time reset to 0."
puts ""

# ============================================================================
# KEY NODE DEFINITIONS FOR MONITORING
# ============================================================================
puts "============================================================"
puts "  KEY MONITORING NODES"
puts "============================================================"

set H_building 153.0  ;# cm (roof z-coordinate)

set roofNode_T1  809   ;# Tower 1 roof center (11.0, 7.4, 153.0)
set roofNode_T2  1641  ;# Tower 2 roof center (11.0, 31.4, 153.0)
set midNode_T1   405   ;# Tower 1 mid-height

puts "  Roof Node Tower 1:   $roofNode_T1  (11.0, 7.4, 153.0 cm)"
puts "  Roof Node Tower 2:   $roofNode_T2  (11.0, 31.4, 153.0 cm)"
puts "  Mid Node Tower 1:    $midNode_T1"
puts "  Building Height:     $H_building cm"
puts ""

set baseNodes_T1 {0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31}
set baseNodes_T2 {832 833 834 835 836 837 838 839 840 841 842 843 844 845 846 847 848 849 850 851 852 853 854 855 856 857 858 859 860 861 862 863}

puts "  Base Nodes Tower 1:  0 - 31 (32 nodes)"
puts "  Base Nodes Tower 2:  832 - 863 (32 nodes)"
puts ""

# ============================================================================
# GROUND MOTION SELECTION
# ============================================================================
# DASK 2026 provides three ground motions:
#   KYH-1: PGA = 0.335 g
#   KYH-2: PGA = 1.243 g
#   KYH-3: PGA = 1.896 g
# All: dt = 0.001 s, duration = 32.232 s, NPTS = 32233
# Format: tab-separated, col1=Time [sec], col2=Acceleration [g]
# ============================================================================

# --- SELECT GROUND MOTION HERE ---
set gmID     "KYH1"
set gmFile   "C:/Users/lenovo/Desktop/DASK_NEW/ground_motion_dask/KYH1.txt"
set dt_gm    0.001    ;# s
set npts_gm  32233

puts "============================================================"
puts "  GROUND MOTION INPUT"
puts "============================================================"
puts ""
puts "  Record:       DASK 2026 $gmID"
puts "  Format:       Tab-separated (Time, Accel [g])"
puts "  NPTS:         $npts_gm"
puts "  DT:           $dt_gm sec"
puts "  Duration:     [format "%.3f" [expr $npts_gm * $dt_gm]] s"
puts ""

# ============================================================================
# READ TAB-SEPARATED GROUND MOTION FILE
# ============================================================================
puts ">>> Reading ground motion file: $gmFile"

if {![file exists $gmFile]} {
    puts "*** FATAL: Ground motion file not found: $gmFile"
    return
}

set gmData {}
set fp [open $gmFile r]
set lineNum 0

while {[gets $fp line] >= 0} {
    incr lineNum
    # Skip header line
    if {$lineNum <= 1} {
        puts "  Header: $line"
        continue
    }
    # Parse tab-separated: Time<tab>Accel
    set fields [split $line "\t"]
    if {[llength $fields] >= 2} {
        set val [string trim [lindex $fields 1]]
        if {$val ne ""} {
            if {![catch {expr double($val)} numVal]} {
                lappend gmData $numVal
            }
        }
    }
}
close $fp

set nRead [llength $gmData]
puts ""
puts ">>> Parsed $nRead acceleration values"
puts "    Expected: $npts_gm values"

# Find PGA
set pga_gm 0.0
foreach val $gmData {
    if {[expr abs($val)] > $pga_gm} {
        set pga_gm [expr abs($val)]
    }
}
puts "    PGA (read) = [format "%.5f" $pga_gm] g = [format "%.4f" [expr $pga_gm * 981.0]] cm/s2"
puts ""

# Write single-column file for OpenSees timeSeries (convert g -> cm/s2)
file mkdir ground_motion
set tempGMfile "ground_motion/${gmID}_opensees.txt"
set fpOut [open $tempGMfile w]
foreach val $gmData {
    puts $fpOut [format "%.8f" [expr $val * 981.0]]
}
close $fpOut
puts ">>> Converted to single-column format: $tempGMfile"
puts "    Units: g -> cm/s2 (x 981.0)"
puts ""

# ============================================================================
# SETUP RECORDERS FOR TIME HISTORY
# ============================================================================
puts "============================================================"
puts "  RECORDER SETUP"
puts "============================================================"

file mkdir results
file mkdir results/time_history

recorder Node -file results/time_history/roof_disp_T1.txt    -node $roofNode_T1 -dof 1 2 3 disp
recorder Node -file results/time_history/roof_disp_T2.txt    -node $roofNode_T2 -dof 1 2 3 disp
puts "  [OK] Roof displacement recorders (T1: node $roofNode_T1, T2: node $roofNode_T2)"

recorder Node -file results/time_history/roof_vel_T1.txt     -node $roofNode_T1 -dof 1 2 3 vel
recorder Node -file results/time_history/roof_vel_T2.txt     -node $roofNode_T2 -dof 1 2 3 vel
puts "  [OK] Roof velocity recorders"

recorder Node -file results/time_history/roof_accel_T1.txt   -node $roofNode_T1 -dof 1 2 3 accel
recorder Node -file results/time_history/roof_accel_T2.txt   -node $roofNode_T2 -dof 1 2 3 accel
puts "  [OK] Roof acceleration recorders"

recorder Node -file results/time_history/mid_disp_T1.txt     -node $midNode_T1 -dof 1 2 3 disp
puts "  [OK] Mid-height displacement recorder (node $midNode_T1)"

recorder Node -file results/time_history/base_reaction_T1.txt -node 0 1 2 3 4 5 6 7 8 9 -dof 1 2 3 reaction
recorder Node -file results/time_history/base_reaction_T2.txt -node 832 833 834 835 836 837 838 839 840 841 -dof 1 2 3 reaction
puts "  [OK] Base reaction recorders"

recorder EnvelopeNode -file results/time_history/envelope_roof_T1.txt -node $roofNode_T1 -dof 1 2 3 disp
recorder EnvelopeNode -file results/time_history/envelope_roof_T2.txt -node $roofNode_T2 -dof 1 2 3 disp
puts "  [OK] Envelope displacement recorders"

recorder Node -file results/time_history/all_roof_ux_T1.txt -node 800 801 802 803 804 805 806 807 808 809 810 811 812 813 814 815 816 817 818 819 820 821 822 823 824 825 826 827 828 829 830 831 -dof 1 disp
recorder Node -file results/time_history/all_roof_ux_T2.txt -node 1632 1633 1634 1635 1636 1637 1638 1639 1640 1641 1642 1643 1644 1645 1646 1647 1648 1649 1650 1651 1652 1653 1654 1655 1656 1657 1658 1659 1660 1661 1662 1663 -dof 1 disp
puts "  [OK] All roof nodes X-displacement recorders (dynamic torsion check)"

recorder Drift -file results/time_history/drift_story_05.txt -iNode 137 -jNode 169 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_10.txt -iNode 297 -jNode 329 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_15.txt -iNode 457 -jNode 489 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_20.txt -iNode 617 -jNode 649 -dof 1 -perpDirn 3
recorder Drift -file results/time_history/drift_story_25.txt -iNode 777 -jNode 809 -dof 1 -perpDirn 3
puts "  [OK] Interstory drift recorders (floors 5, 10, 15, 20, 25)"

puts ""
puts ">>> Total recorders configured: 17"
puts ""

# ============================================================================
# RAYLEIGH DAMPING (5% critical - TBDY 2018 typical for steel structures)
# ============================================================================
puts "============================================================"
puts "  RAYLEIGH DAMPING CONFIGURATION"
puts "============================================================"

set omega1_th [expr 2.0 * 3.14159265358979 / $T1]
set omega3_th [expr $omega1_th * 3.5]
set xi_damp 0.05

set a0_damp [expr 2.0 * $xi_damp * $omega1_th * $omega3_th / ($omega1_th + $omega3_th)]
set a1_damp [expr 2.0 * $xi_damp / ($omega1_th + $omega3_th)]

puts ""
puts "  Damping ratio (xi):          [expr $xi_damp * 100.0]%"
puts "  Fundamental period T1:       [format "%.4f" $T1] s"
puts "  omega_1:                     [format "%.4f" $omega1_th] rad/s"
puts "  omega_3 (estimated):         [format "%.4f" $omega3_th] rad/s"
puts "  Rayleigh a0 (mass-prop):     [format "%.6f" $a0_damp]"
puts "  Rayleigh a1 (stiffness-prop):[format "%.6f" $a1_damp]"
puts ""

rayleigh $a0_damp $a1_damp 0.0 0.0
puts ">>> Rayleigh damping applied"
puts ""

# ============================================================================
# GROUND MOTION EXCITATION PATTERN
# ============================================================================
puts "============================================================"
puts "  APPLYING GROUND MOTION EXCITATION"
puts "============================================================"
puts ""

set tsTag_TH 100
timeSeries Path $tsTag_TH -dt $dt_gm -filePath $tempGMfile -factor 1.0
puts ">>> Time series created (Tag=$tsTag_TH)"
puts "    dt = $dt_gm s, source = $tempGMfile"
puts "    Factor = 1.0 (data already in cm/s2)"
puts ""

# Uniform excitation in X-direction (DOF 1)
pattern UniformExcitation 200 1 -accel $tsTag_TH
puts ">>> Uniform Excitation applied:"
puts "    Pattern Tag:  200"
puts "    Direction:    1 (X-direction)"
puts ""

# ============================================================================
# TRANSIENT ANALYSIS CONFIGURATION
# ============================================================================
puts "============================================================"
puts "  TRANSIENT ANALYSIS CONFIGURATION"
puts "============================================================"
puts ""

# dt_gm = 0.001 s is very fine; use a larger analysis dt for efficiency.
# OpenSees interpolates the ground motion between time series points.
# dt_analysis = 0.005 s => 5x the input dt, still well within Nyquist.
set dt_analysis 0.005
set duration_TH [expr $npts_gm * $dt_gm]
set Nsteps_TH [expr int($duration_TH / $dt_analysis)]

constraints Transformation
puts "  Constraints handler:  Transformation"

numberer RCM
puts "  DOF numberer:         RCM (Reverse Cuthill-McKee)"

system BandGeneral
puts "  System of equations:  BandGeneral"

test NormDispIncr 1.0e-6 50
puts "  Convergence test:     NormDispIncr (tol=1e-6, maxIter=50)"

algorithm Newton
puts "  Solution algorithm:   Newton-Raphson"

integrator Newmark 0.5 0.25
puts "  Time integrator:      Newmark (gamma=0.5, beta=0.25)"

analysis Transient
puts "  Analysis type:        Transient"
puts ""
puts "  Analysis time step:   $dt_analysis s"
puts "  Ground motion dt:     $dt_gm s"
puts "  Total duration:       [format "%.3f" $duration_TH] s"
puts "  Total analysis steps: $Nsteps_TH"
puts ""

# ============================================================================
# RUN TIME HISTORY ANALYSIS
# ============================================================================
puts "============================================================"
puts "  RUNNING TIME HISTORY ANALYSIS ($gmID)"
puts "  $Nsteps_TH steps x $dt_analysis s = [format "%.1f" $duration_TH] s"
puts "============================================================"
puts ""

set ok_th 0
set failedSteps 0
set maxRoofUx_T1 0.0
set maxRoofUx_T2 0.0
set maxRoofUy_T1 0.0

set progInterval [expr int($Nsteps_TH / 20)]
if {$progInterval < 1} { set progInterval 1 }

puts ">>> Step | Time(s) | Roof-T1 Ux(cm) | Roof-T2 Ux(cm) | Status"
puts ">>> -----|---------|----------------|----------------|-------"

for {set step 1} {$step <= $Nsteps_TH} {incr step} {

    set ok_th [analyze 1 $dt_analysis]

    if {$ok_th != 0} {
        # Strategy 1: Modified Newton
        algorithm ModifiedNewton
        set ok_th [analyze 1 $dt_analysis]

        if {$ok_th != 0} {
            # Strategy 2: Relaxed tolerance
            test NormDispIncr 1.0e-5 100
            algorithm Newton
            set ok_th [analyze 1 $dt_analysis]

            if {$ok_th != 0} {
                # Strategy 3: Subdivide time step (10 substeps)
                algorithm ModifiedNewton
                test NormDispIncr 1.0e-4 200
                set dt_sub [expr $dt_analysis / 10.0]
                set subOK 0
                for {set sub 1} {$sub <= 10} {incr sub} {
                    set subOK [analyze 1 $dt_sub]
                    if {$subOK != 0} {
                        puts "  *** Substep $sub/10 failed at step $step (t=[format "%.3f" [expr $step*$dt_analysis]]s)"
                        incr failedSteps
                        break
                    }
                }
                set ok_th $subOK
            }
        }

        # Restore defaults
        algorithm Newton
        test NormDispIncr 1.0e-6 50
    }

    if {$ok_th != 0} {
        incr failedSteps
        if {$failedSteps > 20} {
            puts ""
            puts "*** ANALYSIS STOPPED: Too many convergence failures ($failedSteps)"
            puts "*** Last successful time: [format "%.3f" [expr ($step - $failedSteps) * $dt_analysis]] s"
            break
        }
    }

    if {[expr $step % $progInterval] == 0 || $step == $Nsteps_TH || $step <= 3} {
        set ux_t1 [nodeDisp $roofNode_T1 1]
        set ux_t2 [nodeDisp $roofNode_T2 1]
        set uy_t1 [nodeDisp $roofNode_T1 2]

        if {[expr abs($ux_t1)] > $maxRoofUx_T1} { set maxRoofUx_T1 [expr abs($ux_t1)] }
        if {[expr abs($ux_t2)] > $maxRoofUx_T2} { set maxRoofUx_T2 [expr abs($ux_t2)] }
        if {[expr abs($uy_t1)] > $maxRoofUy_T1} { set maxRoofUy_T1 [expr abs($uy_t1)] }

        set pct [expr int(100.0 * $step / $Nsteps_TH)]
        set tNow [format "%.3f" [expr $step * $dt_analysis]]
        puts ">>> [format "%4d" $step] | [format "%7s" $tNow] | [format "%14.6f" $ux_t1] | [format "%14.6f" $ux_t2] | ${pct}%"
    }
}

puts ""
if {$failedSteps == 0} {
    puts ">>> TIME HISTORY ANALYSIS COMPLETED SUCCESSFULLY ($gmID)"
    puts ">>> All $Nsteps_TH steps converged"
} else {
    puts ">>> TIME HISTORY ANALYSIS COMPLETED WITH $failedSteps CONVERGENCE ISSUES ($gmID)"
}
puts ""

# ============================================================================
# TIME HISTORY RESULTS SUMMARY
# ============================================================================
puts "============================================================"
puts "  TIME HISTORY RESULTS SUMMARY ($gmID)"
puts "============================================================"
puts ""

set finalUx_T1 [nodeDisp $roofNode_T1 1]
set finalUy_T1 [nodeDisp $roofNode_T1 2]
set finalUz_T1 [nodeDisp $roofNode_T1 3]
set finalUx_T2 [nodeDisp $roofNode_T2 1]
set finalUy_T2 [nodeDisp $roofNode_T2 2]
set finalUz_T2 [nodeDisp $roofNode_T2 3]

puts "  --- Final State Displacements ---"
puts "  Tower 1 Roof (Node $roofNode_T1):"
puts "    Ux = [format "%12.6f" $finalUx_T1] cm"
puts "    Uy = [format "%12.6f" $finalUy_T1] cm"
puts "    Uz = [format "%12.6f" $finalUz_T1] cm"
puts ""
puts "  Tower 2 Roof (Node $roofNode_T2):"
puts "    Ux = [format "%12.6f" $finalUx_T2] cm"
puts "    Uy = [format "%12.6f" $finalUy_T2] cm"
puts "    Uz = [format "%12.6f" $finalUz_T2] cm"
puts ""

puts "  --- Maximum Absolute Responses ---"
puts "  Max Roof Ux (Tower 1): [format "%.6f" $maxRoofUx_T1] cm"
puts "  Max Roof Ux (Tower 2): [format "%.6f" $maxRoofUx_T2] cm"
puts "  Max Roof Uy (Tower 1): [format "%.6f" $maxRoofUy_T1] cm"
puts ""

set driftX_T1 [expr $maxRoofUx_T1 / $H_building]
set driftX_T2 [expr $maxRoofUx_T2 / $H_building]

puts "  --- Roof Drift Ratios ---"
puts "  Tower 1 X-drift: [format "%.6f" $driftX_T1] = [format "%.3f" [expr $driftX_T1 * 100]]%"
puts "  Tower 2 X-drift: [format "%.6f" $driftX_T2] = [format "%.3f" [expr $driftX_T2 * 100]]%"
puts ""

set driftLimit_service 0.008
set driftLimit_collapse 0.020

puts "  --- TBDY 2018 Drift Limit Check ---"
puts "  Serviceability limit (Table 4.9):      $driftLimit_service"
puts "  Collapse prevention limit:              $driftLimit_collapse"
puts ""

if {$driftX_T1 > $driftLimit_collapse} {
    puts "  >>> WARNING: Tower 1 EXCEEDS collapse prevention limit!"
} elseif {$driftX_T1 > $driftLimit_service} {
    puts "  >>> Tower 1: Within collapse prevention, EXCEEDS serviceability"
} else {
    puts "  >>> Tower 1: WITHIN serviceability limits - OK"
}

if {$driftX_T2 > $driftLimit_collapse} {
    puts "  >>> WARNING: Tower 2 EXCEEDS collapse prevention limit!"
} elseif {$driftX_T2 > $driftLimit_service} {
    puts "  >>> Tower 2: Within collapse prevention, EXCEEDS serviceability"
} else {
    puts "  >>> Tower 2: WITHIN serviceability limits - OK"
}
puts ""

set diffDisp [expr abs($maxRoofUx_T1 - $maxRoofUx_T2)]
puts "  --- Sky Bridge Differential Movement ---"
puts "  Max differential roof X-disp: [format "%.6f" $diffDisp] cm"
puts ""

# ============================================================================
# SAVE TIME HISTORY SUMMARY
# ============================================================================
set thSumFile [open "results/time_history/th_summary_${gmID}.txt" w]
puts $thSumFile "==============================================="
puts $thSumFile "TBDY 2018 TIME HISTORY ANALYSIS - RESULTS"
puts $thSumFile "Ground Motion: DASK 2026 $gmID"
puts $thSumFile "==============================================="
puts $thSumFile ""
puts $thSumFile "Model: Twin Towers V9 (1:50 Scale)"
puts $thSumFile "Nodes: 1680, Elements: 4248"
puts $thSumFile ""
puts $thSumFile "Ground Motion: $gmID"
puts $thSumFile "  PGA: [format "%.5f" $pga_gm] g"
puts $thSumFile "  NPTS: $nRead, DT: $dt_gm s"
puts $thSumFile "  Duration: [format "%.3f" $duration_TH] s"
puts $thSumFile ""
puts $thSumFile "Damping: $xi_damp (Rayleigh)"
puts $thSumFile "T1 = [format "%.4f" $T1] s"
puts $thSumFile ""
puts $thSumFile "RESULTS:"
puts $thSumFile "  Tower 1 Max Roof Ux: [format "%.6f" $maxRoofUx_T1] cm"
puts $thSumFile "  Tower 2 Max Roof Ux: [format "%.6f" $maxRoofUx_T2] cm"
puts $thSumFile "  Tower 1 Max Roof Uy: [format "%.6f" $maxRoofUy_T1] cm"
puts $thSumFile "  Tower 1 Drift Ratio: [format "%.6f" $driftX_T1]"
puts $thSumFile "  Tower 2 Drift Ratio: [format "%.6f" $driftX_T2]"
puts $thSumFile "  Differential Disp:   [format "%.6f" $diffDisp] cm"
puts $thSumFile ""
puts $thSumFile "Convergence failures: $failedSteps / $Nsteps_TH steps"
close $thSumFile

puts ">>> Results saved to results/time_history/th_summary_${gmID}.txt"
puts ""
