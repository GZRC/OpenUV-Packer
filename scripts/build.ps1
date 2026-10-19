param([string]$Configuration = 'Release')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
cmake -S $projectRoot -B "$projectRoot/build"
if ($LASTEXITCODE -ne 0) { throw 'CMake configuration failed' }
cmake --build "$projectRoot/build" --config $Configuration
if ($LASTEXITCODE -ne 0) { throw 'Compilation failed' }
ctest --test-dir "$projectRoot/build" -C $Configuration --output-on-failure
if ($LASTEXITCODE -ne 0) { throw 'Native tests failed' }
cmake --install "$projectRoot/build" --config $Configuration --prefix $projectRoot
if ($LASTEXITCODE -ne 0) { throw 'Installation failed' }
