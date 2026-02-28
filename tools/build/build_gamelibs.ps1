param(
    [string]$GameLibsRepo = "",
    [string]$BuildDir = "",
    [switch]$SetupOnly
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$openD3Root = [System.IO.Path]::GetFullPath((Join-Path $scriptDir "..\.."))

$gameLibsRepoOverride = ""
if (-not [string]::IsNullOrWhiteSpace($env:OPEND3_GAMELIBS_REPO)) {
    $gameLibsRepoOverride = $env:OPEND3_GAMELIBS_REPO
} elseif (-not [string]::IsNullOrWhiteSpace($env:OPENQ4_GAMELIBS_REPO)) {
    $gameLibsRepoOverride = $env:OPENQ4_GAMELIBS_REPO
}

if ([string]::IsNullOrWhiteSpace($GameLibsRepo)) {
    if (-not [string]::IsNullOrWhiteSpace($gameLibsRepoOverride)) {
        $GameLibsRepo = $gameLibsRepoOverride
    } else {
        $GameLibsRepo = Join-Path $openD3Root "..\OpenD3-GameLibs"
    }
}
if ([string]::IsNullOrWhiteSpace($BuildDir)) {
    $BuildDir = Join-Path $GameLibsRepo "builddir"
}

$gameLibsRoot = [System.IO.Path]::GetFullPath($GameLibsRepo)
$gameLibsBuildDir = [System.IO.Path]::GetFullPath($BuildDir)
$gameLibsCoreData = Join-Path $gameLibsBuildDir "meson-private\coredata.dat"
$gameLibsBuildNinja = Join-Path $gameLibsBuildDir "build.ninja"

$mesonSetupCandidates = @(
    (Join-Path $gameLibsRoot "tools\build\meson_setup.ps1"),
    (Join-Path $gameLibsRoot "meson_setup.ps1")
)

$gameLibsMesonSetup = $null
foreach ($candidate in $mesonSetupCandidates) {
    if (Test-Path $candidate) {
        $gameLibsMesonSetup = $candidate
        break
    }
}

if (-not (Test-Path $gameLibsRoot)) {
    throw "OpenD3-GameLibs repository not found at '$gameLibsRoot'. Set OPEND3_GAMELIBS_REPO (or OPENQ4_GAMELIBS_REPO for compatibility) or pass -GameLibsRepo."
}

if ($null -eq $gameLibsMesonSetup) {
    Write-Host "OpenD3-GameLibs has no standalone Meson build wrapper; skipping optional companion build."
    $global:LASTEXITCODE = 0
    exit 0
}

Write-Host "Building OpenD3 game libraries from:"
Write-Host "  Repo: $gameLibsRoot"
Write-Host "  BuildDir: $gameLibsBuildDir"

if ((Test-Path $gameLibsCoreData) -and (Test-Path $gameLibsBuildNinja)) {
    & $gameLibsMesonSetup setup --reconfigure $gameLibsBuildDir $gameLibsRoot
} else {
    & $gameLibsMesonSetup setup --wipe $gameLibsBuildDir $gameLibsRoot --backend ninja --buildtype release --vsenv
}
$setupExit = [int]$LASTEXITCODE
if ($setupExit -ne 0) {
    exit $setupExit
}

if ($SetupOnly) {
    exit 0
}

& $gameLibsMesonSetup compile -C $gameLibsBuildDir
$compileExit = [int]$LASTEXITCODE
if ($compileExit -ne 0) {
    exit $compileExit
}

Write-Host "OpenD3-GameLibs build complete."
