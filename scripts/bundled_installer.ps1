function Write-OutputWithInvertedColors([String] $Message) {
    Write-Host $Message -ForegroundColor Black -BackgroundColor White
}

function Get-HomePath() {
    if (Test-Path Env:\USERPROFILE) {
        return $env:USERPROFILE
    } elseif (Test-Path Env:\HOMEDRIVE -and Env:\HOMEPATH) {
        return $env:HOMEDRIVE + $env:HOMEPATH
    } elseif (Test-Path Env:\LOCALAPPDATA) {
        return $env:LOCALAPPDATA
    } elseif (Test-Path Env:\APPDATA) {
        return $env:APPDATA
    } else {
        Write-Host "Cannot determine user's home directory." -ForegroundColor Red
        Exit 1
    }
}

function Exit-OnFailure() {
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Exiting due to failure" -ForegroundColor Red
        exit 1
    }
}

function Update-UserEnvironmentPath {
    $env:Path =
        [System.Environment]::GetEnvironmentVariable("Path","Machine") +
        ";" +
        [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Write-StepTitle([String] $Message) {
    $equals = "=" * 46
    Write-Host ""
    Write-OutputWithInvertedColors $equals
    Write-OutputWithInvertedColors $Message
    Write-OutputWithInvertedColors $equals
}
Write-StepTitle "I. Installing Python                          "
powershell "$PSScriptRoot\install-python.ps1"
Exit-OnFailure
Update-UserEnvironmentPath

Write-StepTitle "II. Creating self-contained EBCLI installation"
$HomeDir = Get-HomePath
Write-Host "Installing the EBCLI in $HomeDir\.ebcli-virtual-env"
python "$PSScriptRoot\ebcli_installer.py" --virtualenv-executable "$PSScriptRoot\virtualenv\bin\virtualenv.exe" --hide-export-recommendation --location $HomeDir
Exit-OnFailure

$PathExporter = "$HomeDir\.ebcli-virtual-env\executables\path_exporter.vbs"
if ([System.IO.File]::Exists($PathExporter)) {
    Write-StepTitle "III. Exporting `eb` PATH's                    "
    Start-Process "cscript.exe" -ArgumentList "$HomeDir\.ebcli-virtual-env\executables\path_exporter.vbs" -Wait
    Update-UserEnvironmentPath
}
