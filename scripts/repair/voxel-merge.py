"""
voxel-merge.py - Join all objects and voxel remesh into single watertight mesh

Usage:
    blender --background myfile.blend --python voxel-merge.py
    blender --background --python voxel-merge.py -- model.fbx 0.05
    blender --background --python voxel-merge.py -- model.stl 0.05 /output/dir/

Arguments (after --):
    input_file  - Model file to process (STL, OBJ, FBX, or blend)
    voxel_size  - Remesh resolution in scene units (default: 0.1, smaller = more detail)
    output_dir  - Where to save the result (default: next to input file)

Requires: Blender 5.0+

This is the "nuclear option" for combining multiple meshes that are touching
but not overlapping. Destroys original topology but guarantees a watertight result.
"""

import bpy
import os
import sys

# Add lib/ to path for helpers imports
script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(script_dir, '..', '..', 'lib')
sys.path.insert(0, lib_dir)

from helpers import (
    deselect_all,
    join_all_meshes,
    export_stl,
    benchmark_start,
    benchmark_log,
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
    require_meshes,
)


def voxel_remesh(obj, voxel_size):
    """Apply voxel remesh to make mesh watertight."""
    deselect_all()
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.context.object.data.remesh_voxel_size = voxel_size
    bpy.ops.object.voxel_remesh()

    vert_count = len(obj.data.vertices)
    face_count = len(obj.data.polygons)
    print(f"Remeshed: {vert_count:,} verts, {face_count:,} faces")

    return obj


def main():
    parser = create_parser("Join all meshes and voxel remesh into single watertight mesh")
    parser.add_argument(
        '--voxel-size', type=float, default=0.1,
        help='Remesh resolution in scene units (default: 0.1, smaller = more detail)'
    )
    args = parse_args(parser)
    voxel_size = args.namespace.voxel_size

    # Load model
    load_model(args)
    output_dir = setup_output_dir(args)
    output_path = os.path.join(output_dir, f"{args.base_name}_merged.stl")

    print(f"Voxel size: {voxel_size}")
    print(f"Output: {output_path}")
    print()

    timer = benchmark_start()

    # Step 1: Join all meshes
    meshes = require_meshes()
    print(f"Joining {len(meshes)} mesh(es)...")
    obj = join_all_meshes()
    if obj:
        print(f"Joined into: {obj.name}")
    timer = benchmark_log(timer, "Join completed")

    # Step 2: Voxel remesh
    print(f"Applying voxel remesh (size={voxel_size})...")
    obj = voxel_remesh(obj, voxel_size)
    timer = benchmark_log(timer, "Remesh completed")

    # Step 3: Export
    deselect_all()
    obj.select_set(True)
    export_stl(output_path, selection_only=True)
    print(f"Exported: {output_path}")
    benchmark_log(timer, "Export completed")

    print("\nDone!")


if __name__ == "__main__":
    main()
