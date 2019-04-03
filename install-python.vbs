' Copyright 2019 Amazon.com, Inc. or its affiliates. All Rights Reserved.
'
' Licensed under the Apache License, Version 2.0 (the "License"). You
' may not use this file except in compliance with the License. A copy of
' the License is located at
'
' http://aws.amazon.com/apache2.0/
'
' or in the "license" file accompanying this file. This file is
' distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
' ANY KIND, either express or implied. See the License for the specific
' language governing permissions and limitations under the License.

' Python installation script for Windows.
' To run this script, type "cscript install-python.vbs && exit" from the command line.
dim fso: set fso = CreateObject ("Scripting.FileSystemObject")
dim stdout: set stdout = fso.GetStandardStream(1)
currentDirectory = left(WScript.ScriptFullName,(Len(WScript.ScriptFullName))-(len(WScript.ScriptName)))

if NOT(isPythonInstalled()) then
   downloadUrl = pythonDownload()
   stdout.WriteLine "Downloading Python from " + downloadUrl
   if len(downloadUrl) > 0 then
      if (installPython() = 0) then
         openNewCommandWindow()
         WScript.Quit 0
      end if
   else
      WScript.Quit -1
   end if
end if

set stdout = Nothing
set fso = Nothing
  
function installPython()
   dim http: set http = createobject("Microsoft.XMLHTTP")
   dim stream: set stream = createobject("Adodb.Stream")
   http.Open "GET", downloadUrl, False
   http.Send

   with stream
      .type = 1 'binary
      .open
      .write http.responseBody
      .savetofile "python3.7.3.exe", 2 'overwrite
   end with
   stream.Flush()
   stdout.WriteLine "Download complete."

   set stream = Nothing
   set http = Nothing

   dim shell: set shell =  CreateObject("WScript.Shell")
   stdout.WriteLine "Silently installing Python. Do not close this window."
   exitCode = shell.Run("python3.7.3.exe " + "/quiet InstallAllUsers=1 PrependPath=1",,true) 'Wait on return
   if (exitCode = 0) then
      stdout.WriteLine "Installation completed successfully."
   else
      stdout.WriteLine "Installation failed with exit code " & exitCode 
   end if

   if (fso.FileExists(currentDirectory & "python3.7.3.exe")) then
      fso.DeleteFile(currentDirectory & "python3.7.3.exe") 
   end if
 
   installPython = exitCode

   set shell = Nothing

end function

function isPythonInstalled()
   dim wmi: set wmi = GetObject("winmgmts:{impersonationLevel=impersonate}!\\.\root\cimv2")
   dim query: set query = wmi.ExecQuery ("Select * from Win32_Product where Caption Like '%Python 3.7.3 Executables%'")
   isPythonInstalled = (query.Count <> 0)
   if (isPythonInstalled) then
      stdout.WriteLine "Found an existing Python installation."
   end if
   set query = Nothing
   set wmi = Nothing
end function

function openNewCommandWindow()
   dim wmi: set wmi = GetObject("winmgmts:\\.\root\cimv2")
   dim config: set config = wmi.Get("Win32_ProcessStartup")
   config.SpawnInstance_
      config.X = 100
      config.Y = 100

   dim commandProcess: set commandProcess = wmi.Get("Win32_Process")
   commandProcess.Create "cmd.exe", currentDirectory, config, procId

   set config = Nothing
   set wmi = Nothing
end function

function pythonDownload()
   dim shell : set shell = CreateObject("WScript.Shell")
   dim process: set process = shell.Environment("Process")

   processor = process("PROCESSOR_ARCHITECTURE") 
   select case LCase(processor)
      case "x86"
      stdout.WriteLine "Downloading x86 version of Python."
      pythonDownload = "https://www.python.org/ftp/python/3.7.3/python-3.7.3-webinstall.exe"
   case "amd64"
      stdout.WriteLine "Downloading x64 version of Python."
      pythonDownload = "https://www.python.org/ftp/python/3.7.3/python-3.7.3-amd64-webinstall.exe"
   case else
      stdout.WriteLine "Unable to determine the Python download url for processor type: " & processor
      pythonDownload = ""
   end select

   set process = Nothing
   set shell = Nothing
end function
