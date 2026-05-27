' Este script executa create_task.ps1 com privilégios de administrador
' Criado para automatizar a instalação do bot como serviço Windows

If WScript.Arguments.Named.Exists("elevate") then
  ' Já foi elevado
  Set objShell = CreateObject("Shell.Application")
  Set objFso = CreateObject("Scripting.FileSystemObject")
  strScript = objFso.GetParentFolderName(WScript.ScriptFullName) & "\create_task.ps1"
  strCommand = "PowerShell -NoProfile -ExecutionPolicy Bypass -Command """ & strScript & """"
  objShell.ShellExecute "cmd.exe", "/c " & strCommand, "", "open", 1
else
  ' Pedir elevação
  Set objShell = CreateObject("Shell.Application")
  objShell.ShellExecute "wscript.exe", """" & WScript.ScriptFullName & """ /elevate", "", "runas", 1
end if
