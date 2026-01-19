#!/bin/bash
# render-snapshot.sh - Render a single snapshot of a model
#
# Usage:
#   ./render-snapshot.sh model.stl
#   ./render-snapshot.sh model.stl /output/dir/

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/render/render-snapshot.py"
TEMPLATE="$REPO_ROOT/templates/turntable.blend"

if [ -z "$1" ]; then
    echo "Usage: render-snapshot.sh <model.stl|fbx|obj> [output_dir]"
    echo ""
    echo "  output_dir - Where to save render (default: next to model)"
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
