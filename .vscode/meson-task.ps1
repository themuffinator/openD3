param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('setup', 'compile', 'install', 'fastbuild')]
    [string]$Action
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$workspaceRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$mesonWrapper = Join-Path $workspaceRoot 'tools\build\meson_setup.ps1'
$buildDir = Join-Path $workspaceRoot 'builddir'
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

# openD3's standard tree (AGENTS.md): builddir, optimized code with symbols and
# assert() left on, so the tasks and the documented commands share one build.
$expectedBuildOptions = [ordered]@{
    'buildtype' = 'debugoptimized'
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

# Meson discovers the engine's sources when it configures
# (tools/build/meson_sources.py), so a compile alone never builds a source file
# added since then, and fails to link once something calls into it. The set of
# C and C++ files under src/ at the last configure is kept in builddir; the
# compile task reconfigures when it differs.
$sourceSetStamp = Join-Path $buildDir 'opend3-source-set.txt'

function Get-openD3SourceSet {
    $sourceRoot = Join-Path $workspaceRoot 'src'
    $prefix = $workspaceRoot.TrimEnd('\').Length + 1
    $names = Get-ChildItem -Path $sourceRoot -Recurse -File -Include '*.c', '*.cc', '*.cpp' |
        ForEach-Object { $_.FullName.Substring($prefix).Replace('\', '/') } |
        Sort-Object
    return ($names -join "`n")
}

function Save-openD3SourceSet {
    if (Test-Path $buildDir) {
        [System.IO.File]::WriteAllText($sourceSetStamp, (Get-openD3SourceSet))
    }
}

function Test-openD3SourceSetChanged {
    if (-not (Test-Path $sourceSetStamp)) {
        return $true
    }
    return [System.IO.File]::ReadAllText($sourceSetStamp) -ne (Get-openD3SourceSet)
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
    Save-openD3SourceSet
}

# An existing build directory keeps whatever it was configured with, and the
# compile tasks never reconfigure on their own, so bring it up to the expected
# options before compiling.
function Invoke-openD3Compile {
    $stale = @(Get-StaleBuildOptions $buildDir)
    if ($stale.Count -gt 0) {
        Write-Host "builddir options out of date ($($stale -join ', ')); reconfiguring."
        Invoke-openD3Setup
    } elseif (Test-openD3SourceSetChanged) {
        Write-Host 'Source files were added or removed since builddir was configured; reconfiguring.'
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
