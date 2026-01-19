#!/bin/bash
# hollow.sh - Hollow out model for resin printing
#
# Usage:
#   ./hollow.sh model.stl
#   ./hollow.sh model.stl 2.0
#   ./hollow.sh model.stl 2.0 /output/dir/

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/repair/hollow.py"

if [ -z "$1" ]; then
    echo "Usage: hollow.sh <model.stl|fbx|obj|blend> [wall_thickness] [output_dir]"
    echo ""
    echo "  wall_thickness - Wall thickness in mm (default: 2.0)"
    echo "  output_dir     - Where to save result (default: next to model)"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"
echo "Using Blender: $BLENDER"
echo "Processing: $INPUT_FILE"

# Pass all args to python script
"$BLENDER" --background --python "$SCRIPT" -- "$@"
