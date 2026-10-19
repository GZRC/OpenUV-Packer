$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path $PSScriptRoot -Parent
$destination = Join-Path (Split-Path $projectRoot -Parent) 'OpenUV-Packer-addon.zip'
Add-Type -AssemblyName System.IO.Compression
$stream = [IO.File]::Open($destination, [IO.FileMode]::Create)
$archive = [IO.Compression.ZipArchive]::new($stream, [IO.Compression.ZipArchiveMode]::Create)
try {
    $source = Join-Path $projectRoot 'addon'
    foreach ($file in Get-ChildItem -LiteralPath $source -Recurse -File) {
        if ($file.Extension -notin @('.py', '.exe') -or $file.FullName -match '__pycache__') { continue }
        $relative = [IO.Path]::GetRelativePath($source, $file.FullName).Replace('\','/')
        [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, $file.FullName, "openuv_packer/$relative") | Out-Null
    }
    foreach ($name in @('LICENSE','README.md')) {
        [IO.Compression.ZipFileExtensions]::CreateEntryFromFile($archive, "$projectRoot/$name", "openuv_packer/$name") | Out-Null
    }
} finally {
    $archive.Dispose()
    $stream.Dispose()
}
Write-Output $destination
