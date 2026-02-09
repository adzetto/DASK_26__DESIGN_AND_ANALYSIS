"""
SAP2000 OAPI - Complete Analysis & Pushover (v3)
=================================================
Model: sap_gursoy.sdb (DASK 2026 Twin Towers with Bracing)
Units: N, cm, s (code=15)

Fixes from v2:
  - GM loading: ValueType=2 (time+value pairs) instead of 1
  - Pushover: SetLoadApplication(8 args) for displacement control
  - SetResultsSaved(name, 2, 50) for multi-step pushover output
  - Unicode-safe console output (no Greek chars)
  - Better error handling and verification
"""

import sys
import os
import time
import json
import numpy as np
import pandas as pd
import comtypes.client

# ===========================================================================
# CONFIGURATION
# ===========================================================================
BASE_DIR = r"c:\Users\lenovo\Desktop\DASK_NEW"
SAP_DIR = os.path.join(BASE_DIR, "sap_bracing")
SAP_FILE = os.path.join(SAP_DIR, u"sap_g\u00FCrsoy.sdb")
RESULTS_DIR = os.path.join(BASE_DIR, "results", "sap_bracing")
os.makedirs(RESULTS_DIR, exist_ok=True)

# Clean GM files (space-separated: time value, no header)
KYH_SAP = {
    "KYH1": os.path.join(SAP_DIR, "KYH1_sap.txt"),
    "KYH2": os.path.join(SAP_DIR, "KYH2_sap.txt"),
    "KYH3": os.path.join(SAP_DIR, "KYH3_sap.txt"),
}
KYH_PGA = {"KYH1": 0.335, "KYH2": 1.243, "KYH3": 1.896}

GRAVITY = 981.0  # cm/s^2

# Section: 0.6 x 0.6 cm BALSA
SECT_A = 0.36       # cm^2
SECT_I = 0.0108     # cm^4
SECT_c = 0.3        # cm

# TH case definitions
TH_CASES = {
    "KYH1_X": ("U1", "KYH1"), "KYH1_Y": ("U2", "KYH1"),
    "KYH2_X": ("U1", "KYH2"), "KYH2_Y": ("U2", "KYH2"),
    "KYH3_X": ("U1", "KYH3"), "KYH3_Y": ("U2", "KYH3"),
}


# ===========================================================================
# CONNECT & OPEN
# ===========================================================================
def connect():
    print("=" * 70)
    print("SAP2000 OAPI - FULL ANALYSIS & PUSHOVER (v3)")
    print("=" * 70)
    try:
        obj = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
        print("Connected to running SAP2000")
    except Exception:
        print("Starting SAP2000...")
        obj = comtypes.client.CreateObject("CSI.SAP2000.API.SapObject")
        obj.ApplicationStart()
        time.sleep(5)
    return obj, obj.SapModel


def get_all_joint_names(sap):
    ret = sap.PointObj.GetNameList()
    return list(ret[1]) if ret[0] > 0 else []


def get_all_frame_names(sap):
    ret = sap.FrameObj.GetNameList()
    return list(ret[1]) if ret[0] > 0 else []


def get_joint_coordinates(sap, joint_names):
    joints = {}
    for name in joint_names:
        ret = sap.PointObj.GetCoordCartesian(name)
        joints[name] = {"x": float(ret[0]), "y": float(ret[1]), "z": float(ret[2])}
    return joints


# ===========================================================================
# GROUND MOTION LOADING (Fixed: ValueType=2)
# ===========================================================================
def load_ground_motions(sap):
    """Load GM data from clean files using SetFromFile with ValueType=2."""
    print("\n--- LOADING GROUND MOTIONS ---")

    for gm_name, gm_path in KYH_SAP.items():
        if not os.path.exists(gm_path):
            print(f"  {gm_name}: NOT FOUND at {gm_path}")
            continue

        abs_path = os.path.abspath(gm_path)
        expected_pga = KYH_PGA[gm_name]

        # Delete existing function
        try:
            sap.Func.Delete(gm_name)
        except Exception:
            pass

        # SetFromFile: HeaderLines=0, PrefixChars=0, PtsPerLine=1,
        #              ValueType=2 (time+value pairs), FreeFormat=True
        ret = sap.Func.FuncTH.SetFromFile(gm_name, abs_path, 0, 0, 1, 2, True)

        # Verify
        v = sap.Func.GetValues(gm_name, 0, [0.0], [0.0])
        n_pts = v[0]
        if n_pts > 0:
            vals = v[2]
            actual_pga = max(abs(x) for x in vals)
            ok = abs(actual_pga - expected_pga) / expected_pga < 0.05
            status = "(OK)" if ok else "(PGA MISMATCH!)"
            print(f"  {gm_name}: {n_pts} pts, PGA={actual_pga:.4f}g {status}")
        else:
            print(f"  {gm_name}: WARNING - 0 pts loaded! (ret={ret})")


def update_th_cases(sap):
    """Update TH load cases: set functions and TransAccSF=981."""
    print("\n--- UPDATING TH LOAD CASES (SF=981) ---")

    for case_name, (direction, func_name) in TH_CASES.items():
        try:
            ret = sap.LoadCases.ModHistLinear.SetLoads(
                case_name, 1,
                ["Accel"], [direction], [func_name],
                [GRAVITY], [1.0], [0.0], ["GLOBAL"], [0.0]
            )
            print(f"  {case_name}: dir={direction}, func={func_name}, SF={GRAVITY}")
        except Exception as e:
            print(f"  {case_name}: SetLoads error - {e}")


# ===========================================================================
# ANALYSIS PHASES
# ===========================================================================
def run_modal(sap):
    print("\n--- PHASE 1: MODAL ANALYSIS ---")
    sap.Analyze.SetRunCaseFlag("", False, True)  # Disable all
    sap.Analyze.SetRunCaseFlag("MODAL", True, False)

    t0 = time.time()
    sap.Analyze.RunAnalysis()
    print(f"  Completed in {time.time() - t0:.1f}s")

    # Extract periods
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput("MODAL", True)

    modal_data = []
    try:
        ret = sap.Results.ModalPeriod(
            0, [""], [""], [0.0], [0.0], [0.0], [0.0], [0.0]
        )
        n_modes = ret[0]
        periods = ret[4]
        freqs = ret[5]

        print(f"\n  {'Mode':<6} {'Period (s)':<14} {'Freq (Hz)':<14}")
        print(f"  {'-' * 34}")
        for i in range(min(12, n_modes)):
            print(f"  {i+1:<6} {periods[i]:<14.6f} {freqs[i]:<14.4f}")
            modal_data.append({
                "mode": i + 1,
                "period_s": float(periods[i]),
                "freq_hz": float(freqs[i]),
            })
        print(f"\n  T1 = {periods[0]:.6f} s")
    except Exception as e:
        print(f"  Modal extraction error: {e}")

    return modal_data


def run_static(sap):
    print("\n--- PHASE 2: STATIC ANALYSIS ---")
    sap.Analyze.SetRunCaseFlag("", False, True)
    for c in ["DEAD", "EQ_X", "EQ_Y", "TIJLER"]:
        try:
            sap.Analyze.SetRunCaseFlag(c, True, False)
        except Exception:
            pass
    t0 = time.time()
    sap.Analyze.RunAnalysis()
    print(f"  Completed in {time.time() - t0:.1f}s")


def run_time_history(sap):
    print("\n--- PHASE 3: TIME HISTORY ANALYSES ---")
    sap.Analyze.SetRunCaseFlag("", False, True)
    sap.Analyze.SetRunCaseFlag("MODAL", True, False)
    for c in TH_CASES:
        try:
            sap.Analyze.SetRunCaseFlag(c, True, False)
        except Exception:
            print(f"  Warning: case {c} not found")

    t0 = time.time()
    print("  Running 6 TH cases...")
    sap.Analyze.RunAnalysis()
    print(f"  Completed in {time.time() - t0:.1f}s")


def setup_pushover(sap, case_name, direction, monitored_joint, target=5.0):
    """Setup displacement-controlled nonlinear static pushover."""
    try:
        sap.LoadCases.Delete(case_name)
    except Exception:
        pass

    # Create case
    ret = sap.LoadCases.StaticNonlinear.SetCase(case_name)
    print(f"    SetCase({case_name}): ret={ret}")

    # Initial condition: start from DEAD
    try:
        sap.LoadCases.StaticNonlinear.SetInitialCase(case_name, "DEAD")
        print(f"    InitialCase: DEAD")
    except Exception as e:
        print(f"    InitialCase error: {e}")

    # Load: acceleration in push direction
    try:
        sap.LoadCases.StaticNonlinear.SetLoads(
            case_name, 1, ["Accel"], [direction], [1.0]
        )
        print(f"    Load: Accel {direction}")
    except Exception as e:
        print(f"    SetLoads error: {e}")
        # Fallback to load pattern
        pat = "EQ_X" if direction == "U1" else "EQ_Y"
        try:
            sap.LoadCases.StaticNonlinear.SetLoads(
                case_name, 1, ["Load"], [pat], [1.0]
            )
            print(f"    Load (fallback): pattern {pat}")
        except Exception as e2:
            print(f"    Load fallback failed: {e2}")

    # P-Delta + Large Displacement
    try:
        sap.LoadCases.StaticNonlinear.SetGeometricNonlinearity(case_name, 2)
    except Exception:
        pass

    # Displacement control (8 args: Name, LoadControl, DispType, Displ, Monitor, DOF, PointName, GenDispl)
    dof = 1 if direction == "U1" else 2
    try:
        ret = sap.LoadCases.StaticNonlinear.SetLoadApplication(
            case_name, 2, 2, target, True, dof, monitored_joint, ""
        )
        print(f"    DispControl: target={target}cm, DOF={dof}, joint={monitored_joint} (ret={ret})")
    except Exception as e:
        print(f"    SetLoadApplication error: {e}")
        print(f"    (Pushover will use force control)")

    # Save multiple steps
    try:
        ret = sap.LoadCases.StaticNonlinear.SetResultsSaved(case_name, 2, 50)
        print(f"    ResultsSaved: 50 steps (ret={ret})")
    except Exception as e:
        print(f"    SetResultsSaved error: {e}")


def run_pushover(sap, monitored_joint):
    print("\n--- PHASE 4: PUSHOVER ANALYSIS ---")
    print(f"  Monitored joint: {monitored_joint}")

    setup_pushover(sap, "PUSHOVER_X", "U1", monitored_joint, target=5.0)
    setup_pushover(sap, "PUSHOVER_Y", "U2", monitored_joint, target=5.0)

    sap.Analyze.SetRunCaseFlag("", False, True)
    sap.Analyze.SetRunCaseFlag("DEAD", True, False)
    sap.Analyze.SetRunCaseFlag("PUSHOVER_X", True, False)
    sap.Analyze.SetRunCaseFlag("PUSHOVER_Y", True, False)

    t0 = time.time()
    print("  Running pushover...")
    sap.Analyze.RunAnalysis()
    print(f"  Completed in {time.time() - t0:.1f}s")


# ===========================================================================
# RESULT EXTRACTION
# ===========================================================================
def extract_joint_envelopes(sap, case_name, joint_names):
    """Extract envelope displacements for all joints."""
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case_name, True)
    try:
        sap.Results.Setup.SetOptionModalHist(1)  # 1=Envelopes
    except Exception:
        pass

    results = {}
    errors = 0
    for name in joint_names:
        try:
            ret = sap.Results.JointDispl(name, 0)
            if ret[0] > 0:
                n = ret[0]
                max_ux = max(abs(float(ret[6][i])) for i in range(n))
                max_uy = max(abs(float(ret[7][i])) for i in range(n))
                max_uz = max(abs(float(ret[8][i])) for i in range(n))
                results[name] = {
                    "max_ux": max_ux, "max_uy": max_uy, "max_uz": max_uz
                }
        except Exception:
            errors += 1

    if errors > 0:
        print(f"    ({errors} joints with errors)")
    return results


def extract_frame_envelopes(sap, case_name, frame_names):
    """Extract envelope forces for all frame elements."""
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case_name, True)
    try:
        sap.Results.Setup.SetOptionModalHist(1)
    except Exception:
        pass

    results = {}
    errors = 0
    for name in frame_names:
        try:
            ret = sap.Results.FrameForce(name, 0)
            if ret[0] > 0:
                n = ret[0]
                # Correct indices: [8]=P, [9]=V2, [10]=V3, [11]=T, [12]=M2, [13]=M3
                results[name] = {
                    "max_P": max(abs(float(ret[8][i])) for i in range(n)),
                    "min_P": min(float(ret[8][i]) for i in range(n)),
                    "max_V2": max(abs(float(ret[9][i])) for i in range(n)),
                    "max_V3": max(abs(float(ret[10][i])) for i in range(n)),
                    "max_T": max(abs(float(ret[11][i])) for i in range(n)),
                    "max_M2": max(abs(float(ret[12][i])) for i in range(n)),
                    "max_M3": max(abs(float(ret[13][i])) for i in range(n)),
                }
        except Exception:
            errors += 1

    if errors > 0:
        print(f"    ({errors} frames with errors)")
    return results


def extract_base_reactions(sap, case_name):
    """Extract base reactions."""
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case_name, True)
    try:
        sap.Results.Setup.SetOptionModalHist(1)
    except Exception:
        pass

    try:
        ret = sap.Results.BaseReact()
        if ret[0] > 0:
            n = ret[0]
            return {
                "max_Fx": max(abs(float(ret[4][i])) for i in range(n)),
                "max_Fy": max(abs(float(ret[5][i])) for i in range(n)),
                "Fz": float(ret[6][0]),
            }
    except Exception as e:
        print(f"    BaseReact error: {e}")
    return {}


def extract_pushover_curve(sap, case_name, monitored_joint, direction):
    """Extract base shear vs roof displacement (step-by-step)."""
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case_name, True)
    try:
        sap.Results.Setup.SetOptionNLStatic(1)  # 1=Step-by-step
    except Exception:
        pass

    curve = []
    try:
        ret = sap.Results.JointDispl(monitored_joint, 0)
        if ret[0] > 0:
            n_steps = ret[0]
            steps = ret[5]
            u1 = ret[6]
            u2 = ret[7]

            br = sap.Results.BaseReact()
            if br[0] == n_steps:
                fx = br[4]
                fy = br[5]
                for i in range(n_steps):
                    d = float(u1[i]) if direction == "U1" else float(u2[i])
                    v = float(fx[i]) if direction == "U1" else float(fy[i])
                    curve.append({
                        "step": float(steps[i]),
                        "displacement_cm": d,
                        "base_shear_N": v,
                    })
            else:
                print(f"    BaseReact step count mismatch: {br[0]} vs {n_steps}")
    except Exception as e:
        print(f"    Pushover curve error: {e}")

    return curve


def extract_pushover_all_nodes(sap, case_name, joint_names):
    """Extract last-step pushover displacements for all nodes."""
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case_name, True)
    try:
        sap.Results.Setup.SetOptionNLStatic(2)  # 2=Last step
    except Exception:
        pass

    results = {}
    for name in joint_names:
        try:
            ret = sap.Results.JointDispl(name, 0)
            if ret[0] > 0:
                i = ret[0] - 1  # Last step
                results[name] = {
                    "ux": float(ret[6][i]),
                    "uy": float(ret[7][i]),
                    "uz": float(ret[8][i]),
                }
        except Exception:
            pass
    return results


def compute_stresses(frame_forces):
    """Compute stresses from frame forces. Returns N/cm^2 and MPa."""
    stresses = {}
    for elem, f in frame_forces.items():
        sigma_axial = f["max_P"] / SECT_A
        sigma_bend = (f["max_M2"] + f["max_M3"]) * SECT_c / SECT_I
        sigma_total = sigma_axial + sigma_bend
        tau = 1.5 * (f["max_V2"]**2 + f["max_V3"]**2)**0.5 / SECT_A

        stresses[elem] = {
            "sigma_total_Ncm2": sigma_total,
            "tau_total_Ncm2": tau,
            "sigma_total_MPa": sigma_total / 100,  # N/cm^2 -> MPa
            "tau_total_MPa": tau / 100,
        }
    return stresses


# ===========================================================================
# MAIN
# ===========================================================================
def main():
    sap_obj, sap = connect()

    # Open model
    print(f"\nOpening model...")
    sap.File.OpenFile(SAP_FILE)
    time.sleep(2)
    units = sap.GetPresentUnits()
    print(f"  Units code: {units} (15=N_cm_C)")

    # Load ground motions (ValueType=2 fix)
    load_ground_motions(sap)

    # Update TH load cases (SF=981)
    update_th_cases(sap)

    # Save after updates
    sap.File.Save(SAP_FILE)
    print("  Model saved.")

    # Model info
    joint_names = get_all_joint_names(sap)
    frame_names = get_all_frame_names(sap)
    print(f"\n  Model: {len(joint_names)} joints, {len(frame_names)} frames")

    joints = get_joint_coordinates(sap, joint_names)
    max_z = max(j["z"] for j in joints.values())
    z_levels = sorted(set(round(j["z"], 1) for j in joints.values()))
    print(f"  Height: {max_z} cm, {len(z_levels)} levels")

    # Top-center joint for pushover monitoring
    top_joints = {n: j for n, j in joints.items() if abs(j["z"] - max_z) < 0.5}
    cx = np.mean([j["x"] for j in top_joints.values()])
    cy = np.mean([j["y"] for j in top_joints.values()])
    monitored = min(top_joints.keys(),
                    key=lambda n: (top_joints[n]["x"]-cx)**2 + (top_joints[n]["y"]-cy)**2)
    mj = joints[monitored]
    print(f"  Monitored: {monitored} at ({mj['x']:.1f}, {mj['y']:.1f}, {mj['z']:.1f})")

    # === RUN ALL ANALYSES (no pushover - convergence issues) ===
    modal_data = run_modal(sap)
    run_static(sap)
    run_time_history(sap)

    # === QUICK TH VERIFICATION ===
    print("\n--- TH VERIFICATION ---")
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput("KYH2_X", True)
    sap.Results.Setup.SetOptionModalHist(1)
    try:
        ret = sap.Results.JointDispl(monitored, 0)
        if ret[0] > 0:
            for i in range(ret[0]):
                print(f"  KYH2_X {monitored}: type={ret[4][i]}, "
                      f"U1={float(ret[6][i]):.6f}, U2={float(ret[7][i]):.6f}")
        else:
            print(f"  KYH2_X: No results for {monitored}")
    except Exception as e:
        print(f"  KYH2_X verification error: {e}")

    # === EXTRACT ALL RESULTS ===
    print("\n" + "=" * 70)
    print("EXTRACTING ALL RESULTS")
    print("=" * 70)

    all_cases = ["DEAD", "EQ_X", "EQ_Y"] + list(TH_CASES.keys())
    th_summary = []
    all_env_rows = []
    all_frame_rows = []

    for case in all_cases:
        print(f"\n  {case}...")
        t0 = time.time()

        # Joint envelopes
        j_env = extract_joint_envelopes(sap, case, joint_names)

        # Frame envelopes (only for key cases to save time)
        f_env = {}
        if case in ["KYH1_X", "KYH2_X", "KYH3_X", "KYH1_Y", "KYH2_Y", "KYH3_Y", "EQ_X", "EQ_Y"]:
            f_env = extract_frame_envelopes(sap, case, frame_names)

        base_r = extract_base_reactions(sap, case)
        stresses = compute_stresses(f_env) if f_env else {}

        elapsed = time.time() - t0

        if j_env:
            max_ux = max(r["max_ux"] for r in j_env.values())
            max_uy = max(r["max_uy"] for r in j_env.values())
            drift_x = max_ux / max_z * 100
            drift_y = max_uy / max_z * 100
            sigma_max = max((s["sigma_total_MPa"] for s in stresses.values()), default=0)
            tau_max = max((s["tau_total_MPa"] for s in stresses.values()), default=0)

            print(f"    {len(j_env)} joints | Ux={max_ux:.4f}cm Uy={max_uy:.4f}cm | "
                  f"drift={max(drift_x,drift_y):.3f}% | "
                  f"sig={sigma_max:.2f}MPa tau={tau_max:.2f}MPa | {elapsed:.1f}s")

            if case in TH_CASES:
                th_summary.append({
                    "case": case,
                    "max_ux_cm": max_ux, "max_uy_cm": max_uy,
                    "drift_x_pct": drift_x, "drift_y_pct": drift_y,
                    "sigma_max_MPa": sigma_max, "tau_max_MPa": tau_max,
                    "base_Fx_N": base_r.get("max_Fx", 0),
                    "base_Fy_N": base_r.get("max_Fy", 0),
                })

            # Per-node envelope rows
            for node, vals in j_env.items():
                all_env_rows.append({
                    "case": case, "joint": node,
                    "x_cm": joints[node]["x"], "y_cm": joints[node]["y"],
                    "z_cm": joints[node]["z"],
                    "max_ux_cm": vals["max_ux"],
                    "max_uy_cm": vals["max_uy"],
                    "max_uz_cm": vals["max_uz"],
                })

        # Per-frame force rows
        if f_env:
            for elem, vals in f_env.items():
                row = {"case": case, "frame": elem}
                row.update(vals)
                if elem in stresses:
                    row.update(stresses[elem])
                all_frame_rows.append(row)

    # === SAVE CSVs ===
    print("\n--- SAVING RESULTS ---")

    if all_env_rows:
        pd.DataFrame(all_env_rows).to_csv(
            os.path.join(RESULTS_DIR, "all_envelopes.csv"), index=False)
        print(f"  all_envelopes.csv: {len(all_env_rows)} rows")

    if all_frame_rows:
        pd.DataFrame(all_frame_rows).to_csv(
            os.path.join(RESULTS_DIR, "all_frame_forces.csv"), index=False)
        print(f"  all_frame_forces.csv: {len(all_frame_rows)} rows")

    if th_summary:
        pd.DataFrame(th_summary).to_csv(
            os.path.join(RESULTS_DIR, "th_summary.csv"), index=False)
        print(f"  th_summary.csv: {len(th_summary)} rows")

    coord_rows = [{"joint": n, **j} for n, j in joints.items()]
    pd.DataFrame(coord_rows).to_csv(
        os.path.join(RESULTS_DIR, "joint_coordinates.csv"), index=False)
    print(f"  joint_coordinates.csv: {len(coord_rows)} rows")

    # Summary JSON
    summary = {
        "model": {
            "n_joints": len(joint_names),
            "n_frames": len(frame_names),
            "max_z_cm": max_z,
            "units": "N_cm_C",
            "monitored_joint": monitored,
        },
        "modal": modal_data,
        "th_summary": th_summary,
    }
    with open(os.path.join(RESULTS_DIR, "analysis_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"  analysis_summary.json")

    # === FINAL SUMMARY ===
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    if modal_data and len(modal_data) >= 3:
        print(f"\n  T1={modal_data[0]['period_s']:.4f}s  "
              f"T2={modal_data[1]['period_s']:.4f}s  "
              f"T3={modal_data[2]['period_s']:.4f}s")

    if th_summary:
        print(f"\n  {'Case':<12} {'Ux(cm)':<10} {'Uy(cm)':<10} {'Drft%':<8} "
              f"{'sig(MPa)':<10} {'tau(MPa)':<10}")
        print(f"  {'-' * 60}")
        for r in th_summary:
            print(f"  {r['case']:<12} {r['max_ux_cm']:<10.4f} {r['max_uy_cm']:<10.4f} "
                  f"{max(r['drift_x_pct'],r['drift_y_pct']):<8.3f} "
                  f"{r['sigma_max_MPa']:<10.2f} {r['tau_max_MPa']:<10.2f}")

    print(f"\n  Results saved to: {RESULTS_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    main()
