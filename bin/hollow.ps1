# hollow.ps1 - Hollow out model for resin printing
#
# Usage:
#   .\hollow.ps1 model.stl
#   .\hollow.ps1 model.stl 2.0
#   .\hollow.ps1 model.stl 2.0 C:\output\dir

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [double]$WallThickness = 2.0,

    [Parameter(Position=2)]
    [string]$OutputDir
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\repair\hollow.py"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Processing: $InputFile"
Write-Host "Wall thickness: ${WallThickness}mm"

$args = @("--background", "--python", $Script, "--", $InputFile, $WallThickness)
if ($OutputDir) {
    $args += $OutputDir
}

& $Blender @args
