# Script para instalar o bot como servico Windows
# Auto-eleva para admin se necessario

# Verificar se tem privilegios de admin
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")

if (-not $isAdmin) {
    Write-Host "Este script precisa rodar como administrador."
    Write-Host "Elevando privilégios..."
    Write-Host ""

    # Re-executar como admin
    $scriptPath = $MyInvocation.MyCommand.Path
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`"" -Verb RunAs
    exit
}

# Agora estamos rodando como admin
Write-Host ""
Write-Host "========================================"
Write-Host "Instalacao do Bot Telegram - Servico Windows"
Write-Host "========================================"
Write-Host ""

# Definir caminhos
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$botPath = $scriptDir
$batchFile = Join-Path $botPath "run_bot.bat"

Write-Host "Bot path: $botPath"
Write-Host "Batch file: $batchFile"
Write-Host ""

# Verificar se o batch file existe
if (-not (Test-Path $batchFile)) {
    Write-Host "ERRO: Arquivo $batchFile nao encontrado!"
    Write-Host ""
    Write-Host "Verifique que todos os arquivos estao no lugar correto."
    Read-Host "Pressione Enter para sair"
    exit 1
}

# Criar a tarefa agendada
try {
    Write-Host "Criando tarefa agendada..."

    $action = New-ScheduledTaskAction -Execute $batchFile -WorkingDirectory $botPath
    $trigger = New-ScheduledTaskTrigger -AtStartup
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -StartWhenAvailable `
        -MultipleInstances IgnoreNew

    $principal = New-ScheduledTaskPrincipal `
        -UserID $env:USERNAME `
        -RunLevel Highest `
        -LogonType ServiceAccount

    # Remover tarefa existente se ela ja existe
    $existingTask = Get-ScheduledTask -TaskName "TelegramClientBot" -ErrorAction SilentlyContinue
    if ($existingTask) {
        Write-Host "Removendo tarefa existente..."
        Unregister-ScheduledTask -TaskName "TelegramClientBot" -Confirm:$false
    }

    Register-ScheduledTask -TaskName "TelegramClientBot" `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Principal $principal `
        -Description "Bot Telegram para coleta de dados de cliente com Claude API" `
        -Force | Out-Null

    Write-Host ""
    Write-Host "========================================"
    Write-Host "SUCESSO! Tarefa instalada com exito!"
    Write-Host "========================================"
    Write-Host ""
    Write-Host "Detalhes da tarefa:"
    Write-Host "  Nome: TelegramClientBot"
    Write-Host "  Status: Pronta para executar"
    Write-Host "  Arquivo: $batchFile"
    Write-Host ""

    # Verificar se a tarefa foi criada
    $task = Get-ScheduledTask -TaskName "TelegramClientBot" -ErrorAction SilentlyContinue
    if ($task) {
        Write-Host "Status: $($task.State)"
    }

    Write-Host ""
    Write-Host "Proximos passos:"
    Write-Host ""
    Write-Host "1. Para iniciar o bot agora:"
    Write-Host "   Start-ScheduledTask -TaskName 'TelegramClientBot'"
    Write-Host ""
    Write-Host "2. Para ver o status:"
    Write-Host "   Get-ScheduledTask -TaskName 'TelegramClientBot'"
    Write-Host ""
    Write-Host "3. Para parar o bot:"
    Write-Host "   Stop-ScheduledTask -TaskName 'TelegramClientBot'"
    Write-Host ""

}
catch {
    Write-Host ""
    Write-Host "ERRO ao criar tarefa:"
    Write-Host $_.Exception.Message
    Write-Host ""
    Write-Host "Verifique que:"
    Write-Host "  - Voce tem privilegios de administrador"
    Write-Host "  - Todos os arquivos estao no lugar correto"
    Write-Host "  - O Windows Task Scheduler esta funcionando"
    Write-Host ""
}

Write-Host ""
Write-Host "Pressione Enter para fechar..."
Read-Host
