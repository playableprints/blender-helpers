# render-360.ps1 - Render 360 degree turntable animation
#
# Usage:
#   .\render-360.ps1 model.stl
#   .\render-360.ps1 model.stl 24
#   .\render-360.ps1 model.stl 24 C:\output\dir
#   .\render-360.ps1 model.stl -Gif

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [int]$Frames = 15,

    [Parameter(Position=2)]
    [string]$OutputDir,

    [switch]$Gif
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\render\render-360.py"
$Template = Join-Path $RepoRoot "templates\turntable.blend"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Model: $InputFile"
Write-Host "Frames: $Frames"
if ($Gif) {
    Write-Host "GIF: Yes"
}

$blenderArgs = @()
if (Test-Path $Template) {
    $blenderArgs += @("--background", $Template, "--python", $Script, "--", $InputFile, $Frames)
} else {
    $blenderArgs += @("--background", "--python", $Script, "--", $InputFile, $Frames)
}

if ($OutputDir) {
    $blenderArgs += $OutputDir
}

if ($Gif) {
    $blenderArgs += "--gif"
}

& $Blender @blenderArgs
