"""
render-360.py - Render a 360° turntable animation of a model

Usage:
    blender --background --python render-360.py -- model.stl
    blender --background --python render-360.py -- model.stl 24
    blender --background --python render-360.py -- model.stl 24 /output/dir/
    blender --background --python render-360.py -- model.stl --gif
    blender --background template.blend --python render-360.py -- model.stl

Arguments (after --):
    model_path  - STL/OBJ file to render (required)
    frames      - Number of frames in animation (default: 15)
    output_dir  - Where to save renders (default: next to model file)
    --gif       - Create animated GIF from rendered frames (requires ImageMagick or FFmpeg)

Requires: Blender 5.0+

If no template .blend is provided, uses templates/turntable.blend from this repo.
"""

import bpy
import os
import sys
import math
import subprocess
import shutil
import glob

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


# -----------------------------------------------------------------------------
# Material / Rendering
# -----------------------------------------------------------------------------

def apply_material(obj, material_name="Material"):
    """Apply a material to the object. Uses existing material if found."""
    material = None
    for mat_name in [material_name, "Material.001", "Material.002"]:
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


def setup_rotation_animation(obj, start_frame, end_frame):
    """Set up 360° rotation animation around Z axis."""
    if obj.animation_data:
        obj.animation_data_clear()

    obj.rotation_euler[2] = 0
    obj.keyframe_insert(data_path="rotation_euler", frame=start_frame)

    obj.rotation_euler[2] = 2 * math.pi
    obj.keyframe_insert(data_path="rotation_euler", frame=end_frame)

    for fcurve in obj.animation_data.action.fcurves:
        for keyframe in fcurve.keyframe_points:
            keyframe.interpolation = 'LINEAR'

    bpy.context.scene.frame_start = start_frame
    bpy.context.scene.frame_end = end_frame


def render_animation(output_dir, base_name, start_frame, end_frame):
    """Render all frames of the animation. Returns list of rendered file paths."""
    bpy.context.scene.render.image_settings.file_format = 'PNG'
    rendered_files = []

    for frame in range(start_frame, end_frame + 1):
        bpy.context.scene.frame_set(frame)
        filepath = os.path.join(output_dir, f"{base_name}_{frame:04d}.png")
        bpy.context.scene.render.filepath = filepath
        bpy.ops.render.render(write_still=True)
        rendered_files.append(filepath)
        print(f"Rendered: {filepath}")

    return rendered_files


def create_gif(output_dir, base_name, frame_pattern, delay=10):
    """Create animated GIF from rendered frames using ImageMagick or FFmpeg.

    Args:
        output_dir: Directory containing the frames
        base_name: Base name for output GIF
        frame_pattern: Glob pattern for frame files (e.g., "model_*.png")
        delay: Delay between frames in centiseconds (default: 10 = 100ms)

    Returns:
        Path to created GIF, or None if creation failed
    """
    gif_path = os.path.join(output_dir, f"{base_name}.gif")
    full_pattern = os.path.join(output_dir, frame_pattern)

    # Try ImageMagick first (more common, better quality)
    convert_cmd = shutil.which("convert") or shutil.which("magick")
    if convert_cmd:
        try:
            # Use magick convert on newer ImageMagick versions
            cmd = [convert_cmd]
            if "magick" in convert_cmd:
                cmd.append("convert")
            cmd.extend([
                "-delay", str(delay),
                "-loop", "0",
                full_pattern,
                gif_path
            ])
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Created GIF (ImageMagick): {gif_path}")
            return gif_path
        except subprocess.CalledProcessError as e:
            print(f"ImageMagick failed: {e.stderr.decode() if e.stderr else e}")
        except Exception as e:
            print(f"ImageMagick error: {e}")

    # Fallback to FFmpeg
    ffmpeg_cmd = shutil.which("ffmpeg")
    if ffmpeg_cmd:
        try:
            # FFmpeg needs explicit frame rate, delay is in centiseconds
            # delay=10 means 10/100 = 0.1s per frame = 10 fps
            fps = 100 / delay
            cmd = [
                ffmpeg_cmd,
                "-y",  # Overwrite output
                "-framerate", str(fps),
                "-pattern_type", "glob",
                "-i", full_pattern,
                "-vf", "split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse",
                gif_path
            ]
            subprocess.run(cmd, check=True, capture_output=True)
            print(f"Created GIF (FFmpeg): {gif_path}")
            return gif_path
        except subprocess.CalledProcessError as e:
            print(f"FFmpeg failed: {e.stderr.decode() if e.stderr else e}")
        except Exception as e:
            print(f"FFmpeg error: {e}")

    # Neither worked - print helpful message
    print()
    print("Could not create GIF automatically. Install ImageMagick or FFmpeg, or run manually:")
    print()
    print("  ImageMagick:")
    print(f"    convert -delay {delay} -loop 0 \"{full_pattern}\" \"{gif_path}\"")
    print()
    print("  FFmpeg:")
    print(f"    ffmpeg -framerate {100/delay:.0f} -pattern_type glob -i '{full_pattern}' \\")
    print(f"           -vf 'split[s0][s1];[s0]palettegen[p];[s1][p]paletteuse' \"{gif_path}\"")
    print()
    return None


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = create_parser("Render a 360° turntable animation of a model")
    parser.add_argument(
        '--frames', type=int, default=15,
        help='Number of frames in animation (default: 15)'
    )
    parser.add_argument(
        '--gif', action='store_true',
        help='Create animated GIF from rendered frames (requires ImageMagick or FFmpeg)'
    )
    args = parse_args(parser)

    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    model_path = args.input_file
    num_frames = args.namespace.frames
    make_gif = args.namespace.gif
    output_dir = args.output_dir or os.path.dirname(model_path) or os.getcwd()

    os.makedirs(output_dir, exist_ok=True)

    base_name = get_basename(model_path)
    start_frame = 1
    end_frame = num_frames

    # If no blend file was loaded, try to load template
    if not bpy.data.filepath:
        template = os.path.join(templates_dir, "turntable.blend")
        if os.path.exists(template):
            print(f"Loading template: {template}")
            bpy.ops.wm.open_mainfile(filepath=template)
        else:
            print("Warning: No template found, using default scene")

    print(f"Model: {model_path}")
    print(f"Frames: {num_frames}")
    print(f"Output: {output_dir}")
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

    # Fix orientation if needed
    if is_y_up(obj):
        print("Y-Up detected, rotating to Z-Up...")
        obj.rotation_euler[0] = math.pi / 2
        deselect_all()
        obj.select_set(True)
        bpy.ops.object.transform_apply(rotation=True)

    # Center and set up
    center_object(obj)
    apply_material(obj)

    # Create framing cube and aim camera
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

    # Set up animation
    setup_rotation_animation(obj, start_frame, end_frame)
    timer = benchmark_log(timer, "Setup completed")

    # Render
    print(f"Rendering {num_frames} frames...")
    rendered_files = render_animation(output_dir, base_name, start_frame, end_frame)
    benchmark_log(timer, "Render completed")

    # Create GIF if requested
    if make_gif:
        print()
        print("Creating animated GIF...")
        frame_pattern = f"{base_name}_*.png"
        gif_path = create_gif(output_dir, base_name, frame_pattern)
        if gif_path:
            benchmark_log(timer, "GIF created")

    print(f"\nDone! {num_frames} frames saved to: {output_dir}")


if __name__ == "__main__":
    main()
