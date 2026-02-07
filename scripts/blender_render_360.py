"""
Twin Towers 360° Rotation Render Script
========================================
- Caches loaded model as .blend file for faster subsequent runs
- 360° camera rotation animation
- D5-level lighting and materials
- High quality Cycles render
"""

import bpy
import csv
import math
import os
import sys

# ==============================================================================
# PATHS (relative to script location)
# ==============================================================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent of scripts/ folder
CSV_POS_PATH = os.path.join(BASE_DIR, 'data', 'twin_position_matrix.csv')
CSV_CONN_PATH = os.path.join(BASE_DIR, 'data', 'twin_connectivity_matrix.csv')
BLEND_CACHE_PATH = os.path.join(BASE_DIR, 'results', 'twin_towers_cached.blend')
OUTPUT_DIR = os.path.join(BASE_DIR, 'results', 'visualizations', '360_render')
OUTPUT_VIDEO = os.path.join(BASE_DIR, 'results', 'visualizations', 'twin_towers_360.mp4')

# ==============================================================================
# SETTINGS
# ==============================================================================
MODEL_SCALE = 0.01  # cm to meters
FRAME_SIZE = 0.006  # 6mm frame members

# Animation
TOTAL_FRAMES = 360  # 360 frames = 360 degrees
FPS = 30
CAMERA_RADIUS = 3.0  # Distance from center
CAMERA_HEIGHT = 1.2  # Camera Z position

# Render Quality
RENDER_SAMPLES = 256  # High quality
RESOLUTION_X = 1920
RESOLUTION_Y = 1080

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup():
    """Remove all objects and data"""
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

# ==============================================================================
# D5-STYLE MATERIALS
# ==============================================================================
def create_materials():
    """Create photorealistic balsa wood materials"""
    mats = {}
    
    # --- Balsa Frame Material (D5-style wood) ---
    mat_frame = bpy.data.materials.new(name="Balsa_Frame")
    mat_frame.use_nodes = True
    nodes = mat_frame.node_tree.nodes
    links = mat_frame.node_tree.links
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (300, 0)
    
    # Texture Coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    # Mapping for scale
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-400, 0)
    mapping.inputs['Scale'].default_value = (20, 20, 20)
    
    # Wood grain noise
    noise1 = nodes.new(type='ShaderNodeTexNoise')
    noise1.location = (-200, 100)
    noise1.inputs['Scale'].default_value = 150
    noise1.inputs['Detail'].default_value = 8
    noise1.inputs['Roughness'].default_value = 0.6
    
    # Second noise for variation
    noise2 = nodes.new(type='ShaderNodeTexNoise')
    noise2.location = (-200, -100)
    noise2.inputs['Scale'].default_value = 50
    noise2.inputs['Detail'].default_value = 4
    
    # Color ramp for wood grain
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (0, 100)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (0.75, 0.60, 0.45, 1)  # Darker grain
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (0.90, 0.78, 0.62, 1)  # Light balsa
    
    # Roughness ramp
    ramp_rough = nodes.new(type='ShaderNodeValToRGB')
    ramp_rough.location = (0, -100)
    ramp_rough.color_ramp.elements[0].color = (0.5, 0.5, 0.5, 1)
    ramp_rough.color_ramp.elements[1].color = (0.7, 0.7, 0.7, 1)
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (600, 0)
    
    # Connect nodes
    links.new(tex_coord.outputs['Object'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise1.inputs['Vector'])
    links.new(mapping.outputs['Vector'], noise2.inputs['Vector'])
    links.new(noise1.outputs['Fac'], ramp.inputs['Fac'])
    links.new(noise2.outputs['Fac'], ramp_rough.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(ramp_rough.outputs['Color'], bsdf.inputs['Roughness'])
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    mats['frame'] = mat_frame
    
    # --- Panel Material (slightly different tone) ---
    mat_panel = bpy.data.materials.new(name="Balsa_Panel")
    mat_panel.use_nodes = True
    nodes_p = mat_panel.node_tree.nodes
    links_p = mat_panel.node_tree.links
    nodes_p.clear()
    
    bsdf_p = nodes_p.new(type='ShaderNodeBsdfPrincipled')
    bsdf_p.location = (0, 0)
    bsdf_p.inputs['Base Color'].default_value = (0.82, 0.72, 0.58, 1)
    bsdf_p.inputs['Roughness'].default_value = 0.65
    bsdf_p.inputs['Specular IOR Level'].default_value = 0.25
    
    output_p = nodes_p.new(type='ShaderNodeOutputMaterial')
    output_p.location = (300, 0)
    links_p.new(bsdf_p.outputs['BSDF'], output_p.inputs['Surface'])
    
    mats['panel'] = mat_panel
    
    return mats

# ==============================================================================
# LOAD DATA AND BUILD MODEL
# ==============================================================================
def load_data_and_build(mats):
    """Load CSV data and create 3D geometry"""
    print("Loading Data from CSV files...")
    
    # Read nodes
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
    
    # Create collection
    col = bpy.data.collections.new("TwinTowers")
    bpy.context.scene.collection.children.link(col)
    
    # Helper function
    def create_stick(p1, p2, width, depth, mat_name, name):
        import mathutils
        
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        
        cx, cy, cz = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
        dx, dy, dz = x2-x1, y2-y1, z2-z1
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if length < 0.0001:
            return None
        
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
        obj = bpy.context.active_object
        obj.name = name
        obj.scale = (width, depth, length)
        
        vec = mathutils.Vector((dx, dy, dz))
        quat = vec.to_track_quat('Z', 'Y')
        obj.rotation_euler = quat.to_euler()
        
        if obj.data.materials:
            obj.data.materials[0] = mats[mat_name]
        else:
            obj.data.materials.append(mats[mat_name])
        
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        
        return obj
    
    # Read elements and create geometry
    element_count = 0
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
                create_stick(p1, p2, 0.006, 0.003, 'panel', f"panel_{element_count}")
            else:
                create_stick(p1, p2, 0.006, 0.006, 'frame', f"frame_{element_count}")
            
            element_count += 1
            
            if element_count % 500 == 0:
                print(f"  Created {element_count} elements...")
    
    print(f"  Total: {element_count} elements created")
    
    # Apply transforms for better performance
    bpy.ops.object.select_all(action='DESELECT')
    for obj in col.objects:
        obj.select_set(True)
    if col.objects:
        bpy.context.view_layer.objects.active = col.objects[0]
        bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    
    return col

# ==============================================================================
# D5-STYLE LIGHTING SETUP
# ==============================================================================
def setup_d5_lighting():
    """Create professional studio lighting like D5 Render"""
    scene = bpy.context.scene
    
    # Model center (approximate)
    center = (0.15, 0.08, 0.75)
    
    # --- Key Light (Main Sun) ---
    sun_data = bpy.data.lights.new(name="Key_Sun", type='SUN')
    sun_data.energy = 4
    sun_data.angle = math.radians(1)  # Soft sun
    sun_data.color = (1.0, 0.98, 0.95)  # Slightly warm
    sun_obj = bpy.data.objects.new(name="Key_Sun", object_data=sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))
    
    # --- Fill Light (Large Area) ---
    fill_data = bpy.data.lights.new(name="Fill_Area", type='AREA')
    fill_data.energy = 300
    fill_data.size = 8
    fill_data.color = (0.95, 0.97, 1.0)  # Slightly cool
    fill_obj = bpy.data.objects.new(name="Fill_Area", object_data=fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.location = (-4, -3, 2.5)
    
    # Track to center
    target = bpy.data.objects.new("LightTarget", None)
    scene.collection.objects.link(target)
    target.location = center
    
    cons = fill_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'
    
    # --- Rim Light (Back light for depth) ---
    rim_data = bpy.data.lights.new(name="Rim_Light", type='AREA')
    rim_data.energy = 400
    rim_data.size = 4
    rim_data.color = (1.0, 0.95, 0.9)
    rim_obj = bpy.data.objects.new(name="Rim_Light", object_data=rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.location = (3, 4, 2)
    
    cons2 = rim_obj.constraints.new(type='TRACK_TO')
    cons2.target = target
    cons2.track_axis = 'TRACK_NEGATIVE_Z'
    cons2.up_axis = 'UP_Y'
    
    # --- Top Light (Soft overhead) ---
    top_data = bpy.data.lights.new(name="Top_Light", type='AREA')
    top_data.energy = 150
    top_data.size = 10
    top_obj = bpy.data.objects.new(name="Top_Light", object_data=top_data)
    scene.collection.objects.link(top_obj)
    top_obj.location = (0, 0, 5)
    top_obj.rotation_euler = (0, 0, 0)
    
    # --- World/Environment ---
    world = bpy.data.worlds.new("StudioWorld")
    scene.world = world
    world.use_nodes = True
    nodes = world.node_tree.nodes
    links = world.node_tree.links
    nodes.clear()
    
    # Gradient background
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-600, 0)
    
    gradient = nodes.new(type='ShaderNodeTexGradient')
    gradient.location = (-400, 0)
    gradient.gradient_type = 'LINEAR'
    
    mapping = nodes.new(type='ShaderNodeMapping')
    mapping.location = (-500, 0)
    mapping.inputs['Rotation'].default_value = (math.radians(90), 0, 0)
    
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-200, 0)
    ramp.color_ramp.elements[0].position = 0.3
    ramp.color_ramp.elements[0].color = (0.02, 0.02, 0.03, 1)  # Dark bottom
    ramp.color_ramp.elements[1].position = 0.7
    ramp.color_ramp.elements[1].color = (0.08, 0.08, 0.12, 1)  # Lighter top
    
    bg = nodes.new(type='ShaderNodeBackground')
    bg.location = (0, 0)
    bg.inputs['Strength'].default_value = 1.0
    
    output = nodes.new(type='ShaderNodeOutputWorld')
    output.location = (200, 0)
    
    links.new(tex_coord.outputs['Generated'], mapping.inputs['Vector'])
    links.new(mapping.outputs['Vector'], gradient.inputs['Vector'])
    links.new(gradient.outputs['Color'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bg.inputs['Color'])
    links.new(bg.outputs['Background'], output.inputs['Surface'])
    
    # --- Floor ---
    bpy.ops.mesh.primitive_plane_add(size=20, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Floor"
    
    mat_floor = bpy.data.materials.new(name="Floor_Material")
    mat_floor.use_nodes = True
    nodes_f = mat_floor.node_tree.nodes
    bsdf_f = nodes_f.get('Principled BSDF')
    bsdf_f.inputs['Base Color'].default_value = (0.03, 0.03, 0.03, 1)
    bsdf_f.inputs['Roughness'].default_value = 0.15
    bsdf_f.inputs['Specular IOR Level'].default_value = 0.8
    floor.data.materials.append(mat_floor)
    
    return target

# ==============================================================================
# 360° CAMERA ANIMATION
# ==============================================================================
def setup_360_camera(target):
    """Create camera with 360° rotation animation"""
    scene = bpy.context.scene
    
    # Camera
    cam_data = bpy.data.cameras.new(name='Camera')
    cam_data.lens = 50  # 50mm lens
    cam_data.dof.use_dof = True
    cam_data.dof.focus_object = target
    cam_data.dof.aperture_fstop = 4.0
    
    cam_obj = bpy.data.objects.new(name='Camera', object_data=cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Create empty at center for camera to orbit around
    orbit_center = bpy.data.objects.new("OrbitCenter", None)
    scene.collection.objects.link(orbit_center)
    orbit_center.location = target.location
    
    # Parent camera to empty
    cam_obj.parent = orbit_center
    cam_obj.location = (CAMERA_RADIUS, 0, CAMERA_HEIGHT - target.location[2])
    
    # Track to target
    cons = cam_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'
    
    # Animate rotation of orbit center
    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES
    scene.render.fps = FPS
    
    # Keyframe at frame 1: rotation = 0
    orbit_center.rotation_euler = (0, 0, 0)
    orbit_center.keyframe_insert(data_path="rotation_euler", frame=1)
    
    # Keyframe at last frame: rotation = 360°
    orbit_center.rotation_euler = (0, 0, math.radians(360))
    orbit_center.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)
    
    # Make rotation linear
    if orbit_center.animation_data and orbit_center.animation_data.action:
        for fcurve in orbit_center.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'
    
    print(f"  Camera animation: {TOTAL_FRAMES} frames, {FPS} fps")
    
    return cam_obj

# ==============================================================================
# GPU SETUP
# ==============================================================================
def setup_gpu():
    """Configure GPU rendering with automatic device detection"""
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons.get('cycles')

    if not cycles_prefs:
        print("  WARNING: Cycles addon not found, using CPU")
        return False

    cprefs = cycles_prefs.preferences

    # Try GPU compute types in order of preference (fastest first)
    compute_types = ['OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI', 'OPENCL']
    gpu_found = False

    for compute_type in compute_types:
        try:
            cprefs.compute_device_type = compute_type
            # Refresh device list
            cprefs.get_devices()

            # Check if any GPU devices are available
            devices = cprefs.devices
            gpu_devices = [d for d in devices if d.type != 'CPU']

            if gpu_devices:
                # Enable all GPU devices
                for device in devices:
                    device.use = (device.type != 'CPU')
                    if device.use:
                        print(f"  Enabled GPU: {device.name} ({compute_type})")

                gpu_found = True
                print(f"  Using compute type: {compute_type}")
                break
        except Exception as e:
            continue

    if not gpu_found:
        print("  No GPU found, falling back to CPU")
        # Enable CPU as fallback
        try:
            cprefs.compute_device_type = 'NONE'
            for device in cprefs.devices:
                device.use = (device.type == 'CPU')
        except:
            pass

    return gpu_found

# ==============================================================================
# RENDER SETTINGS
# ==============================================================================
def setup_render_settings():
    """Configure high-quality Cycles render with GPU acceleration"""
    scene = bpy.context.scene

    # Cycles engine
    scene.render.engine = 'CYCLES'

    # Setup GPU rendering
    print("\n[GPU] Configuring GPU acceleration...")
    gpu_enabled = setup_gpu()

    cycles = scene.cycles
    cycles.device = 'GPU' if gpu_enabled else 'CPU'
    cycles.samples = RENDER_SAMPLES
    cycles.use_denoising = True if gpu_enabled else False

    # Optimize for GPU rendering
    if gpu_enabled:
        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.01
        cycles.tile_size = 256  # Larger tiles for GPU

    # Resolution
    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100

    # Output for animation
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.ffmpeg.ffmpeg_preset = 'GOOD'
    scene.render.filepath = OUTPUT_VIDEO

    # Motion blur for smooth animation
    scene.render.use_motion_blur = True
    scene.render.motion_blur_shutter = 0.5

    # Color management
    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

    print(f"  Render device: {cycles.device}")
    print(f"  Render: {RESOLUTION_X}x{RESOLUTION_Y}, {RENDER_SAMPLES} samples")

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    # Check if cached blend exists
    if os.path.exists(BLEND_CACHE_PATH):
        print(f"Loading cached scene from: {BLEND_CACHE_PATH}")
        bpy.ops.wm.open_mainfile(filepath=BLEND_CACHE_PATH)
        
        # Still need to setup animation and render (these are quick)
        target = bpy.data.objects.get("LightTarget")
        if not target:
            target = bpy.data.objects.new("LightTarget", None)
            bpy.context.scene.collection.objects.link(target)
            target.location = (0.15, 0.08, 0.75)
        
        # Check if camera animation exists
        orbit = bpy.data.objects.get("OrbitCenter")
        if not orbit:
            setup_360_camera(target)
        
        setup_render_settings()
    else:
        print("Building scene from scratch...")
        cleanup()
        
        print("\n[1/5] Creating materials...")
        mats = create_materials()
        
        print("\n[2/5] Loading data and building model...")
        col = load_data_and_build(mats)
        
        print("\n[3/5] Setting up D5-style lighting...")
        target = setup_d5_lighting()
        
        print("\n[4/5] Setting up 360° camera animation...")
        setup_360_camera(target)
        
        print("\n[5/5] Configuring render settings...")
        setup_render_settings()
        
        # Create output directory
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        os.makedirs(os.path.dirname(BLEND_CACHE_PATH), exist_ok=True)
        
        # Save cached blend file
        print(f"\nSaving cached scene to: {BLEND_CACHE_PATH}")
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_CACHE_PATH)
    
    print("\n" + "="*60)
    print("SCENE READY!")
    print("="*60)
    print(f"Output video: {OUTPUT_VIDEO}")
    print(f"Frames: {TOTAL_FRAMES} @ {FPS}fps = {TOTAL_FRAMES/FPS:.1f} seconds")
    print("\nStarting render...")
    
    # Render animation
    bpy.ops.render.render(animation=True)
    
    print(f"\nRender complete! Video saved to: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    main()
