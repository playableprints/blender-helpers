"""
export-obj.py - Export mesh objects to OBJ format

Usage:
    blender --background model.blend --python export-obj.py
    blender --background --python export-obj.py -- model.fbx
    blender --background --python export-obj.py -- model.fbx /output/dir/
    blender --background --python export-obj.py -- model.fbx /output/dir/ --selected

Arguments (after --):
    input_file   - Model file to process (STL, OBJ, FBX, or blend)
    output_dir   - Where to save files (default: next to input file)
    --selected   - Only export selected objects (default: all meshes)
    --single     - Export all as single combined OBJ
    --no-cleanup - Skip animation/transform cleanup

Requires: Blender 5.0+
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
    get_mesh_objects,
    get_selected_meshes,
    export_obj,
    clean_name,
    clear_animation,
    apply_transforms,
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
)


def cleanup_for_export(obj):
    """Prepare object for export - clear animations, apply transforms."""
    clear_animation(obj)
    apply_transforms(obj)


def main():
    parser = create_parser("Export mesh objects to OBJ format")
    parser.add_argument(
        '--selected', action='store_true',
        help='Only export selected objects (default: all meshes)'
    )
    parser.add_argument(
        '--single', action='store_true',
        help='Export all as single combined OBJ'
    )
    parser.add_argument(
        '--no-cleanup', action='store_true',
        help='Skip animation/transform cleanup'
    )
    args = parse_args(parser)
    selected_only = args.namespace.selected
    single_file = args.namespace.single
    do_cleanup = not args.namespace.no_cleanup

    load_model(args)
    output_dir = setup_output_dir(args)

    # Get objects to export
    if selected_only:
        objects = get_selected_meshes()
        if not objects:
            print("Error: No mesh objects selected")
            sys.exit(1)
    else:
        objects = get_mesh_objects()
        if not objects:
            print("Error: No mesh objects in scene")
            sys.exit(1)

    print(f"Output directory: {output_dir}")

    if single_file:
        if do_cleanup:
            for obj in objects:
                cleanup_for_export(obj)
        deselect_all()
        for obj in objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = objects[0]
        output_path = os.path.join(output_dir, f"{args.base_name}.obj")
        export_obj(output_path, selection_only=True)
        print(f"Exported: {output_path}")
        print("\nDone! Exported as single OBJ.")
    else:
        for obj in objects:
            if do_cleanup:
                cleanup_for_export(obj)

            deselect_all()
            obj.select_set(True)
            bpy.context.view_layer.objects.active = obj

            filename = clean_name(obj.name) + ".obj"
            filepath = os.path.join(output_dir, filename)
            export_obj(filepath, selection_only=True)
            print(f"Exported: {filepath}")

        print(f"\nDone! {len(objects)} object(s) exported.")


if __name__ == "__main__":
    main()
