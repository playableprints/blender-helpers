# make-manifold.ps1 - Make mesh watertight/manifold
#
# Usage:
#   .\make-manifold.ps1 model.stl
#   .\make-manifold.ps1 model.fbx C:\output\dir

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [string]$OutputDir
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\repair\make-manifold.py"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Processing: $InputFile"

$args = @("--background", "--python", $Script, "--", $InputFile)
if ($OutputDir) {
    $args += $OutputDir
}

& $Blender @args
