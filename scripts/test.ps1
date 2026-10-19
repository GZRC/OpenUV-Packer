param([string]$Python = 'python', [string]$Blender = 'blender')
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
& $Python "$projectRoot/tests/test_packing.py"
if ($LASTEXITCODE -ne 0) { throw 'Packing tests failed' }
& $Blender --background --factory-startup --python-exit-code 1 --python "$projectRoot/tests/blender_smoke.py"
if ($LASTEXITCODE -ne 0) { throw 'Blender tests failed' }
