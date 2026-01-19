"""
analyze-for-print.py - Analyze model for 3D printing and recommend repairs

Usage:
    blender --background model.blend --python analyze-for-print.py
    blender --background --python analyze-for-print.py -- model.stl
    blender --background --python analyze-for-print.py -- --enable-addons model.stl

Options:
    --enable-addons    Automatically enable required addons (Print3D Toolbox)

Requires: Blender 5.0+ (Print3D Toolbox addon recommended)

Outputs:
- Volume (cm³)
- Surface area (cm²)
- Bounding box dimensions (mm)
- Manifold check (non-manifold edges, holes)
- Normal check (flipped/inconsistent normals)
- Hollowing recommendation for resin printing
- Suggested repair scripts
"""

import os
import sys

# Add lib/ to path for helpers imports
script_dir = os.path.dirname(os.path.realpath(__file__))
lib_dir = os.path.join(script_dir, '..', '..', 'lib')
sys.path.insert(0, lib_dir)

from helpers import (
    get_mesh_objects,
    get_bounding_box_mm,
    create_parser,
    parse_args,
    load_model,
    MeshIssues,
    analyze_mesh,
    check_intersections,
    calculate_volume,
    calculate_area,
    ensure_print3d_addon,
)


# -----------------------------------------------------------------------------
# Hollowing recommendation
# -----------------------------------------------------------------------------

def recommend_hollow(volume_cm3, max_dim_mm, is_manifold):
    """
    Recommend whether to hollow based on resin printing considerations.

    Thresholds (adjustable):
    - Volume > 10 cm³: significant resin savings
    - Max dimension > 40mm: larger prints benefit more
    - Must be manifold for hollowing to work
    """
    VOLUME_THRESHOLD = 10.0  # cm³
    SIZE_THRESHOLD = 40.0    # mm
    WALL_THICKNESS = 1.5     # mm (recommended minimum)

    reasons = []

    if volume_cm3 is None:
        return "UNKNOWN", ["Could not calculate volume"], WALL_THICKNESS

    if not is_manifold:
        return "FIX FIRST", ["Model is not manifold/watertight - fix before hollowing"], WALL_THICKNESS

    if volume_cm3 > VOLUME_THRESHOLD:
        reasons.append(f"Volume ({volume_cm3:.1f} cm³) exceeds {VOLUME_THRESHOLD} cm³")

    if max_dim_mm > SIZE_THRESHOLD:
        reasons.append(f"Max dimension ({max_dim_mm:.1f} mm) exceeds {SIZE_THRESHOLD} mm")

    if reasons:
        return "HOLLOW", reasons, WALL_THICKNESS
    else:
        return "SOLID", ["Model is small enough to print solid"], WALL_THICKNESS


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

def main():
    parser = create_parser("Analyze model for 3D printing and recommend repairs")
    parser.add_argument(
        '--enable-addons', action='store_true',
        help='Automatically enable required addons (Print3D Toolbox)'
    )
    args = parse_args(parser)
    load_model(args)

    # Check for Print3D addon (auto-enable if flag provided)
    auto_enable = args.namespace.enable_addons
    has_print3d = ensure_print3d_addon(auto_enable=auto_enable)

    if not has_print3d:
        print("Note: Print3D Toolbox addon not enabled.")
        print("      - Surface area calculation unavailable")
        print("      - Self-intersection checks unavailable")
        print("      - Volume calculation will use bmesh fallback (less accurate)")
        print("      To enable automatically, add --enable-addons flag:")
        print("      blender --background --python analyze-for-print.py -- --enable-addons model.stl")
        print()

    # Get mesh objects
    meshes = get_mesh_objects()
    if not meshes:
        print("Error: No mesh objects found")
        sys.exit(1)

    print("=" * 60)
    print("3D PRINT ANALYSIS")
    print("=" * 60)

    all_issues = []

    for obj in meshes:
        print(f"\nObject: {obj.name}")
        print("-" * 40)

        # Dimensions
        dims = get_bounding_box_mm(obj)
        print(f"Dimensions: {dims['x']:.1f} x {dims['y']:.1f} x {dims['z']:.1f} mm")
        print(f"Max dimension: {dims['max']:.1f} mm")

        # Volume
        volume = calculate_volume(obj, use_print3d=has_print3d)

        if volume is not None:
            print(f"Volume: {volume:.2f} cm³")
            # Estimate resin cost (typical resin ~$30-50/L)
            resin_ml = volume  # 1 cm³ = 1 mL
            cost_low = resin_ml * 0.03
            cost_high = resin_ml * 0.05
            print(f"Resin estimate: {resin_ml:.1f} mL (${cost_low:.2f}-${cost_high:.2f})")

        # Surface area
        if has_print3d:
            area = calculate_area(obj)
            if area is not None:
                print(f"Surface area: {area:.2f} cm²")

        # Detailed mesh analysis
        print()
        print("Mesh Quality:")
        issues = analyze_mesh(obj)
        all_issues.append(issues)

        # Check for self-intersections if Print3D available
        if has_print3d:
            issues.intersecting_faces = check_intersections(obj)

        # Report issues
        if issues.is_manifold:
            print("  Manifold: Yes (watertight)")
        else:
            print("  Manifold: NO")
            if issues.non_manifold_edges:
                print(f"    - {issues.non_manifold_edges} non-manifold edges")
            if issues.non_manifold_verts:
                print(f"    - {issues.non_manifold_verts} non-manifold vertices")

        if issues.flipped_normals:
            print(f"  Flipped normals: {issues.flipped_normals} faces pointing inward")
        else:
            print("  Normals: OK")

        if issues.island_count == 1:
            print("  Islands: 1 (single connected mesh)")
        else:
            print(f"  Islands: {issues.island_count} disconnected parts")

        if issues.loose_geometry:
            print(f"  Loose geometry: {issues.loose_geometry} floating vertices")

        if issues.zero_area_faces:
            print(f"  Degenerate faces: {issues.zero_area_faces} zero-area faces")

        if issues.intersecting_faces:
            print(f"  Self-intersecting: {issues.intersecting_faces} faces")

        # Recommendation
        print()
        recommendation, reasons, wall = recommend_hollow(volume, dims['max'], issues.is_manifold)

        if recommendation == "HOLLOW":
            print(f">>> RECOMMENDATION: HOLLOW")
            print(f"    Wall thickness: {wall} mm")
        elif recommendation == "SOLID":
            print(f">>> RECOMMENDATION: PRINT SOLID")
        elif recommendation == "FIX FIRST":
            print(f">>> RECOMMENDATION: FIX MESH FIRST")
        else:
            print(f">>> RECOMMENDATION: {recommendation}")

        for reason in reasons:
            print(f"    - {reason}")

    # Summary with repair suggestions
    print()
    print("=" * 60)

    # Collect all suggested scripts
    suggested = {}
    for issues in all_issues:
        for script, desc in issues.suggested_scripts():
            suggested[script] = desc

    if suggested:
        print("SUGGESTED REPAIRS:")
        print("-" * 40)
        for script, desc in suggested.items():
            print(f"  {script}.sh / {script}.ps1")
            print(f"    {desc}")
            print()

        if args.input_file:
            print("Example commands:")
            basename = os.path.basename(args.input_file)
            for script in suggested.keys():
                print(f"  ./{script}.sh {basename}")
    else:
        print("No repairs needed - model is print-ready!")

    print("=" * 60)


if __name__ == "__main__":
    main()
