# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Command-line tools for automating Blender 3D workflows, focused on 3D printing preparation and rendering. Requires **Blender 5.0+**.

## Running Scripts

Scripts are run via Blender's Python interpreter. Shell wrappers in `bin/` handle Blender discovery:

```bash
# Via shell wrapper (recommended)
./bin/fix-normals.sh model.fbx

# Direct invocation
blender --background --python scripts/repair/fix-normals.py -- model.fbx [output_dir] [options]
```

Arguments after `--` are passed to the Python script. Use `--help` on any script for options.

## Architecture

### Script Pattern

All scripts follow a consistent structure:

1. **Path setup** - Add `lib/` to Python path for helper imports
2. **Argument parsing** - Use `create_parser()` / `parse_args()` from helpers
3. **Model loading** - `load_model(args)` imports or opens the file
4. **Processing** - Work with mesh objects via `require_meshes()`
5. **Export** - Use `export_stl()`, `export_obj()`, etc.

```python
script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(script_dir, '..', '..', 'lib')
sys.path.insert(0, lib_dir)

from helpers import create_parser, parse_args, load_model, require_meshes
```

### Helper Library (`lib/helpers/`)

Core modules:
- **script_utils.py** - `ScriptArgs` dataclass, `create_parser()`, `parse_args()`, `load_model()`, `require_meshes()`
- **mesh_repair.py** - `fix_normals()`, `make_manifold()`, `hollow_mesh()`, `voxel_remesh()`
- **mesh_analysis.py** - `MeshIssues` dataclass, `analyze_mesh()`, `calculate_volume()`, `calculate_area()`
- **io.py** - `import_model()`, `export_stl()`, `export_obj()`, `export_gltf()`
- **geometry.py** - `get_bounding_box_mm()`, `center_object()`, `origin_to_bottom()`
- **selection.py** - `get_mesh_objects()`, `deselect_all()`, `select_by_name()`
- **objects.py** - `join_all_meshes()`, `apply_transforms()`, `clear_scene()`

### Shell Wrappers (`bin/`)

- `common.sh` / `common.ps1` - Shared functions (`find_blender`, `require_blender`, `require_file`)
- Each script has `.sh` (bash) and `.ps1` (PowerShell) wrappers

## Key Conventions

- Scripts use Blender's `--background` mode (headless)
- All scripts accept: `input_file [output_dir] [options]`
- Output defaults to same directory as input file
- Mesh analysis uses Print3D Toolbox addon when available (optional)
- Input formats: STL, OBJ, FBX, GLTF/GLB, .blend

## Testing Scripts

No automated test suite. Test manually:

```bash
# Test with sample model
blender --background --python scripts/repair/fix-normals.py -- /path/to/test.stl

# View help
blender --background --python scripts/repair/hollow.py -- --help
```
