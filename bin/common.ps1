# common.ps1 - Shared functions for Blender helper scripts
#
# Usage: . "$PSScriptRoot\common.ps1"

$ErrorActionPreference = "Stop"

function Find-Blender {
    <#
    .SYNOPSIS
    Find Blender executable on the system
    #>

    # Check PATH first
    $blender = Get-Command blender -ErrorAction SilentlyContinue
    if ($blender) {
        return $blender.Source
    }

    # Check common Windows locations
    $locations = @(
        "$env:ProgramFiles\Blender Foundation\Blender 5.0\blender.exe",
        "$env:ProgramFiles\Blender Foundation\Blender 4.2\blender.exe",
        "$env:ProgramFiles\Blender Foundation\Blender 4.1\blender.exe",
        "$env:ProgramFiles\Blender Foundation\Blender 4.0\blender.exe",
        "${env:ProgramFiles(x86)}\Blender Foundation\Blender 5.0\blender.exe",
        "$env:LOCALAPPDATA\Programs\Blender Foundation\Blender 5.0\blender.exe"
    )

    foreach ($loc in $locations) {
        if (Test-Path $loc) {
            return $loc
        }
    }

    return $null
}

function Get-RequiredBlender {
    <#
    .SYNOPSIS
    Get Blender path or exit with error
    #>
    $blender = Find-Blender
    if (-not $blender) {
        Write-Error "Error: Blender not found. Please add it to your PATH or install Blender 5.0+"
        exit 1
    }
    return $blender
}

function Get-RepoRoot {
    <#
    .SYNOPSIS
    Get the repository root directory (parent of bin/)
    #>
    return Split-Path -Parent $PSScriptRoot
}

function Test-RequiredFile {
    <#
    .SYNOPSIS
    Check if file exists, exit with error if not
    #>
    param([string]$Path)

    if (-not (Test-Path $Path)) {
        Write-Error "Error: File not found: $Path"
        exit 1
    }
}
