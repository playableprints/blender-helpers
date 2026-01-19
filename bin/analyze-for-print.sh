#!/bin/bash
# analyze-for-print.sh - Analyze model for 3D printing
#
# Usage:
#   ./analyze-for-print.sh model.stl
#   ./analyze-for-print.sh model.fbx

set -e

source "$(dirname "${BASH_SOURCE[0]}")/common.sh"

REPO_ROOT="$(get_repo_root)"
SCRIPT="$REPO_ROOT/scripts/analyze/analyze-for-print.py"

if [ -z "$1" ]; then
    echo "Usage: analyze-for-print.sh <model.stl|fbx|obj|blend>"
    exit 1
fi

INPUT_FILE="$1"
require_file "$INPUT_FILE"

BLENDER="$(require_blender)"

# Pass to python script which handles all formats
"$BLENDER" --background --python "$SCRIPT" -- "$INPUT_FILE"
