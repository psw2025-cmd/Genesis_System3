Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Get the script directory
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)
batFile = scriptDir & "\start_system3_autorun.bat"

' Check if batch file exists
If fso.FileExists(batFile) Then
    ' Run the batch file invisibly
    WshShell.Run """" & batFile & """", 0, False
Else
    ' If batch file doesn't exist, try to run Python directly
    pythonScript = scriptDir & "\system3_autorun_master.py"
    If fso.FileExists(pythonScript) Then
        venvPython = scriptDir & "\venv\Scripts\python.exe"
        If fso.FileExists(venvPython) Then
            WshShell.Run """" & venvPython & """ """ & pythonScript & """", 0, False
        Else
            ' Fallback to system Python
            WshShell.Run "python """ & pythonScript & """", 0, False
        End If
    End If
End If

