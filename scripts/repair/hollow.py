"""
hollow.py - Hollow out a solid model for resin printing

Usage:
    blender --background --python hollow.py -- model.stl
    blender --background --python hollow.py -- model.stl 2.0
    blender --background --python hollow.py -- model.stl 2.0 /output/dir/

Arguments (after --):
    model_path   - STL/OBJ/FBX file to hollow (required)
    wall_thickness - Wall thickness in mm (default: 2.0)
    output_dir   - Where to save result (default: next to model)

Requires: Blender 5.0+

Uses Solidify modifier with negative offset to create hollow interior.
This reduces resin usage and print time for resin printing.
"""

import os
import sys

# Add lib/ to path for helpers imports
script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(script_dir, '..', '..', 'lib')
sys.path.insert(0, lib_dir)

from helpers import (
    deselect_all,
    export_stl,
    clean_name,
    hollow_mesh,
    clear_scene,
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
    require_meshes,
)


def main():
    parser = create_parser("Hollow out a solid model for resin printing")
    parser.add_argument(
        '--wall-thickness', type=float, default=2.0,
        help='Wall thickness in mm (default: 2.0)'
    )
    args = parse_args(parser)
    wall_thickness = args.namespace.wall_thickness

    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    clear_scene()

    load_model(args)
    output_dir = setup_output_dir(args)

    meshes = require_meshes()
    print(f"Processing {len(meshes)} mesh object(s)...")
    print(f"Wall thickness: {wall_thickness}mm")

    for obj in meshes:
        print(f"  Hollowing: {obj.name}")
        hollow_mesh(obj, wall_thickness)

        # Export
        deselect_all()
        obj.select_set(True)
        filename = clean_name(obj.name) + "_hollow.stl"
        filepath = os.path.join(output_dir, filename)
        export_stl(filepath, selection_only=True)
        print(f"  Exported: {filepath}")

    print(f"\nDone. {len(meshes)} file(s) exported to: {output_dir}")


if __name__ == "__main__":
    main()
