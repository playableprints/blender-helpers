"""
rendering.py - Rendering helpers for Blender scripts

Functions for materials, camera framing, and rendering operations.
"""

import bpy
from .selection import deselect_all
from .geometry import create_framing_cube


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
