param(
    [string]$Source = '',
    [string]$Destination = (Get-Location).Path,
    [string]$Python = '',
    [string]$Repo = ''
)
$ErrorActionPreference = 'Stop'
if (-not $Source) {
    $Source = Join-Path $env:LOCALAPPDATA 'hermes'
    if ($env:HERMES_HOME) {
        $Source = [Environment]::ExpandEnvironmentVariables($env:HERMES_HOME)
        if ($Source.StartsWith('~')) { $Source = Join-Path $env:USERPROFILE $Source.Substring(1).TrimStart('\', '/') }
        $Source = [IO.Path]::GetFullPath($Source)
        $profileParent = Split-Path -Parent $Source
        if ((Split-Path -Leaf $profileParent) -eq 'profiles') { $Source = Split-Path -Parent $profileParent }
    }
}
if (-not $Repo) { $Repo = Join-Path $Source 'hermes-agent' }
if (-not $Python) {
    foreach ($relative in @('venv\Scripts\python.exe', '.venv\Scripts\python.exe')) {
        $candidate = Join-Path $Repo $relative
        if (Test-Path -LiteralPath $candidate) { $Python = $candidate; break }
    }
}
if (-not (Test-Path -LiteralPath $Python)) { throw 'Pass -Python with the Hermes Python interpreter path.' }
& $Python (Join-Path $PSScriptRoot 'export_profiles.py') --source $Source --repo $Repo --dest $Destination
if ($LASTEXITCODE -ne 0) { throw "Export failed (exit $LASTEXITCODE)." }
