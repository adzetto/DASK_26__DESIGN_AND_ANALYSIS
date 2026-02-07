# ============================================================================
# ADVANCED DAMPING PARAMETRIC STUDY - DASK 2026
# Tests multiple damping ratios with KYH1, saves results for pgfplots
# ============================================================================
# Usage: OpenSees damping_parametric_study.tcl
# Output files (in results/damping_study/):
#   - peak_response.csv        : xi, a0, a1, maxUx_T1, maxUx_T2, maxUy_T1, maxUy_T2
#   - rayleigh_curve.csv       : T, xi_002, xi_005, xi_010 (damping ratio vs period)
#   - time_history_xiXX.csv    : t, Ux_T1, Ux_T2, Uy_T1 (displacement time histories)
# ============================================================================

puts "================================================================"
puts "  ADVANCED DAMPING PARAMETRIC STUDY"
puts "  DASK 2026 - V9 Twin Towers"
puts "================================================================"
set t_start [clock seconds]

# --- Build model ---
puts ">>> Building V9 model..."
if {[catch {source tbdy2018_torsion_analysis_trimmed.tcl} errMsg]} {
    puts ">>> Model built"
}

puts ">>> T1 = $T1 s"
set omega1 [expr 2.0 * 3.14159265358979 / $T1]
puts ">>> omega1 = [format "%.4f" $omega1] rad/s"

# --- Read ground motion ---
set gmFile "C:/Users/lenovo/Desktop/DASK_NEW/ground_motion_dask/KYH1.txt"
set data {}
set fp [open $gmFile r]
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
puts ">>> Ground motion: KYH1, [llength $data] points, PGA = 0.335g"

# Write cm/s2 file
file mkdir ground_motion
set osfp [open ground_motion/KYH1_dps.txt w]
foreach val $data {
    puts $osfp [format "%.8f" [expr $val * 981.0]]
}
close $osfp

# --- Output directory ---
file mkdir results/damping_study

# --- Parameters ---
set dt_gm 0.001
set dt_analysis 0.005
set roofNode_T1 809
set roofNode_T2 1641
set omega2 [expr $omega1 * 3.5]
set nSteps 6446
set totalTime [expr $nSteps * $dt_analysis]

# Damping ratios to test
set xiList {0.005 0.010 0.020 0.030 0.050 0.070 0.100 0.150 0.200}

# Time history recording interval (every N steps -> save to file)
set thInterval 4   ;# save every 4 steps = every 0.02s

puts ">>> omega2 = [format "%.4f" $omega2] rad/s (= 3.5 * omega1)"
puts ">>> Analysis: $nSteps steps x ${dt_analysis}s = ${totalTime}s"
puts ">>> Damping ratios: $xiList"
puts ""

# ============================================================================
# PART 1: RAYLEIGH DAMPING CURVE (analytical, no analysis needed)
# ============================================================================
puts ">>> Writing Rayleigh damping curves..."

set rfp [open results/damping_study/rayleigh_curve.csv w]
puts $rfp "T,f,xi_0.005,xi_0.010,xi_0.020,xi_0.030,xi_0.050,xi_0.070,xi_0.100,xi_0.150,xi_0.200"

# Period range: 0.02s to 1.0s (50 points, log-spaced manually)
set Tvals {0.020 0.025 0.030 0.035 0.040 0.050 0.060 0.070 0.080 0.090
           0.100 0.110 0.120 0.130 0.135 0.140 0.147 0.150 0.160 0.170
           0.180 0.190 0.200 0.220 0.240 0.260 0.280 0.300 0.350 0.400
           0.450 0.500 0.600 0.700 0.800 0.900 1.000}

foreach T $Tvals {
    set w [expr 2.0 * 3.14159265358979 / $T]
    set f [expr 1.0 / $T]
    set line "[format "%.4f" $T],[format "%.4f" $f]"
    foreach xi $xiList {
        set a0_t [expr 2.0 * $xi * $omega1 * $omega2 / ($omega1 + $omega2)]
        set a1_t [expr 2.0 * $xi / ($omega1 + $omega2)]
        set xi_eff [expr $a0_t / (2.0 * $w) + $a1_t * $w / 2.0]
        append line ",[format "%.6f" $xi_eff]"
    }
    puts $rfp $line
}
close $rfp
puts ">>> Rayleigh curves saved to results/damping_study/rayleigh_curve.csv"

# ============================================================================
# PART 2: SPECTRAL DAMPING CORRECTION CURVE (eta_b vs xi)
# ============================================================================
puts ">>> Writing spectral damping correction curve..."

set sfp [open results/damping_study/eta_b_curve.csv w]
puts $sfp "xi_pct,xi,eta_b"
foreach xp {0.5 1.0 1.5 2.0 2.5 3.0 3.5 4.0 4.5 5.0 6.0 7.0 8.0 9.0 10.0 12.0 15.0 20.0} {
    set xi_dec [expr $xp / 100.0]
    set eta [expr sqrt(10.0 / (5.0 + $xp))]
    puts $sfp "[format "%.1f" $xp],[format "%.4f" $xi_dec],[format "%.4f" $eta]"
}
close $sfp
puts ">>> eta_b curve saved to results/damping_study/eta_b_curve.csv"

# ============================================================================
# PART 3: TIME HISTORY ANALYSIS FOR EACH DAMPING RATIO
# ============================================================================
puts ""
puts "================================================================"
puts "  TIME HISTORY ANALYSES"
puts "================================================================"
puts ""
puts [format "  %-8s %-12s %-14s %-14s %-14s %-14s %-14s %s" \
    "xi" "a0" "a1" "maxUx_T1(cm)" "maxUx_T2(cm)" "maxUy_T1(cm)" "maxUy_T2(cm)" "fail"]
puts "  ---------------------------------------------------------------------------------------------------------"

# Open peak response CSV
set pfp [open results/damping_study/peak_response.csv w]
puts $pfp "xi,a0,a1,maxUx_T1_cm,maxUx_T2_cm,maxUy_T1_cm,maxUy_T2_cm,failed_steps"

set runIdx 0
foreach xi $xiList {
    incr runIdx
    set tRun [clock seconds]

    # Reset model state
    catch {wipeAnalysis}
    catch {remove recorders}
    catch {reset}
    catch {loadConst -time 0.0}

    # Remove old patterns/timeSeries
    for {set tag 50} {$tag <= 400} {incr tag} {
        catch {remove loadPattern $tag}
        catch {remove timeSeries $tag}
    }
    for {set tag 1} {$tag <= 20} {incr tag} {
        catch {remove loadPattern $tag}
        catch {remove timeSeries $tag}
    }

    # Rayleigh damping
    set a0 [expr 2.0 * $xi * $omega1 * $omega2 / ($omega1 + $omega2)]
    set a1 [expr 2.0 * $xi / ($omega1 + $omega2)]
    rayleigh $a0 $a1 0.0 0.0

    # Ground motion
    set tsTag 150
    set patTag 250
    timeSeries Path $tsTag -dt $dt_gm -filePath ground_motion/KYH1_dps.txt -factor 1.0
    pattern UniformExcitation $patTag 1 -accel $tsTag

    # Analysis setup
    constraints Transformation
    numberer RCM
    system BandGeneral
    test NormDispIncr 1.0e-6 50
    algorithm Newton
    integrator Newmark 0.5 0.25
    analysis Transient

    # Open time history file for selected xi values
    set xiStr [format "%03d" [expr int($xi * 1000)]]
    set thfp [open "results/damping_study/time_history_xi${xiStr}.csv" w]
    puts $thfp "t_s,Ux_T1_cm,Ux_T2_cm,Uy_T1_cm,Uy_T2_cm"

    # Run analysis
    set maxUx_T1 0.0
    set maxUx_T2 0.0
    set maxUy_T1 0.0
    set maxUy_T2 0.0
    set failed 0

    for {set step 1} {$step <= $nSteps} {incr step} {
        set ok [analyze 1 $dt_analysis]
        if {$ok != 0} {
            # Recovery strategy 1: ModifiedNewton
            algorithm ModifiedNewton
            test NormDispIncr 1.0e-5 100
            set ok [analyze 1 $dt_analysis]
            if {$ok != 0} {
                # Recovery strategy 2: smaller timestep
                test NormDispIncr 1.0e-4 200
                set ok [analyze 5 [expr $dt_analysis / 5.0]]
                if {$ok != 0} {
                    # Recovery strategy 3: Broyden
                    algorithm Broyden 20
                    set ok [analyze 5 [expr $dt_analysis / 5.0]]
                    algorithm ModifiedNewton
                }
            }
            # Restore defaults
            algorithm Newton
            test NormDispIncr 1.0e-6 50
            if {$ok != 0} { incr failed }
        }

        # Track max displacements every step
        set ux1 [expr abs([nodeDisp $roofNode_T1 1])]
        set ux2 [expr abs([nodeDisp $roofNode_T2 1])]
        set uy1 [expr abs([nodeDisp $roofNode_T1 2])]
        set uy2 [expr abs([nodeDisp $roofNode_T2 2])]
        if {$ux1 > $maxUx_T1} { set maxUx_T1 $ux1 }
        if {$ux2 > $maxUx_T2} { set maxUx_T2 $ux2 }
        if {$uy1 > $maxUy_T1} { set maxUy_T1 $uy1 }
        if {$uy2 > $maxUy_T2} { set maxUy_T2 $uy2 }

        # Save time history at interval
        if {[expr $step % $thInterval] == 0} {
            set t [format "%.4f" [expr $step * $dt_analysis]]
            set u1x [nodeDisp $roofNode_T1 1]
            set u2x [nodeDisp $roofNode_T2 1]
            set u1y [nodeDisp $roofNode_T1 2]
            set u2y [nodeDisp $roofNode_T2 2]
            puts $thfp "$t,[format "%.8f" $u1x],[format "%.8f" $u2x],[format "%.8f" $u1y],[format "%.8f" $u2y]"
        }

        # Progress
        if {[expr $step % 1000] == 0} {
            puts "    xi=$xi: step $step/$nSteps ([format "%.1f" [expr 100.0*$step/$nSteps]]%), maxUx_T1=[format "%.4f" $maxUx_T1] cm"
        }
    }

    close $thfp

    # Write peak response
    puts $pfp [format "%.4f,%.6f,%.10f,%.8f,%.8f,%.8f,%.8f,%d" \
        $xi $a0 $a1 $maxUx_T1 $maxUx_T2 $maxUy_T1 $maxUy_T2 $failed]

    set elapsed [expr [clock seconds] - $tRun]
    puts [format "  %-8.4f %-12.6f %-14.10f %-14.8f %-14.8f %-14.8f %-14.8f %d  (%ds)" \
        $xi $a0 $a1 $maxUx_T1 $maxUx_T2 $maxUy_T1 $maxUy_T2 $failed $elapsed]
}

close $pfp
puts ""
puts ">>> Peak response saved to results/damping_study/peak_response.csv"

# ============================================================================
# PART 4: SUMMARY
# ============================================================================
set t_total [expr [clock seconds] - $t_start]
puts ""
puts "================================================================"
puts "  SUMMARY"
puts "================================================================"
puts "  Total elapsed time: ${t_total}s ([format "%.1f" [expr $t_total/60.0]] min)"
puts "  Ground motion: KYH1 (PGA = 0.335g)"
puts "  Model: V9 Twin Towers, T1 = $T1 s"
puts "  Rayleigh: omega1 = [format "%.4f" $omega1], omega2 = [format "%.4f" $omega2] rad/s"
puts "  Analysis: $nSteps steps x ${dt_analysis}s = [format "%.1f" $totalTime]s"
puts ""
puts "  Output files:"
puts "    results/damping_study/peak_response.csv"
puts "    results/damping_study/rayleigh_curve.csv"
puts "    results/damping_study/eta_b_curve.csv"
puts "    results/damping_study/time_history_xiXXX.csv (per xi)"
puts ""
puts ">>> DONE"
