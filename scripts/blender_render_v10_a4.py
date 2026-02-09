"""
DASK 2026 — V10 Twin Towers — Single A4 Composite Render
=========================================================
Renders 8 key views and composites them into one A4 image.

Usage:  blender --background --python scripts/blender_render_v10_a4.py
Output: results/renders/DASK2026_V10_composite_A4.png
"""

import bpy
import csv
import math
import os
import sys
import numpy as np
from mathutils import Vector, Euler

# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════
SCRIPT_DIR  = os.path.dirname(os.path.abspath(__file__))
BASE_DIR    = os.path.dirname(SCRIPT_DIR)
CSV_POS     = os.path.join(BASE_DIR, 'data', 'twin_position_matrix_v10.csv')
CSV_CONN    = os.path.join(BASE_DIR, 'data', 'twin_connectivity_matrix_v10.csv')
RENDER_DIR  = os.path.join(BASE_DIR, 'results', 'renders')
BLEND_CACHE = os.path.join(BASE_DIR, 'results', 'twin_towers_v10_a4.blend')

# ═══════════════════════════════════════════════════════════════════
# A4 LAYOUT  (300 DPI)
# ═══════════════════════════════════════════════════════════════════
A4_W, A4_H   = 2480, 3508          # A4 @ 300 DPI
MARGIN        = 60                   # px
TITLE_H       = 120                  # title bar height
LABEL_H       = 40                   # label height below each cell
GAP           = 30                   # gap between cells
COLS, ROWS    = 2, 4                 # 2×4 grid = 8 views

# cell size (auto-calculated)
CELL_W = (A4_W - 2*MARGIN - (COLS-1)*GAP) // COLS          # ≈1165
CELL_H = (A4_H - 2*MARGIN - TITLE_H - ROWS*(LABEL_H) - (ROWS-1)*GAP) // ROWS  # ≈700

SCALE     = 0.01
SECTION   = 0.006
CX, CY, CZ = 0.15, 0.20, 0.765

SAMPLES = 128

# ═══════════════════════════════════════════════════════════════════
# 8 CAMERA PRESETS  (name, label, loc, target, lens, ortho_scale|None)
# ═══════════════════════════════════════════════════════════════════
D = 4.0
ISO = 3.2

VIEWS = [
    # Row 1
    ("front",     "Ön Görünüm (XZ)",
     (CX, CY - D, CZ), (CX, CY, CZ), 50, 2.2),
    ("side",      "Yan Görünüm (YZ) — Mega Brace",
     (CX - D, CY, CZ), (CX, CY, CZ), 50, 2.2),
    # Row 2
    ("iso_ne",    "İzometrik — Kuzeydoğu",
     (CX+ISO*0.7, CY-ISO*0.7, CZ+0.9), (CX, CY, CZ), 55, None),
    ("iso_sw",    "İzometrik — Güneybatı",
     (CX-ISO*0.7, CY+ISO*0.7, CZ+0.9), (CX, CY, CZ), 55, None),
    # Row 3
    ("back",      "Arka Görünüm (XZ)",
     (CX, CY + D, CZ), (CX, CY, CZ), 50, 2.2),
    ("right",     "Sağ Yan Görünüm (YZ)",
     (CX + D, CY, CZ), (CX, CY, CZ), 50, 2.2),
    # Row 4
    ("top",       "Üst Görünüm (Plan)",
     (CX, CY, CZ + D), (CX, CY, CZ), 50, 0.65),
    ("hero",      "3/4 Perspektif",
     (CX+2.5, CY-1.8, CZ+1.6), (CX, CY, CZ-0.05), 42, None),
]

# ═══════════════════════════════════════════════════════════════════
# UTILITY
# ═══════════════════════════════════════════════════════════════════
def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=True)
    for block in [bpy.data.materials, bpy.data.lights,
                  bpy.data.cameras, bpy.data.meshes, bpy.data.worlds]:
        for item in list(block):
            block.remove(item)
    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)

def track_to(obj, target_loc, scene):
    tgt = bpy.data.objects.new(f"Tgt_{obj.name}", None)
    scene.collection.objects.link(tgt)
    tgt.location = target_loc
    c = obj.constraints.new('TRACK_TO')
    c.target = tgt; c.track_axis = 'TRACK_NEGATIVE_Z'; c.up_axis = 'UP_Y'

# ═══════════════════════════════════════════════════════════════════
# MATERIALS  — warm balsa palette, distinct per element type
# ═══════════════════════════════════════════════════════════════════
def make_mat(name, base_color, roughness=0.50, specular=0.3):
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    N = mat.node_tree.nodes; L = mat.node_tree.links
    N.clear()
    bsdf = N.new('ShaderNodeBsdfPrincipled'); bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = base_color
    bsdf.inputs['Roughness'].default_value = roughness
    bsdf.inputs['Specular IOR Level'].default_value = specular
    out = N.new('ShaderNodeOutputMaterial'); out.location = (300, 0)
    L.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat

def make_wood_mat():
    """Procedural balsa wood with grain."""
    mat = bpy.data.materials.new("Balsa_Wood")
    mat.use_nodes = True
    N = mat.node_tree.nodes; L = mat.node_tree.links
    N.clear()

    coord = N.new('ShaderNodeTexCoord');  coord.location = (-800, 0)
    mapn  = N.new('ShaderNodeMapping');   mapn.location  = (-600, 0)
    mapn.inputs['Scale'].default_value = (25, 25, 25)

    noise = N.new('ShaderNodeTexNoise');  noise.location = (-350, 80)
    noise.inputs['Scale'].default_value  = 200
    noise.inputs['Detail'].default_value = 12
    noise.inputs['Roughness'].default_value = 0.5

    wave  = N.new('ShaderNodeTexWave');   wave.location  = (-350, -120)
    wave.inputs['Scale'].default_value = 35
    wave.inputs['Distortion'].default_value = 5
    wave.inputs['Detail'].default_value = 4
    wave.bands_direction = 'Z'

    mix   = N.new('ShaderNodeMixRGB');    mix.location   = (-100, 0)
    mix.inputs['Fac'].default_value = 0.30

    ramp  = N.new('ShaderNodeValToRGB'); ramp.location  = (100, 0)
    els = ramp.color_ramp.elements
    els[0].position = 0.30; els[0].color = (0.68, 0.54, 0.38, 1)
    els[1].position = 0.70; els[1].color = (0.94, 0.84, 0.68, 1)

    bsdf  = N.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 0)
    bsdf.inputs['Roughness'].default_value = 0.48
    bsdf.inputs['Specular IOR Level'].default_value = 0.35
    bsdf.inputs['Sheen Weight'].default_value = 0.08

    out   = N.new('ShaderNodeOutputMaterial'); out.location = (700, 0)

    L.new(coord.outputs['Object'], mapn.inputs['Vector'])
    L.new(mapn.outputs['Vector'],  noise.inputs['Vector'])
    L.new(mapn.outputs['Vector'],  wave.inputs['Vector'])
    L.new(noise.outputs['Fac'],    mix.inputs['Color1'])
    L.new(wave.outputs['Color'],   mix.inputs['Color2'])
    L.new(mix.outputs['Color'],    ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'],   bsdf.inputs['Base Color'])
    L.new(bsdf.outputs['BSDF'],   out.inputs['Surface'])
    return mat

def create_materials():
    mats = {}
    mats['column']      = make_wood_mat()
    mats['beam']        = make_mat("Beam",  (0.88, 0.76, 0.58, 1), 0.50)
    mats['brace_xz']    = make_mat("BraceXZ", (0.82, 0.65, 0.42, 1), 0.45, 0.35)
    mats['brace_yz']    = make_mat("BraceYZ", (0.90, 0.55, 0.30, 1), 0.42, 0.40)  # warmer / redder for mega
    mats['bridge']      = make_mat("Bridge",  (0.60, 0.48, 0.32, 1), 0.40, 0.38)
    mats['floor_brace'] = make_mat("FloorBr", (0.78, 0.70, 0.56, 1), 0.55)
    return mats

def mat_for_etype(etype, mats):
    if 'bridge' in etype:   return mats['bridge']
    if etype == 'brace_xz': return mats['brace_xz']
    if etype == 'brace_yz': return mats['brace_yz']
    if etype == 'floor_brace': return mats['floor_brace']
    if 'beam' in etype:     return mats['beam']
    return mats['column']

# ═══════════════════════════════════════════════════════════════════
# BUILD MODEL
# ═══════════════════════════════════════════════════════════════════
def build_model(mats):
    print("[MODEL] Reading CSV …")
    nodes = {}
    with open(CSV_POS) as f:
        for row in csv.DictReader(f):
            nid = int(row['node_id'])
            nodes[nid] = Vector((float(row['x'])*SCALE,
                                 float(row['y'])*SCALE,
                                 float(row['z'])*SCALE))

    col = bpy.data.collections.new("TwinTowers_V10")
    bpy.context.scene.collection.children.link(col)

    count = 0
    with open(CSV_CONN) as f:
        for row in csv.DictReader(f):
            ni, nj = int(row['node_i']), int(row['node_j'])
            etype  = row['element_type']
            if ni not in nodes or nj not in nodes: continue
            p1, p2 = nodes[ni], nodes[nj]
            mid = (p1 + p2) / 2
            diff = p2 - p1
            length = diff.length
            if length < 1e-5: continue

            w = d = SECTION
            mat = mat_for_etype(etype, mats)

            bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
            obj = bpy.context.active_object
            obj.name = f"{etype}_{count}"
            obj.scale = (w, d, length)
            obj.rotation_euler = diff.to_track_quat('Z', 'Y').to_euler()
            obj.data.materials.append(mat)

            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)
            count += 1
            if count % 500 == 0:
                print(f"  … {count}")

    print(f"[MODEL] {count} elements")

    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)
    if col.objects:
        bpy.context.view_layer.objects.active = col.objects[0]
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    return col

# ═══════════════════════════════════════════════════════════════════
# LIGHTING — warm golden-hour studio
# ═══════════════════════════════════════════════════════════════════
def setup_lighting():
    scene = bpy.context.scene
    tgt = (CX, CY, CZ)

    # Key sun — warm golden hour
    sun = bpy.data.lights.new("Sun_Key", 'SUN')
    sun.energy = 3.0;  sun.angle = math.radians(2.0)
    sun.color = (1.0, 0.92, 0.80)
    so = bpy.data.objects.new("Sun_Key", sun)
    scene.collection.objects.link(so)
    so.rotation_euler = Euler((math.radians(45), math.radians(10), math.radians(40)))

    # Cool fill — opposite side
    fill = bpy.data.lights.new("Fill", 'AREA')
    fill.energy = 200;  fill.size = 10;  fill.color = (0.85, 0.92, 1.0)
    fo = bpy.data.objects.new("Fill", fill)
    scene.collection.objects.link(fo)
    fo.location = (CX - 5, CY - 3, CZ + 0.8)
    track_to(fo, tgt, scene)

    # Warm rim — backlight
    rim = bpy.data.lights.new("Rim", 'AREA')
    rim.energy = 300;  rim.size = 5;  rim.color = (1.0, 0.88, 0.72)
    ro = bpy.data.objects.new("Rim", rim)
    scene.collection.objects.link(ro)
    ro.location = (CX + 4, CY + 4, CZ + 1.2)
    track_to(ro, tgt, scene)

    # Subtle top fill
    top = bpy.data.lights.new("Top", 'AREA')
    top.energy = 100;  top.size = 14
    to = bpy.data.objects.new("Top", top)
    scene.collection.objects.link(to)
    to.location = (CX, CY, CZ + 6)

    # Ground bounce (underneath, cool)
    bounce = bpy.data.lights.new("Bounce", 'AREA')
    bounce.energy = 40;  bounce.size = 10;  bounce.color = (0.8, 0.85, 1.0)
    bo = bpy.data.objects.new("Bounce", bounce)
    scene.collection.objects.link(bo)
    bo.location = (CX, CY, -1.5)
    bo.rotation_euler = (math.radians(180), 0, 0)

    # ── World — warm-cool gradient ──
    world = bpy.data.worlds.new("Env")
    scene.world = world
    world.use_nodes = True
    wN = world.node_tree.nodes;  wL = world.node_tree.links
    wN.clear()

    coord = wN.new('ShaderNodeTexCoord');   coord.location = (-700, 0)
    mapn  = wN.new('ShaderNodeMapping');    mapn.location  = (-500, 0)
    mapn.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    grad  = wN.new('ShaderNodeTexGradient'); grad.location = (-300, 0)

    ramp  = wN.new('ShaderNodeValToRGB');   ramp.location  = (-100, 0)
    els = ramp.color_ramp.elements
    # warm bottom → cool top (studio backdrop feel)
    els[0].position = 0.0;  els[0].color = (0.035, 0.028, 0.022, 1)  # warm dark
    els[1].position = 1.0;  els[1].color = (0.04, 0.05, 0.07, 1)     # cool dark

    bg  = wN.new('ShaderNodeBackground'); bg.location = (100, 0)
    bg.inputs['Strength'].default_value = 0.6
    out = wN.new('ShaderNodeOutputWorld'); out.location = (300, 0)

    wL.new(coord.outputs['Generated'], mapn.inputs['Vector'])
    wL.new(mapn.outputs['Vector'],     grad.inputs['Vector'])
    wL.new(grad.outputs['Color'],      ramp.inputs['Fac'])
    wL.new(ramp.outputs['Color'],      bg.inputs['Color'])
    wL.new(bg.outputs['Background'],   out.inputs['Surface'])

    # ── Reflective studio floor ──
    bpy.ops.mesh.primitive_plane_add(size=30, location=(CX, CY, -0.001))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    mf = bpy.data.materials.new("Floor")
    mf.use_nodes = True
    bsdf = mf.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.018, 0.018, 0.020, 1)
    bsdf.inputs['Roughness'].default_value = 0.08
    bsdf.inputs['Specular IOR Level'].default_value = 0.95
    floor.data.materials.append(mf)

    print("[LIGHT] Golden-hour studio ready.")

# ═══════════════════════════════════════════════════════════════════
# RENDER SETUP
# ═══════════════════════════════════════════════════════════════════
def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'

    prefs = bpy.context.preferences
    cp = prefs.addons.get('cycles')
    gpu_ok = False
    if cp:
        for ct in ('CUDA', 'OPTIX', 'HIP', 'METAL', 'ONEAPI'):
            try:
                cp.preferences.compute_device_type = ct
                cp.preferences.get_devices()
                devs = [d for d in cp.preferences.devices if d.type != 'CPU']
                if devs:
                    for d in cp.preferences.devices:
                        d.use = (d.type != 'CPU')
                    gpu_ok = True
                    print(f"[GPU] {ct} — {devs[0].name}")
                    break
            except:
                continue

    cy = scene.cycles
    cy.device = 'GPU' if gpu_ok else 'CPU'
    cy.samples = SAMPLES
    cy.use_denoising = True
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.01

    # Per-cell resolution
    scene.render.resolution_x = CELL_W
    scene.render.resolution_y = CELL_H
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = False

    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.4

    print(f"[RENDER] {CELL_W}×{CELL_H} per cell, {SAMPLES} spp, {cy.device}")

# ═══════════════════════════════════════════════════════════════════
# RENDER ALL VIEWS → individual PNGs
# ═══════════════════════════════════════════════════════════════════
def render_views():
    scene = bpy.context.scene
    os.makedirs(RENDER_DIR, exist_ok=True)

    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj  = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    cam_data.dof.use_dof = False

    cam_tgt = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(cam_tgt)
    tc = cam_obj.constraints.new('TRACK_TO')
    tc.target = cam_tgt
    tc.track_axis = 'TRACK_NEGATIVE_Z'
    tc.up_axis = 'UP_Y'

    paths = []
    for name, label, loc, tgt, lens, ortho in VIEWS:
        print(f"\n>>> {name}: {label}")
        cam_obj.location = Vector(loc)
        cam_tgt.location = Vector(tgt)
        cam_data.lens = lens

        if ortho is not None:
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = ortho
        else:
            cam_data.type = 'PERSP'

        if 'hero' in name:
            cam_data.dof.use_dof = True
            cam_data.dof.focus_object = cam_tgt
            cam_data.dof.aperture_fstop = 3.2
        else:
            cam_data.dof.use_dof = False

        # Transparent bg for plan view so it composes nicely
        scene.render.film_transparent = ('top' in name)

        fpath = os.path.join(RENDER_DIR, f"v10_{name}")
        scene.render.filepath = fpath
        bpy.ops.render.render(write_still=True)
        paths.append((fpath + ".png", label))
        print(f"    ✓ saved")

    return paths

# ═══════════════════════════════════════════════════════════════════
# COMPOSITE INTO SINGLE A4 IMAGE
# ═══════════════════════════════════════════════════════════════════
def composite_a4(view_paths):
    """Load rendered PNGs and composite onto a single A4 canvas using numpy."""
    print("\n[COMPOSITE] Building A4 layout …")

    # Create canvas (RGBA float, white bg)
    canvas = np.ones((A4_H, A4_W, 4), dtype=np.float32)
    # Dark charcoal background
    canvas[:, :, 0] = 0.12
    canvas[:, :, 1] = 0.12
    canvas[:, :, 2] = 0.13
    canvas[:, :, 3] = 1.0

    # Title bar — slightly lighter
    canvas[:MARGIN+TITLE_H, :, 0] = 0.08
    canvas[:MARGIN+TITLE_H, :, 1] = 0.08
    canvas[:MARGIN+TITLE_H, :, 2] = 0.09

    # Place each rendered view
    for idx, (fpath, label) in enumerate(view_paths):
        row = idx // COLS
        col_idx = idx % COLS

        x0 = MARGIN + col_idx * (CELL_W + GAP)
        y0 = MARGIN + TITLE_H + row * (CELL_H + LABEL_H + GAP)

        # Load image via Blender
        try:
            img = bpy.data.images.load(fpath)
        except:
            print(f"  WARNING: could not load {fpath}")
            continue

        w, h = img.size
        pixels = np.array(img.pixels[:]).reshape(h, w, 4)
        # Blender stores bottom-up → flip
        pixels = pixels[::-1, :, :]

        # Resize if needed (simple nearest-neighbor)
        if w != CELL_W or h != CELL_H:
            from numpy import interp
            ys = np.linspace(0, h-1, CELL_H).astype(int)
            xs = np.linspace(0, w-1, CELL_W).astype(int)
            pixels = pixels[np.ix_(ys, xs)]

        # Paste onto canvas
        y1 = min(y0 + CELL_H, A4_H)
        x1 = min(x0 + CELL_W, A4_W)
        ph = y1 - y0
        pw = x1 - x0
        canvas[y0:y1, x0:x1] = pixels[:ph, :pw]

        # Thin white border around cell
        canvas[y0:y0+2, x0:x1]   = [0.9, 0.9, 0.9, 1.0]   # top
        canvas[y1-2:y1, x0:x1]   = [0.9, 0.9, 0.9, 1.0]   # bottom
        canvas[y0:y1, x0:x0+2]   = [0.9, 0.9, 0.9, 1.0]   # left
        canvas[y0:y1, x1-2:x1]   = [0.9, 0.9, 0.9, 1.0]   # right

        bpy.data.images.remove(img)

    # Save composite
    comp = bpy.data.images.new("A4_Composite", width=A4_W, height=A4_H, alpha=True)
    # Blender expects bottom-up
    canvas_flip = canvas[::-1, :, :]
    comp.pixels = canvas_flip.flatten().tolist()

    out_path = os.path.join(RENDER_DIR, "DASK2026_V10_composite_A4.png")
    comp.filepath_raw = out_path
    comp.file_format = 'PNG'
    comp.save_render(out_path)
    print(f"[COMPOSITE] Saved → {out_path}")
    print(f"            {A4_W}×{A4_H} px  (A4 @ 300 DPI)")

    # Also save label map as text for reference
    label_path = os.path.join(RENDER_DIR, "composite_labels.txt")
    with open(label_path, 'w', encoding='utf-8') as f:
        f.write("DASK 2026 — Twin Towers V10 — Mega Brace System\n")
        f.write("=" * 50 + "\n\n")
        for idx, (fpath, label) in enumerate(view_paths):
            r = idx // COLS + 1
            c = idx % COLS + 1
            f.write(f"  Row {r}, Col {c}: {label}\n")
    print(f"[LABELS] {label_path}")

# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
def main():
    if os.path.exists(BLEND_CACHE):
        print(f"[CACHE] Loading {BLEND_CACHE}")
        bpy.ops.wm.open_mainfile(filepath=BLEND_CACHE)
        setup_render()
    else:
        print("[BUILD] Creating scene …")
        cleanup()
        mats = create_materials()
        build_model(mats)
        setup_lighting()
        setup_render()
        os.makedirs(os.path.dirname(BLEND_CACHE), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_CACHE)
        print(f"[CACHE] → {BLEND_CACHE}")

    view_paths = render_views()
    composite_a4(view_paths)

    print("\n" + "=" * 60)
    print("A4 COMPOSITE RENDER COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    main()
