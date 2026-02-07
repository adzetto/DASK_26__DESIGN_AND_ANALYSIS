"""
Twin Towers 360° Rotation Render Script - OPTIMIZED
====================================================
- All geometry merged into single mesh (prevents crashes)
- Caches model as .blend file
- 360° camera rotation animation
- D5-level lighting
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
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent of scripts/ folder
CSV_POS_PATH = os.path.join(BASE_DIR, 'data', 'twin_position_matrix.csv')
CSV_CONN_PATH = os.path.join(BASE_DIR, 'data', 'twin_connectivity_matrix.csv')
BLEND_CACHE_PATH = os.path.join(BASE_DIR, 'results', 'twin_towers_cached.blend')
OUTPUT_VIDEO = os.path.join(BASE_DIR, 'results', 'visualizations', 'twin_towers_360.mp4')

# ==============================================================================
# SETTINGS
# ==============================================================================
MODEL_SCALE = 0.01
FRAME_SIZE = 0.006

# Animation
TOTAL_FRAMES = 120  # Reduced for faster render
FPS = 24
CAMERA_RADIUS = 3.0
CAMERA_HEIGHT = 1.2

# Render
RENDER_SAMPLES = 64  # Reduced for speed
RESOLUTION_X = 1920
RESOLUTION_Y = 1080

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
# MATERIALS
# ==============================================================================
def create_materials():
    mats = {}
    
    # Balsa Wood Material
    mat = bpy.data.materials.new(name="Balsa_Wood")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()
    
    # Texture Coordinate
    tex_coord = nodes.new(type='ShaderNodeTexCoord')
    tex_coord.location = (-500, 0)
    
    # Noise for wood grain
    noise = nodes.new(type='ShaderNodeTexNoise')
    noise.location = (-300, 0)
    noise.inputs['Scale'].default_value = 100
    noise.inputs['Detail'].default_value = 8
    
    # Color Ramp
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.location = (-100, 0)
    ramp.color_ramp.elements[0].position = 0.4
    ramp.color_ramp.elements[0].color = (0.72, 0.58, 0.42, 1)
    ramp.color_ramp.elements[1].position = 0.6
    ramp.color_ramp.elements[1].color = (0.88, 0.76, 0.60, 1)
    
    # BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.location = (200, 0)
    bsdf.inputs['Roughness'].default_value = 0.6
    bsdf.inputs['Specular IOR Level'].default_value = 0.3
    
    # Output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    output.location = (500, 0)
    
    links.new(tex_coord.outputs['Object'], noise.inputs['Vector'])
    links.new(noise.outputs['Fac'], ramp.inputs['Fac'])
    links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    mats['wood'] = mat
    return mats

# ==============================================================================
# BUILD MODEL AS SINGLE MESH
# ==============================================================================
def build_model_optimized(mats):
    """Build entire model as a single mesh using bmesh"""
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
    
    # Create bmesh
    bm = bmesh.new()
    
    # Read elements and create geometry
    element_count = 0
    
    def add_beam_to_bmesh(bm, p1, p2, width, depth):
        """Add a beam between two points to bmesh"""
        import mathutils
        
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        
        dx, dy, dz = x2-x1, y2-y1, z2-z1
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        if length < 0.0001:
            return
        
        # Create a cube at origin
        hw = width / 2
        hd = depth / 2
        hl = length / 2
        
        # 8 vertices of cube centered at origin, Z-aligned
        verts = [
            (-hw, -hd, -hl),
            ( hw, -hd, -hl),
            ( hw,  hd, -hl),
            (-hw,  hd, -hl),
            (-hw, -hd,  hl),
            ( hw, -hd,  hl),
            ( hw,  hd,  hl),
            (-hw,  hd,  hl),
        ]
        
        # Transform: rotate to align with direction, then translate to center
        vec = mathutils.Vector((dx, dy, dz))
        quat = vec.to_track_quat('Z', 'Y')
        rot_mat = quat.to_matrix().to_4x4()
        
        cx, cy, cz = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
        trans_mat = mathutils.Matrix.Translation((cx, cy, cz))
        
        transform = trans_mat @ rot_mat
        
        # Add vertices
        bm_verts = []
        for v in verts:
            co = transform @ mathutils.Vector(v)
            bm_verts.append(bm.verts.new(co))
        
        # Add faces
        # Bottom
        bm.faces.new([bm_verts[0], bm_verts[1], bm_verts[2], bm_verts[3]])
        # Top
        bm.faces.new([bm_verts[4], bm_verts[7], bm_verts[6], bm_verts[5]])
        # Sides
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
            
            if element_count % 1000 == 0:
                print(f"  Created {element_count} elements...")
    
    print(f"  Total: {element_count} elements")
    
    # Create mesh from bmesh
    mesh = bpy.data.meshes.new("TwinTowers_Mesh")
    bm.to_mesh(mesh)
    bm.free()
    
    # Create object
    obj = bpy.data.objects.new("TwinTowers", mesh)
    bpy.context.scene.collection.objects.link(obj)
    
    # Assign material
    obj.data.materials.append(mats['wood'])
    
    # Smooth shading
    for poly in obj.data.polygons:
        poly.use_smooth = False
    
    print("  Model built as single mesh!")
    return obj

# ==============================================================================
# LIGHTING
# ==============================================================================
def setup_lighting():
    scene = bpy.context.scene
    center = (0.15, 0.08, 0.75)
    
    # Target
    target = bpy.data.objects.new("Target", None)
    scene.collection.objects.link(target)
    target.location = center
    
    # Sun
    sun_data = bpy.data.lights.new(name="Sun", type='SUN')
    sun_data.energy = 4
    sun_data.angle = math.radians(1)
    sun_obj = bpy.data.objects.new(name="Sun", object_data=sun_data)
    scene.collection.objects.link(sun_obj)
    sun_obj.rotation_euler = (math.radians(50), math.radians(15), math.radians(30))
    
    # Fill Light
    fill_data = bpy.data.lights.new(name="Fill", type='AREA')
    fill_data.energy = 200
    fill_data.size = 6
    fill_obj = bpy.data.objects.new(name="Fill", object_data=fill_data)
    scene.collection.objects.link(fill_obj)
    fill_obj.location = (-3, -2, 2)
    
    cons = fill_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'
    
    # Rim Light
    rim_data = bpy.data.lights.new(name="Rim", type='AREA')
    rim_data.energy = 300
    rim_data.size = 4
    rim_obj = bpy.data.objects.new(name="Rim", object_data=rim_data)
    scene.collection.objects.link(rim_obj)
    rim_obj.location = (3, 3, 2)
    
    cons2 = rim_obj.constraints.new(type='TRACK_TO')
    cons2.target = target
    cons2.track_axis = 'TRACK_NEGATIVE_Z'
    cons2.up_axis = 'UP_Y'
    
    # World
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.02, 0.02, 0.04, 1)
    bg.inputs['Strength'].default_value = 1.0
    
    # Floor
    bpy.ops.mesh.primitive_plane_add(size=15, location=(0, 0, -0.001))
    floor = bpy.context.active_object
    floor.name = "Floor"
    
    mat_floor = bpy.data.materials.new(name="Floor")
    mat_floor.use_nodes = True
    bsdf = mat_floor.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (0.02, 0.02, 0.02, 1)
    bsdf.inputs['Roughness'].default_value = 0.1
    bsdf.inputs['Specular IOR Level'].default_value = 0.8
    floor.data.materials.append(mat_floor)
    
    return target

# ==============================================================================
# CAMERA ANIMATION
# ==============================================================================
def setup_camera(target):
    scene = bpy.context.scene
    
    cam_data = bpy.data.cameras.new(name='Camera')
    cam_data.lens = 50
    
    cam_obj = bpy.data.objects.new(name='Camera', object_data=cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Orbit empty
    orbit = bpy.data.objects.new("OrbitCenter", None)
    scene.collection.objects.link(orbit)
    orbit.location = target.location
    
    cam_obj.parent = orbit
    cam_obj.location = (CAMERA_RADIUS, 0, CAMERA_HEIGHT - target.location[2])
    
    cons = cam_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'
    
    # Animation
    scene.frame_start = 1
    scene.frame_end = TOTAL_FRAMES
    scene.render.fps = FPS
    
    orbit.rotation_euler = (0, 0, 0)
    orbit.keyframe_insert(data_path="rotation_euler", frame=1)
    
    orbit.rotation_euler = (0, 0, math.radians(360))
    orbit.keyframe_insert(data_path="rotation_euler", frame=TOTAL_FRAMES)
    
    # Linear interpolation
    if orbit.animation_data and orbit.animation_data.action:
        for fcurve in orbit.animation_data.action.fcurves:
            for kf in fcurve.keyframe_points:
                kf.interpolation = 'LINEAR'
    
    return cam_obj

# ==============================================================================
# GPU SETUP
# ==============================================================================
def setup_gpu():
    """Configure GPU rendering with automatic device detection"""
    import subprocess

    # Check for NVIDIA GPU using nvidia-smi
    print("\n[GPU] Checking for GPU hardware...")
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader'],
                               capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"  NVIDIA GPU detected: {result.stdout.strip()}")
        else:
            print("  nvidia-smi failed - no NVIDIA GPU or driver issue")
    except Exception as e:
        print(f"  nvidia-smi not available: {e}")

    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons.get('cycles')

    if not cycles_prefs:
        print("  WARNING: Cycles addon not found, using CPU")
        return False

    cprefs = cycles_prefs.preferences

    # Try GPU compute types in order of preference (fastest first)
    # CUDA is more reliable than OPTIX in headless/cloud environments
    compute_types = ['CUDA', 'OPTIX', 'HIP', 'METAL', 'ONEAPI', 'OPENCL']
    gpu_found = False

    print("\n[GPU] Scanning for available compute devices...")

    for compute_type in compute_types:
        try:
            cprefs.compute_device_type = compute_type
            # Refresh device list
            cprefs.get_devices()

            # Check if any GPU devices are available
            devices = cprefs.devices

            print(f"\n  Trying {compute_type}...")
            for d in devices:
                print(f"    - {d.name} (type: {d.type}, available: {d.type != 'CPU'})")

            gpu_devices = [d for d in devices if d.type != 'CPU']

            if gpu_devices:
                # Enable all GPU devices, also enable CPU for hybrid rendering
                for device in devices:
                    if device.type != 'CPU':
                        device.use = True
                        print(f"  ✓ Enabled GPU: {device.name}")
                    else:
                        device.use = False  # Disable CPU when GPU is available

                gpu_found = True
                print(f"\n  ✓ Using compute type: {compute_type}")
                break
            else:
                print(f"    No GPU devices found for {compute_type}")

        except Exception as e:
            print(f"    {compute_type} failed: {e}")
            continue

    if not gpu_found:
        print("\n  ✗ No GPU found, falling back to CPU")
        try:
            cprefs.compute_device_type = 'NONE'
            for device in cprefs.devices:
                device.use = (device.type == 'CPU')
                if device.use:
                    print(f"  Using CPU: {device.name}")
        except:
            pass

    return gpu_found

# ==============================================================================
# RENDER SETTINGS
# ==============================================================================
def setup_render():
    scene = bpy.context.scene

    scene.render.engine = 'CYCLES'

    # Setup GPU rendering
    print("\n[GPU] Configuring GPU acceleration...")
    gpu_enabled = setup_gpu()

    cycles = scene.cycles
    cycles.device = 'GPU' if gpu_enabled else 'CPU'
    cycles.samples = RENDER_SAMPLES

    # Denoising setup
    try:
        cycles.use_denoising = True if gpu_enabled else False
    except:
        print("  Denoising not available in this Blender version")

    # Optimize for GPU rendering
    if gpu_enabled:
        try:
            cycles.use_adaptive_sampling = True
            cycles.adaptive_threshold = 0.01
        except:
            pass
        # Tile size: larger for GPU (256-512), smaller for CPU (32-64)
        try:
            scene.cycles.tile_size = 256
        except:
            pass

    # Print final configuration
    print(f"\n[RENDER CONFIG]")
    print(f"  Engine: {scene.render.engine}")
    print(f"  Device setting: {cycles.device}")
    print(f"  Samples: {cycles.samples}")

    scene.render.resolution_x = RESOLUTION_X
    scene.render.resolution_y = RESOLUTION_Y
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    scene.render.filepath = OUTPUT_VIDEO

    scene.render.use_motion_blur = False

    scene.view_settings.view_transform = 'Filmic'
    scene.view_settings.look = 'Medium High Contrast'

    print(f"  Render device: {cycles.device}")
    print(f"  Samples: {cycles.samples}")

# ==============================================================================
# MAIN
# ==============================================================================
def main():
    if os.path.exists(BLEND_CACHE_PATH):
        print(f"Loading cached scene: {BLEND_CACHE_PATH}")
        bpy.ops.wm.open_mainfile(filepath=BLEND_CACHE_PATH)
        setup_render()
    else:
        print("Building scene from scratch...")
        cleanup()
        
        print("\n[1/4] Creating materials...")
        mats = create_materials()
        
        print("\n[2/4] Building model (single mesh)...")
        model = build_model_optimized(mats)
        
        print("\n[3/4] Setting up lighting...")
        target = setup_lighting()
        
        print("\n[4/4] Setting up camera...")
        setup_camera(target)
        setup_render()
        
        # Save cache
        os.makedirs(os.path.dirname(BLEND_CACHE_PATH), exist_ok=True)
        print(f"\nSaving cache: {BLEND_CACHE_PATH}")
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_CACHE_PATH)
    
    print("\n" + "="*50)
    print("Starting render...")
    print(f"Output: {OUTPUT_VIDEO}")
    print(f"Frames: {TOTAL_FRAMES} @ {FPS}fps")
    print("="*50)
    
    bpy.ops.render.render(animation=True)
    
    print(f"\nComplete! Video: {OUTPUT_VIDEO}")

if __name__ == "__main__":
    main()
