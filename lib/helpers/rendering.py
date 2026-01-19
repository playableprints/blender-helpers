"""
rendering.py - Rendering helpers for Blender scripts

Functions for materials, camera framing, and rendering operations.
"""

import bpy
from .selection import deselect_all
from .geometry import create_framing_cube


def setup_gpu_rendering():
    """Auto-detect and enable GPU rendering for Cycles.

    Tries device types in order of preference:
    - OPTIX (NVIDIA RTX, fastest)
    - CUDA (NVIDIA, widely compatible)
    - HIP (AMD)
    - ONEAPI (Intel)
    - METAL (Apple Silicon)

    Returns:
        Tuple of (device_type, device_names) if GPU enabled, or (None, []) if CPU only
    """
    if bpy.context.scene.render.engine != 'CYCLES':
        print("GPU rendering requires Cycles engine")
        return None, []

    cycles_prefs = bpy.context.preferences.addons['cycles'].preferences

    # Device types in order of preference
    device_types = ['OPTIX', 'CUDA', 'HIP', 'ONEAPI', 'METAL']

    for device_type in device_types:
        try:
            cycles_prefs.compute_device_type = device_type
            cycles_prefs.get_devices()

            # Check if we have any usable devices of this type
            gpu_devices = [d for d in cycles_prefs.devices
                          if d.type == device_type and d.type != 'CPU']

            if gpu_devices:
                # Enable all GPU devices
                for device in cycles_prefs.devices:
                    device.use = device.type != 'CPU'

                # Set scene to use GPU
                bpy.context.scene.cycles.device = 'GPU'

                device_names = [d.name for d in gpu_devices]
                print(f"GPU rendering enabled: {device_type}")
                for name in device_names:
                    print(f"  - {name}")
                return device_type, device_names

        except Exception:
            continue

    print("No GPU found, using CPU rendering")
    return None, []


def set_render_samples(samples=128):
    """Set the number of render samples for Cycles.

    Higher samples = less noise but longer render time.
    Typical values:
    - 32-64: Fast preview, noisy
    - 128-256: Good quality for most renders
    - 512+: High quality, slow

    Args:
        samples: Number of samples (default: 128)
    """
    if bpy.context.scene.render.engine == 'CYCLES':
        bpy.context.scene.cycles.samples = samples
        print(f"Render samples set to {samples}")


def apply_material(obj, material_name="Material"):
    """Apply a material to the object. Uses existing material if found.

    Searches for materials in order: material_name, Material.002, Material.001.
    Creates a new node-based material if none found.

    Args:
        obj: Blender mesh object
        material_name: Name of material to search for first
    """
    material = None
    for mat_name in [material_name, "Material.002", "Material.001"]:
        material = bpy.data.materials.get(mat_name)
        if material:
            break

    if not material:
        material = bpy.data.materials.new(name="RenderMaterial")
        material.use_nodes = True

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def frame_camera_to_object(obj, padding=1.1):
    """Create framing cube and aim camera at object.

    Creates an invisible cube slightly larger than the object, then
    uses Blender's camera_to_view_selected to frame it.

    Args:
        obj: Object to frame
        padding: Scale multiplier for framing cube (1.1 = 10% padding)

    Returns:
        The framing cube object (hidden from render)
    """
    framing_cube = create_framing_cube(obj, padding)
    deselect_all()
    framing_cube.select_set(True)
    bpy.context.view_layer.objects.active = framing_cube

    # Frame camera to cube
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                bpy.ops.view3d.camera_to_view_selected()
            break

    return framing_cube


def render_frame(output_path, file_format='PNG'):
    """Render a single frame to the specified path.

    Args:
        output_path: Full path for output file
        file_format: Image format (PNG, JPEG, etc.)
    """
    bpy.context.scene.render.image_settings.file_format = file_format
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {output_path}")
