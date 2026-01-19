#!/bin/bash
# export-stl.sh - Export mesh objects to STL
#
# Usage:
#   ./export-stl.sh model.fbx
#   ./export-stl.sh model.fbx /output/dir/
#   ./export-stl.sh model.fbx /output/dir/ --single

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/export/export-stl.py"

if [ -z "$1" ]; then
    echo "Usage: export-stl.sh <model.stl|fbx|obj|blend> [output_dir] [--selected] [--single]"
    echo ""
    echo "  --selected  Only export selected objects"
    echo "  --single    Export all as single combined file"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"
echo "Using Blender: $BLENDER"
echo "Processing: $INPUT_FILE"

# Pass all args to python script
"$BLENDER" --background --python "$SCRIPT" -- "$@"
