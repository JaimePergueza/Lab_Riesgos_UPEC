$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$outputDir = Join-Path $projectRoot 'Saved/ImportManifests'
New-Item -ItemType Directory -Force -Path $outputDir | Out-Null

$sources = @(
    'MobileAssets/TouchButtons/Import_Mobile_Touch_Icons.json',
    'SourceAssets/PauseUI/import_pause_ui.json'
)

foreach ($source in $sources) {
    $inputPath = Join-Path $projectRoot $source
    $manifest = Get-Content -LiteralPath $inputPath -Raw | ConvertFrom-Json
    foreach ($group in $manifest.ImportGroups) {
        $group.Filenames = @($group.Filenames | ForEach-Object {
            $assetPath = Join-Path $projectRoot $_
            if (-not (Test-Path -LiteralPath $assetPath -PathType Leaf)) {
                throw "Falta el archivo de origen: $assetPath"
            }
            (Resolve-Path -LiteralPath $assetPath).Path.Replace('\', '/')
        })
    }
    $outputPath = Join-Path $outputDir (Split-Path $source -Leaf)
    $manifest | ConvertTo-Json -Depth 20 | Set-Content -LiteralPath $outputPath -Encoding utf8
    Write-Output $outputPath
}
