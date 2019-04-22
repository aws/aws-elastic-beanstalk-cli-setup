$python = "$PSScriptRoot\python3.7.3.exe"

function Assert-IsPythonRequired {
    $result = Get-WmiObject -Namespace "root/cimv2" -Class Win32_Product -Filter "Name Like 'Python 3.7.3 Executables%'"
    return $result.Count -eq 0
}

function Cleanup {
    Remove-Item $python
    Start-Process powershell
    Stop-Process $PID
}

function Download-Python {
    $arch ="$env:PROCESSOR_ARCHITECTURE"
    $url = ""

    switch($arch) {
        "amd64" {
            Write-Host "Downloading x64 version of Python."
            $url = "https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64-webinstall.exe"
        }
        "x86" {
            Write-Host "Downloading x86 version of Python."
	        $url = "https://www.python.org/ftp/python/3.7.3/python-3.7.3-webinstall.exe"
        }
        default {
            Write-Host "Unable to determine the Python download url for processor type: $arch."
        }
    }

    if (-not ([string]::IsNullOrEmpty($url))) {
        $client = New-Object System.Net.WebClient
        $client.DownloadFile($url, $python)
        return $True
    }

    return $False
}

if (Assert-IsPythonRequired) {
    if (Download-Python) {
        Write-Host "Silently installing Python. Do not close this window."
        $install = Start-Process $python -ArgumentList "/quiet InstallAllUsers=1 PrependPath=1" -PassThru -wait
        if ($install.ExitCode -eq 0) {
            Write-Host "Installation completed successfully."
        }
        else {
            Write-Host "Installation failed with exit code $install.ExitCode"
        }
    }
}

Cleanup
