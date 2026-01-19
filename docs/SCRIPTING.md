# Writing Your Own Blender Scripts

This guide helps you create custom scripts using the blender-helpers library. You don't need deep Blender or Python knowledge — just copy the template and modify it.

## Quick Start Template

Copy this template to create a new script:

```python
"""
my-script.py - [Describe what your script does]

Usage:
    blender --background --python my-script.py -- model.stl
    blender --background --python my-script.py -- model.fbx /output/dir/
    blender --background --python my-script.py -- model.stl --my-option

Requires: Blender 5.0+
"""

import os
import sys

# =============================================================================
# Setup: This block lets Python find the helpers library.
# Copy this exactly to any new script you create.
# =============================================================================
script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(script_dir, '..', '..', 'lib')
sys.path.insert(0, lib_dir)

# =============================================================================
# Imports: Pick what you need from the helpers library.
# See "Available Functions" below for the full list.
# =============================================================================
from helpers import (
    create_parser,
    parse_args,
    load_model,
    setup_output_dir,
    require_meshes,
    deselect_all,
    export_stl,
)


def main():
    # -------------------------------------------------------------------------
    # 1. Parse command-line arguments
    # -------------------------------------------------------------------------
    parser = create_parser("Description shown in --help")

    # Add your own options (optional):
    parser.add_argument(
        '--my-option', type=float, default=1.0,
        help='Description of what this option does (default: 1.0)'
    )
    parser.add_argument(
        '--dry-run', action='store_true',
        help='Preview changes without saving'
    )

    args = parse_args(parser)

    # Access your options:
    my_value = args.namespace.my_option
    is_dry_run = args.namespace.dry_run

    # -------------------------------------------------------------------------
    # 2. Load the model and set up output directory
    # -------------------------------------------------------------------------
    if not args.input_file:
        parser.print_help()
        sys.exit(1)

    load_model(args)
    output_dir = setup_output_dir(args)

    # -------------------------------------------------------------------------
    # 3. Get mesh objects and do your work
    # -------------------------------------------------------------------------
    meshes = require_meshes()  # Exits if no meshes found

    print(f"Processing {len(meshes)} mesh(es)...")

    for obj in meshes:
        print(f"  Working on: {obj.name}")

        # YOUR CODE HERE: Do something with obj
        # Example: obj.scale = (2.0, 2.0, 2.0)

    # -------------------------------------------------------------------------
    # 4. Export results (optional)
    # -------------------------------------------------------------------------
    if not is_dry_run:
        for obj in meshes:
            deselect_all()
            obj.select_set(True)
            filepath = os.path.join(output_dir, f"{obj.name}.stl")
            export_stl(filepath, selection_only=True)
            print(f"  Exported: {filepath}")

    print("\nDone!")


if __name__ == "__main__":
    main()
```

## Understanding Blender's Python API

All `bpy.*` calls are Blender's Python API. Here's a quick reference:

### Key Concepts

| Concept | What It Means |
|---------|---------------|
| `bpy.data.objects` | All objects in the scene (meshes, cameras, lights, etc.) |
| `bpy.context` | The current state (what's selected, active object, etc.) |
| `bpy.ops` | Operations (like menu actions: import, export, transform) |
| `obj.data` | The actual mesh data (vertices, faces) for a mesh object |

### Common Patterns

```python
import bpy

# Get all mesh objects
meshes = [obj for obj in bpy.data.objects if obj.type == 'MESH']

# Select an object
obj.select_set(True)
bpy.context.view_layer.objects.active = obj  # Make it the "active" object

# Deselect all
bpy.ops.object.select_all(action='DESELECT')

# Enter edit mode (to modify mesh geometry)
bpy.ops.object.mode_set(mode='EDIT')

# Return to object mode
bpy.ops.object.mode_set(mode='OBJECT')

# Apply all transformations (scale, rotation, location)
bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
```

### Official Documentation

For detailed API reference:
- **Blender Python API**: https://docs.blender.org/api/current/
- **bpy.ops reference**: https://docs.blender.org/api/current/bpy.ops.html
- **bpy.types.Object**: https://docs.blender.org/api/current/bpy.types.Object.html

## Available Helper Functions

### Argument Parsing & Setup

```python
from helpers import create_parser, parse_args, load_model, setup_output_dir, require_meshes

# Create argument parser with input_file and output_dir already defined
parser = create_parser("My script description")
parser.add_argument('--my-flag', action='store_true')
parser.add_argument('--my-value', type=float, default=1.0)

args = parse_args(parser)
# args.input_file      - Input file path (or None)
# args.output_dir      - Output directory (or None)
# args.base_name       - Input filename without extension
# args.namespace       - argparse namespace with your custom args

load_model(args)              # Import the model file
output_dir = setup_output_dir(args)  # Ensure output dir exists
meshes = require_meshes()     # Get meshes, exit if none found
```

### Object Selection

```python
from helpers import deselect_all, select_by_name, get_mesh_objects, get_selected_meshes

deselect_all()                # Clear all selections
get_mesh_objects()            # List of all mesh objects in scene
get_selected_meshes()         # List of currently selected meshes
select_by_name("Cube")        # Select object by name
```

### Object Manipulation

```python
from helpers import join_all_meshes, apply_transforms, clear_animation, clear_scene

join_all_meshes()             # Merge all meshes into one object
apply_transforms(obj)         # Apply location/rotation/scale
clear_animation(obj)          # Remove animation data
clear_scene()                 # Remove all objects from scene
```

### Import/Export

```python
from helpers import import_model, export_stl, export_obj, export_gltf, save_blend

import_model("model.fbx")     # Import any supported format
export_stl("out.stl")         # Export to STL
export_obj("out.obj")         # Export to OBJ
export_gltf("out")            # Export to GLTF/GLB (adds .glb extension)
save_blend("scene.blend")     # Save as .blend file
```

### Mesh Repair

```python
from helpers import fix_normals, make_manifold, hollow_mesh, voxel_remesh

fix_normals(obj)              # Recalculate normals to point outward
make_manifold(obj)            # Fix holes, loose geometry, etc.
hollow_mesh(obj, wall=2.0)    # Hollow for resin printing
voxel_remesh(obj, size=0.1)   # Voxel remesh (destroys topology)
```

### Mesh Analysis

```python
from helpers import analyze_mesh, calculate_volume, calculate_area

issues = analyze_mesh(obj)
# issues.is_manifold          - True if watertight
# issues.non_manifold_edges   - Count of problem edges
# issues.flipped_normals      - Count of inward-facing faces
# issues.island_count         - Number of disconnected parts

volume = calculate_volume(obj)   # Volume in cm³
area = calculate_area(obj)       # Surface area in cm² (needs Print3D addon)
```

### Geometry

```python
from helpers import get_bounding_box_mm, center_object, origin_to_bottom, is_y_up

dims = get_bounding_box_mm(obj)  # {'x': w, 'y': d, 'z': h, 'max': max_dim}
center_object(obj)               # Move object to world origin
origin_to_bottom(obj)            # Set origin to bottom center
is_y_up(obj)                     # True if model uses Y-up convention
```

### Boolean Operations

```python
from helpers import boolean_union, boolean_subtract

boolean_union(obj_a, obj_b)      # Merge two meshes
boolean_subtract(obj_a, obj_b)   # Subtract obj_b from obj_a
```

### Utilities

```python
from helpers import clean_name, get_basename, benchmark_start, benchmark_log

clean_name("Mesh.001")           # Returns "Mesh" (removes .001 suffix)
get_basename("/path/to/file.stl")  # Returns "file"

timer = benchmark_start()
# ... do work ...
timer = benchmark_log(timer, "Step completed")  # Prints elapsed time
```

## Creating a Shell Wrapper

After creating your script, add shell wrappers for easy command-line use.

### Mac/Linux (bin/my-script.sh)

```bash
#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

require_blender

if [ -z "$1" ]; then
    echo "Usage: $0 <model_file> [output_dir] [options]"
    exit 1
fi

require_file "$1"

"$BLENDER" --background --python "$SCRIPT_DIR/../scripts/category/my-script.py" -- "$@"
```

### Windows (bin/my-script.ps1)

```powershell
param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [string]$OutputDir,
    [switch]$MyFlag
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
. "$ScriptDir\common.ps1"

Require-Blender
Require-File $InputFile

$Args = @($InputFile)
if ($OutputDir) { $Args += $OutputDir }
if ($MyFlag) { $Args += "--my-flag" }

& $Blender --background --python "$ScriptDir\..\scripts\category\my-script.py" -- @Args
```

## Tips

1. **Test interactively first**: Open Blender, go to Scripting workspace, and test your bpy code in the Python console before putting it in a script.

2. **Print debugging**: Use `print()` liberally — output appears in the terminal when running with `--background`.

3. **Check object mode**: Many operations require being in OBJECT mode. If something fails, try:
   ```python
   bpy.ops.object.mode_set(mode='OBJECT')
   ```

4. **Selection matters**: Most `bpy.ops` functions work on selected objects. Always select what you want to modify.

5. **Error messages**: If Blender exits with an error, run without `--background` to see the full error in Blender's UI.
