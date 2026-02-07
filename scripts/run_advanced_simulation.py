"""
ADVANCED OPENSEES SIMULATION & ANIMATION
========================================
1. Builds V8 Twin Towers Model.
2. Runs Nonlinear Dynamic Analysis (Bolu Earthquake).
3. Records Displacement and Element Forces.
4. Generates MP4 Animation with Stress Visualization.

Usage:
  python scripts/run_advanced_simulation.py

Requirements:
  - openseespy
  - matplotlib
  - numpy
  - pandas
  - ffmpeg (System installed)
"""

import os
import sys
import numpy as np
import pandas as pd
import openseespy.opensees as ops
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from mpl_toolkits.mplot3d.art3d import Line3DCollection
from pathlib import Path
import matplotlib.cm as cm
import matplotlib.colors as mcolors

# ============================================ 
# 1. CONFIGURATION
# ============================================ 
SCRIPT_DIR = Path(__file__).parent
DATA_DIR = SCRIPT_DIR.parent / 'data'
GM_FILE = SCRIPT_DIR.parent / 'ground_motion' / 'BOL090.AT2'
OUTPUT_DIR = SCRIPT_DIR.parent / 'results' / 'simulation'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Animation Settings
VIDEO_FPS = 30
SCALE_FACTOR = 50.0  # Magnify displacements for visibility
STRESS_LIMIT = 5000.0 # kPa (5 MPa) for color scaling (Red=Comp, Blue=Tens)
SKIP_STEPS = 5       # Record every Nth step (0.01s * 5 = 0.05s frame time)

# Material (Balsa)
E_long = 3.5e6   # kPa
G_balsa = 0.2e6  # kPa
A_frame = 0.006**2
A_panel = 0.003 * 0.017 # Reduced width panel

# ============================================ 
# 2. MODEL BUILDER
# ============================================ 
def build_model():
    print("Building Model...")
    ops.wipe()
    ops.model('basic', '-ndm', 3, '-ndf', 6)
    
    # Load Data
    pos_df = pd.read_csv(DATA_DIR / 'twin_position_matrix.csv')
    conn_df = pd.read_csv(DATA_DIR / 'twin_connectivity_matrix.csv')
    
    # Nodes
    node_coords = {}
    for _, row in pos_df.iterrows():
        nid = int(row['node_id'])
        x, y, z = row['x']*0.01, row['y']*0.01, row['z']*0.01
        ops.node(nid, x, y, z)
        node_coords[nid] = (x, y, z)
        
    # Fix Base
    for nid in pos_df[pos_df['floor']==0]['node_id']:
        ops.fix(int(nid), 1, 1, 1, 1, 1, 1)
        
    # Transformations
    ops.geomTransf('Linear', 1, 0, 1, 0)
    ops.geomTransf('Linear', 2, 1, 0, 0)
    ops.geomTransf('Linear', 3, 0, 1, 0)
    
    # Elements
    elem_map = {} # eid -> (ni, nj)
    truss_mat = 1
    ops.uniaxialMaterial('Elastic', truss_mat, E_long)
    
    pin_types = ['brace_xz', 'brace_yz', 'floor_brace', 'bridge_truss', 'bridge_brace_bot', 'bridge_brace_top', 'shear_wall_xz', 'shear_wall_yz']
    
    for _, row in conn_df.iterrows():
        eid = int(row['element_id'])
        ni, nj = int(row['node_i']), int(row['node_j'])
        etype = row['element_type']
        elem_map[eid] = (ni, nj)
        
        p1, p2 = node_coords[ni], node_coords[nj]
        dx, dy, dz = abs(p1[0]-p2[0]), abs(p1[1]-p2[1]), abs(p1[2]-p2[2])
        
        area = A_panel if 'shear_wall' in etype else A_frame
        
        if etype in pin_types:
            ops.element('Truss', eid, ni, nj, area, truss_mat)
        else:
            transf = 3
            if dz < 0.1 * max(dx, dy): transf = 1 if dx > dy else 2
            # I, J simplified
            I_val = 0.006**4 / 12
            ops.element('elasticBeamColumn', eid, ni, nj, area, E_long, G_balsa, 1.0, I_val, I_val, transf)

    # Masses
    MASS_FLOORS = [3, 6, 9, 12, 15, 18, 21, 24]
    plate_mass = 1.60/1000
    for f in MASS_FLOORS:
        ns = pos_df[pos_df['floor']==f]['node_id'].tolist()
        m = plate_mass/len(ns)
        for n in ns: ops.mass(int(n), m, m, m, 0,0,0)
        
    top_ns = pos_df[pos_df['floor']==pos_df['floor'].max()]['node_id'].tolist()
    m_top = (2.22/1000)/len(top_ns)
    for n in top_ns: ops.mass(int(n), m_top, m_top, m_top, 0,0,0)
    
    return node_coords, elem_map, len(conn_df)

# ============================================ 
# 3. ANALYSIS RUNNER
# ============================================ 
def run_analysis(node_coords, elem_map):
    print("Setting up Analysis...")
    
    # Damping
    vals = ops.eigen(2)
    w1, w2 = np.sqrt(vals[0]), np.sqrt(vals[1])
    ops.rayleigh(0.02*2*w1*w2/(w1+w2), 0.0, 0.02*2/(w1+w2), 0.0)
    
    # Gravity
    ops.timeSeries('Linear', 1)
    ops.pattern('Plain', 1, 1)
    for nid in node_coords:
        m = ops.nodeMass(nid)
        if sum(m) > 0: ops.load(nid, 0, 0, -m[2]*9.81, 0,0,0)
        
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-6, 10)
    ops.algorithm('Newton')
    ops.integrator('LoadControl', 0.1)
    ops.analysis('Static')
    ops.analyze(10)
    
    # Earthquake
    ops.loadConst('-time', 0.0)
    
    # Load GM
    accel = []
    dt = 0.01
    with open(GM_FILE) as f:
        lines = f.readlines()
        for line in lines[4:]:
            accel.extend([float(x) for x in line.split()])
    
    ops.timeSeries('Path', 2, '-dt', dt, '-values', *accel, '-factor', 9.81)
    ops.pattern('UniformExcitation', 2, 2, '-accel', 2) # Y direction
    
    ops.wipeAnalysis()
    ops.constraints('Transformation')
    ops.numberer('RCM')
    ops.system('BandGeneral')
    ops.test('NormDispIncr', 1e-6, 10)
    ops.algorithm('Newton')
    ops.integrator('Newmark', 0.5, 0.25)
    ops.analysis('Transient')
    
    # RECORDING LOOP
    # We record manually to memory to avoid massive file I/O parsing later
    # Format: [Time, [NodeDisps], [ElemForces]]
    
    total_steps = len(accel)
    frames = []
    
    print(f"Running Analysis ({total_steps} steps)...")
    
    node_ids = list(node_coords.keys())
    elem_ids = list(elem_map.keys())
    
    # Pre-map indices
    node_idx_map = {nid: i for i, nid in enumerate(node_ids)}
    
    for i in range(total_steps):
        ok = ops.analyze(1, dt)
        if ok != 0:
            print("Analysis Failed!")
            break
            
        if i % SKIP_STEPS == 0:
            t = ops.getTime()
            
            # Capture Displacements (Nx3)
            # Optimization: ops.nodeDisp is slow in loop. 
            # But for 1600 nodes every 5 steps, it's ok.
            disps = np.zeros((len(node_ids), 3))
            for j, nid in enumerate(node_ids):
                # We need full coords: Original + Disp
                u = ops.nodeDisp(nid) # [ux, uy, uz, rx, ry, rz]
                disps[j] = [u[0], u[1], u[2]]
            
            # Capture Forces (M) -> Stress
            # Just get Axial Force (P) for color
            stresses = np.zeros(len(elem_ids))
            for j, eid in enumerate(elem_ids):
                # eleResponse 'axialForce' not always available for all types
                # 'basicForce' 1 is axial usually
                f = ops.eleResponse(eid, 'force') # returns list
                # Truss: [P, 0, 0...]
                # Beam: [P, V, M...]
                p = f[0]
                # Stress = P / A (Approx 6x6mm)
                # Comp negative
                stresses[j] = p / A_frame # kPa
                
            frames.append({
                'time': t,
                'disp': disps,
                'stress': stresses,
                'ground': accel[i] if i < len(accel) else 0
            })
            
        if i % 500 == 0:
            print(f"  Step {i}/{total_steps}")
            
    print("Analysis Complete.")
    return frames, node_ids, elem_ids

import time

# ... (Imports remain the same)

# ... (Configuration remains the same)

# ... (build_model remains the same)

# ... (run_analysis remains the same)

# ============================================
# 4. ANIMATION GENERATOR
# ============================================
def create_animation(frames, node_coords, elem_map, node_ids, elem_ids):
    print("Generating Animation (this may take a while)...")
    
    # Calculate Total Duration from last frame
    total_duration = frames[-1]['time'] if frames else 0.0
    
    # Setup Plot
    fig = plt.figure(figsize=(12, 8), dpi=100)
    ax = fig.add_subplot(111, projection='3d')
    
    # ... (Plot setup remains the same until title_text)
    
    # Info Text
    title_text = ax.text2D(0.05, 0.95, "", transform=ax.transAxes, fontsize=12, color='black')
    
    # ... (Colorbar and indices map remain the same)
    
    def update(frame_idx):
        data = frames[frame_idx]
        t = data['time']
        disps = data['disp']
        stresses = data['stress']
        ga = data['ground']
        
        # ... (Deformation logic remains the same)
        
        # Deformed Coords = Base + Disp * Scale
        deformed = base_coords + disps * SCALE_FACTOR
        
        p1s = deformed[[x[0] for x in elem_node_indices]]
        p2s = deformed[[x[1] for x in elem_node_indices]]
        new_segs = np.stack((p1s, p2s), axis=1)
        
        lc.set_segments(new_segs)
        lc.set_array(stresses) 
        
        # UPDATED HUD TEXT
        title_text.set_text(f"Time: {t:.2f} / {total_duration:.2f} s\nGround Accel: {ga:.3f} g\nScale Factor: {SCALE_FACTOR}x")
        return lc, title_text
    
    anim = FuncAnimation(fig, update, frames=len(frames), interval=1000/VIDEO_FPS, blit=False)
    
    vid_path = OUTPUT_DIR / 'twin_towers_stress.mp4'
    print(f"Saving video to {vid_path}...")
    
    try:
        writer = FFMpegWriter(fps=VIDEO_FPS, metadata=dict(artist='Gemini'), bitrate=3000)
        anim.save(vid_path, writer=writer)
        print("Success!")
    except Exception as e:
        print(f"Error saving video (ffmpeg installed?): {e}")
        
# ============================================
# MAIN
# ============================================
if __name__ == "__main__":
    start_time = time.time()
    
    coords, elems, n_elems = build_model()
    frames, nids, eids = run_analysis(coords, elems)
    create_animation(frames, coords, elems, nids, eids)
    
    end_time = time.time()
    elapsed = end_time - start_time
    print(f"\n========================================")
    print(f"TOTAL ELAPSED TIME: {elapsed:.2f} seconds ({elapsed/60:.2f} minutes)")
    print(f"========================================")
