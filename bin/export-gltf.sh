#!/bin/bash
# export-gltf.sh - Export mesh objects to GLTF (web-ready)
#
# Usage:
#   ./export-gltf.sh model.fbx
#   ./export-gltf.sh model.fbx /output/dir/
#   ./export-gltf.sh model.fbx /output/dir/ --single

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/export/export-gltf.py"

if [ -z "$1" ]; then
    echo "Usage: export-gltf.sh <model.stl|fbx|obj|blend> [output_dir] [--selected] [--single] [--no-cleanup]"
    echo ""
    echo "  --selected    Only export selected objects"
    echo "  --single      Export entire scene as single GLTF"
    echo "  --no-cleanup  Skip animation/transform cleanup"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"
echo "Using Blender: $BLENDER"
echo "Processing: $INPUT_FILE"

# Pass all args to python script
"$BLENDER" --background --python "$SCRIPT" -- "$@"
