"""
naming.py - Filename and path helpers
"""

import os
import re


def clean_name(name):
    """
    Clean up object names:
    - Remove Blender duplicate suffixes (.001, .002)
    - Remove trailing underscore + numbers (_12345)
    """
    # Remove .001 style suffixes
    name = re.sub(r'\.\d{3}$', '', name)
    # Remove _-1234567890 style suffixes
    name = re.sub(r'_-?\d+$', '', name)
    return name


def output_path_next_to(input_path, suffix='_output', extension=None):
    """
    Generate output path next to input file.
    e.g., /path/to/model.stl -> /path/to/model_output.stl
    """
    base, ext = os.path.splitext(input_path)
    if extension:
        ext = extension if extension.startswith('.') else f'.{extension}'
    return f"{base}{suffix}{ext}"


def ensure_extension(filepath, extension):
    """Ensure filepath has the given extension."""
    if not extension.startswith('.'):
        extension = f'.{extension}'
    if not filepath.lower().endswith(extension.lower()):
        filepath += extension
    return filepath


def get_basename(filepath):
    """Get filename without extension."""
    return os.path.splitext(os.path.basename(filepath))[0]
