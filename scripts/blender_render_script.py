import bpy
import csv
import math
import os
import bmesh

# ==============================================================================
# SETTINGS
# ==============================================================================
# Path to your CSV files (UPDATE THIS PATH TO MATCH YOUR SYSTEM)
# In Blender, os.getcwd() might be different, so use absolute paths if needed.
# We will assume the script is run from the project root or we can hardcode for this generated file.
# Since we are generating this for the user, we will try to find the data relative to the script
# or default to the known path.

# PATHS (relative to script location)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Parent of scripts/ folder
CSV_POS_PATH = os.path.join(BASE_DIR, 'data', 'twin_position_matrix.csv')
CSV_CONN_PATH = os.path.join(BASE_DIR, 'data', 'twin_connectivity_matrix.csv')
OUTPUT_PATH = os.path.join(BASE_DIR, 'results', 'visualizations', 'twin_towers_render_4k.png')

# Scaling
MODEL_SCALE = 0.01  # Data is in cm, Blender units = meters. 1 unit = 1m. 1cm = 0.01m.

# Sections (in meters)
FRAME_WIDTH = 0.006    # 6mm
PANEL_THICKNESS = 0.003 # 3mm
PANEL_WIDTH_XZ = 0.034  # 3.4cm
PANEL_WIDTH_YZ = 0.034  # Generic width for YZ panels (if any)

# ==============================================================================
# CLEANUP
# ==============================================================================
def cleanup():
    # Remove all meshes and objects
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear collections
    for c in bpy.data.collections:
        bpy.data.collections.remove(c)
        
    # Clear materials
    for m in bpy.data.materials:
        bpy.data.materials.remove(m)

# ==============================================================================
# MATERIALS
# ==============================================================================
def create_materials():
    mats = {}
    
    # 1. Balsa Wood (Frame)
    mat_balsa = bpy.data.materials.new(name="Balsa_Frame")
    mat_balsa.use_nodes = True
    nodes = mat_balsa.node_tree.nodes
    nodes.clear()
    
    # Principled BSDF
    bsdf = nodes.new(type='ShaderNodeBsdfPrincipled')
    bsdf.inputs['Base Color'].default_value = (0.85, 0.75, 0.6, 1) # Light wood color
    bsdf.inputs['Roughness'].default_value = 0.7
    bsdf.inputs['Specular IOR Level'].default_value = 0.2
    
    # Texture - Noise for grain
    tex_noise = nodes.new(type='ShaderNodeTexNoise')
    tex_noise.inputs['Scale'].default_value = 50.0
    tex_noise.inputs['Detail'].default_value = 10.0
    tex_noise.inputs['Roughness'].default_value = 0.5
    
    # Color Ramp for grain
    ramp = nodes.new(type='ShaderNodeValToRGB')
    ramp.color_ramp.elements[0].color = (0.8, 0.7, 0.55, 1)
    ramp.color_ramp.elements[1].color = (0.9, 0.8, 0.65, 1)
    
    # Mix texture with base
    # Connect
    mat_balsa.node_tree.links.new(tex_noise.outputs['Fac'], ramp.inputs['Fac'])
    mat_balsa.node_tree.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    
    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat_balsa.node_tree.links.new(bsdf.outputs['BSDF'], output.inputs['Surface'])
    
    mats['frame'] = mat_balsa

    # 2. Balsa Panel (Slightly darker/different)
    mat_panel = bpy.data.materials.new(name="Balsa_Panel")
    mat_panel.use_nodes = True
    nodes_p = mat_panel.node_tree.nodes
    # Copy from frame but maybe slightly different
    # For now simply link to frame logic or make new
    # Let's just use the same for visual consistency, maybe slightly different color
    bsdf_p = nodes_p.new(type='ShaderNodeBsdfPrincipled')
    bsdf_p.inputs['Base Color'].default_value = (0.8, 0.7, 0.55, 1) 
    out_p = nodes_p.new(type='ShaderNodeOutputMaterial')
    mat_panel.node_tree.links.new(bsdf_p.outputs['BSDF'], out_p.inputs['Surface'])
    
    mats['panel'] = mat_panel

    # 3. Steel (Weights if visible, but we assume empty gap)
    
    return mats

# ==============================================================================
# GEOMETRY GENERATION
# ==============================================================================
def load_data_and_build(mats):
    print("Loading Data...")
    
    # READ NODES
    nodes = {}
    if not os.path.exists(CSV_POS_PATH):
        print(f"ERROR: Position file not found at {CSV_POS_PATH}")
        return
        
    with open(CSV_POS_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nid = int(row['node_id'])
            x = float(row['x']) * MODEL_SCALE
            y = float(row['y']) * MODEL_SCALE
            z = float(row['z']) * MODEL_SCALE
            nodes[nid] = (x, y, z)
            
    # READ ELEMENTS
    if not os.path.exists(CSV_CONN_PATH):
        print(f"ERROR: Connectivity file not found at {CSV_CONN_PATH}")
        return

    # CREATE COLLECTION
    col = bpy.data.collections.new("TwinTowers")
    bpy.context.scene.collection.children.link(col)
    
    # Helper to create stick
    def create_stick(p1, p2, width, depth, mat_name, name_prefix):
        # Calculate center, length, rotation
        x1, y1, z1 = p1
        x2, y2, z2 = p2
        
        cx, cy, cz = (x1+x2)/2, (y1+y2)/2, (z1+z2)/2
        dx, dy, dz = x2-x1, y2-y1, z2-z1
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        
        # Create Cube
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cx, cy, cz))
        obj = bpy.context.active_object
        obj.name = f"{name_prefix}"
        obj.data.name = f"{name_prefix}_mesh"
        
        # Scale
        # Local Z is length. X and Y are width/depth.
        obj.scale = (width, depth, length)
        
        # Rotate
        # Default cube is aligned to world. We need to align Z axis to p1->p2
        # Direction vector
        import mathutils
        vec = mathutils.Vector((dx, dy, dz))
        quat = vec.to_track_quat('Z', 'Y')
        obj.rotation_euler = quat.to_euler()
        
        # Assign Material
        if obj.data.materials:
            obj.data.materials[0] = mats[mat_name]
        else:
            obj.data.materials.append(mats[mat_name])
            
        # Move to collection
        # (primitive_add puts it in active collection, so ensure it is active or move)
        # We manually link/unlink
        for c in obj.users_collection:
            c.objects.unlink(obj)
        col.objects.link(obj)
        
        return obj

    # Iterate Elements
    with open(CSV_CONN_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            nid1, nid2 = int(row['node_i']), int(row['node_j'])
            etype = row['element_type']
            
            p1 = nodes[nid1]
            p2 = nodes[nid2]
            
            # Determine Geometry based on type
            # Panels: Modeled as X-braces in the script (diagonals)
            # We want to render them as SOLID PANELS if they are 'shear_wall' type?
            # The connectivity matrix has 2 diagonals for each panel.
            # Rendering 2 diagonals as sticks is fine for visualization, 
            # OR we can try to detect pairs and make a plane.
            # For simplicity and "Balsa Model" look, rendering them as sticks (frame members) is also accurate 
            # if the physical model uses diagonal struts.
            # But the user said "Panels". 
            # If they are solid sheets, we should make planes.
            # Let's stick to "Sticks" for now because detecting the quad from diagonals is tricky 
            # without logic. The generated DXF was lines. 
            # Wait, 3mm Balsa "Panel" usually means a solid sheet.
            # But `regenerate` script generated `shear_wall_xz` as 2 diagonals.
            # I will render them as THICKER sticks (like a filled zone) or just sticks.
            # Given the request for "Real appearance", solid plates are better.
            # But I don't have the 4 corner nodes in a single row.
            # I will render them as FLAT WIDE sticks (Width = 3.4cm, Thickness=3mm).
            # A diagonal with width = Bay Width covers the area visually.
            
            if 'shear_wall' in etype:
                # Wide flat strut
                # Thickness 3mm. Width 34mm? No, that would overlap weirdly.
                # Let's render as 6mm x 3mm sticks (Diagonal braces) 
                # to look like a braced frame which is what the analysis assumed.
                create_stick(p1, p2, 0.006, 0.003, 'panel', etype)
                
            elif 'brace' in etype or 'truss' in etype:
                 # Braces: 6x6mm? Or thinner? Usually balsa strips are consistent.
                 create_stick(p1, p2, 0.006, 0.006, 'frame', etype)
                 
            else:
                # Columns/Beams: 6x6mm
                create_stick(p1, p2, 0.006, 0.006, 'frame', etype)

# ==============================================================================
# SCENE SETUP
# ==============================================================================
def setup_scene():
    scene = bpy.context.scene
    
    # Camera
    cam_data = bpy.data.cameras.new(name='Camera')
    cam_obj = bpy.data.objects.new(name='Camera', object_data=cam_data)
    scene.collection.objects.link(cam_obj)
    scene.camera = cam_obj
    
    # Position Camera
    # Model is 0.3 x 0.16 x 1.53m. Center approx (0.15, 0.08, 0.76)
    # Camera should be Front-Right-Up
    cam_obj.location = (2.5, -2.5, 1.5)
    
    # Point camera at target
    # Simple LookAt constraint
    target = bpy.data.objects.new("Target", None)
    scene.collection.objects.link(target)
    target.location = (0.15, 0.08, 0.75) # Center of model
    
    cons = cam_obj.constraints.new(type='TRACK_TO')
    cons.target = target
    cons.track_axis = 'TRACK_NEGATIVE_Z'
    cons.up_axis = 'UP_Y'
    
    # Lighting
    # Sun
    light_data = bpy.data.lights.new(name="Sun", type='SUN')
    light_data.energy = 5
    light_obj = bpy.data.objects.new(name="Sun", object_data=light_data)
    scene.collection.objects.link(light_obj)
    light_obj.location = (5, -5, 10)
    light_obj.rotation_euler = (math.radians(45), 0, math.radians(45))
    
    # Area Light (Fill)
    light_data2 = bpy.data.lights.new(name="Fill", type='AREA')
    light_data2.energy = 200
    light_data2.size = 5
    light_obj2 = bpy.data.objects.new(name="Fill", object_data=light_data2)
    scene.collection.objects.link(light_obj2)
    light_obj2.location = (-2, -2, 2)
    # Point at model manually or use constraint
    cons2 = light_obj2.constraints.new(type='TRACK_TO')
    cons2.target = target
    cons2.track_axis = 'TRACK_NEGATIVE_Z'
    cons2.up_axis = 'TRACK_Y'

    # Background / World
    world = bpy.data.worlds.new("World")
    scene.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes['Background']
    bg.inputs['Color'].default_value = (0.05, 0.05, 0.1, 1) # Dark Blue/Grey Studio
    bg.inputs['Strength'].default_value = 0.5

    # Floor Plane
    bpy.ops.mesh.primitive_plane_add(size=10, location=(0,0,-0.01))
    plane = bpy.context.active_object
    mat_floor = bpy.data.materials.new(name="Floor")
    mat_floor.use_nodes = True
    bsdf_f = mat_floor.node_tree.nodes.get('Principled BSDF')
    bsdf_f.inputs['Base Color'].default_value = (0.1, 0.1, 0.1, 1)
    bsdf_f.inputs['Roughness'].default_value = 0.1
    bsdf_f.inputs['Specular IOR Level'].default_value = 0.5
    plane.data.materials.append(mat_floor)

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
            cprefs.get_devices()

            devices = cprefs.devices
            gpu_devices = [d for d in devices if d.type != 'CPU']

            if gpu_devices:
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
def setup_render():
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'

    # Setup GPU rendering
    print("Configuring GPU acceleration...")
    gpu_enabled = setup_gpu()

    cycles = scene.cycles
    cycles.device = 'GPU' if gpu_enabled else 'CPU'
    cycles.samples = 128

    # Optimize for GPU rendering
    if gpu_enabled:
        cycles.use_adaptive_sampling = True
        cycles.adaptive_threshold = 0.01
        cycles.tile_size = 256
        cycles.use_denoising = True

    # 4K Resolution
    scene.render.resolution_x = 3840
    scene.render.resolution_y = 2160
    scene.render.resolution_percentage = 100

    scene.render.filepath = OUTPUT_PATH
    print(f"  Render device: {cycles.device}")

# ==============================================================================
# MAIN EXECUTION
# ==============================================================================
if __name__ == "__main__":
    cleanup()
    mats = create_materials()
    load_data_and_build(mats)
    setup_scene()
    setup_render()
    
    print("Starting Render...")
    # Uncomment to render immediately when script runs
    bpy.ops.render.render(write_still=True)
    print(f"Render saved to {OUTPUT_PATH}")
