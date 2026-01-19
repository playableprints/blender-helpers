"""
fix-normals.py - Recalculate normals for all mesh objects and export to STL

Usage:
    blender --background myfile.blend --python fix-normals.py
    blender --background --python fix-normals.py -- model.fbx
    blender --background --python fix-normals.py -- model.stl /output/dir/

Requires: Blender 5.0+

Exports each mesh object as STL next to the input file (or to specified output dir).
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
    fix_normals,
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
    require_meshes,
)


def main():
    parser = create_parser("Recalculate normals and export to STL")
    args = parse_args(parser)
    load_model(args)
    output_dir = setup_output_dir(args)

    meshes = require_meshes()
    print(f"Processing {len(meshes)} mesh object(s)...")

    for obj in meshes:
        print(f"  Fixing normals: {obj.name}")
        fix_normals(obj)

        # Export
        deselect_all()
        obj.select_set(True)
        filename = clean_name(obj.name) + ".stl"
        filepath = os.path.join(output_dir, filename)
        export_stl(filepath, selection_only=True)
        print(f"  Exported: {filepath}")

    print(f"\nDone. {len(meshes)} file(s) exported to: {output_dir}")


if __name__ == "__main__":
    main()
