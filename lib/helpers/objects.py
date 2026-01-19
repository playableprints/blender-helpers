"""
objects.py - Object manipulation helpers
"""

import bpy
from .selection import object_exists, deselect_all


def remove_by_name(name):
    """Remove an object by name."""
    if object_exists(name):
        bpy.data.objects.remove(bpy.data.objects[name], do_unlink=True)


def clear_scene():
    """Remove all objects from the scene."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)


def join_all_meshes():
    """Join all mesh objects into a single object. Returns the joined object."""
    from .selection import get_mesh_objects

    meshes = get_mesh_objects()
    if not meshes:
        return None

    if len(meshes) == 1:
        return meshes[0]

    deselect_all()
    for obj in meshes:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.join()

    return bpy.context.active_object


def apply_transforms(obj, location=True, rotation=True, scale=True):
    """Apply transforms to an object."""
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=location, rotation=rotation, scale=scale)


def set_origin_to_cursor(obj):
    """Set object origin to 3D cursor (usually world origin)."""
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.origin_set(type="ORIGIN_CURSOR")


def clear_animation(obj):
    """Clear all animation data from an object."""
    if obj.animation_data:
        obj.animation_data_clear()
