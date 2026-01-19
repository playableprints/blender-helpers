"""
boolean.py - Boolean operations on meshes
"""

import bpy
from .selection import select_by_name
from .objects import remove_by_name


def boolean_subtract(target, cutter):
    """
    Subtract 'cutter' from 'target' using Boolean modifier.
    Removes the cutter object after operation.
    """
    select_by_name(target)
    mod = bpy.data.objects[target].modifiers.new(type="BOOLEAN", name=f"Diff-{cutter}")
    mod.object = bpy.data.objects[cutter]
    mod.operation = 'DIFFERENCE'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    remove_by_name(cutter)


def boolean_union(target, other):
    """
    Union 'other' into 'target' using Boolean modifier.
    Removes the other object after operation.
    """
    select_by_name(target)
    mod = bpy.data.objects[target].modifiers.new(type="BOOLEAN", name=f"Union-{other}")
    mod.object = bpy.data.objects[other]
    mod.operation = 'UNION'
    bpy.ops.object.modifier_apply(modifier=mod.name)
    remove_by_name(other)
