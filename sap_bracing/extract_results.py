"""Extract results from already-completed SAP2000 analysis (corrected frame force indices)."""
import os, time, json
import numpy as np
import pandas as pd
import comtypes.client

BASE_DIR = r"c:\Users\lenovo\Desktop\DASK_NEW"
SAP_DIR = os.path.join(BASE_DIR, "sap_bracing")
RESULTS_DIR = os.path.join(BASE_DIR, "results", "sap_bracing")
os.makedirs(RESULTS_DIR, exist_ok=True)

SECT_A = 0.36
SECT_I = 0.0108
SECT_c = 0.3

TH_CASES = {
    "KYH1_X": ("U1", "KYH1"), "KYH1_Y": ("U2", "KYH1"),
    "KYH2_X": ("U1", "KYH2"), "KYH2_Y": ("U2", "KYH2"),
    "KYH3_X": ("U1", "KYH3"), "KYH3_Y": ("U2", "KYH3"),
}

sap_obj = comtypes.client.GetActiveObject("CSI.SAP2000.API.SapObject")
sap = sap_obj.SapModel
print("Connected")

joint_names = list(sap.PointObj.GetNameList()[1])
frame_names = list(sap.FrameObj.GetNameList()[1])
print(f"Model: {len(joint_names)} joints, {len(frame_names)} frames")

joints = {}
for name in joint_names:
    ret = sap.PointObj.GetCoordCartesian(name)
    joints[name] = {"x": float(ret[0]), "y": float(ret[1]), "z": float(ret[2])}
max_z = max(j["z"] for j in joints.values())

# Modal
sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
sap.Results.Setup.SetCaseSelectedForOutput("MODAL", True)
ret = sap.Results.ModalPeriod(0, [""], [""], [0.0], [0.0], [0.0], [0.0], [0.0])
modal_data = []
for i in range(min(12, ret[0])):
    modal_data.append({"mode": i+1, "period_s": float(ret[4][i]), "freq_hz": float(ret[5][i])})
print(f"Modal: T1={ret[4][0]:.4f}s")


def extract_joint_env(case):
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case, True)
    try:
        sap.Results.Setup.SetOptionModalHist(1)
    except Exception:
        pass
    results = {}
    for name in joint_names:
        try:
            ret = sap.Results.JointDispl(name, 0)
            if ret[0] > 0:
                n = ret[0]
                results[name] = {
                    "max_ux": max(abs(float(ret[6][i])) for i in range(n)),
                    "max_uy": max(abs(float(ret[7][i])) for i in range(n)),
                    "max_uz": max(abs(float(ret[8][i])) for i in range(n)),
                }
        except Exception:
            pass
    return results


def extract_frame_env(case):
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case, True)
    try:
        sap.Results.Setup.SetOptionModalHist(1)
    except Exception:
        pass
    results = {}
    errs = 0
    for name in frame_names:
        try:
            ret = sap.Results.FrameForce(name, 0)
            if ret[0] > 0:
                n = ret[0]
                # Corrected: [8]=P, [9]=V2, [10]=V3, [11]=T, [12]=M2, [13]=M3
                results[name] = {
                    "max_P": max(abs(float(ret[8][i])) for i in range(n)),
                    "min_P": min(float(ret[8][i]) for i in range(n)),
                    "max_V2": max(abs(float(ret[9][i])) for i in range(n)),
                    "max_V3": max(abs(float(ret[10][i])) for i in range(n)),
                    "max_T": max(abs(float(ret[11][i])) for i in range(n)),
                    "max_M2": max(abs(float(ret[12][i])) for i in range(n)),
                    "max_M3": max(abs(float(ret[13][i])) for i in range(n)),
                }
        except Exception as e:
            errs += 1
            if errs <= 2:
                print(f"    Frame {name} err: {e}")
    if errs > 0:
        print(f"    ({errs} frames with errors)")
    return results


def extract_base_react(case):
    sap.Results.Setup.DeselectAllCasesAndCombosForOutput()
    sap.Results.Setup.SetCaseSelectedForOutput(case, True)
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
        print(f"    BaseReact err: {e}")
    return {}


def compute_stresses(ff):
    stresses = {}
    for elem, f in ff.items():
        sig_ax = f["max_P"] / SECT_A
        sig_bend = (f["max_M2"] + f["max_M3"]) * SECT_c / SECT_I
        sig_total = sig_ax + sig_bend
        tau = 1.5 * (f["max_V2"]**2 + f["max_V3"]**2)**0.5 / SECT_A
        stresses[elem] = {
            "sigma_total_Ncm2": sig_total,
            "tau_total_Ncm2": tau,
            "sigma_total_MPa": sig_total / 100,
            "tau_total_MPa": tau / 100,
        }
    return stresses


# === EXTRACT ALL RESULTS ===
print()
all_cases = ["DEAD", "EQ_X", "EQ_Y"] + list(TH_CASES.keys())
th_summary = []
all_env_rows = []
all_frame_rows = []

for case in all_cases:
    t0 = time.time()
    print(f"{case}...", end=" ", flush=True)

    j_env = extract_joint_env(case)

    f_env = {}
    if case in list(TH_CASES.keys()) + ["EQ_X", "EQ_Y"]:
        f_env = extract_frame_env(case)

    base_r = extract_base_react(case)
    stresses = compute_stresses(f_env) if f_env else {}

    elapsed = time.time() - t0

    if j_env:
        max_ux = max(r["max_ux"] for r in j_env.values())
        max_uy = max(r["max_uy"] for r in j_env.values())
        drift_x = max_ux / max_z * 100
        drift_y = max_uy / max_z * 100
        sigma_max = max((s["sigma_total_MPa"] for s in stresses.values()), default=0)
        tau_max = max((s["tau_total_MPa"] for s in stresses.values()), default=0)

        print(f"{len(j_env)}j | Ux={max_ux:.4f} Uy={max_uy:.4f} | "
              f"drift={max(drift_x,drift_y):.3f}% | "
              f"sig={sigma_max:.1f}MPa tau={tau_max:.1f}MPa | {elapsed:.0f}s")

        if case in TH_CASES:
            th_summary.append({
                "case": case,
                "max_ux_cm": max_ux, "max_uy_cm": max_uy,
                "drift_x_pct": drift_x, "drift_y_pct": drift_y,
                "sigma_max_MPa": sigma_max, "tau_max_MPa": tau_max,
                "base_Fx_N": base_r.get("max_Fx", 0),
                "base_Fy_N": base_r.get("max_Fy", 0),
            })

        for node, vals in j_env.items():
            all_env_rows.append({
                "case": case, "joint": node,
                "x_cm": joints[node]["x"], "y_cm": joints[node]["y"],
                "z_cm": joints[node]["z"],
                "max_ux_cm": vals["max_ux"],
                "max_uy_cm": vals["max_uy"],
                "max_uz_cm": vals["max_uz"],
            })

    if f_env:
        for elem, vals in f_env.items():
            row = {"case": case, "frame": elem}
            row.update(vals)
            if elem in stresses:
                row.update(stresses[elem])
            all_frame_rows.append(row)

# === SAVE ===
print("\n--- SAVING ---")
if all_env_rows:
    pd.DataFrame(all_env_rows).to_csv(os.path.join(RESULTS_DIR, "all_envelopes.csv"), index=False)
    print(f"all_envelopes.csv: {len(all_env_rows)} rows")

if all_frame_rows:
    pd.DataFrame(all_frame_rows).to_csv(os.path.join(RESULTS_DIR, "all_frame_forces.csv"), index=False)
    print(f"all_frame_forces.csv: {len(all_frame_rows)} rows")

if th_summary:
    pd.DataFrame(th_summary).to_csv(os.path.join(RESULTS_DIR, "th_summary.csv"), index=False)
    print(f"th_summary.csv: {len(th_summary)} rows")

coord_rows = [{"joint": n, **j} for n, j in joints.items()]
pd.DataFrame(coord_rows).to_csv(os.path.join(RESULTS_DIR, "joint_coordinates.csv"), index=False)
print(f"joint_coordinates.csv: {len(coord_rows)} rows")

summary = {
    "model": {"n_joints": len(joint_names), "n_frames": len(frame_names),
              "max_z_cm": max_z, "units": "N_cm_C"},
    "modal": modal_data,
    "th_summary": th_summary,
}
with open(os.path.join(RESULTS_DIR, "analysis_summary.json"), "w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
print("analysis_summary.json")

# Final summary table
print("\n" + "=" * 70)
print("FINAL SUMMARY")
print("=" * 70)
t = modal_data
print(f"T1={t[0]['period_s']:.4f}s  T2={t[1]['period_s']:.4f}s  T3={t[2]['period_s']:.4f}s")
hdr = f"{'Case':<12} {'Ux(cm)':<10} {'Uy(cm)':<10} {'Drft%':<8} {'sig(MPa)':<10} {'tau(MPa)':<10} {'Vb_x(N)':<12} {'Vb_y(N)':<12}"
print(f"\n{hdr}")
print("-" * 82)
for r in th_summary:
    dr = max(r["drift_x_pct"], r["drift_y_pct"])
    print(f"{r['case']:<12} {r['max_ux_cm']:<10.4f} {r['max_uy_cm']:<10.4f} "
          f"{dr:<8.3f} {r['sigma_max_MPa']:<10.1f} {r['tau_max_MPa']:<10.1f} "
          f"{r['base_Fx_N']:<12.1f} {r['base_Fy_N']:<12.1f}")
print(f"\nResults: {RESULTS_DIR}")
