$botPath = "C:\Users\hiros\Mirai\telegram_bot_cliente"
$batchFile = "$botPath\run_bot.bat"

Write-Host "Creating Task Scheduler job..."
Write-Host "Bot path: $botPath"
Write-Host "Batch file: $batchFile"
Write-Host ""

$action = New-ScheduledTaskAction -Execute $batchFile -WorkingDirectory $botPath
$trigger = New-ScheduledTaskTrigger -AtStartup
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable -MultipleInstances IgnoreNew
$principal = New-ScheduledTaskPrincipal -UserID $env:USERNAME -RunLevel Highest

try {
    Register-ScheduledTask -TaskName "TelegramClientBot" `
      -Action $action `
      -Trigger $trigger `
      -Settings $settings `
      -Principal $principal `
      -Description "Telegram Bot para coleta de dados de cliente" `
      -Force

    Write-Host "SUCCESS: Task 'TelegramClientBot' created!"
    Write-Host ""
    Write-Host "Start the task with:"
    Write-Host "  Start-ScheduledTask -TaskName 'TelegramClientBot'"
    Write-Host ""
    Write-Host "Stop the task with:"
    Write-Host "  Stop-ScheduledTask -TaskName 'TelegramClientBot'"
}
catch {
    Write-Host "ERROR: $($_.Exception.Message)"
    Write-Host ""
    Write-Host "Try running PowerShell as Administrator and execute this script again"
}
