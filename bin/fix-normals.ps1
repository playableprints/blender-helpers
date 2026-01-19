# fix-normals.ps1 - Fix normals and export all meshes to STL
#
# Usage:
#   .\fix-normals.ps1 model.blend
#   .\fix-normals.ps1 model.stl C:\output\dir

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [string]$OutputDir
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\repair\fix-normals.py"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Processing: $InputFile"

$args = @("--background", "--python", $Script, "--", $InputFile)
if ($OutputDir) {
    $args += $OutputDir
}

& $Blender @args
