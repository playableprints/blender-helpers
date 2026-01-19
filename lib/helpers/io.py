"""
io.py - Import/export helpers for various 3D formats
"""

import bpy
import os
import sys


# Known non-mesh objects to ignore when identifying imported objects
IGNORE_OBJECTS = {"Area", "Camera", "Plane", "Point", "Light", "Sun", "Cube"}


def import_model(filepath):
    """
    Import a 3D model file (STL, OBJ, FBX, GLTF, blend).
    Returns list of imported mesh objects.
    """
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    ext = os.path.splitext(filepath)[1].lower()

    # Track existing objects to find what was imported
    existing = set(bpy.data.objects.keys())

    if ext == '.stl':
        bpy.ops.wm.stl_import(filepath=filepath)
    elif ext == '.obj':
        bpy.ops.wm.obj_import(filepath=filepath)
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=filepath)
    elif ext in ('.glb', '.gltf'):
        bpy.ops.import_scene.gltf(filepath=filepath)
    elif ext == '.blend':
        bpy.ops.wm.open_mainfile(filepath=filepath)
        from .selection import get_mesh_objects
        return get_mesh_objects()
    else:
        print(f"Error: Unsupported format: {ext}")
        sys.exit(1)

    # Find newly imported objects
    new_objects = set(bpy.data.objects.keys()) - existing - IGNORE_OBJECTS
    imported = [bpy.data.objects[name] for name in new_objects if bpy.data.objects[name].type == 'MESH']

    if not imported:
        print(f"Warning: No mesh objects imported from {filepath}")

    return imported


def import_stl(filepath):
    """Import an STL file. Exits if file not found."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    bpy.ops.wm.stl_import(filepath=filepath)


def import_obj(filepath):
    """Import an OBJ file. Exits if file not found."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    bpy.ops.wm.obj_import(filepath=filepath)


def import_fbx(filepath):
    """Import an FBX file. Exits if file not found."""
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    bpy.ops.import_scene.fbx(filepath=filepath)


def export_stl(filepath, selection_only=True, apply_modifiers=True):
    """Export to STL."""
    bpy.ops.wm.stl_export(
        filepath=filepath,
        export_selected_objects=selection_only,
        apply_modifiers=apply_modifiers
    )


def export_obj(filepath, selection_only=True, apply_modifiers=True):
    """Export to OBJ."""
    bpy.ops.wm.obj_export(
        filepath=filepath,
        export_selected_objects=selection_only,
        apply_modifiers=apply_modifiers
    )


def export_gltf(filepath, selection_only=True, apply_modifiers=True):
    """Export to GLTF for rendering with ThreeJS."""
    bpy.ops.export_scene.gltf(
        filepath=filepath,
        use_selection=selection_only,
        export_apply=apply_modifiers,
        check_existing=False,
        filter_glob='*.glb', 
        export_format='GLB', 
        export_materials="EXPORT",
        export_vertex_color="MATERIAL", 
        export_normals=True,
        export_yup=True, 
        export_draco_mesh_compression_enable=True
    )


def save_blend(filepath):
    """Save current scene as .blend file."""
    bpy.ops.wm.save_as_mainfile(filepath=filepath)


def get_format_from_path(filepath):
    """Get format string from file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    return {
        '.stl': 'STL',
        '.obj': 'OBJ',
        '.fbx': 'FBX',
        '.glb': 'GLTF',
        '.gltf': 'GLTF',
        '.blend': 'BLEND',
    }.get(ext, None)
