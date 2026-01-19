# render-snapshot.ps1 - Render a single snapshot of a model
#
# Usage:
#   .\render-snapshot.ps1 model.stl
#   .\render-snapshot.ps1 model.stl C:\output\dir
#   .\render-snapshot.ps1 model.stl -Rotation 45

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [string]$OutputDir,

    [float]$Rotation = 35
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\render\render-snapshot.py"
$Template = Join-Path $RepoRoot "templates\turntable.blend"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Model: $InputFile"

$blenderArgs = @()
if (Test-Path $Template) {
    $blenderArgs += @("--background", $Template, "--python", $Script, "--", $InputFile)
} else {
    $blenderArgs += @("--background", "--python", $Script, "--", $InputFile)
}

if ($OutputDir) {
    $blenderArgs += $OutputDir
}

$blenderArgs += @("--rotation", $Rotation)

& $Blender @blenderArgs
