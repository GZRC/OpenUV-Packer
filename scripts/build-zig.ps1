param(
    [Parameter(Mandatory=$true)][string]$Zig,
    [string]$CMake = 'cmake',
    [string]$Ninja = 'ninja',
    [string]$CacheDirectory = ''
)
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$buildDir = Join-Path $projectRoot 'build-zig'
$toolDir = Join-Path $buildDir 'tools'
New-Item -ItemType Directory -Force $toolDir | Out-Null
$zigExe = (Get-Command $Zig).Source
$ninjaExe = (Get-Command $Ninja).Source
foreach ($pair in @(@('cxx','c++'),@('ar','ar'),@('ranlib','ranlib'))) {
    @('@echo off', ('"' + $zigExe + '" ' + $pair[1] + ' %*')) | Set-Content -Encoding ascii (Join-Path $toolDir ($pair[0]+'.cmd'))
}
if (-not $CacheDirectory) { $CacheDirectory = Join-Path $buildDir 'zig-cache' }
New-Item -ItemType Directory -Force $CacheDirectory | Out-Null
$env:ZIG_GLOBAL_CACHE_DIR = (Resolve-Path $CacheDirectory).Path
$env:ZIG_LOCAL_CACHE_DIR = Join-Path $buildDir 'zig-local'
$env:TEMP = (Resolve-Path $toolDir).Path
$env:TMP = $env:TEMP
& $CMake -S $projectRoot -B $buildDir -G Ninja "-DCMAKE_MAKE_PROGRAM=$ninjaExe" "-DCMAKE_CXX_COMPILER=$toolDir/cxx.cmd" "-DCMAKE_AR:FILEPATH=$toolDir/ar.cmd" "-DCMAKE_RANLIB:FILEPATH=$toolDir/ranlib.cmd" -DCMAKE_BUILD_TYPE=Release
if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed' }
& $CMake --build $buildDir --parallel 2
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
$ctest = Join-Path (Split-Path (Get-Command $CMake).Source -Parent) 'ctest.exe'
& $ctest --test-dir $buildDir --output-on-failure
if ($LASTEXITCODE -ne 0) { throw 'Native tests failed' }
& $CMake --install $buildDir --prefix $projectRoot
if ($LASTEXITCODE -ne 0) { throw 'Installation failed' }
