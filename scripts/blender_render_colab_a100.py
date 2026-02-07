"""
Twin Towers 360° Render - A100 40GB Optimized for Google Colab
==============================================================
Optimized settings to utilize ~90% of A100 40GB GPU:
- High resolution (4K)
- High sample count with fast denoising
- CUDA compute (A100 has no RT cores, so CUDA > OPTIX)
- Persistent data for animation (keeps BVH in VRAM)
- Large memory buffers
- No part-by-part rendering - full frame GPU utilization
"""

import bpy
import bmesh
import csv
import math
import os

# ==============================================================================
# PATHS (relative to script location)
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CSV_POS_PATH = os.path.join(BASE_DIR, 'data', 'twin_position_matrix.csv')
CSV_CONN_PATH = os.path.join(BASE_DIR, 'data', 'twin_connectivity_matrix.csv')
BLEND_CACHE_PATH = os.path.join(BASE_DIR, 'results', 'twin_towers_a100_cached.blend')
OUTPUT_VIDEO = os.path.join(BASE_DIR, 'results', 'visualizations', 'twin_towers_360_8k.mp4')

# ==============================================================================
# A100 OPTIMIZED SETTINGS
# ==============================================================================
MODEL_SCALE = 0.01
FRAME_SIZE = 0.006

# Animation
TOTAL_FRAMES = 360        # Full 360 degrees
FPS = 30                  # Smooth playback
CAMERA_RADIUS = 3.0
CAMERA_HEIGHT = 1.2

# =============================================================================
# A100 40GB GPU OPTIMIZED RENDER SETTINGS
# =============================================================================
# With 40GB VRAM, we can push much higher settings

# Resolution - 8K to actually stress the A100 (4K is too easy)
RESOLUTION_X = 7680
RESOLUTION_Y = 4320

# Samples - Much higher since A100 is extremely fast
# This will create more GPU work and push utilization up
RENDER_SAMPLES = 512

# Denoising will clean up noise efficiently
USE_DENOISER = True

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()

    for c in list(bpy.data.collections):
        bpy.data.collections.remove(c)
    for m in list(bpy.data.materials):
        bpy.data.materials.remove(m)
    for l in list(bpy.data.lights):
        bpy.data.lights.remove(l)
    for c in list(bpy.data.cameras):
        bpy.data.cameras.remove(c)
    for mesh in list(bpy.data.meshes):
        bpy.data.meshes.remove(mesh)

# ==============================================================================
# MATERIALS (High quality PBR)
# ==============================================================================
def create_materials():
    mats = {}

    # Balsa Wood Material with subsurface scattering
    mat = bpy.data.materials.new(name="Balsa_Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    # Texture Coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)

    # Mapping
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Scale'].default_value = (15, 15, 15)

    # Noise for wood grain
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-200, 100)
    noise.inputs['Scale'].default_value = 80
    noise.inputs['Detail'].default_value = 10
    noise.inputs['Roughness'].default_value = 0.6

    # Second noise for micro variation
    noise2 = nodes.new(type='ShaderNodeTexNoise')
    noise2.location = (-200, -100)
    noise2.inputs['Scale'].default_value = 200
    noise2.inputs['Detail'].default_value = 4

    # Color Ramp for main grain
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (0, 100)
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.70, 0.55, 0.38, 1)
    ramp.color_ramp.elements[1].position = 0.65
    ramp.color_ramp.elements[1].color = (0.90, 0.78, 0.62, 1)

    # Roughness ramp
    ramp_rough = nodes.new(type='ShaderNodeValToRGB')
    ramp_rough.location = (0, -100)
    ramp_rough.color_ramp.elements[0].color = (0.55, 0.55, 0.55, 1)
    ramp_rough.color_ramp.elements[1].color = (0.75, 0.75, 0.75, 1)

    # BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    bsdf.inputs['Roughness'].default_value = 0.6
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    # Subtle subsurface for wood
    bsdf.inputs['Subsurface Weight'].default_value = 0.05
    bsdf.inputs['Subsurface Radius'].default_value = (0.1, 0.05, 0.02)

    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)

    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(noise2.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])

    mats['wood'] = mat
    return mats

# ==============================================================================
# BUILD MODEL AS SINGLE MESH (Memory efficient for GPU)
# ==============================================================================
def build_model_optimized(mats):
    """Build entire model as a single mesh using bmesh - GPU friendly"""
    print("Loading Data from CSV files...")

    nodes = {}
    with open(CSV_POS_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nid = int(row['node_id'])
            x = float(row['x']) * MODEL_SCALE
            y = float(row['y']) * MODEL_SCALE
            z = float(row['z']) * MODEL_SCALE
            nodes[nid] = (x, y, z)

    print(f"  Loaded {len(nodes)} nodes")

    bm = bmesh.new()
    element_count = 0

    def add_beam_to_bmesh(bm, p1, p2, width, depth):
        import mathutils

        x1, y1, z1 = p1
        x2, y2, z2 = p2

        dx, dy, dz = x2-x1, y2-y1, z2-z1
        length = math.sqrt(dx*dx + dy*dy + dz*dz)

        if length < 0.0001:
            return

        hw = width / 2
        hd = depth / 2
        hl = length / 2

        verts = [
            (-hw, -hd, -hl), ( hw, -hd, -hl), ( hw,  hd, -hl), (-hw,  hd, -hl),
            (-hw, -hd,  hl), ( hw, -hd,  hl), ( hw,  hd,  hl), (-hw,  hd,  hl),
        ]

        vec = mathutils.Vector((dx, dy, dz))
        quat = vec.to_track_quat('Z', 'Y')
        rot_mat = quat.to_matrix().to_4x4()

        cx, cy, cz = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
        trans_mat = mathutils.Matrix.Translation((cx, cy, cz))
        transform = trans_mat @ rot_mat

        bm_verts = []
        for v in verts:
            co = transform @ mathutils.Vector(v)
            bm_verts.append(bm.verts.new(co))

        bm.faces.new([bm_verts[0], bm_verts[1], bm_verts[2], bm_verts[3]])
        bm.faces.new([bm_verts[4], bm_verts[7], bm_verts[6], bm_verts[5]])
        bm.faces.new([bm_verts[0], bm_verts[4], bm_verts[5], bm_verts[1]])
        bm.faces.new([bm_verts[1], bm_verts[5], bm_verts[6], bm_verts[2]])
        bm.faces.new([bm_verts[2], bm_verts[6], bm_verts[7], bm_verts[3]])
        bm.faces.new([bm_verts[3], bm_verts[7], bm_verts[4], bm_verts[0]])

    with open(CSV_CONN_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nid1, nid2 = int(row['node_i']), int(row['node_j'])
            etype = row['element_type']

            if nid1 not in nodes or nid2 not in nodes:
                continue

            p1 = nodes[nid1]
            p2 = nodes[nid2]

            if 'shear_wall' in etype:
                add_beam_to_bmesh(bm, p1, p2, 0.006, 0.003)
            else:
                add_beam_to_bmesh(bm, p1, p2, 0.006, 0.006)

            element_count += 1

    print(f"  Total: {element_count} elements")

    mesh = bpy.data.meshes.new("TwinTowers_Mesh")
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("TwinTowers", mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.data.materials.append(mats['wood'])

    for poly in obj.data.polygons:
        poly.use_smooth = False

    print("  Model built as single mesh (GPU optimized)")
    return obj

# ==============================================================================
# LIGHTING (Studio quality)
# ==============================================================================
def setup_lighting():
    scene = bpy.context.scene
    center = (0.15, 0.08, 0.75)

    target = bpy.data.objects.new("Target", None)
    scene.collection.objects.link(target)
    target.location = center

    # Key Light (Sun)
    sun_data = bpy.data.lights.new(name="Sun", type='SUN')
    sun_data.energy = 5
    sun_data.angle = math.radians(0.5)
    sun_data.color = (1.0, 0.98, 0.95)
    sun_obj = bpy.data.objects.new(name="Sun", object_data=sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(55), math.radians(10), math.radians(35))

    # Fill Light (Large soft area)
    fill_data = bpy.data.lights.new(name="Fill", type='AREA')
    fill_data.energy = 400
    fill_data.size = 8
    fill_data.color = (0.95, 0.97, 1.0)
    fill_obj = bpy.data.objects.new(name="Fill", object_data=fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.location = (-4, -3, 2.5)

    cons = fill_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'

    # Rim Light (Back/edge definition)
    rim_data = bpy.data.lights.new(name="Rim", type='AREA')
    rim_data.energy = 500
    rim_data.size = 5
    rim_data.color = (1.0, 0.95, 0.9)
    rim_obj = bpy.data.objects.new(name="Rim", object_data=rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.location = (4, 4, 2.5)

    cons2 = rim_obj.constraints.new(type='TRACK_TO')
    cons2.target = target
    cons2.track_axis = 'TRACK_NEGATIVE_Z'
    cons2.up_axis = 'UP_Y'

    # Top Light
    top_data = bpy.data.lights.new(name="Top", type='AREA')
    top_data.energy = 200
    top_data.size = 12
    top_obj = bpy.data.objects.new(name="Top", object_data=top_data)
    scene.collection.objects.link(top_obj)
    top_obj.location = (0, 0, 5)

    # World/Environment
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()

    # Gradient background
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.inputs['Rotation'].default_value = (math.radians(90), 0, 0)

    gradient = nodes.new(type='ShaderNodeTexGradient')
    gradient.gradient_type = 'LINEAR'

    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].position = 0.25
    ramp.color_ramp.elements[0].color = (0.015, 0.015, 0.025, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.06, 0.06, 0.10, 1)

    bg = nodes.new(type='ShaderNodeBackground')
    bg.inputs['Strength'].default_value = 1.0

    output = nodes.new(type='ShaderNodeOutputWorld')

    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])

    # Reflective floor
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Floor"

    mat_floor = bpy.data.materials.new(name="Floor")
    mat_floor.use_nodes = True
    bsdf = mat_floor.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    bsdf.inputs['Roughness'].default_value = 0.08
    bsdf.inputs['Specular IOR Level'].default_value = 1.0
    floor.data.materials.append(mat_floor)

    return target

# ==============================================================================
# CAMERA ANIMATION
# ==============================================================================
def setup_camera(target):
    scene = bpy.context.scene

    cam_data = bpy.data.cameras.new(name='Camera')
    cam_data.lens = 50
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 5.6

    cam_obj = bpy.data.objects.new(name='Camera', object_data=cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj

    orbit = bpy.data.objects.new("OrbitCenter", None)
    scene.collection.objects.link(orbit)
    orbit.location = target.location

    cam_obj.parent = orbit
    cam_obj.location = (CAMERA_RADIUS, 0, CAMERA_HEIGHT - target.location[2])

    cons = cam_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'

    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES
    scene.render.fps = FPS

    orbit.rotation_euler = (0, 0, 0)
    orbit.keyframe_insert(data_path="rotation_euler", frame=1)

    orbit.rotation_euler = (0, 0, math.radians(360))
    orbit.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)

    if orbit.animation_data and orbit.animation_data.action:
        for fcurve in orbit.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'

    return cam_obj

# ==============================================================================
# A100 GPU SETUP - MAXIMUM UTILIZATION
# ==============================================================================
def setup_gpu_a100():
    """
    Configure GPU rendering optimized for A100 40GB.
    A100 has no RT cores, so CUDA is preferred over OptiX.
    """
    import subprocess

    print("\n" + "="*60)
    print("A100 40GB GPU CONFIGURATION")
    print("="*60)

    # Check GPU
    try:
        result = subprocess.run(
            ['nvidia-smi', '--query-gpu=name,memory.total,memory.free,utilization.gpu',
             '--format=csv,noheader'],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            print(f"GPU Detected: {result.stdout.strip()}")
    except Exception as e:
        print(f"nvidia-smi check: {e}")

    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons.get('cycles')

    if not cycles_prefs:
        print("ERROR: Cycles addon not found!")
        return False

    cprefs = cycles_prefs.preferences

    # A100 optimization: Use CUDA (no RT cores, so CUDA = OptiX performance)
    # CUDA is more stable in headless/Colab environments
    compute_priority = ['CUDA', 'OPTIX']
    gpu_found = False

    for compute_type in compute_priority:
        try:
            cprefs.compute_device_type = compute_type
            cprefs.get_devices()

            devices = cprefs.devices
            gpu_devices = [d for d in devices if d.type != 'CPU']

            if gpu_devices:
                for device in devices:
                    if device.type != 'CPU':
                        device.use = True
                        print(f"  ENABLED: {device.name} ({compute_type})")
                    else:
                        device.use = False  # Disable CPU - use only GPU

                gpu_found = True
                print(f"  Compute Type: {compute_type}")
                break

        except Exception as e:
            print(f"  {compute_type} failed: {e}")
            continue

    if not gpu_found:
        print("  WARNING: No GPU found, using CPU")
        cprefs.compute_device_type = 'NONE'
        for device in cprefs.devices:
            device.use = (device.type == 'CPU')

    return gpu_found

# ==============================================================================
# RENDER SETTINGS - A100 OPTIMIZED
# ==============================================================================
def setup_render_a100():
    """
    Configure Cycles for maximum A100 utilization (~90% GPU usage).

    Key optimizations:
    1. DISABLE auto-tiling - render entire frame at once
    2. Persistent data - keep BVH in VRAM between frames
    3. High memory limit - use all 40GB VRAM
    4. Path guiding - more GPU compute
    5. Higher samples and resolution
    """
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'

    # Setup GPU
    print("\n[GPU] Configuring A100 for maximum utilization...")
    gpu_enabled = setup_gpu_a100()

    cycles = scene.cycles

    # =========================================================================
    # CORE SETTINGS FOR ~90% GPU UTILIZATION
    # =========================================================================

    # 1. Device - GPU only
    cycles.device = 'GPU' if gpu_enabled else 'CPU'

    # 2. Samples - Much higher to stress the GPU
    cycles.samples = RENDER_SAMPLES

    # 3. DISABLE ADAPTIVE SAMPLING - Force all samples for more GPU work
    # Adaptive sampling terminates early on simple areas, reducing GPU load
    cycles.use_adaptive_sampling = False

    # 4. Denoising - GPU accelerated
    cycles.use_denoising = USE_DENOISER
    cycles.denoiser = 'OPTIX' if gpu_enabled else 'OPENIMAGEDENOISE'
    cycles.denoising_input_passes = 'RGB_ALBEDO_NORMAL'

    # 5. PERSISTENT DATA - CRITICAL FOR ANIMATION
    cycles.use_persistent_data = True

    # 6. PATH GUIDING - Adds significant GPU compute load
    try:
        cycles.use_guiding = True
        cycles.guiding_training_samples = 128
        cycles.use_surface_guiding = True
        cycles.use_volume_guiding = True
        cycles.guiding_distribution_type = 'PARALLAX_AWARE_VMM'
    except:
        print("  Path guiding not available")

    # 7. Light paths - INCREASE for more bounces = more GPU work
    cycles.max_bounces = 12
    cycles.diffuse_bounces = 6
    cycles.glossy_bounces = 6
    cycles.transmission_bounces = 12
    cycles.volume_bounces = 2
    cycles.transparent_max_bounces = 12

    # 8. DISABLE AUTO-TILING - Render entire frame at once
    # This is the KEY setting to eliminate "Rendered X/4 Tiles"
    try:
        # Blender 4.x setting
        scene.cycles.use_auto_tile = False
        print("  Auto-tiling DISABLED - full frame rendering")
    except:
        pass

    # Force large tile size as fallback
    try:
        cycles.tile_size = 8192  # Larger than frame = single tile
    except:
        pass

    # 9. Use more memory for faster BVH
    try:
        cycles.debug_use_spatial_splits = True
        cycles.debug_bvh_time_steps = 4
    except:
        pass

    # 10. Scrambling distance for better sampling (Blender 4.x)
    try:
        cycles.auto_scrambling_distance = False
        cycles.scrambling_distance = 1.0  # Maximum quality
    except:
        pass

    # =========================================================================
    # OUTPUT SETTINGS
    # =========================================================================

    # Resolution - 4K
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100

    # Video output - H.264 high quality
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.ffmpeg.gopsize = 18
    scene.render.filepath = OUTPUT_VIDEO

    # Disable motion blur (faster, cleaner for architecture)
    scene.render.use_motion_blur = False

    # Color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0

    # =========================================================================
    # STATUS REPORT
    # =========================================================================
    print("\n" + "="*60)
    print("A100 RENDER CONFIGURATION - MAXIMUM GPU UTILIZATION")
    print("="*60)
    print(f"  Device:              {cycles.device}")
    print(f"  Resolution:          {RESOLUTION_X}x{RESOLUTION_Y} (8K)")
    print(f"  Samples:             {cycles.samples}")
    print(f"  Adaptive Sampling:   {cycles.use_adaptive_sampling} (DISABLED for max GPU)")
    print(f"  Denoiser:            {cycles.denoiser}")
    print(f"  Persistent Data:     {cycles.use_persistent_data}")
    print(f"  Max Bounces:         {cycles.max_bounces}")
    try:
        print(f"  Path Guiding:        {cycles.use_guiding}")
        print(f"  Auto-Tiling:         {scene.cycles.use_auto_tile}")
    except:
        pass
    print(f"  Frames:              {TOTAL_FRAMES} @ {FPS}fps")
    print("="*60)

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    import sys

    # Check for --force-rebuild flag
    force_rebuild = '--force-rebuild' in sys.argv or '-f' in sys.argv

    if os.path.exists(BLEND_CACHE_PATH) and not force_rebuild:
        print(f"Loading cached scene: {BLEND_CACHE_PATH}")
        print("  (Use --force-rebuild or -f to rebuild from scratch)")
        bpy.ops.wm.open_mainfile(filepath=BLEND_CACHE_PATH)
        setup_render_a100()
    else:
        if force_rebuild and os.path.exists(BLEND_CACHE_PATH):
            print("Force rebuild requested - ignoring cache")
        print("Building scene from scratch...")
        cleanup()

        print("\n[1/4] Creating materials...")
        mats = create_materials()

        print("\n[2/4] Building model (single mesh for GPU)...")
        model = build_model_optimized(mats)

        print("\n[3/4] Setting up lighting...")
        target = setup_lighting()

        print("\n[4/4] Setting up camera...")
        setup_camera(target)
        setup_render_a100()

        # Save cache
        os.makedirs(os.path.dirname(BLEND_CACHE_PATH), exist_ok=True)
        print(f"\nSaving cache: {BLEND_CACHE_PATH}")
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_CACHE_PATH)

    print("\n" + "="*60)
    print("STARTING A100 OPTIMIZED RENDER")
    print("="*60)
    print(f"Output: {OUTPUT_VIDEO}")
    print(f"Resolution: {RESOLUTION_X}x{RESOLUTION_Y}")
    print(f"Frames: {TOTAL_FRAMES} @ {FPS}fps = {TOTAL_FRAMES/FPS:.1f}s video")
    print("\nExpected GPU utilization: ~90%")
    print("Monitor with: nvidia-smi -l 1")
    print("="*60 + "\n")

    bpy.ops.render.render(animation=True)

    print(f"\nRender complete! Video saved to: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    main()
