"""
geometry.py - Geometry manipulation helpers for Blender objects

Functions for bounding boxes, origins, centering, and orientation detection.
"""

import bpy
from mathutils import Matrix, Vector


def get_bounding_dimensions(obj):
    """Get world-space bounding box dimensions.

    Returns:
        Tuple of (width, depth, height)
    """
    bbox_corners = [obj.matrix_world @ Vector(corner) for corner in obj.bound_box]

    min_x = min(c.x for c in bbox_corners)
    max_x = max(c.x for c in bbox_corners)
    min_y = min(c.y for c in bbox_corners)
    max_y = max(c.y for c in bbox_corners)
    min_z = min(c.z for c in bbox_corners)
    max_z = max(c.z for c in bbox_corners)

    return (max_x - min_x, max_y - min_y, max_z - min_z)


def get_bounding_box_mm(obj):
    """Get bounding box dimensions in mm (assuming 1 BU = 1mm).

    Returns:
        Dict with 'x', 'y', 'z', and 'max' dimensions
    """
    width, depth, height = get_bounding_dimensions(obj)
    return {
        'x': width,
        'y': depth,
        'z': height,
        'max': max(width, depth, height)
    }


def origin_to_bottom(obj):
    """Move object origin to bottom center of bounding box."""
    me = obj.data
    mw = obj.matrix_world
    local_verts = [Vector(v[:]) for v in obj.bound_box]

    # Center XY, bottom Z
    o = sum(local_verts, Vector()) / 8
    o.z = min(v.z for v in local_verts)

    me.transform(Matrix.Translation(-o))
    mw.translation = mw @ o


def center_object(obj):
    """Center object at world origin with bottom on ground plane."""
    origin_to_bottom(obj)
    obj.location = (0, 0, 0)


def is_y_up(obj):
    """Detect if model was exported with Y-up orientation (common in game engines).

    Analyzes face normals to determine if model uses Y-up or Z-up convention.
    """
    z_up_count = 0
    y_up_count = 0

    for poly in obj.data.polygons:
        normal = poly.normal
        if abs(normal.z) > abs(normal.y):
            z_up_count += 1
        else:
            y_up_count += 1

    return y_up_count > z_up_count


def create_framing_cube(obj, padding=1.1):
    """Create an invisible cube slightly larger than object for camera framing.

    Args:
        obj: Object to frame
        padding: Scale multiplier (1.1 = 10% larger)

    Returns:
        The framing cube object
    """
    width, depth, height = get_bounding_dimensions(obj)

    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, height / 2))
    cube = bpy.context.active_object
    cube.scale = (width * padding, depth * padding, height * padding)
    cube.hide_render = True
    cube.name = "_FramingCube"

    return cube
