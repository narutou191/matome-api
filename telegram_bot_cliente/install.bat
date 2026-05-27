@echo off
REM Script para instalar o bot como serviço Windows
REM Execute com privilégios de administrador

setlocal enabledelayedexpansion

REM Verificar se tem privilégios de admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo Este script precisa rodar com privilegios de administrador.
    echo Executando como admin...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd %CD% ^& %~0' -Verb runAs"
    exit /b
)

echo.
echo ====================================
echo Instalacao do Bot Telegram - Servico Windows
echo ====================================
echo.
echo Caminho: %CD%
echo.

REM Executar o script PowerShell
powershell -NoProfile -ExecutionPolicy Bypass -Command "& '.\create_task.ps1'"

echo.
echo ====================================
echo Instalacao concluida!
echo ====================================
echo.
echo Para iniciar o bot agora, execute:
echo   Start-ScheduledTask -TaskName 'TelegramClientBot'
echo.
echo Para ver mais opcoes, abra:
echo   SETUP_WINDOWS_SERVICE.md
echo.
pause
