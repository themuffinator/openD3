param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('setup', 'compile', 'install', 'fastbuild')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$mesonWrapper = Join-Path $workspaceRoot 'tools\build\meson_setup.ps1'
$buildDir = Join-Path $workspaceRoot 'builddir-perf'
$installDir = Join-Path $workspaceRoot '.install'
$fastStageScript = Join-Path $workspaceRoot 'tools\build\stage_fast_install.py'
$checkStagedContentScript = Join-Path $workspaceRoot 'tools\build\check_staged_content_edits.py'

if (-not (Test-Path $mesonWrapper)) {
    throw "openD3 Meson wrapper not found at '$mesonWrapper'."
}

function Invoke-openD3Meson([string[]]$MesonArgs) {
    & powershell -NoProfile -ExecutionPolicy Bypass -File $mesonWrapper @MesonArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Invoke-PythonTool([string[]]$ToolArgs) {
    & python @ToolArgs
    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

function Test-MesonBuildDirectory([string]$Path) {
    $coreData = Join-Path $Path 'meson-private\coredata.dat'
    $ninjaFile = Join-Path $Path 'build.ninja'
    return (Test-Path $coreData) -and (Test-Path $ninjaFile)
}

# Match the release packages: optimized code with symbols, and C assert() compiled
# out (b_ndebug), including in the SDL3, GLEW and stb_vorbis subprojects.
$expectedBuildOptions = [ordered]@{
    'buildtype' = 'debugoptimized'
    'b_ndebug' = 'true'
}

function Get-StaleBuildOptions([string]$Path) {
    $optionsFile = Join-Path $Path 'meson-info\intro-buildoptions.json'
    if (-not (Test-Path $optionsFile)) {
        return @($expectedBuildOptions.Keys)
    }
    $configured = @{}
    foreach ($option in (Get-Content $optionsFile -Raw | ConvertFrom-Json)) {
        $configured[$option.name] = "$($option.value)".ToLowerInvariant()
    }
    return @($expectedBuildOptions.Keys | Where-Object { $configured[$_] -ne $expectedBuildOptions[$_] })
}

function Invoke-openD3Setup {
    $optionArgs = @('--backend', 'ninja', '--wrap-mode=forcefallback')
    foreach ($name in $expectedBuildOptions.Keys) {
        $optionArgs += "-D$name=$($expectedBuildOptions[$name])"
    }
    if (Test-MesonBuildDirectory $buildDir) {
        Invoke-openD3Meson (@('setup', $buildDir, $workspaceRoot, '--reconfigure') + $optionArgs)
    } else {
        Invoke-openD3Meson (@('setup', '--wipe', $buildDir, $workspaceRoot) + $optionArgs)
    }
}

# An existing build directory keeps whatever it was configured with, and the
# compile tasks never reconfigure on their own, so bring it up to the expected
# options before compiling.
function Invoke-openD3Compile {
    $stale = @(Get-StaleBuildOptions $buildDir)
    if ($stale.Count -gt 0) {
        Write-Host "builddir-perf options out of date ($($stale -join ', ')); reconfiguring."
        Invoke-openD3Setup
    }
    Invoke-openD3Meson @(
        'compile',
        '-C',
        $buildDir
    )
}

switch ($Action) {
    'setup' {
        Invoke-openD3Setup
    }
    'compile' {
        Invoke-openD3Compile
    }
    'fastbuild' {
        if (-not (Test-Path $fastStageScript)) {
            throw "openD3 fast staging script not found at '$fastStageScript'."
        }
        if (-not (Test-Path $checkStagedContentScript)) {
            throw "openD3 staged content edit check script not found at '$checkStagedContentScript'."
        }

        Invoke-openD3Compile
        Invoke-PythonTool @(
            $checkStagedContentScript,
            '--source-root',
            $workspaceRoot
        )
        Invoke-PythonTool @(
            $fastStageScript,
            '--source-root',
            $workspaceRoot,
            '--build-dir',
            $buildDir,
            '--install-dir',
            $installDir
        )
    }
    'install' {
        Invoke-openD3Meson @(
            'install',
            '-C',
            $buildDir,
            '--no-rebuild',
            '--skip-subprojects'
        )
    }
}
