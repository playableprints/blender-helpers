# Blender Helpers

A collection of command-line tools for automating Blender workflows, focused on 3D printing and rendering pipelines.

**Requires: Blender 5.0+**

## Quick Start

```bash
# Fix inverted normals and export to STL
./bin/fix-normals.sh model.fbx

# Merge multiple touching meshes into one watertight model
./bin/voxel-merge.sh parts.fbx 0.05

# Make a mesh manifold (watertight) for 3D printing
./bin/make-manifold.sh model.stl

# Hollow a model for resin printing
./bin/hollow.sh model.stl 2.0

# Render a 360° turntable animation (with optional animated GIF)
./bin/render-360.sh model.stl --gif

# Render a single snapshot (auto-orients and frames camera)
./bin/render-snapshot.sh model.stl

# Check various things about a model, including it's hollowed status
./bin/analyze-for-print.sh model.stl
```

**Note:** These scripts by default output to <inputFileName>.stl and they *will* overwrite the input file if it's set to STL. You can set the output file path using the second argument (see below for more details).

## Installation

1. Clone or download this repository
2. Ensure Blender 5.0+ is installed and either:
   - Added to your system PATH, or
   - Installed in the default location (`/Applications/Blender.app` on Mac, `C:\Program Files\Blender Foundation\Blender 5.0` on Windows)

## Input Formats

All scripts accept multiple input formats:
- **STL** - Common 3D printing format
- **OBJ** - Wavefront OBJ
- **FBX** - Autodesk interchange format (common for purchased models)
- **GLTF/GLB** - Web-ready format
- **blend** - Native Blender files

## Tools

### Repair Tools

#### fix-normals
Recalculates normals (fixes inside-out faces) for all mesh objects and exports each as STL.

```bash
./bin/fix-normals.sh model.fbx                      # Output next to input
./bin/fix-normals.sh model.stl /path/to/output/     # Custom output dir
```

#### voxel-merge
Joins all objects and applies voxel remesh to create a single watertight mesh. This is the "nuclear option" for combining meshes that are touching but not overlapping (where Boolean union fails).

```bash
./bin/voxel-merge.sh model.fbx                      # Default voxel size (0.1)
./bin/voxel-merge.sh model.fbx --voxel-size 0.05    # Finer detail (slower)
./bin/voxel-merge.sh model.fbx /output/ --voxel-size 0.05  # Custom output dir
```

**Note:** Smaller voxel size = more detail but higher poly count. Start with 0.1 and decrease if you're losing detail.

#### make-manifold
Fixes non-manifold geometry (holes, loose vertices, non-manifold edges) to make a mesh watertight for 3D printing.

```bash
./bin/make-manifold.sh model.stl                    # Output next to input
./bin/make-manifold.sh model.stl /output/           # Custom output dir
```

#### hollow
Hollows a solid model for resin printing by adding a solidify modifier. Reduces resin usage and print time. You will need to add drain holes as a separate step.

```bash
./bin/hollow.sh model.stl                           # Default wall thickness (2mm)
./bin/hollow.sh model.stl --wall-thickness 1.5      # 1.5mm wall thickness
./bin/hollow.sh model.stl /output/ --wall-thickness 2.0  # Custom output dir
```

**Note:** Model should be manifold before hollowing. Run `make-manifold.sh` first if needed.

### Render Tools

#### render-360
Imports a model, auto-orients it, and renders a 360° turntable animation.

```bash
./bin/render-360.sh model.stl                       # Uses default template, 15 frames
./bin/render-360.sh model.stl --frames 24           # 24 frames
./bin/render-360.sh model.stl /output/ --frames 24  # Custom output dir
./bin/render-360.sh model.stl --gif                 # Create animated GIF
./bin/render-360.sh model.stl /output/ --frames 24 --gif  # All options
```

Output: PNG sequence (`model_0001.png`, `model_0002.png`, etc.)

With `--gif`: Also creates `model.gif` using ImageMagick or FFmpeg (if installed).

#### render-snapshot
Imports a model, auto-detects orientation (Y-up vs Z-up), orients it correctly, rotates for a better viewing angle, and renders a single frame.

```bash
./bin/render-snapshot.sh model.stl                  # Uses default template, 35° rotation
./bin/render-snapshot.sh model.stl /output/         # Custom output dir
./bin/render-snapshot.sh model.stl --rotation 45    # Custom rotation angle
./bin/render-snapshot.sh model.stl --rotation 0     # Face-on view (no rotation)
```

Output: Single PNG (`model.png`)

### Analyze Tools

#### analyze-for-print
Checks model properties and recommends whether to hollow for resin printing. Analyzes mesh quality, detects issues, and suggests repair scripts.

```bash
./bin/analyze-for-print.sh model.stl
```

Output:
```
Dimensions: 45.2 x 32.1 x 72.3 mm
Volume: 45.2 cm³
Resin estimate: 45.2 mL ($1.36-$2.26)

Mesh Quality:
  Manifold: Yes (watertight)
  Normals: OK
  Islands: 1 (single connected mesh)

>>> RECOMMENDATION: HOLLOW
    Wall thickness: 1.5 mm
    - Volume (45.2 cm³) exceeds 10 cm³

============================================================
No repairs needed - model is print-ready!
```

If issues are found, suggests repair scripts:
```
SUGGESTED REPAIRS:
----------------------------------------
  fix-normals.sh / fix-normals.ps1
    Recalculate normals to fix flipped faces

  make-manifold.sh / make-manifold.ps1
    Fix non-manifold geometry and holes
```

### Export Tools

#### export-stl / export-obj / export-gltf
Export mesh objects with automatic filename cleanup.

```bash
./bin/export-stl.sh model.fbx                       # FBX -> STL
./bin/export-stl.sh model.fbx /output/              # Custom output dir
./bin/export-stl.sh model.fbx /output/ --single     # All meshes as one file
./bin/export-stl.sh model.fbx /output/ --selected   # Only selected objects
./bin/export-gltf.sh model.fbx /output/             # FBX -> GLTF (web-ready)
./bin/export-gltf.sh model.fbx /output/ --no-cleanup  # Keep animations
```

## Windows (PowerShell)

All tools have PowerShell equivalents:

```powershell
.\bin\fix-normals.ps1 model.fbx
.\bin\voxel-merge.ps1 model.fbx -VoxelSize 0.05
.\bin\make-manifold.ps1 model.stl
.\bin\hollow.ps1 model.stl -Thickness 2.0
.\bin\render-360.ps1 model.stl -Frames 24 -Gif
.\bin\render-snapshot.ps1 model.stl -Rotation 45
.\bin\analyze-for-print.ps1 model.stl
.\bin\export-stl.ps1 model.fbx -Single
.\bin\export-gltf.ps1 model.fbx -OutputDir C:\output
```

## Pipelines

Chain tools together for common workflows:

### Downloaded FBX to print-ready STL
```bash
# Full pipeline: analyze, fix issues, hollow if needed
./bin/analyze-for-print.sh character.fbx
./bin/fix-normals.sh character.fbx ./output/
./bin/make-manifold.sh ./output/character.stl
./bin/hollow.sh ./output/character.stl --wall-thickness 1.5
```

### Multiple parts to single watertight model
```bash
# When Boolean union fails on touching-but-not-overlapping meshes
./bin/voxel-merge.sh assembled-parts.fbx ./output/ --voxel-size 0.05
```

### FBX to web-ready GLTF
```bash
# Clean up animations/transforms and export for web viewer
./bin/export-gltf.sh character.fbx ./web-assets/
```

### Batch process a folder
```bash
# Fix normals on all FBX files in a directory
for f in ./models/*.fbx; do
    ./bin/fix-normals.sh "$f" ./fixed/
done
```

### Create turntable GIF for product showcase
```bash
./bin/render-360.sh product.stl ./renders/ --frames 24 --gif
# Creates: product_0001.png through product_0024.png + product.gif
```

## Running Scripts Directly

You can also run the Python scripts directly with Blender:

```bash
blender --background --python scripts/repair/fix-normals.py -- model.fbx
blender --background --python scripts/repair/voxel-merge.py -- model.fbx --voxel-size 0.05
blender --background --python scripts/repair/make-manifold.py -- model.stl
blender --background --python scripts/repair/hollow.py -- model.stl --wall-thickness 2.0
blender --background --python scripts/render/render-snapshot.py -- model.stl

# Get help for any script:
blender --background --python scripts/repair/hollow.py -- --help
```

Arguments after `--` are passed to the script. Use `--help` to see available options.

## Project Structure

```
blender-helpers/
├── bin/                    # Shell wrappers (.sh for Mac/Linux, .ps1 for Windows)
│   ├── common.sh           # Shared shell functions
│   └── common.ps1          # Shared PowerShell functions
├── docs/
│   └── SCRIPTING.md        # Guide for writing your own scripts
├── lib/
│   └── helpers/            # Python helper modules
│       ├── __init__.py
│       ├── selection.py    # Object selection helpers
│       ├── objects.py      # Object manipulation
│       ├── boolean.py      # Boolean operations
│       ├── io.py           # Import/export
│       ├── naming.py       # Filename helpers
│       ├── benchmark.py    # Timing utilities
│       ├── script_utils.py # Argument parsing, model loading
│       ├── geometry.py     # Bounding box, centering, orientation
│       ├── mesh_repair.py  # Normals, manifold, hollowing
│       └── mesh_analysis.py # Volume, area, mesh quality checks
├── scripts/
│   ├── analyze/            # Model analysis tools
│   ├── export/             # Format exporters
│   ├── render/             # Rendering tools
│   └── repair/             # Mesh repair tools
├── templates/
│   └── turntable.blend     # Pre-configured render scene
└── archive/                # Original project-specific scripts (reference only)
```

## Writing Your Own Scripts

Want to create custom scripts? See **[docs/SCRIPTING.md](docs/SCRIPTING.md)** for:

- Copy-paste starter template
- Complete list of helper functions
- Blender Python API basics
- How to create shell wrappers

## Troubleshooting

**"Blender not found"**
- Add Blender to your PATH, or
- Edit `bin/common.sh` / `bin/common.ps1` to add your Blender location

**"No mesh objects found"**
- The file might only contain cameras/lights/armatures
- Check the file in Blender's UI first

**Voxel remesh is too slow / runs out of memory**
- Increase voxel size (e.g., 0.2 instead of 0.1)
- Close other applications
- Consider decimating the source meshes first

**Print3D Toolbox operators not found**
- Enable the addon: Edit > Preferences > Add-ons > search "3D Print"

**FBX imports with wrong scale**
- FBX files can have varying scale factors
- Check the model in Blender first, then adjust or apply scale

**GIF creation fails**
- Install ImageMagick (`brew install imagemagick` / `choco install imagemagick`) or
- Install FFmpeg (`brew install ffmpeg` / `choco install ffmpeg`)
- The script will print manual commands if neither is found

## License

MIT License. See [LICENSE.txt](./LICENSE.txt)

The turntable template image courtesy calculuschild of PPL Discord.
