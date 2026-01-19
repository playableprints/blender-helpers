#!/bin/bash
# common.sh - Shared functions for shell wrappers
# Source this file: source "$(dirname "$0")/common.sh"

# Find Blender executable
find_blender() {
    if command -v blender &> /dev/null; then
        echo "blender"
    elif [ -f "/Applications/Blender.app/Contents/MacOS/Blender" ]; then
        echo "/Applications/Blender.app/Contents/MacOS/Blender"
    elif [ -f "/usr/bin/blender" ]; then
        echo "/usr/bin/blender"
    else
        echo ""
    fi
}

# Get Blender or exit with error
require_blender() {
    local blender=$(find_blender)
    if [ -z "$blender" ]; then
        echo "Error: Blender not found. Please add it to your PATH." >&2
        exit 1
    fi
    echo "$blender"
}

# Get the directory containing bin/
get_repo_root() {
    local script_dir="$(cd "$(dirname "${BASH_SOURCE[1]}")" && pwd)"
    echo "$(dirname "$script_dir")"
}

# Check if file exists
require_file() {
    local file="$1"
    if [ ! -f "$file" ]; then
        echo "Error: File not found: $file" >&2
        exit 1
    fi
}

# Print usage and exit
usage_exit() {
    local script_name="$1"
    local usage="$2"
    echo "Usage: $script_name $usage"
    exit 1
}
