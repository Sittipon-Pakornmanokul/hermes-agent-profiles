param(
    [string]$Source = (Join-Path (Get-Location).Path 'profiles'),
    [string]$HermesHome = '',
    [string]$Python = '',
    [string[]]$Profile = @(),
    [switch]$Update,
    [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$runtimeHome = Join-Path $env:LOCALAPPDATA 'hermes'
if (-not $Python) {
    foreach ($relative in @('hermes-agent\venv\Scripts\python.exe', 'hermes-agent\.venv\Scripts\python.exe')) {
        $candidate = Join-Path $runtimeHome $relative
        if (Test-Path -LiteralPath $candidate) { $Python = $candidate; break }
    }
}
if (-not $Python -or -not (Test-Path -LiteralPath $Python)) { throw 'Pass -Python with a Python interpreter that has PyYAML installed.' }
$importArgs = @((Join-Path $PSScriptRoot 'import_profiles.py'), '--source', $Source)
if ($HermesHome) { $importArgs += @('--hermes-home', $HermesHome) }
foreach ($role in $Profile) { $importArgs += @('--profile', $role) }
if ($Update) { $importArgs += '--update' }
if ($DryRun) { $importArgs += '--dry-run' }
& $Python @importArgs
if ($LASTEXITCODE -ne 0) { throw "Import failed (exit $LASTEXITCODE)." }
