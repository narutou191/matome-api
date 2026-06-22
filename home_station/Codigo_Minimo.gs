const TEMPLATE_ID = "11H63Fh54-P0Ue5_kVot8H8uW13cVLZzpaplE3L6cwSs";

// FUNCAO PRINCIPAL: Salvar Ficha com solucao alternativa (SpreadsheetApp.create + copyTo)
function salvarFichaCliente(dados) {
  try {
    Logger.log('1. Validando dados...');
    if (!dados.nome || dados.nome.length < 3) {
      throw new Error('Nome obrigatorio');
    }

    Logger.log('2. Abrindo template...');
    const templateSheet = SpreadsheetApp.openById(TEMPLATE_ID);
    Logger.log('Template aberto: ' + templateSheet.getName());

    const nomeArquivo = gerarNomeArquivo(dados.nome);
    Logger.log('3. Criando novo arquivo: ' + nomeArquivo);

    // SOLUCAO: Usar SpreadsheetApp.create() + copyTo() em vez de makeCopy()
    const novoSheet = SpreadsheetApp.create(nomeArquivo);
    const novoSheetId = novoSheet.getId();
    Logger.log('4. Novo Sheet criado: ' + novoSheetId);

    // Copiar sheet do template para o novo arquivo
    const templateSourceSheet = templateSheet.getSheets()[0];
    const novaAbaCopiada = templateSourceSheet.copyTo(novoSheet);
    Logger.log('5. Sheet copiado com sucesso');

    // Remover aba padrao vazia criada pelo create()
    const abasNovoSheet = novoSheet.getSheets();
    for (let i = 0; i < abasNovoSheet.length; i++) {
      if (abasNovoSheet[i].getName() !== novaAbaCopiada.getName()) {
        novoSheet.deleteSheet(abasNovoSheet[i]);
      }
    }
    Logger.log('6. Aba padrao removida');

    // Mover arquivo para raiz do Drive (Meu Drive)
    try {
      const fileObj = DriveApp.getFileById(novoSheetId);
      Logger.log('7. Arquivo encontrado no Drive: ' + fileObj.getName());
      const rootFolder = DriveApp.getRootFolder();
      fileObj.moveTo(rootFolder);
      Logger.log('8. Arquivo movido para Meu Drive');
    } catch (driveError) {
      Logger.log('7. Aviso - Problema ao mover arquivo: ' + driveError.toString());
    }

    const link = 'https://docs.google.com/spreadsheets/d/' + novoSheetId + '/edit';
    const mensagem = 'OK: Ficha de ' + dados.nome + ' criada!\n\nLink: ' + link;
    Logger.log('9. SUCESSO: ' + mensagem);
    return mensagem;
  } catch (erro) {
    Logger.log('ERRO: ' + erro.toString());
    throw erro;
  }
}

// Funcoes auxiliares
function gerarNomeArquivo(nome) {
  const hoje = new Date();
  const dia = String(hoje.getDate()).padStart(2, '0');
  const mes = String(hoje.getMonth() + 1).padStart(2, '0');
  const ano = hoje.getFullYear();
  return nome.trim().toUpperCase() + ' - Ficha ' + dia + '-' + mes + '-' + ano;
}

// TESTE
function testeCompleto() {
  var dados = {
    nome: 'SILVA TARO'
  };
  var resultado = salvarFichaCliente(dados);
  Logger.log(resultado);
  return resultado;
}
