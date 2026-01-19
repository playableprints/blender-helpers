"""
mesh_analysis.py - Mesh quality analysis for 3D printing

Provides tools to analyze mesh quality, detect issues, and calculate
volume/area for print preparation.
"""

import bpy
import bmesh
from mathutils import Vector

from .selection import deselect_all


# -----------------------------------------------------------------------------
# Analysis thresholds
# -----------------------------------------------------------------------------

# Faces smaller than this (in Blender units²) are considered degenerate.
# 1e-8 is effectively zero for any practical mesh.
ZERO_AREA_THRESHOLD = 1e-8

# If more than this fraction of faces point toward the mesh center,
# we flag the mesh as having flipped normals. 10% allows for some
# internal geometry (e.g., mouth interior) without false positives.
FLIPPED_NORMAL_RATIO = 0.1


# -----------------------------------------------------------------------------
# Issue tracking
# -----------------------------------------------------------------------------

class MeshIssues:
    """Track issues found during mesh analysis."""

    def __init__(self):
        self.non_manifold_edges = 0
        self.non_manifold_verts = 0
        self.loose_geometry = 0
        self.flipped_normals = 0
        self.intersecting_faces = 0
        self.zero_area_faces = 0
        self.island_count = 1  # At least 1 island (the mesh itself)

    @property
    def has_issues(self):
        """Check if any issues were found."""
        return any([
            self.non_manifold_edges,
            self.non_manifold_verts,
            self.loose_geometry,
            self.flipped_normals,
            self.intersecting_faces,
            self.zero_area_faces,
            self.island_count > 1,
        ])

    @property
    def is_manifold(self):
        """Check if mesh is manifold (watertight)."""
        return self.non_manifold_edges == 0 and self.non_manifold_verts == 0

    @property
    def has_multiple_islands(self):
        """Check if mesh has disconnected parts."""
        return self.island_count > 1

    def suggested_scripts(self):
        """Return list of suggested repair scripts based on issues.

        Returns:
            List of tuples: (script_name, description)
        """
        scripts = []
        if self.flipped_normals > 0:
            scripts.append(("fix-normals", "Recalculate normals to fix flipped faces"))
        if self.non_manifold_edges > 0 or self.non_manifold_verts > 0 or self.loose_geometry > 0:
            scripts.append(("make-manifold", "Fix non-manifold geometry and holes"))
        if self.intersecting_faces > 0 or self.island_count > 1:
            scripts.append(("voxel-merge", "Join islands / fix intersections via voxel remesh"))
        return scripts


# -----------------------------------------------------------------------------
# Mesh analysis
# -----------------------------------------------------------------------------

def count_islands(bm):
    """Count disconnected mesh islands using flood fill.

    Args:
        bm: BMesh object

    Returns:
        Number of disconnected islands
    """
    if not bm.verts:
        return 0

    visited = set()
    island_count = 0

    for start_vert in bm.verts:
        if start_vert.index in visited:
            continue

        # Flood fill from this vertex
        island_count += 1
        stack = [start_vert]

        while stack:
            vert = stack.pop()
            if vert.index in visited:
                continue
            visited.add(vert.index)

            # Add all connected vertices (via edges)
            for edge in vert.link_edges:
                other = edge.other_vert(vert)
                if other.index not in visited:
                    stack.append(other)

    return island_count


def analyze_mesh(obj):
    """Perform detailed mesh analysis.

    Checks for:
    - Non-manifold edges and vertices
    - Loose geometry (floating vertices)
    - Zero-area (degenerate) faces
    - Disconnected islands
    - Flipped normals (faces pointing inward)

    Args:
        obj: Blender mesh object

    Returns:
        MeshIssues object with analysis results
    """
    issues = MeshIssues()

    # Create bmesh from object
    bm = bmesh.new()
    bm.from_mesh(obj.data)
    bm.edges.ensure_lookup_table()
    bm.verts.ensure_lookup_table()
    bm.faces.ensure_lookup_table()

    # Check for non-manifold edges (edges with != 2 faces)
    for edge in bm.edges:
        if not edge.is_manifold:
            issues.non_manifold_edges += 1

    # Check for non-manifold verts (verts that would split mesh)
    for vert in bm.verts:
        if not vert.is_manifold:
            issues.non_manifold_verts += 1

    # Check for loose geometry (verts/edges not part of faces)
    for vert in bm.verts:
        if not vert.link_faces:
            issues.loose_geometry += 1

    # Check for zero-area faces (degenerate)
    for face in bm.faces:
        if face.calc_area() < ZERO_AREA_THRESHOLD:
            issues.zero_area_faces += 1

    # Count disconnected islands
    issues.island_count = count_islands(bm)

    # Check for flipped normals (faces pointing inward)
    # Heuristic: if most normals point away from center, find ones pointing toward
    if bm.faces:
        center = sum((f.calc_center_median() for f in bm.faces), Vector()) / len(bm.faces)
        flipped = 0
        for face in bm.faces:
            face_center = face.calc_center_median()
            to_center = center - face_center
            # If normal points toward center, it's likely flipped
            if face.normal.dot(to_center) > 0:
                flipped += 1
        # If more than FLIPPED_NORMAL_RATIO are "flipped", flag it
        if flipped > len(bm.faces) * FLIPPED_NORMAL_RATIO:
            issues.flipped_normals = flipped

    bm.free()
    return issues


def check_intersections(obj):
    """Check for self-intersecting faces using Print3D Toolbox.

    Args:
        obj: Blender mesh object

    Returns:
        Number of intersecting faces, or 0 if check unavailable
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.mesh.print3d_check_intersect()
        # Count selected faces (intersecting ones get selected)
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action='DESELECT')
        bpy.ops.mesh.print3d_check_intersect()
        bpy.ops.object.mode_set(mode='OBJECT')

        count = sum(1 for f in obj.data.polygons if f.select)
        return count
    except (RuntimeError, AttributeError):
        return 0  # Print3D addon not available


# -----------------------------------------------------------------------------
# Volume/Area calculations
# -----------------------------------------------------------------------------

def calculate_volume(obj, use_print3d=True):
    """Calculate mesh volume in cm³.

    Args:
        obj: Blender mesh object
        use_print3d: Try Print3D Toolbox first (more accurate)

    Returns:
        Volume in cm³, or None if calculation failed
    """
    if use_print3d:
        try:
            deselect_all()
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj
            bpy.ops.mesh.print3d_info_volume()
            volume = bpy.context.scene.print3d.volume
            return volume / 1000  # mm³ to cm³
        except (RuntimeError, AttributeError):
            pass  # Print3D addon not available, fall through to bmesh method

    # Fallback: use bmesh
    bm = None
    try:
        bm = bmesh.new()
        bm.from_mesh(obj.data)
        volume = bm.calc_volume()
        bm.free()
        return abs(volume) / 1000  # mm³ to cm³
    except Exception:
        if bm:
            bm.free()
        return None


def calculate_area(obj):
    """Calculate mesh surface area in cm² using Print3D Toolbox.

    Args:
        obj: Blender mesh object

    Returns:
        Surface area in cm², or None if calculation failed
    """
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    try:
        bpy.ops.mesh.print3d_info_area()
        area = bpy.context.scene.print3d.area
        return area / 100  # mm² to cm²
    except (RuntimeError, AttributeError):
        return None  # Print3D addon not available


def ensure_print3d_addon():
    """Check if Print3D Toolbox addon is available.

    Returns:
        True if addon is available/enabled, False otherwise
    """
    # Blender 5.0+ uses extensions with bl_ext prefix
    # Legacy addons used object_print3d_utils
    addon_names = [
        "bl_ext.blender_org.print3d_toolbox",  # Blender 5.0+ extension
        "object_print3d_utils",                 # Legacy addon name
    ]

    for addon_name in addon_names:
        if addon_name in bpy.context.preferences.addons:
            return True

    return False
