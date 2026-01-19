"""
helpers - Lightweight convenience functions for Blender pipeline scripts

Usage:
    from helpers import deselect_all, get_mesh_objects, import_model

    # Or import from specific modules:
    from helpers.io import import_model, export_stl
    from helpers.selection import get_mesh_objects
"""

# Selection
from .selection import (
    deselect_all,
    object_exists,
    select_by_name,
    get_mesh_objects,
    get_selected_meshes,
)

# Object manipulation
from .objects import (
    remove_by_name,
    clear_scene,
    join_all_meshes,
    apply_transforms,
    set_origin_to_cursor,
    clear_animation,
)

# Boolean operations
from .boolean import (
    boolean_subtract,
    boolean_union,
)

# Import/Export
from .io import (
    import_model,
    import_stl,
    import_obj,
    import_fbx,
    export_stl,
    export_obj,
    export_gltf,
    save_blend,
    get_format_from_path,
)

# Naming/paths
from .naming import (
    clean_name,
    output_path_next_to,
    ensure_extension,
    get_basename,
)

# Benchmarking
from .benchmark import (
    benchmark_start,
    benchmark_log,
)

# Script utilities
from .script_utils import (
    ScriptArgs,
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
    require_meshes,
)

# Geometry
from .geometry import (
    get_bounding_dimensions,
    get_bounding_box_mm,
    origin_to_bottom,
    center_object,
    is_y_up,
    create_framing_cube,
)

# Mesh repair
from .mesh_repair import (
    fix_normals,
    remove_doubles,
    fill_holes,
    delete_loose,
    make_manifold,
    voxel_remesh,
    hollow_mesh,
)

# Mesh analysis
from .mesh_analysis import (
    MeshIssues,
    count_islands,
    analyze_mesh,
    check_intersections,
    calculate_volume,
    calculate_area,
    ensure_print3d_addon,
)

# Rendering
from .rendering import (
    setup_gpu_rendering,
    set_render_samples,
    apply_material,
    frame_camera_to_object,
    render_frame,
)
