# Instalação do Bot como Serviço Windows 24/7

Siga os passos abaixo para configurar o bot Telegram para rodar automaticamente 24/7 no seu PC.

## Opção 1: Instalação Automatizada (Recomendado)

### Passo 1: Executar o script de instalação

1. Abra o **Explorador de Arquivos** (Windows Explorer)
2. Navegue até: `C:\Users\hiros\Mirai\telegram_bot_cliente`
3. Clique com o botão direito em **`RunAsAdmin.vbs`**
4. Selecione **"Executar com privilégios de administrador"**

O script solicitará confirmação de privilégios de administrador. Clique em **"Sim"**.

### Passo 2: Verificar instalação

Após o script terminar, o bot deve estar instalado como tarefa agendada.

Para confirmar, abra o PowerShell como administrador e execute:
```powershell
Get-ScheduledTask -TaskName "TelegramClientBot" | Select-Object State, TaskName
```

Você deve ver: `State: Ready`

## Opção 2: Instalação Manual (Caso 1 falhe)

### Passo 1: Abrir PowerShell como Administrador

1. Pressione `Windows + X`
2. Selecione **"Windows PowerShell (Admin)"**
3. Clique **"Sim"** no aviso de controle de conta

### Passo 2: Executar comando de instalação

Cole e execute este comando no PowerShell:

```powershell
cd "C:\Users\hiros\Mirai\telegram_bot_cliente"
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
& ".\create_task.ps1"
```

### Passo 3: Confirmar criação da tarefa

Você deve ver uma mensagem de sucesso.

## Gerenciar o Serviço

### Iniciar o bot imediatamente

```powershell
Start-ScheduledTask -TaskName "TelegramClientBot"
```

### Parar o bot

```powershell
Stop-ScheduledTask -TaskName "TelegramClientBot"
```

### Ver status do bot

```powershell
Get-ScheduledTask -TaskName "TelegramClientBot" | Select-Object State, TaskName, LastRunTime
```

### Ver logs de execução

O bot escreve logs automaticamente. Para ver os últimos 50 linhas:

```powershell
Get-EventLog -LogName System -Source "TelegramClientBot" -Newest 50
```

## Desinstalar o Serviço

Se precisar remover a tarefa agendada:

```powershell
Unregister-ScheduledTask -TaskName "TelegramClientBot" -Confirm:$false
```

## Troubleshooting

### O bot não está rodando

1. Verifique se a tarefa foi criada:
   ```powershell
   Get-ScheduledTask -TaskName "TelegramClientBot"
   ```

2. Verifique o status:
   ```powershell
   Get-ScheduledTask -TaskName "TelegramClientBot" | Select-Object State
   ```

3. Veja o arquivo de log em: `C:\Users\hiros\Mirai\telegram_bot_cliente\logs\`

### Privilégios insuficientes

Se receber erro "Acesso negado":
- Abra PowerShell como **Administrador**
- Execute o comando novamente

### Arquivo run_bot.bat não encontrado

Isso significa que o arquivo foi deletado ou movido. Recrie-o:
```powershell
cd "C:\Users\hiros\Mirai\telegram_bot_cliente"
# O arquivo deve ser criado automaticamente
```

## Verificação Final

Para confirmar que tudo está funcionando:

1. Abra o **Agendador de Tarefas** (Task Scheduler)
2. Procure por **"TelegramClientBot"** na lista de tarefas
3. O status deve mostrar **"Pronto"** ou **"Executando"**
4. Clique com botão direito e selecione **"Propriedades"** para ver detalhes

## Próximos Passos

Com o bot rodando 24/7, você pode:

1. Abrir Telegram e conversar com seu bot
2. Enviar `/start` para começar o cadastro de clientes
3. Responder às perguntas em sequência (5 blocos de dados)
4. Enviar `/complete` ao final para gerar o Excel

Os arquivos Excel serão salvos em:
```
C:\Users\hiros\Mirai\telegram_bot_cliente\output\
```

## Suporte

Se encontrar problemas:
1. Verifique que as chaves de API estão corretas em `.env`
2. Verifique que o Python 3.14 está instalado
3. Verifique se todos os arquivos estão no lugar correto
