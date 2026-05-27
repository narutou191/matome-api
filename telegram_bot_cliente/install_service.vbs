' Script para instalar o bot como serviço Windows usando Task Scheduler
' Requer privilégios de administrador

Set objShell = CreateObject("Shell.Application")
Set objFSO = CreateObject("Scripting.FileSystemObject")

' Verificar se rodando como admin
strComputer = "."
Set objWMI = GetObject("winmgmts:\\" & strComputer & "\root\cimv2")
Set colItems = objWMI.ExecQuery("Select * from Win32_Process where Name='explorer.exe'")

If colItems.Count = 0 Then
    ' Não é admin, pedir elevação
    MsgBox "Este script precisa rodar como administrador.", vbInformation, "Elevando privilégios..."
    objShell.ShellExecute "cscript.exe", """" & WScript.ScriptFullName & """", "", "runas", 1
    WScript.Quit
End If

' Caminhos
strBotPath = "C:\Users\hiros\Mirai\telegram_bot_cliente"
strBatchFile = strBotPath & "\run_bot.bat"

MsgBox "Instalando bot como tarefa agendada..." & vbCrLf & vbCrLf & _
    "Caminho: " & strBotPath & vbCrLf & _
    "Arquivo: " & strBatchFile, vbInformation, "Instalação do Bot"

' Criar comando para agendar tarefa
strCommand = "powershell -Command """ & _
    "$action = New-ScheduledTaskAction -Execute '" & strBatchFile & "' -WorkingDirectory '" & strBotPath & "'; " & _
    "$trigger = New-ScheduledTaskTrigger -AtStartup; " & _
    "$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable; " & _
    "$principal = New-ScheduledTaskPrincipal -UserID $env:USERNAME -LogonType ServiceAccount -RunLevel Highest; " & _
    "Register-ScheduledTask -TaskName 'TelegramClientBot' -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description 'Bot Telegram para cadastro de clientes' -Force;" & _
    """"

Set objShell2 = CreateObject("WScript.Shell")
intReturn = objShell2.Run(strCommand, 1, True)

If intReturn = 0 Then
    MsgBox "Tarefa 'TelegramClientBot' instalada com sucesso!" & vbCrLf & vbCrLf & _
        "Para iniciar agora:" & vbCrLf & _
        "  Start-ScheduledTask -TaskName 'TelegramClientBot'" & vbCrLf & vbCrLf & _
        "Para parar:" & vbCrLf & _
        "  Stop-ScheduledTask -TaskName 'TelegramClientBot'", vbInformation, "Sucesso"
Else
    MsgBox "Erro ao instalar tarefa. Codigo: " & intReturn, vbCritical, "Erro"
End If
