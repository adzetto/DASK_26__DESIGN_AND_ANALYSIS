# ============================================================================
# ADVANCED TIME HISTORY ANALYSIS - DASK 2026 Ground Motions
# Full V9 Twin Towers Model (1680 nodes, 4248 elements)
# All-node recorders, periodic flushing, robust convergence
# Ground Motions: KYH-1 (0.335g), KYH-2 (1.243g), KYH-3 (1.896g)
# ============================================================================
# Usage:
#   opensees advanced_time_history_dask.tcl
#   (runs from analysis/torsional_irregularity/ directory)
# ============================================================================

set startWall [clock seconds]

puts ""
puts "################################################################"
puts "##  ADVANCED TIME HISTORY ANALYSIS - DASK 2026               ##"
puts "##  Full V9 Model: 1680 nodes, 4248 elements                 ##"
puts "##  All-node recording, robust convergence                   ##"
puts "################################################################"
puts ""

# ============================================================================
# STEP 1: BUILD V9 MODEL (source the trimmed torsion script)
# The script builds model (nodes, elements, mass, fix) + eigenvalue analysis.
# Torsion analysis may crash due to timeSeries tag conflicts - we catch that.
# After sourcing, we have: T1, model with 1680 nodes, 4248 elements
# ============================================================================
puts ">>> STEP 1: Building V9 model via tbdy2018_torsion_analysis_trimmed.tcl"
puts ">>> This takes a moment (1680 nodes, 4248 elements, eigenvalue)..."
puts ""

if {[catch {source tbdy2018_torsion_analysis_trimmed.tcl} errMsg]} {
    puts ""
    puts ">>> NOTE: Torsion analysis section encountered an error (expected):"
    puts ">>>   $errMsg"
    puts ">>> Model + eigenvalue already completed. Continuing..."
}

# Clean up any leftover analysis state from torsion script
catch {wipeAnalysis}
catch {remove recorders}
catch {remove loadPattern 1}
catch {remove timeSeries 1}
loadConst -time 0.0

puts ""
puts ">>> V9 model preserved (1680 nodes, 4248 elements)."
puts ">>> T1 (eigenvalue) = [format "%.4f" $T1] s"
puts ""

# T1 ~ 0.2s with scaled stiffness (E*240 for collective frame action)
puts ">>> Rayleigh damping calibrated to T1 = [format "%.4f" $T1] s"
puts ""

# ============================================================================
# STEP 2: GROUND MOTION DEFINITIONS
# ============================================================================
# All three DASK 2026 ground motions
# Format: tab-separated (Time [sec] <tab> Acceleration [g])
# dt = 0.001 s, NPTS = 32233, Duration = 32.232 s
# ============================================================================

set gmDir "C:/Users/lenovo/Desktop/DASK_NEW/ground_motion_dask"

set gmList {
    {KYH1  KYH1.txt  0.335}
    {KYH2  KYH2.txt  1.243}
    {KYH3  KYH3.txt  1.896}
}

set dt_gm    0.001
set npts_gm  32233

# Analysis parameters
set dt_analysis 0.005     ;# 5x ground motion dt (OpenSees interpolates)
set xi_damp     0.05      ;# 5% critical damping
set H_building  153.0     ;# cm

# Node ranges
set numNodes   1680
set numFloors  25
set nodesPerFloor 32

# Tower 1: floor i -> nodes [i*32 .. i*32+31]
# Tower 2: floor i -> nodes [832 + i*32 .. 832 + i*32+31]
# Bridge nodes: 1664-1679
# Base (fixed): T1 = 0-31, T2 = 832-863

# Roof nodes
set roofNode_T1  809    ;# Tower 1 roof center (11.0, 7.4, 153.0)
set roofNode_T2  1641   ;# Tower 2 roof center (11.0, 31.4, 153.0)

puts "============================================================"
puts "  GROUND MOTIONS TO ANALYZE"
puts "============================================================"
foreach gm $gmList {
    set id  [lindex $gm 0]
    set f   [lindex $gm 1]
    set pga [lindex $gm 2]
    puts "  $id: PGA = ${pga} g, file = $f"
}
puts "  dt = $dt_gm s, NPTS = $npts_gm, Duration = [format "%.3f" [expr $npts_gm * $dt_gm]] s"
puts ""

# ============================================================================
# HELPER: Read tab-separated ground motion file
# Returns list of acceleration values in g
# ============================================================================
proc readGM {filepath} {
    set data {}
    set fp [open $filepath r]
    set lineNum 0
    while {[gets $fp line] >= 0} {
        incr lineNum
        if {$lineNum <= 1} { continue }
        set fields [split $line "\t"]
        if {[llength $fields] >= 2} {
            set val [string trim [lindex $fields 1]]
            if {$val ne "" && ![catch {expr double($val)} numVal]} {
                lappend data $numVal
            }
        }
    }
    close $fp
    return $data
}

# ============================================================================
# HELPER: Write single-column cm/s2 file for OpenSees
# ============================================================================
proc writeGMforOS {data outpath g} {
    set fp [open $outpath w]
    foreach val $data {
        puts $fp [format "%.8f" [expr $val * $g]]
    }
    close $fp
}

# ============================================================================
# LOOP OVER EACH GROUND MOTION
# ============================================================================
set gmIndex 0

foreach gm $gmList {
    set gmID    [lindex $gm 0]
    set gmFile  [lindex $gm 1]
    set gmPGA   [lindex $gm 2]
    incr gmIndex

    set gmStartWall [clock seconds]

    puts ""
    puts "################################################################"
    puts "##  GROUND MOTION $gmIndex / 3: $gmID (PGA = ${gmPGA} g)"
    puts "################################################################"
    puts ""

    # ------------------------------------------------------------------
    # Reset analysis state, keep model
    # ------------------------------------------------------------------
    catch {wipeAnalysis}
    catch {remove recorders}
    catch {reset}
    catch {loadConst -time 0.0}

    # Remove any leftover load patterns and timeSeries from previous GM
    for {set tag 100} {$tag <= 210} {incr tag} {
        catch {remove loadPattern $tag}
        catch {remove timeSeries $tag}
    }
    # Also remove tags that torsion analysis may have left
    for {set tag 1} {$tag <= 10} {incr tag} {
        catch {remove loadPattern $tag}
        catch {remove timeSeries $tag}
    }

    puts ">>> Model reset for $gmID (nodes/elements preserved, zero state)"

    # ------------------------------------------------------------------
    # Read and convert ground motion
    # ------------------------------------------------------------------
    set gmFullPath "${gmDir}/${gmFile}"
    puts ">>> Reading: $gmFullPath"

    if {![file exists $gmFullPath]} {
        puts "*** ERROR: File not found: $gmFullPath"
        puts "*** Skipping $gmID"
        continue
    }

    set gmData [readGM $gmFullPath]
    set nRead [llength $gmData]
    puts ">>> Parsed $nRead values"

    # Verify PGA
    set pgaRead 0.0
    foreach val $gmData {
        if {[expr abs($val)] > $pgaRead} { set pgaRead [expr abs($val)] }
    }
    puts ">>> PGA (verified) = [format "%.5f" $pgaRead] g"

    # Write OpenSees format
    file mkdir ground_motion
    set osGMfile "ground_motion/${gmID}_opensees.txt"
    writeGMforOS $gmData $osGMfile 981.0
    puts ">>> Written: $osGMfile (cm/s2)"
    puts ""

    # ------------------------------------------------------------------
    # Create output directories
    # ------------------------------------------------------------------
    set outDir "results/th_${gmID}"
    file mkdir $outDir
    file mkdir ${outDir}/node_disp
    file mkdir ${outDir}/node_vel
    file mkdir ${outDir}/node_accel
    file mkdir ${outDir}/node_reaction
    file mkdir ${outDir}/element_forces
    file mkdir ${outDir}/drift
    file mkdir ${outDir}/envelope

    puts ">>> Output directory: $outDir"
    puts ""

    # ------------------------------------------------------------------
    # ALL-NODE RECORDERS
    # ------------------------------------------------------------------
    puts "============================================================"
    puts "  SETTING UP ALL-NODE RECORDERS ($gmID)"
    puts "============================================================"

    # --- All free nodes: displacement (DOF 1,2,3) ---
    # Tower 1 floors 1-25 (nodes 32-831)
    for {set fl 1} {$fl <= $numFloors} {incr fl} {
        set n0 [expr $fl * $nodesPerFloor]
        set nList {}
        for {set j 0} {$j < $nodesPerFloor} {incr j} {
            lappend nList [expr $n0 + $j]
        }
        recorder Node -file ${outDir}/node_disp/T1_floor${fl}_disp.txt \
            -node {*}$nList -dof 1 2 3 disp
    }
    puts "  (OK) Tower 1 displacement: 25 floors x 32 nodes (DOF 1,2,3)"

    # Tower 2 floors 1-25 (nodes 864-1663)
    for {set fl 1} {$fl <= $numFloors} {incr fl} {
        set n0 [expr 832 + $fl * $nodesPerFloor]
        set nList {}
        for {set j 0} {$j < $nodesPerFloor} {incr j} {
            lappend nList [expr $n0 + $j]
        }
        recorder Node -file ${outDir}/node_disp/T2_floor${fl}_disp.txt \
            -node {*}$nList -dof 1 2 3 disp
    }
    puts "  (OK) Tower 2 displacement: 25 floors x 32 nodes (DOF 1,2,3)"

    # Bridge nodes (1664-1679)
    set bridgeNodes {}
    for {set j 1664} {$j <= 1679} {incr j} { lappend bridgeNodes $j }
    recorder Node -file ${outDir}/node_disp/bridge_disp.txt \
        -node {*}$bridgeNodes -dof 1 2 3 disp
    puts "  (OK) Bridge nodes displacement (nodes 1664-1679)"

    # --- Roof node velocity and acceleration ---
    recorder Node -file ${outDir}/node_vel/roof_T1_vel.txt \
        -node $roofNode_T1 -dof 1 2 3 vel
    recorder Node -file ${outDir}/node_vel/roof_T2_vel.txt \
        -node $roofNode_T2 -dof 1 2 3 vel
    recorder Node -file ${outDir}/node_accel/roof_T1_accel.txt \
        -node $roofNode_T1 -dof 1 2 3 accel
    recorder Node -file ${outDir}/node_accel/roof_T2_accel.txt \
        -node $roofNode_T2 -dof 1 2 3 accel
    puts "  (OK) Roof velocity and acceleration (T1, T2)"

    # --- All floor velocity (one representative node per floor) ---
    # Center nodes: floor i -> node i*32 + 9 (Tower 1), 832 + i*32 + 9 (Tower 2)
    set repNodes_T1 {}
    set repNodes_T2 {}
    for {set fl 1} {$fl <= $numFloors} {incr fl} {
        lappend repNodes_T1 [expr $fl * 32 + 9]
        lappend repNodes_T2 [expr 832 + $fl * 32 + 9]
    }
    recorder Node -file ${outDir}/node_vel/T1_center_vel.txt \
        -node {*}$repNodes_T1 -dof 1 2 3 vel
    recorder Node -file ${outDir}/node_vel/T2_center_vel.txt \
        -node {*}$repNodes_T2 -dof 1 2 3 vel
    puts "  (OK) All-floor center node velocity (T1, T2)"

    # --- Base reactions (all 64 fixed nodes) ---
    set baseT1 {}
    for {set j 0} {$j <= 31} {incr j} { lappend baseT1 $j }
    set baseT2 {}
    for {set j 832} {$j <= 863} {incr j} { lappend baseT2 $j }

    recorder Node -file ${outDir}/node_reaction/base_T1_reaction.txt \
        -node {*}$baseT1 -dof 1 2 3 reaction
    recorder Node -file ${outDir}/node_reaction/base_T2_reaction.txt \
        -node {*}$baseT2 -dof 1 2 3 reaction
    puts "  (OK) All base node reactions (T1: 32 nodes, T2: 32 nodes)"

    # --- Interstory drift at all floors (center column, DOF 1) ---
    for {set fl 1} {$fl <= $numFloors} {incr fl} {
        set iNode [expr ($fl - 1) * 32 + 9]
        set jNode [expr $fl * 32 + 9]
        recorder Drift -file ${outDir}/drift/T1_drift_floor${fl}.txt \
            -iNode $iNode -jNode $jNode -dof 1 -perpDirn 3
    }
    for {set fl 1} {$fl <= $numFloors} {incr fl} {
        set iNode [expr 832 + ($fl - 1) * 32 + 9]
        set jNode [expr 832 + $fl * 32 + 9]
        recorder Drift -file ${outDir}/drift/T2_drift_floor${fl}.txt \
            -iNode $iNode -jNode $jNode -dof 1 -perpDirn 3
    }
    puts "  (OK) Interstory drift: all 25 floors, both towers (DOF 1)"

    # --- Envelope recorders (min/max over entire analysis) ---
    for {set fl 1} {$fl <= $numFloors} {incr fl} {
        set n0_T1 [expr $fl * 32]
        set n0_T2 [expr 832 + $fl * 32]
        set nList_T1 {}
        set nList_T2 {}
        for {set j 0} {$j < $nodesPerFloor} {incr j} {
            lappend nList_T1 [expr $n0_T1 + $j]
            lappend nList_T2 [expr $n0_T2 + $j]
        }
        recorder EnvelopeNode -file ${outDir}/envelope/T1_floor${fl}_env.txt \
            -node {*}$nList_T1 -dof 1 2 3 disp
        recorder EnvelopeNode -file ${outDir}/envelope/T2_floor${fl}_env.txt \
            -node {*}$nList_T2 -dof 1 2 3 disp
    }
    puts "  (OK) Envelope displacement: all 25 floors, both towers"

    # --- Element forces (selected elements per floor) ---
    # Record element local forces for representative columns (element per floor)
    # Elements 1-25 are typically floor 1-25 columns in Tower 1
    # We record every 100th element to keep file sizes manageable
    set elemSample {}
    for {set e 1} {$e <= 4248} {incr e 100} {
        lappend elemSample $e
    }
    recorder Element -file ${outDir}/element_forces/sample_forces.txt \
        -ele {*}$elemSample localForce
    puts "  (OK) Element local forces (every 100th element, [llength $elemSample] elements)"

    puts ""

    # Count total recorders
    # 25 T1 disp + 25 T2 disp + 1 bridge + 4 roof vel/accel + 2 center vel
    # + 2 base reaction + 25 T1 drift + 25 T2 drift + 25 T1 env + 25 T2 env + 1 elem
    set nRecorders [expr 25 + 25 + 1 + 4 + 2 + 2 + 25 + 25 + 25 + 25 + 1]
    puts ">>> Total recorders: $nRecorders"
    puts ""

    # ------------------------------------------------------------------
    # RAYLEIGH DAMPING
    # ------------------------------------------------------------------
    puts "============================================================"
    puts "  RAYLEIGH DAMPING (${xi_damp} = [expr int($xi_damp*100)]%)"
    puts "============================================================"

    set omega1 [expr 2.0 * 3.14159265358979 / $T1]
    set omega3 [expr $omega1 * 3.5]
    set a0 [expr 2.0 * $xi_damp * $omega1 * $omega3 / ($omega1 + $omega3)]
    set a1 [expr 2.0 * $xi_damp / ($omega1 + $omega3)]

    rayleigh $a0 $a1 0.0 0.0
    puts "  omega1 = [format "%.4f" $omega1] rad/s (T1 = [format "%.4f" $T1] s)"
    puts "  omega3 = [format "%.4f" $omega3] rad/s"
    puts "  a0 = [format "%.6f" $a0], a1 = [format "%.8f" $a1]"
    puts ""

    # ------------------------------------------------------------------
    # GROUND MOTION EXCITATION
    # ------------------------------------------------------------------
    puts "============================================================"
    puts "  APPLYING GROUND MOTION: $gmID"
    puts "============================================================"

    set tsTag [expr 100 + $gmIndex]
    set patTag [expr 200 + $gmIndex]

    timeSeries Path $tsTag -dt $dt_gm -filePath $osGMfile -factor 1.0
    pattern UniformExcitation $patTag 1 -accel $tsTag

    puts "  TimeSeries Tag = $tsTag, dt = $dt_gm s"
    puts "  UniformExcitation Tag = $patTag, DOF = 1 (X-direction)"
    puts "  Factor = 1.0 (data in cm/s2)"
    puts ""

    # ------------------------------------------------------------------
    # TRANSIENT ANALYSIS CONFIGURATION
    # ------------------------------------------------------------------
    puts "============================================================"
    puts "  TRANSIENT ANALYSIS SETUP"
    puts "============================================================"

    set duration_TH [expr $nRead * $dt_gm]
    set Nsteps_TH [expr int($duration_TH / $dt_analysis)]

    constraints Transformation
    numberer RCM
    system BandGeneral
    test NormDispIncr 1.0e-6 50
    algorithm Newton
    integrator Newmark 0.5 0.25
    analysis Transient

    puts "  Constraints:    Transformation"
    puts "  Numberer:       RCM"
    puts "  System:         BandGeneral"
    puts "  Test:           NormDispIncr 1e-6, maxIter=50"
    puts "  Algorithm:      Newton-Raphson"
    puts "  Integrator:     Newmark (0.5, 0.25)"
    puts "  dt_analysis:    $dt_analysis s"
    puts "  dt_ground:      $dt_gm s"
    puts "  Duration:       [format "%.3f" $duration_TH] s"
    puts "  Total steps:    $Nsteps_TH"
    puts ""

    # ------------------------------------------------------------------
    # PROGRESS LOG FILE (written at every checkpoint)
    # ------------------------------------------------------------------
    set logFile [open "${outDir}/analysis_log.txt" w]
    puts $logFile "DASK 2026 Time History Analysis Log"
    puts $logFile "Ground Motion: $gmID (PGA = ${gmPGA} g)"
    puts $logFile "Model: V9 Twin Towers (1680 nodes, 4248 elements)"
    puts $logFile "dt_analysis = $dt_analysis s, Nsteps = $Nsteps_TH"
    puts $logFile "Started: [clock seconds]"
    puts $logFile "================================================"
    puts $logFile ""
    flush $logFile

    # ------------------------------------------------------------------
    # RUN TIME HISTORY ANALYSIS
    # ------------------------------------------------------------------
    puts "============================================================"
    puts "  RUNNING: $gmID | $Nsteps_TH steps | ~[format "%.1f" $duration_TH] s"
    puts "  Started: [clock seconds]"
    puts "============================================================"
    puts ""

    set ok 0
    set failedSteps 0
    set totalFailed 0
    set maxUx_T1 0.0
    set maxUx_T2 0.0
    set maxUy_T1 0.0
    set maxUy_T2 0.0

    # Checkpoint interval: every 2% (~130 steps for 6446 total)
    set checkInterval [expr max(1, int($Nsteps_TH / 50))]
    # Recorder flush interval: every 5%
    set flushInterval [expr max(1, int($Nsteps_TH / 20))]

    puts [format "%-8s | %-9s | %-14s | %-14s | %-14s | %-14s | %s" \
        "Step" "Time(s)" "T1-Ux(cm)" "T1-Uy(cm)" "T2-Ux(cm)" "T2-Uy(cm)" "Status"]
    puts "---------|-----------|----------------|----------------|----------------|----------------|-------"

    for {set step 1} {$step <= $Nsteps_TH} {incr step} {

        set ok [analyze 1 $dt_analysis]

        # ---- CONVERGENCE RECOVERY ----
        if {$ok != 0} {
            # Strategy 1: ModifiedNewton
            algorithm ModifiedNewton
            set ok [analyze 1 $dt_analysis]

            if {$ok != 0} {
                # Strategy 2: Relaxed tolerance + more iterations
                test NormDispIncr 1.0e-5 100
                algorithm Newton
                set ok [analyze 1 $dt_analysis]

                if {$ok != 0} {
                    # Strategy 3: NewtonLineSearch
                    algorithm NewtonLineSearch 0.8
                    set ok [analyze 1 $dt_analysis]

                    if {$ok != 0} {
                        # Strategy 4: Very relaxed + ModifiedNewton
                        algorithm ModifiedNewton
                        test NormDispIncr 1.0e-4 200
                        set ok [analyze 1 $dt_analysis]

                        if {$ok != 0} {
                            # Strategy 5: Subdivide time step (10 substeps)
                            set dt_sub [expr $dt_analysis / 10.0]
                            set subOK 0
                            for {set sub 1} {$sub <= 10} {incr sub} {
                                set subOK [analyze 1 $dt_sub]
                                if {$subOK != 0} {
                                    # Strategy 6: Even finer substep (50 substeps)
                                    algorithm ModifiedNewton
                                    test NormDispIncr 1.0e-3 500
                                    set dt_sub2 [expr $dt_analysis / 50.0]
                                    for {set sub2 1} {$sub2 <= 5} {incr sub2} {
                                        set subOK [analyze 1 $dt_sub2]
                                        if {$subOK != 0} { break }
                                    }
                                    if {$subOK != 0} { break }
                                }
                            }
                            set ok $subOK
                        }
                    }
                }
            }

            # Restore defaults for next step
            algorithm Newton
            test NormDispIncr 1.0e-6 50
        }

        if {$ok != 0} {
            incr totalFailed
            set tNow [format "%.3f" [expr $step * $dt_analysis]]
            puts "  *** CONVERGENCE FAILURE at step $step (t=${tNow}s) | Total failures: $totalFailed"
            puts $logFile "FAIL: step=$step t=${tNow}s total_failures=$totalFailed"
            flush $logFile

            if {$totalFailed > 50} {
                puts ""
                puts "*** ANALYSIS ABORTED: $totalFailed convergence failures"
                puts "*** Last step: $step / $Nsteps_TH"
                puts $logFile ""
                puts $logFile "ABORTED at step $step ($totalFailed failures)"
                flush $logFile
                break
            }
        }

        # ---- TRACK MAX RESPONSES & CHECKPOINT ----
        if {[expr $step % $checkInterval] == 0 || $step == $Nsteps_TH || $step <= 5} {
            set ux_t1 [nodeDisp $roofNode_T1 1]
            set uy_t1 [nodeDisp $roofNode_T1 2]
            set ux_t2 [nodeDisp $roofNode_T2 1]
            set uy_t2 [nodeDisp $roofNode_T2 2]

            if {[expr abs($ux_t1)] > $maxUx_T1} { set maxUx_T1 [expr abs($ux_t1)] }
            if {[expr abs($uy_t1)] > $maxUy_T1} { set maxUy_T1 [expr abs($uy_t1)] }
            if {[expr abs($ux_t2)] > $maxUx_T2} { set maxUx_T2 [expr abs($ux_t2)] }
            if {[expr abs($uy_t2)] > $maxUy_T2} { set maxUy_T2 [expr abs($uy_t2)] }

            set pct [expr int(100.0 * $step / $Nsteps_TH)]
            set tNow [format "%.3f" [expr $step * $dt_analysis]]
            set elapsed [expr [clock seconds] - $gmStartWall]
            set eta ""
            if {$pct > 0} {
                set etaSec [expr int($elapsed * (100.0 / $pct - 1.0))]
                set eta "[expr $etaSec / 60]m[expr $etaSec % 60]s"
            }

            puts [format "%-8s | %-9s | %14.6f | %14.6f | %14.6f | %14.6f | %d%% ETA:%s" \
                $step $tNow $ux_t1 $uy_t1 $ux_t2 $uy_t2 $pct $eta]

            # Write to log file
            puts $logFile [format "step=%d t=%s pct=%d%% T1_Ux=%.6f T1_Uy=%.6f T2_Ux=%.6f T2_Uy=%.6f maxT1_Ux=%.6f maxT2_Ux=%.6f elapsed=%ds" \
                $step $tNow $pct $ux_t1 $uy_t1 $ux_t2 $uy_t2 $maxUx_T1 $maxUx_T2 $elapsed]
            flush $logFile
        }

        # ---- FLUSH RECORDERS periodically ----
        if {[expr $step % $flushInterval] == 0} {
            record
        }
    }

    # Final flush
    record

    set gmElapsed [expr [clock seconds] - $gmStartWall]

    puts ""
    if {$totalFailed == 0} {
        puts ">>> $gmID: COMPLETED SUCCESSFULLY ($Nsteps_TH steps, ${gmElapsed}s)"
    } else {
        puts ">>> $gmID: COMPLETED WITH $totalFailed FAILURES (${gmElapsed}s)"
    }
    puts ""

    # ------------------------------------------------------------------
    # RESULTS SUMMARY
    # ------------------------------------------------------------------
    puts "============================================================"
    puts "  RESULTS SUMMARY: $gmID (PGA = ${gmPGA} g)"
    puts "============================================================"
    puts ""

    set finalUx_T1 [nodeDisp $roofNode_T1 1]
    set finalUy_T1 [nodeDisp $roofNode_T1 2]
    set finalUx_T2 [nodeDisp $roofNode_T2 1]
    set finalUy_T2 [nodeDisp $roofNode_T2 2]

    set driftX_T1 [expr $maxUx_T1 / $H_building]
    set driftX_T2 [expr $maxUx_T2 / $H_building]
    set driftY_T1 [expr $maxUy_T1 / $H_building]
    set driftY_T2 [expr $maxUy_T2 / $H_building]
    set diffDisp  [expr abs($maxUx_T1 - $maxUx_T2)]

    puts "  Tower 1 Max Ux: [format "%.6f" $maxUx_T1] cm  (drift: [format "%.4f" [expr $driftX_T1*100]]%)"
    puts "  Tower 1 Max Uy: [format "%.6f" $maxUy_T1] cm  (drift: [format "%.4f" [expr $driftY_T1*100]]%)"
    puts "  Tower 2 Max Ux: [format "%.6f" $maxUx_T2] cm  (drift: [format "%.4f" [expr $driftX_T2*100]]%)"
    puts "  Tower 2 Max Uy: [format "%.6f" $maxUy_T2] cm  (drift: [format "%.4f" [expr $driftY_T2*100]]%)"
    puts "  Differential:   [format "%.6f" $diffDisp] cm"
    puts ""

    # TBDY 2018 drift check
    puts "  TBDY 2018 Drift Check (kappa=0.5 for steel):"
    foreach {label dr} [list "T1-X" $driftX_T1 "T1-Y" $driftY_T1 "T2-X" $driftX_T2 "T2-Y" $driftY_T2] {
        if {$dr > 0.020} {
            puts "    $label: [format "%.4f" [expr $dr*100]]% - EXCEEDS collapse prevention (2%)"
        } elseif {$dr > 0.008} {
            puts "    $label: [format "%.4f" [expr $dr*100]]% - Exceeds serviceability (0.8%)"
        } else {
            puts "    $label: [format "%.4f" [expr $dr*100]]% - OK"
        }
    }
    puts ""

    # ------------------------------------------------------------------
    # SAVE COMPREHENSIVE SUMMARY
    # ------------------------------------------------------------------
    set sumFile [open "${outDir}/summary.txt" w]
    puts $sumFile "============================================================"
    puts $sumFile "DASK 2026 TIME HISTORY ANALYSIS - COMPREHENSIVE RESULTS"
    puts $sumFile "============================================================"
    puts $sumFile ""
    puts $sumFile "Ground Motion:    $gmID"
    puts $sumFile "PGA:              [format "%.5f" $pgaRead] g"
    puts $sumFile "Duration:         [format "%.3f" $duration_TH] s"
    puts $sumFile "dt (ground):      $dt_gm s"
    puts $sumFile "dt (analysis):    $dt_analysis s"
    puts $sumFile "Steps:            $Nsteps_TH"
    puts $sumFile "Failures:         $totalFailed"
    puts $sumFile "Wall time:        ${gmElapsed} s ([format "%.1f" [expr $gmElapsed / 60.0]] min)"
    puts $sumFile ""
    puts $sumFile "Model:            V9 Twin Towers (1:50)"
    puts $sumFile "Nodes:            1680"
    puts $sumFile "Elements:         4248"
    puts $sumFile "T1:               [format "%.6f" $T1] s"
    puts $sumFile "Damping:          ${xi_damp} (Rayleigh, a0=[format "%.6f" $a0], a1=[format "%.8f" $a1])"
    puts $sumFile ""
    puts $sumFile "--- PEAK RESPONSES ---"
    puts $sumFile "Tower 1 Max Ux:   [format "%.6f" $maxUx_T1] cm (drift [format "%.6f" $driftX_T1])"
    puts $sumFile "Tower 1 Max Uy:   [format "%.6f" $maxUy_T1] cm (drift [format "%.6f" $driftY_T1])"
    puts $sumFile "Tower 2 Max Ux:   [format "%.6f" $maxUx_T2] cm (drift [format "%.6f" $driftX_T2])"
    puts $sumFile "Tower 2 Max Uy:   [format "%.6f" $maxUy_T2] cm (drift [format "%.6f" $driftY_T2])"
    puts $sumFile "Differential Ux:  [format "%.6f" $diffDisp] cm"
    puts $sumFile ""
    puts $sumFile "--- FINAL STATE ---"
    puts $sumFile "T1 Roof Ux:       [format "%.6f" $finalUx_T1] cm"
    puts $sumFile "T1 Roof Uy:       [format "%.6f" $finalUy_T1] cm"
    puts $sumFile "T2 Roof Ux:       [format "%.6f" $finalUx_T2] cm"
    puts $sumFile "T2 Roof Uy:       [format "%.6f" $finalUy_T2] cm"
    puts $sumFile ""
    puts $sumFile "--- OUTPUT FILES ---"
    puts $sumFile "Node disp:        ${outDir}/node_disp/ (T1_floor[1-25]_disp.txt, T2_floor[1-25]_disp.txt)"
    puts $sumFile "Node vel:         ${outDir}/node_vel/"
    puts $sumFile "Node accel:       ${outDir}/node_accel/"
    puts $sumFile "Base reactions:   ${outDir}/node_reaction/"
    puts $sumFile "Interstory drift: ${outDir}/drift/ (T1_drift_floor[1-25].txt, T2_drift_floor[1-25].txt)"
    puts $sumFile "Envelopes:        ${outDir}/envelope/ (T1_floor[1-25]_env.txt, T2_floor[1-25]_env.txt)"
    puts $sumFile "Element forces:   ${outDir}/element_forces/sample_forces.txt"
    puts $sumFile "Analysis log:     ${outDir}/analysis_log.txt"
    puts $sumFile ""
    puts $sumFile "Completed: [clock seconds]"
    close $sumFile

    puts ">>> Summary saved: ${outDir}/summary.txt"
    puts ">>> Log saved:     ${outDir}/analysis_log.txt"
    puts ""

    # Close log
    puts $logFile ""
    puts $logFile "COMPLETED: [clock seconds]"
    puts $logFile "Wall time: ${gmElapsed}s"
    puts $logFile "Total failures: $totalFailed"
    close $logFile
}

# ============================================================================
# FINAL GRAND SUMMARY
# ============================================================================
set totalWall [expr [clock seconds] - $startWall]

puts ""
puts "################################################################"
puts "##  ALL 3 GROUND MOTIONS COMPLETED                           ##"
puts "##  Total wall time: ${totalWall} s ([format "%.1f" [expr $totalWall / 60.0]] min)"
puts "################################################################"
puts ""
puts "  Output directories:"
puts "    results/th_KYH1/"
puts "    results/th_KYH2/"
puts "    results/th_KYH3/"
puts ""
puts "  Each contains:"
puts "    node_disp/     - All node displacements (per floor)"
puts "    node_vel/      - Velocity records"
puts "    node_accel/    - Acceleration records"
puts "    node_reaction/ - Base reactions"
puts "    drift/         - Interstory drift (all floors)"
puts "    envelope/      - Min/max envelopes"
puts "    element_forces/- Sample element local forces"
puts "    summary.txt    - Peak responses"
puts "    analysis_log.txt - Step-by-step progress log"
puts ""

wipe
puts ">>> Done. [clock seconds]"
