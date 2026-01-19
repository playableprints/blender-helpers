"""
render-snapshot.py - Render a single frame snapshot of a model

Usage:
    blender --background --python render-snapshot.py -- model.stl
    blender --background --python render-snapshot.py -- model.stl /output/dir/
    blender --background template.blend --python render-snapshot.py -- model.stl

Arguments (after --):
    model_path  - STL/OBJ file to render (required)
    output_dir  - Where to save render (default: next to model file)

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
    create_framing_cube,
    create_parser,
    parse_args,
)


def apply_material(obj, material_name="Material"):
    """Apply a material to the object. Uses existing material if found."""
    material = None
    for mat_name in [material_name, "Material.002", "Material.001"]:
        material = bpy.data.materials.get(mat_name)
        if material:
            break

    if not material:
        material = bpy.data.materials.new(name="RenderMaterial")
        material.use_nodes = True

    if obj.data.materials:
        obj.data.materials[0] = material
    else:
        obj.data.materials.append(material)


def frame_camera_to_object(obj):
    """Create framing cube and aim camera at it."""
    framing_cube = create_framing_cube(obj)
    deselect_all()
    framing_cube.select_set(True)
    bpy.context.view_layer.objects.active = framing_cube

    # Frame camera to cube
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            with bpy.context.temp_override(area=area):
                bpy.ops.view3d.camera_to_view_selected()
            break

    return framing_cube


def render_snapshot(output_path):
    """Render a single frame to the specified path."""
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    bpy.context.scene.render.filepath = output_path
    bpy.ops.render.render(write_still=True)
    print(f"Rendered: {output_path}")


def main():
    parser = create_parser("Render a single snapshot of a model")
    args = parse_args(parser)

    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    model_path = args.input_file
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
    timer = benchmark_log(timer, "Setup completed")

    # Frame camera
    frame_camera_to_object(obj)

    # Render single frame
    print("Rendering snapshot...")
    render_snapshot(output_path)
    benchmark_log(timer, "Render completed")

    print(f"\nDone! Snapshot saved to: {output_path}")


if __name__ == "__main__":
    main()
