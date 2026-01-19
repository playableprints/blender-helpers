#!/bin/bash
# voxel-merge.sh - Join all meshes and voxel remesh into watertight STL
#
# Usage:
#   ./voxel-merge.sh model.fbx
#   ./voxel-merge.sh model.fbx 0.05
#   ./voxel-merge.sh model.fbx 0.05 /output/dir/

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/repair/voxel-merge.py"

if [ -z "$1" ]; then
    echo "Usage: voxel-merge.sh <model.stl|fbx|obj|blend> [voxel_size] [output_dir]"
    echo ""
    echo "  voxel_size  - Remesh resolution (default: 0.1, smaller = more detail)"
    echo "  output_dir  - Where to save result (default: next to input file)"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"
echo "Using Blender: $BLENDER"
echo "Processing: $INPUT_FILE"

# Pass all args to python script
"$BLENDER" --background --python "$SCRIPT" -- "$@"
