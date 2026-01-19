"""
selection.py - Object selection helpers
"""

import bpy


def deselect_all():
    """Deselect all objects in the scene."""
    bpy.ops.object.select_all(action='DESELECT')


def object_exists(name):
    """Check if an object with the given name exists."""
    return name in bpy.data.objects


def select_by_name(name):
    """Select an object by name and make it active."""
    if object_exists(name):
        deselect_all()
        bpy.data.objects[name].select_set(True)
        bpy.context.view_layer.objects.active = bpy.data.objects[name]
        return True
    return False


def get_mesh_objects():
    """Return all mesh objects in the scene (excludes cameras, lights, etc)."""
    return [obj for obj in bpy.data.objects if obj.type == 'MESH']


def get_selected_meshes():
    """Return all selected mesh objects."""
    return [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
