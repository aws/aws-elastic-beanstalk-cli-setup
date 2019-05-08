$PythonInstaller = "$PSScriptRoot\python3.7.3.exe"
$StepNumber = 1

function Write-StepTitle([String] $StepMessage) {
    $StepMessage="$Script:StepNumber. $StepMessage"
    $MessageLength=$StepMessage.length
    $RepeatedStars = "*" * $MessageLength
    Write-Host ""
    Write-Host $RepeatedStars
    Write-Host $StepMessage
    Write-Host $RepeatedStars
    $Script:StepNumber = $Script:StepNumber + 1
}

function Get-PythonExecutable {
    Write-StepTitle "Looking for existing Python 3.7.3 installation."
    return Get-WmiObject -Namespace "root/cimv2" -Class Win32_Product -Filter "Name Like 'Python 3.7.3 Executables%'"
}

function Get-PythonInstallationTarget {
    if ([Environment]::Is64BitOperatingSystem) {
        Write-StepTitle "Downloading x64 version of Python."
        return "https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64-webinstall.exe"
    } else {
        Write-StepTitle "Downloading x86 version of Python."
        return "https://www.python.org/ftp/python/3.7.3/python-3.7.3-webinstall.exe"
    }
}

function Get-PythonMSI {
    if ([System.IO.File]::Exists($PythonInstaller)) {
        Remove-Item $PythonInstaller
    }
    $url = Get-PythonInstallationTarget
    $client = New-Object System.Net.WebClient
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        $client.DownloadFile($url, $PythonInstaller)
    } catch {
        Write-Host "Failed to download Python. The following exception was raised:" -ForegroundColor Red
        Write-Host $_.exception -ForegroundColor Red

        Exit 1
    }
}

function Install-Python {
    Write-StepTitle "Installing Python. Do not close this window."
    Write-Host "Installing Python. Do not close this window."
    $install = Start-Process $PythonInstaller -ArgumentList "InstallAllUsers=1 PrependPath=1" -PassThru -wait
    if ($install.ExitCode -eq 0) {
        Write-Host "Installation completed successfully." -ForegroundColor Green
    } elseif ($install.ExitCode -eq 1602) {
        Write-Host "Installer was exited by the user." -ForegroundColor Red
        Exit 1
    } else {
        Write-Host "Installation failed with exit code $install.ExitCode" -ForegroundColor Red
        Exit 1
    }
}

function Update-UserEnvironmentPath {
    Write-StepTitle "Updating Environment PATH of this shell."
    $env:Path =
        [System.Environment]::GetEnvironmentVariable("Path","Machine") +
        ";" +
        [System.Environment]::GetEnvironmentVariable("Path","User")
}

function Install-Virtualenv {
    Write-StepTitle "Installing virtualenv"
    Invoke-Expression "pip install virtualenv --target $PSScriptRoot\virtualenv"
}

$PythonExecutable = Get-PythonExecutable
if ($PythonExecutable.count -eq 0) {
    Get-PythonMSI
    Install-Python
    Update-UserEnvironmentPath
    Remove-Item $PythonInstaller
} else {
    Write-Host "Python 3.7.3 is already installed." -ForegroundColor Green
}
Install-Virtualenv
