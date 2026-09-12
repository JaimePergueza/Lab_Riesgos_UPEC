$ErrorActionPreference = 'Stop'

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$pluginPath = Join-Path $projectRoot 'Plugins/VibeUE'
$patchPath = Join-Path $projectRoot 'Patches/VibeUE-UE57-SCS-parentage.patch'
$vibeCommit = 'c187526263c0fa5b2de41e83ac02a4538dc248e4'

if (Test-Path -LiteralPath $pluginPath) {
    throw "Plugins/VibeUE ya existe. Revísalo antes de instalar para no sobrescribir cambios locales."
}

git clone https://github.com/kevinpbuckley/VibeUE.git $pluginPath
if ($LASTEXITCODE -ne 0) { throw 'No se pudo clonar VibeUE.' }
git -C $pluginPath checkout --detach $vibeCommit
if ($LASTEXITCODE -ne 0) { throw "No se pudo seleccionar VibeUE $vibeCommit." }
git -C $pluginPath apply --unidiff-zero --check $patchPath
if ($LASTEXITCODE -ne 0) { throw 'El parche de VibeUE no corresponde al commit fijado.' }
git -C $pluginPath apply --unidiff-zero $patchPath
if ($LASTEXITCODE -ne 0) { throw 'No se pudo aplicar el parche de VibeUE.' }

Write-Output "VibeUE $vibeCommit instalado con la corrección UE 5.7."
