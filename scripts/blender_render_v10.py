"""
DASK 2026 — Twin Towers V10 Multi-View Render Script
=====================================================
Blender Python script — balsa wood material, D5-quality lighting.

Produces still images from **14 camera angles**:
  1–4  : Front / Back / Left / Right  (ortho elevations)
  5–8  : 4× isometric corners         (perspective)
  9    : Top-down plan                 (ortho)
  10   : Worm's-eye (from below)       (perspective)
  11–12: YZ section cuts (x=0.3, x=15) — shows mega braces
  13   : Bird's-eye 3/4               (perspective, hero shot)
  14   : Close-up bridge detail        (perspective)

Usage
-----
  blender --background --python scripts/blender_render_v10.py

All output goes to  results/renders/  (PNG 3840×2160, transparent where useful).
A .blend cache is saved so re-runs skip model building.
"""

import bpy
import bmesh
import csv
import math
import os
import sys
from mathutils import Vector, Euler

# ═══════════════════════════════════════════════════════════════════
# PATHS
# ═══════════════════════════════════════════════════════════════════
SCRIPT_DIR   = os.path.dirname(os.path.abspath(__file__))
BASE_DIR     = os.path.dirname(SCRIPT_DIR)
CSV_POS      = os.path.join(BASE_DIR, 'data', 'twin_position_matrix_v10.csv')
CSV_CONN     = os.path.join(BASE_DIR, 'data', 'twin_connectivity_matrix_v10.csv')
BLEND_CACHE  = os.path.join(BASE_DIR, 'results', 'twin_towers_v10.blend')
RENDER_DIR   = os.path.join(BASE_DIR, 'results', 'renders')

# ═══════════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════════
SCALE     = 0.01            # cm → m  (model coords are in cm)
SECTION   = 0.006           # 6 mm balsa stick
BRACE_SEC = 0.006           # same for braces
PANEL_T   = 0.003           # 3 mm (unused in V10 — all sticks)

RES_X, RES_Y = 1920, 1080  # 1080p (raise to 3840×2160 for final)
SAMPLES      = 128          # Cycles (raise to 256 for final)
USE_DENOISE  = True

# Building centre in Blender coords (after cm→m scale)
# X range 0.3–29.7 cm → 0.003–0.297 m   mid ≈ 0.15
# Y range 0.3–39.7 cm → 0.003–0.397 m   mid ≈ 0.20
# Z range 0–153 cm    → 0–1.53 m         mid ≈ 0.765
CX, CY, CZ = 0.15, 0.20, 0.765

# ═══════════════════════════════════════════════════════════════════
# CAMERA PRESETS  (name, location, target, lens_mm, ortho_scale|None)
# If ortho_scale is given → orthographic, else perspective.
# ═══════════════════════════════════════════════════════════════════
CAM_OFFSET = 4.0   # distance for ortho views
ISO_DIST   = 3.5   # distance for iso views

CAMERAS = [
    # — Orthographic elevations —
    ("01_front",    (CX, CY - CAM_OFFSET, CZ), (CX, CY, CZ), 50, 2.2),
    ("02_back",     (CX, CY + CAM_OFFSET, CZ), (CX, CY, CZ), 50, 2.2),
    ("03_left",     (CX - CAM_OFFSET, CY, CZ), (CX, CY, CZ), 50, 2.2),
    ("04_right",    (CX + CAM_OFFSET, CY, CZ), (CX, CY, CZ), 50, 2.2),
    # — Isometric perspectives (4 corners) —
    ("05_iso_NE",   (CX + ISO_DIST*0.7, CY - ISO_DIST*0.7, CZ + 1.0), (CX, CY, CZ), 60, None),
    ("06_iso_NW",   (CX - ISO_DIST*0.7, CY - ISO_DIST*0.7, CZ + 1.0), (CX, CY, CZ), 60, None),
    ("07_iso_SE",   (CX + ISO_DIST*0.7, CY + ISO_DIST*0.7, CZ + 1.0), (CX, CY, CZ), 60, None),
    ("08_iso_SW",   (CX - ISO_DIST*0.7, CY + ISO_DIST*0.7, CZ + 1.0), (CX, CY, CZ), 60, None),
    # — Top / bottom —
    ("09_top",      (CX, CY, CZ + CAM_OFFSET), (CX, CY, CZ), 50, 0.7),
    ("10_worm",     (CX + 0.05, CY - 0.15, -0.15), (CX, CY, CZ + 0.3), 20, None),
    # — Section cuts (YZ plane) — shows mega braces —
    ("11_section_x03",  (-CAM_OFFSET + 0.003, CY, CZ), (0.003, CY, CZ), 50, 2.2),
    ("12_section_x15",  (-CAM_OFFSET + 0.15,  CY, CZ), (0.15,  CY, CZ), 50, 2.2),
    # — Hero & detail —
    ("13_hero",     (CX + 2.8, CY - 2.0, CZ + 1.8), (CX, CY, CZ - 0.1), 45, None),
    ("14_bridge_detail", (CX + 0.6, CY, 0.40), (CX, CY, 0.35), 85, None),
]

# ═══════════════════════════════════════════════════════════════════
#  UTILITY
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


# ═══════════════════════════════════════════════════════════════════
#  MATERIALS  (procedural balsa wood — D5-grade)
# ═══════════════════════════════════════════════════════════════════
def mat_balsa_frame():
    """Realistic light-coloured balsa with subtle wood grain."""
    mat = bpy.data.materials.new("Balsa_Frame")
    mat.use_nodes = True
    N = mat.node_tree.nodes;  L = mat.node_tree.links
    N.clear()

    coord  = N.new('ShaderNodeTexCoord');   coord.location  = (-800, 0)
    mapn   = N.new('ShaderNodeMapping');     mapn.location   = (-600, 0)
    mapn.inputs['Scale'].default_value = (30, 30, 30)

    noise  = N.new('ShaderNodeTexNoise');    noise.location  = (-350, 80)
    noise.inputs['Scale'].default_value  = 180
    noise.inputs['Detail'].default_value = 10
    noise.inputs['Roughness'].default_value = 0.55

    wave   = N.new('ShaderNodeTexWave');     wave.location   = (-350, -120)
    wave.inputs['Scale'].default_value  = 40
    wave.inputs['Distortion'].default_value = 4
    wave.inputs['Detail'].default_value = 3
    wave.bands_direction = 'Z'

    mix    = N.new('ShaderNodeMixRGB');      mix.location    = (-100, 0)
    mix.inputs['Fac'].default_value = 0.35

    ramp   = N.new('ShaderNodeValToRGB');    ramp.location   = (100, 0)
    els = ramp.color_ramp.elements
    els[0].position = 0.35;  els[0].color = (0.72, 0.58, 0.42, 1)   # darker grain
    els[1].position = 0.65;  els[1].color = (0.92, 0.82, 0.66, 1)   # light balsa

    bsdf   = N.new('ShaderNodeBsdfPrincipled'); bsdf.location = (400, 0)
    bsdf.inputs['Roughness'].default_value = 0.55
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    bsdf.inputs['Sheen Weight'].default_value = 0.05

    out    = N.new('ShaderNodeOutputMaterial'); out.location  = (700, 0)

    L.new(coord.outputs['Object'],  mapn.inputs['Vector'])
    L.new(mapn.outputs['Vector'],   noise.inputs['Vector'])
    L.new(mapn.outputs['Vector'],   wave.inputs['Vector'])
    L.new(noise.outputs['Fac'],     mix.inputs['Color1'])
    L.new(wave.outputs['Color'],    mix.inputs['Color2'])
    L.new(mix.outputs['Color'],     ramp.inputs['Fac'])
    L.new(ramp.outputs['Color'],    bsdf.inputs['Base Color'])
    L.new(bsdf.outputs['BSDF'],    out.inputs['Surface'])
    return mat


def mat_balsa_brace():
    """Slightly warmer tone for braces (so they stand out)."""
    mat = bpy.data.materials.new("Balsa_Brace")
    mat.use_nodes = True
    N = mat.node_tree.nodes
    N.clear()
    bsdf = N.new('ShaderNodeBsdfPrincipled'); bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.88, 0.72, 0.50, 1)
    bsdf.inputs['Roughness'].default_value = 0.50
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    out  = N.new('ShaderNodeOutputMaterial');  out.location  = (300, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def mat_bridge():
    """Darker accent for bridge elements."""
    mat = bpy.data.materials.new("Bridge_Material")
    mat.use_nodes = True
    N = mat.node_tree.nodes
    N.clear()
    bsdf = N.new('ShaderNodeBsdfPrincipled'); bsdf.location = (0, 0)
    bsdf.inputs['Base Color'].default_value = (0.65, 0.50, 0.35, 1)
    bsdf.inputs['Roughness'].default_value = 0.45
    bsdf.inputs['Specular IOR Level'].default_value = 0.35
    out  = N.new('ShaderNodeOutputMaterial');  out.location  = (300, 0)
    mat.node_tree.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
    return mat


def mat_floor_surface():
    """Dark reflective studio floor."""
    mat = bpy.data.materials.new("Studio_Floor")
    mat.use_nodes = True
    N = mat.node_tree.nodes
    bsdf = N.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.025, 0.025, 0.025, 1)
    bsdf.inputs['Roughness'].default_value = 0.10
    bsdf.inputs['Specular IOR Level'].default_value = 0.9
    return mat


# ═══════════════════════════════════════════════════════════════════
#  BUILD 3-D MODEL
# ═══════════════════════════════════════════════════════════════════
def build_model(m_frame, m_brace, m_bridge):
    """Read CSV, create box-section sticks for every element."""
    print("[MODEL] Reading CSV data …")
    nodes = {}
    with open(CSV_POS, 'r') as f:
        for row in csv.DictReader(f):
            nid = int(row['node_id'])
            nodes[nid] = Vector((float(row['x'])*SCALE,
                                 float(row['y'])*SCALE,
                                 float(row['z'])*SCALE))

    col = bpy.data.collections.new("TwinTowers_V10")
    bpy.context.scene.collection.children.link(col)

    count = 0
    with open(CSV_CONN, 'r') as f:
        for row in csv.DictReader(f):
            ni, nj = int(row['node_i']), int(row['node_j'])
            etype  = row['element_type']
            if ni not in nodes or nj not in nodes:
                continue

            p1, p2 = nodes[ni], nodes[nj]
            mid = (p1 + p2) / 2
            diff = p2 - p1
            length = diff.length
            if length < 1e-5:
                continue

            # choose section & material
            if 'bridge' in etype:
                w, d, mat = SECTION, SECTION, m_bridge
            elif 'brace' in etype:
                w, d, mat = BRACE_SEC, BRACE_SEC, m_brace
            else:
                w, d, mat = SECTION, SECTION, m_frame

            # create box stick
            bpy.ops.mesh.primitive_cube_add(size=1, location=mid)
            obj = bpy.context.active_object
            obj.name = f"{etype}_{count}"
            obj.scale = (w, d, length)

            quat = diff.to_track_quat('Z', 'Y')
            obj.rotation_euler = quat.to_euler()

            obj.data.materials.append(mat)

            # move to collection
            for c in obj.users_collection:
                c.objects.unlink(obj)
            col.objects.link(obj)

            count += 1
            if count % 500 == 0:
                print(f"  … {count} elements")

    print(f"[MODEL] {count} elements created.")

    # apply transforms
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)
    if col.objects:
        bpy.context.view_layer.objects.active = col.objects[0]
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)

    return col


# ═══════════════════════════════════════════════════════════════════
#  LIGHTING  (3-point + environment)
# ═══════════════════════════════════════════════════════════════════
def setup_lighting():
    scene = bpy.context.scene
    target_loc = (CX, CY, CZ)

    # --- Sun (key) ---
    sun = bpy.data.lights.new("Key_Sun", 'SUN')
    sun.energy = 3.5
    sun.angle = math.radians(1.5)          # soft shadow
    sun.color = (1.0, 0.97, 0.93)          # warm
    sun_o = bpy.data.objects.new("Key_Sun", sun)
    scene.collection.objects.link(sun_o)
    sun_o.rotation_euler = Euler((math.radians(55), math.radians(10), math.radians(35)))

    # --- Fill (large area) ---
    fill = bpy.data.lights.new("Fill_Area", 'AREA')
    fill.energy = 250
    fill.size = 8;  fill.color = (0.93, 0.96, 1.0)
    fill_o = bpy.data.objects.new("Fill_Area", fill)
    scene.collection.objects.link(fill_o)
    fill_o.location = (CX - 4, CY - 3, CZ + 0.5)
    _track(fill_o, target_loc, scene)

    # --- Rim (backlight) ---
    rim = bpy.data.lights.new("Rim_Light", 'AREA')
    rim.energy = 350;  rim.size = 5;  rim.color = (1.0, 0.94, 0.88)
    rim_o = bpy.data.objects.new("Rim_Light", rim)
    scene.collection.objects.link(rim_o)
    rim_o.location = (CX + 3.5, CY + 4, CZ + 0.8)
    _track(rim_o, target_loc, scene)

    # --- Ambient fill (subtle top) ---
    top = bpy.data.lights.new("Top_Fill", 'AREA')
    top.energy = 120;  top.size = 12
    top_o = bpy.data.objects.new("Top_Fill", top)
    scene.collection.objects.link(top_o)
    top_o.location = (CX, CY, CZ + 5)
    top_o.rotation_euler = (0, 0, 0)

    # --- World (gradient HDRI-style) ---
    world = bpy.data.worlds.new("Studio_Env")
    scene.world = world
    world.use_nodes = True
    wN = world.node_tree.nodes;  wL = world.node_tree.links
    wN.clear()

    coord  = wN.new('ShaderNodeTexCoord');   coord.location  = (-700, 0)
    mapn   = wN.new('ShaderNodeMapping');     mapn.location   = (-500, 0)
    mapn.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    grad   = wN.new('ShaderNodeTexGradient'); grad.location   = (-300, 0)
    ramp   = wN.new('ShaderNodeValToRGB');    ramp.location   = (-100, 0)
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.015, 0.015, 0.02, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.06, 0.065, 0.08, 1)
    bg     = wN.new('ShaderNodeBackground'); bg.location = (100, 0)
    bg.inputs['Strength'].default_value = 0.8
    out    = wN.new('ShaderNodeOutputWorld'); out.location = (300, 0)
    wL.new(coord.outputs['Generated'], mapn.inputs['Vector'])
    wL.new(mapn.outputs['Vector'],     grad.inputs['Vector'])
    wL.new(grad.outputs['Color'],      ramp.inputs['Fac'])
    wL.new(ramp.outputs['Color'],      bg.inputs['Color'])
    wL.new(bg.outputs['Background'],   out.inputs['Surface'])

    # --- Studio floor ---
    bpy.ops.mesh.primitive_plane_add(size=30, location=(CX, CY, -0.0005))
    floor = bpy.context.active_object
    floor.name = "Studio_Floor"
    floor.data.materials.append(mat_floor_surface())

    print("[LIGHT] 3-point + environment + floor ready.")


def _track(obj, target_loc, scene):
    """Make *obj* track toward *target_loc* via an empty."""
    tgt = bpy.data.objects.new(f"Tgt_{obj.name}", None)
    scene.collection.objects.link(tgt)
    tgt.location = target_loc
    c = obj.constraints.new('TRACK_TO')
    c.target = tgt;  c.track_axis = 'TRACK_NEGATIVE_Z';  c.up_axis = 'UP_Y'


# ═══════════════════════════════════════════════════════════════════
#  GPU / RENDER SETTINGS
# ═══════════════════════════════════════════════════════════════════
def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'

    # --- GPU ---
    prefs = bpy.context.preferences
    cp = prefs.addons.get('cycles')
    gpu_ok = False
    if cp:
        for ct in ('CUDA', 'OPTIX', 'HIP', 'METAL', 'ONEAPI'):  # CUDA first — OptiX fails in WSL2
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
    cy.use_denoising = USE_DENOISE
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = 0.01

    scene.render.resolution_x = RES_X
    scene.render.resolution_y = RES_Y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.render.image_settings.compression = 15
    scene.render.film_transparent = False       # solid bg by default

    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.3

    print(f"[RENDER] {RES_X}×{RES_Y}, {SAMPLES} spp, device={cy.device}")


# ═══════════════════════════════════════════════════════════════════
#  MULTI-ANGLE RENDER
# ═══════════════════════════════════════════════════════════════════
def render_all_views():
    """Place camera at each preset and render to PNG."""
    scene = bpy.context.scene
    os.makedirs(RENDER_DIR, exist_ok=True)

    # create a single camera object we'll reposition
    cam_data = bpy.data.cameras.new("RenderCam")
    cam_obj  = bpy.data.objects.new("RenderCam", cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    cam_data.dof.use_dof = False   # no depth-of-field for architectural shots

    # Target empty for TRACK_TO
    cam_tgt = bpy.data.objects.new("CamTarget", None)
    scene.collection.objects.link(cam_tgt)
    tc = cam_obj.constraints.new('TRACK_TO')
    tc.target = cam_tgt
    tc.track_axis = 'TRACK_NEGATIVE_Z'
    tc.up_axis = 'UP_Y'

    for name, loc, tgt, lens, ortho in CAMERAS:
        print(f"\n>>> Rendering view: {name}")
        cam_obj.location = Vector(loc)
        cam_tgt.location = Vector(tgt)
        cam_data.lens = lens

        if ortho is not None:
            cam_data.type = 'ORTHO'
            cam_data.ortho_scale = ortho
        else:
            cam_data.type = 'PERSP'

        # DOF only for hero / detail shots
        if 'hero' in name or 'detail' in name:
            cam_data.dof.use_dof = True
            cam_data.dof.focus_object = cam_tgt
            cam_data.dof.aperture_fstop = 2.8
        else:
            cam_data.dof.use_dof = False

        # transparent bg for ortho section views
        if 'section' in name:
            scene.render.film_transparent = True
        else:
            scene.render.film_transparent = False

        outpath = os.path.join(RENDER_DIR, name)
        scene.render.filepath = outpath
        bpy.ops.render.render(write_still=True)
        print(f"    Saved: {outpath}.png")

    print(f"\n[DONE] {len(CAMERAS)} views rendered to {RENDER_DIR}")


# ═══════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════
def main():
    # Check cache
    if os.path.exists(BLEND_CACHE):
        print(f"[CACHE] Loading {BLEND_CACHE}")
        bpy.ops.wm.open_mainfile(filepath=BLEND_CACHE)
        setup_render()
    else:
        print("[BUILD] Creating scene from scratch …")
        cleanup()

        print("\n[1/4] Materials …")
        mf = mat_balsa_frame()
        mb = mat_balsa_brace()
        mbr = mat_bridge()

        print("[2/4] Building model …")
        build_model(mf, mb, mbr)

        print("[3/4] Lighting …")
        setup_lighting()

        print("[4/4] Render settings …")
        setup_render()

        # Save .blend cache
        os.makedirs(os.path.dirname(BLEND_CACHE), exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_CACHE)
        print(f"[CACHE] Saved → {BLEND_CACHE}")

    # Render all views
    render_all_views()

    print("\n" + "=" * 60)
    print("ALL RENDERS COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
