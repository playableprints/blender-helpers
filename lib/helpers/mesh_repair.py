"""
mesh_repair.py - Mesh repair and cleanup operations

Functions for fixing common mesh issues: normals, manifold, etc.
"""

import bpy
from .selection import deselect_all


def fix_normals(obj):
    """Recalculate normals to point outward for a mesh object."""
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)
    bpy.ops.object.mode_set(mode='OBJECT')


def remove_doubles(obj, threshold=0.0001):
    """Merge vertices that are very close together.

    Args:
        obj: Mesh object
        threshold: Distance threshold for merging
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=threshold)
    bpy.ops.object.mode_set(mode='OBJECT')


def fill_holes(obj, sides=0):
    """Fill holes in mesh.

    Args:
        obj: Mesh object
        sides: Max sides for holes to fill (0 = unlimited)
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold(
        extend=False, use_wire=True, use_boundary=True,
        use_multi_face=False, use_non_contiguous=False,
        use_verts=False
    )
    try:
        bpy.ops.mesh.fill_holes(sides=sides)
    except RuntimeError:
        pass  # Blender raises RuntimeError when no holes to fill
    bpy.ops.object.mode_set(mode='OBJECT')


def delete_loose(obj):
    """Delete loose geometry (vertices not connected to faces)."""
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_loose()
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')


def make_manifold(obj):
    """Attempt to make mesh manifold using various repair techniques.

    Applies: remove doubles, fill holes, fix normals, delete loose geometry.
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Enter edit mode for batch operations
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')

    # Remove doubles (merge very close vertices)
    bpy.ops.mesh.remove_doubles(threshold=0.0001)

    # Fill holes
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_non_manifold(
        extend=False, use_wire=True, use_boundary=True,
        use_multi_face=False, use_non_contiguous=False,
        use_verts=False
    )
    try:
        bpy.ops.mesh.fill_holes(sides=0)
    except RuntimeError:
        pass  # No holes to fill

    # Recalculate normals
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.normals_make_consistent(inside=False)

    bpy.ops.object.mode_set(mode='OBJECT')

    # Try Print3D cleanup if available (addon may not be enabled)
    try:
        bpy.ops.mesh.print3d_clean_non_manifold()
    except (RuntimeError, AttributeError):
        pass  # Print3D addon not available or operator failed

    # Delete loose geometry
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.mesh.select_loose()
    bpy.ops.mesh.delete(type='VERT')
    bpy.ops.object.mode_set(mode='OBJECT')


def voxel_remesh(obj, voxel_size=0.1):
    """Apply voxel remesh to make mesh watertight.

    This is destructive - it replaces the mesh topology entirely.

    Args:
        obj: Mesh object
        voxel_size: Resolution in scene units (smaller = more detail)

    Returns:
        The remeshed object
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.context.object.data.remesh_voxel_size = voxel_size
    bpy.ops.object.voxel_remesh()

    return obj


def hollow_mesh(obj, wall_thickness=2.0):
    """Hollow out a mesh using Solidify modifier.

    Args:
        obj: Mesh object
        wall_thickness: Wall thickness in Blender units
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    # Remove any existing solidify modifiers
    for mod in obj.modifiers:
        if mod.type == 'SOLIDIFY':
            obj.modifiers.remove(mod)

    # Add solidify modifier
    solidify = obj.modifiers.new(name="Hollow", type='SOLIDIFY')
    solidify.thickness = -wall_thickness  # Negative = inward
    solidify.offset = 1.0  # Offset outward so exterior stays same
    solidify.use_rim = True  # Fill the rim where inner meets outer
    solidify.use_rim_only = False

    # Apply modifier
    bpy.ops.object.modifier_apply(modifier=solidify.name)

    # Fix normals after hollowing
    fix_normals(obj)
