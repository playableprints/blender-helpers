# voxel-merge.ps1 - Join all objects and voxel remesh into watertight mesh
#
# Usage:
#   .\voxel-merge.ps1 model.blend
#   .\voxel-merge.ps1 model.fbx 0.05
#   .\voxel-merge.ps1 model.stl 0.05 C:\output\dir

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [double]$VoxelSize = 0.1,

    [Parameter(Position=2)]
    [string]$OutputDir
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\repair\voxel-merge.py"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Processing: $InputFile"
Write-Host "Voxel size: $VoxelSize"

$args = @("--background", "--python", $Script, "--", $InputFile, $VoxelSize)
if ($OutputDir) {
    $args += $OutputDir
}

& $Blender @args
