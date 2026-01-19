# export-obj.ps1 - Export mesh objects to OBJ
#
# Usage:
#   .\export-obj.ps1 model.fbx
#   .\export-obj.ps1 model.fbx C:\output\dir
#   .\export-obj.ps1 model.fbx C:\output\dir -Single

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile,

    [Parameter(Position=1)]
    [string]$OutputDir,

    [switch]$Selected,
    [switch]$Single,
    [switch]$NoCleanup
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\export\export-obj.py"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender
Write-Host "Using Blender: $Blender"
Write-Host "Processing: $InputFile"

$args = @("--background", "--python", $Script, "--", $InputFile)
if ($OutputDir) {
    $args += $OutputDir
}
if ($Selected) {
    $args += "--selected"
}
if ($Single) {
    $args += "--single"
}
if ($NoCleanup) {
    $args += "--no-cleanup"
}

& $Blender @args
