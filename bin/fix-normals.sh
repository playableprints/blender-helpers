#!/bin/bash
# fix-normals.sh - Fix normals and export all meshes to STL
#
# Usage:
#   ./fix-normals.sh model.fbx
#   ./fix-normals.sh model.stl /output/dir/

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/repair/fix-normals.py"

if [ -z "$1" ]; then
    echo "Usage: fix-normals.sh <model.stl|fbx|obj|blend> [output_dir]"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"
echo "Using Blender: $BLENDER"
echo "Processing: $INPUT_FILE"

# Pass all args to python script
"$BLENDER" --background --python "$SCRIPT" -- "$@"
