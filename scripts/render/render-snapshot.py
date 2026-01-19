"""
render-snapshot.py - Render a single frame snapshot of a model

Usage:
    blender --background --python render-snapshot.py -- model.stl
    blender --background --python render-snapshot.py -- model.stl /output/dir/
    blender --background --python render-snapshot.py -- model.stl --rotation 45
    blender --background --python render-snapshot.py -- model.stl --samples 256
    blender --background --python render-snapshot.py -- model.stl --cpu
    blender --background template.blend --python render-snapshot.py -- model.stl

Arguments (after --):
    model_path  - STL/OBJ file to render (required)
    output_dir  - Where to save render (default: next to model file)
    --rotation  - Rotation angle in degrees around Z axis (default: 35)
    --cpu       - Use CPU rendering instead of GPU (GPU is default)
    --samples   - Number of render samples (default: from template, typically 128)

Requires: Blender 5.0+

If no template .blend is provided, uses templates/turntable.blend from this repo.
"""

import bpy
import os
import sys
import math

# Add lib/ to path for helpers imports
script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(script_dir, '..', '..', 'lib')
templates_dir = os.path.join(script_dir, '..', '..', 'templates')
sys.path.insert(0, lib_dir)

from helpers import (
    deselect_all,
    import_model,
    benchmark_start,
    benchmark_log,
    get_basename,
    is_y_up,
    center_object,
    create_parser,
    parse_args,
    apply_material,
    frame_camera_to_object,
    render_frame,
    setup_gpu_rendering,
    set_render_samples,
)


def main():
    parser = create_parser("Render a single snapshot of a model")
    parser.add_argument(
        '--rotation', type=float, default=35,
        help='Rotation angle in degrees around Z axis (default: 35)'
    )
    parser.add_argument(
        '--cpu', action='store_true',
        help='Use CPU rendering instead of GPU (GPU is default)'
    )
    parser.add_argument(
        '--samples', type=int, default=None,
        help='Number of render samples (default: use template setting)'
    )
    args = parse_args(parser)

    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    model_path = args.input_file
    rotation_degrees = args.namespace.rotation
    use_cpu = args.namespace.cpu
    samples = args.namespace.samples
    output_dir = args.output_dir or os.path.dirname(model_path) or os.getcwd()

    os.makedirs(output_dir, exist_ok=True)

    base_name = get_basename(model_path)
    output_path = os.path.join(output_dir, f"{base_name}.png")

    # If no blend file was loaded, try to load template
    if not bpy.data.filepath:
        template = os.path.join(templates_dir, "turntable.blend")
        if os.path.exists(template):
            print(f"Loading template: {template}")
            bpy.ops.wm.open_mainfile(filepath=template)
        else:
            print("Warning: No template found, using default scene")

    # Configure rendering
    if not use_cpu:
        setup_gpu_rendering()
    if samples:
        set_render_samples(samples)

    print(f"Model: {model_path}")
    print(f"Output: {output_path}")
    print()

    timer = benchmark_start()

    # Import model
    print("Importing model...")
    imported = import_model(model_path)
    if not imported:
        print("Error: No mesh imported")
        sys.exit(1)
    obj = imported[0]
    timer = benchmark_log(timer, "Import completed")

    # Detect and fix orientation
    if is_y_up(obj):
        print("Y-Up detected, rotating to Z-Up...")
        obj.rotation_euler[0] = math.pi / 2
        deselect_all()
        obj.select_set(True)
        bpy.ops.object.transform_apply(rotation=True)
    else:
        print("Z-Up detected, no rotation needed")

    # Center and set up
    center_object(obj)
    apply_material(obj)

    # Apply rotation for better viewing angle
    if rotation_degrees != 0:
        obj.rotation_euler[2] = math.radians(rotation_degrees)
    timer = benchmark_log(timer, "Setup completed")

    # Frame camera
    frame_camera_to_object(obj)

    # Render single frame
    print("Rendering snapshot...")
    render_frame(output_path)
    benchmark_log(timer, "Render completed")

    print(f"\nDone! Snapshot saved to: {output_path}")


if __name__ == "__main__":
    main()
