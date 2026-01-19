"""
script_utils.py - Common utilities for Blender pipeline scripts

Provides argument parsing and model loading helpers used across scripts.
"""

import argparse
import bpy
import os
import sys
from dataclasses import dataclass, field
from typing import List, Optional, Any

from .io import import_model, get_format_from_path
from .naming import get_basename
from .selection import get_mesh_objects


# -----------------------------------------------------------------------------
# Argument parsing
# -----------------------------------------------------------------------------

@dataclass
class ScriptArgs:
    """Parsed command-line arguments for a script."""
    input_file: Optional[str] = None
    output_dir: Optional[str] = None
    base_name: str = "output"
    # For backward compatibility - flags are stored as a set
    flags: set = field(default_factory=set)
    # For backward compatibility - extra numeric params stored here
    extra: dict = field(default_factory=dict)
    # The actual argparse namespace (for direct attribute access)
    namespace: Any = None


def create_parser(description: str = "Blender pipeline script") -> argparse.ArgumentParser:
    """Create a base argument parser with common options.

    Args:
        description: Script description for --help output

    Returns:
        ArgumentParser with input_file and output_dir already defined
    """
    parser = argparse.ArgumentParser(description=description)

    parser.add_argument(
        'input_file',
        nargs='?',
        help='Input model file (STL, OBJ, FBX, GLTF, or .blend)'
    )
    parser.add_argument(
        'output_dir',
        nargs='?',
        help='Output directory (default: same as input file)'
    )

    return parser


def _get_script_args() -> List[str]:
    """Extract arguments after '--' (Blender convention)."""
    argv = sys.argv
    if "--" in argv:
        return argv[argv.index("--") + 1:]
    return []


def parse_args(
    parser: Optional[argparse.ArgumentParser] = None,
    description: str = "Blender pipeline script"
) -> ScriptArgs:
    """Parse command-line arguments using argparse.

    Args:
        parser: Optional pre-configured ArgumentParser. If None, creates a basic one.
        description: Script description (used if parser is None)

    Returns:
        ScriptArgs with parsed values

    Example:
        # Simple usage (just input_file and output_dir):
        args = parse_args()

        # With custom arguments:
        parser = create_parser("Hollow out a mesh for resin printing")
        parser.add_argument('--wall-thickness', type=float, default=2.0,
                           help='Wall thickness in mm (default: 2.0)')
        parser.add_argument('--gif', action='store_true',
                           help='Create animated GIF')
        args = parse_args(parser)
        # Access via: args.namespace.wall_thickness, args.namespace.gif
    """
    if parser is None:
        parser = create_parser(description)

    script_args = _get_script_args()

    try:
        namespace = parser.parse_args(script_args)
    except SystemExit:
        # argparse calls sys.exit on --help or error; let it through
        raise

    # Build ScriptArgs for backward compatibility
    result = ScriptArgs()
    result.namespace = namespace

    # Map standard fields
    if hasattr(namespace, 'input_file') and namespace.input_file:
        result.input_file = namespace.input_file
        result.base_name = get_basename(namespace.input_file)

    if hasattr(namespace, 'output_dir') and namespace.output_dir:
        result.output_dir = namespace.output_dir

    # Collect flags (boolean args that are True) for backward compat
    for key, value in vars(namespace).items():
        if key not in ('input_file', 'output_dir') and value is True:
            # Convert underscores to dashes for flag names (argparse convention)
            result.flags.add(key.replace('_', '-'))

    # Store numeric values in extra dict for backward compat
    for key, value in vars(namespace).items():
        if key not in ('input_file', 'output_dir') and isinstance(value, (int, float)):
            result.extra[key] = value

    return result


# -----------------------------------------------------------------------------
# Model loading
# -----------------------------------------------------------------------------

def load_model(args: ScriptArgs) -> List[Any]:
    """Load model from parsed args.

    If input_file is a .blend, opens it.
    Otherwise imports the model file.
    If no input_file, uses already-loaded blend file.

    Args:
        args: Parsed ScriptArgs from parse_args()

    Returns:
        List of imported mesh objects (empty if opening blend file)
    """
    imported = []

    if args.input_file:
        fmt = get_format_from_path(args.input_file)
        if fmt == 'BLEND':
            bpy.ops.wm.open_mainfile(filepath=args.input_file)
        else:
            imported = import_model(args.input_file)

        if not args.output_dir:
            args.output_dir = os.path.dirname(args.input_file) or os.getcwd()
    else:
        # Using already-loaded blend file
        blend_path = bpy.data.filepath
        if blend_path:
            args.base_name = get_basename(blend_path)
            if not args.output_dir:
                args.output_dir = os.path.dirname(blend_path)

    args.output_dir = args.output_dir or os.getcwd()
    return imported


def setup_output_dir(args: ScriptArgs) -> str:
    """Ensure output directory exists and return the path."""
    output_dir = args.output_dir or os.getcwd()
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def require_meshes(min_count: int = 1) -> List[Any]:
    """Get mesh objects, exit if not enough found.

    Args:
        min_count: Minimum number of meshes required

    Returns:
        List of mesh objects
    """
    meshes = get_mesh_objects()
    if len(meshes) < min_count:
        if min_count == 1:
            print("No mesh objects found.")
        else:
            print(f"Need at least {min_count} mesh objects, found {len(meshes)}.")
        sys.exit(1)
    return meshes
