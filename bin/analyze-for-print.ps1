# analyze-for-print.ps1 - Analyze model for 3D printing
#
# Usage:
#   .\analyze-for-print.ps1 model.stl
#   .\analyze-for-print.ps1 model.fbx

param(
    [Parameter(Mandatory=$true, Position=0)]
    [string]$InputFile
)

. "$PSScriptRoot\common.ps1"

$RepoRoot = Get-RepoRoot
$Script = Join-Path $RepoRoot "scripts\analyze\analyze-for-print.py"

Test-RequiredFile $InputFile

$Blender = Get-RequiredBlender

& $Blender --background --python $Script -- $InputFile
