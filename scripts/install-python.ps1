$PythonInstaller = "$PSScriptRoot\python3.7.3.exe"

function Get-PythonExecutable {
    return Get-WmiObject -Namespace "root/cimv2" -Class Win32_Product -Filter "Name Like 'Python 3.7.3 Executables%'"
}

function Get-PythonInstallationTarget {
    if ([Environment]::Is64BitOperatingSystem) {
        Write-Host "Downloading x64 version of Python."
        return "https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64-webinstall.exe"
    } else {
        Write-Host "Downloading x86 version of Python."
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
        $client.DownloadFile($url, $PythonInstaller)
    } catch {
        Write-Host "Failed to download Python. The following exception was raised:"
        Write-Host $_.exception

        Exit 1
    }
}

function Install-Python {
    Write-Host "Installing Python. Do not close this window."
    $install = Start-Process $PythonInstaller -ArgumentList "InstallAllUsers=1 PrependPath=1" -PassThru -wait
    if ($install.ExitCode -eq 0) {
        Write-Host "Installation completed successfully."
    } elseif ($install.ExitCode -eq 1602) {
        Write-Host "Installer was exited by the user."
    } else {
        Write-Host "Installation failed with exit code $install.ExitCode"
    }
}

function Update-UserEnvironmentPath {
    $env:Path =
        [System.Environment]::GetEnvironmentVariable("Path","Machine") +
        ";" +
        [System.Environment]::GetEnvironmentVariable("Path","User")
}

$PythonExecutable = Get-PythonExecutable
if ($PythonExecutable.count -eq 0) {
    Get-PythonMSI
    Install-Python
    Update-UserEnvironmentPath
    Remove-Item $PythonInstaller
} else {
    Write-Host "Python 3.7.3 is already installed."
}
