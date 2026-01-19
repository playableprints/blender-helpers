#!/bin/bash
# render-360.sh - Render 360° turntable animation
#
# Usage:
#   ./render-360.sh model.stl
#   ./render-360.sh model.stl 24
#   ./render-360.sh model.stl 24 /output/dir/
#   ./render-360.sh model.stl --gif

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/render/render-360.py"
TEMPLATE="$REPO_ROOT/templates/turntable.blend"

if [ -z "$1" ]; then
    echo "Usage: render-360.sh <model.stl|fbx|obj> [frames] [output_dir] [--gif]"
    echo ""
    echo "  frames     - Number of frames (default: 15)"
    echo "  output_dir - Where to save renders (default: next to model)"
    echo "  --gif      - Create animated GIF from frames"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"
echo "Using Blender: $BLENDER"
echo "Model: $INPUT_FILE"

# Use template if it exists
if [ -f "$TEMPLATE" ]; then
    "$BLENDER" --background "$TEMPLATE" --python "$SCRIPT" -- "$@"
else
    "$BLENDER" --background --python "$SCRIPT" -- "$@"
fi
