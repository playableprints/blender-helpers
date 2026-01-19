"""
make-manifold.py - Make mesh watertight/manifold

Usage:
    blender --background --python make-manifold.py -- model.stl
    blender --background --python make-manifold.py -- model.fbx /output/dir/

Requires: Blender 5.0+

Uses various techniques to fix manifold issues:
- Merge close vertices
- Fill holes
- Fix normals
- Remove loose geometry
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
    export_stl,
    clean_name,
    make_manifold,
    clear_scene,
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
    require_meshes,
)


def main():
    parser = create_parser("Make mesh watertight/manifold for 3D printing")
    args = parse_args(parser)

    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    clear_scene()

    load_model(args)
    output_dir = setup_output_dir(args)

    meshes = require_meshes()
    print(f"Processing {len(meshes)} mesh object(s)...")

    for obj in meshes:
        print(f"  Making manifold: {obj.name}")
        make_manifold(obj)

        # Export
        deselect_all()
        obj.select_set(True)
        filename = clean_name(obj.name) + "_manifold.stl"
        filepath = os.path.join(output_dir, filename)
        export_stl(filepath, selection_only=True)
        print(f"  Exported: {filepath}")

    print(f"\nDone. {len(meshes)} file(s) exported to: {output_dir}")


if __name__ == "__main__":
    main()
