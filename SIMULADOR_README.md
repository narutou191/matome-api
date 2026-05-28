# Simulador de Financiamento Imobiliário

## 📋 Sobre

Simulador interativo para cálculo de parcelas de financiamento imobiliário no Japão, com suporte a 3 modalidades de taxa:
- **100% Fixo Flat Rate** (taxa fixa ao longo de todo o período)
- **Variable 1 (SBI)** (taxa variável do banco)
- **Variable 2 (Roukin)** (taxa variável cooperativa)

Funcionalidades:
✅ Cálculo simultâneo de 3 modalidades de financiamento  
✅ Geração de PDF profissional para apresentação ao cliente  
✅ Design responsivo (mobile, tablet, desktop)  
✅ Interface escura com tema corporativo (Ouro, Verde, Azul, Laranja)  
✅ Formatação em Iene Japonês (¥X,XXX,XXX)  
✅ Integração WordPress Elementor

---

## 🚀 Como Usar

### Opção 1: Elementor Custom HTML Widget (Recomendado)

1. **Acesse seu site WordPress**
2. **Abra a página desejada em modo de edição**
3. **Adicione widget → Custom HTML**
4. **Copie o conteúdo completo do arquivo `simulador-financiamento.html`**
   - Abra o arquivo em um editor de texto (VS Code, Sublime, etc.)
   - Selecione todo o conteúdo (Ctrl+A)
   - Copie (Ctrl+C)
5. **Cole na seção de conteúdo do widget Custom HTML**
6. **Salve a página**

### Opção 2: Arquivo Independente

Se quiser usar o simulador fora do WordPress:

1. **Copie `simulador-financiamento.html` para seu servidor web**
2. **Acesse via navegador**
   - Exemplo: `https://seu-site.com/simulador/`
3. **Ou abra localmente**
   - Windows: Clique duplo no arquivo
   - Mac/Linux: Abra em um navegador

---

## ⚙️ Funcionalidades

### Seção de Simulação
- **Nome do Cliente** — Aparece no cabeçalho e no PDF
- **Valor do Imóvel** — Valor total da propriedade (padrão: ¥25.000.000)
- **Período de Financiamento** — Anos (padrão: 50 anos)

### Taxas de Juros
- **100% Fixo** — Padrão: 2.37% a.a.
- **SBI Variable** — Padrão: 0.81% a.a.
- **Roukin Variable** — Padrão: 1.09% a.a.

### Custos Adicionais
- Seguro Habitacional
- Inspeção de Imóvel
- Registro/Cartório
- Imposto de Transmissão
- Taxa de Gerência
- Análise de Crédito
- Outros

Todos com valores padrão calibrados para imóveis japoneses típicos.

### Resultado da Simulação

Após clicar **Simular**, a página exibe:

1. **Resumo Comparativo**
   - Parcela mensal para cada modalidade
   - Total de juros pagos
   - Comparação percentual

2. **Tabela de Parcelas (50 anos)**
   - Ano, Parcela, Juros, Amortização, Saldo

3. **Botão Gerar PDF**
   - Baixa relatório profissional
   - Inclui nome do cliente e data
   - Pronto para apresentação

---

## 🎨 Características de Design

| Elemento | Descrição |
|----------|-----------|
| **Paleta** | Ouro #d4af37, Verde #2dd4a4, Azul #3b82f6, Laranja #f59e0b, Cinza #333333 |
| **Tipografia** | Sistema Segoe UI, roboto, sans-serif |
| **Responsividade** | Mobile (320px), Tablet (768px), Desktop (1400px) |
| **Modo** | Dark Mode (tema noturno) |
| **PDF** | Paisagem, com logo e rodapé |

---

## 🔧 Compatibilidade

| Requisito | Suporte |
|-----------|---------|
| **Navegadores** | Chrome, Firefox, Safari, Edge (últimas 2 versões) |
| **Mobile** | iOS Safari, Chrome Android |
| **WordPress** | 5.0+ (com Elementor 3.0+) |
| **JavaScript** | ES6+ (nativo, sem dependências externas) |
| **PDF** | html2pdf.js (carregado via CDN) |

---

## 📊 Fórmula de Cálculo

A parcela mensal é calculada usando a fórmula padrão de financiamento:

```
P = VE × [i × (1 + i)^n] / [(1 + i)^n - 1]
```

Onde:
- **P** = Parcela mensal
- **VE** = Valor do empréstimo
- **i** = Taxa mensal (anual ÷ 12)
- **n** = Número total de parcelas (anos × 12)

### Exemplo (Valores Padrão)
```
Valor do Imóvel:  ¥25.000.000
Taxa Fixa:        2.37% a.a.
Período:          50 anos

Parcela Mensal:   ¥78.222
Total de Juros:   ¥21.933.200
Valor Total Pago: ¥46.933.200
```

---

## 🖥️ Estrutura do Arquivo

```html
<!DOCTYPE html>
<html>
  <head>
    <!-- Meta tags, CSS estilos, html2pdf.js -->
  </head>
  <body>
    <!-- HEADER -->
    <!-- SEÇÃO DE FORMULÁRIO -->
    <!-- SEÇÃO DE RESULTADOS -->
    <!-- TEMPLATE PDF OCULTO -->
    <script>
      // Funções de cálculo
      // Funções de formatação
      // Event listeners
    </script>
  </body>
</html>
```

**Nomes de classe/ID utilizam prefixo "sim-"** para evitar conflitos com Elementor:
- `.sim-container` — Container principal
- `.sim-form-*` — Seção de formulário
- `.sim-result-*` — Seção de resultados
- `#sim-input-*` — Campos de entrada

---

## 🐛 Troubleshooting

### PDF não gera
- ✅ Verifique conexão com internet (html2pdf.js é carregado via CDN)
- ✅ Permita pop-ups no navegador
- ✅ Teste em navegador moderno (Chrome, Firefox)

### Números não formatam corretamente
- ✅ Navegador suporta `Intl.NumberFormat`
- ✅ Locale PT-BR está configurado no código

### Elementor não exibe corretamente
- ✅ Desabilite "Estrutura da Página" em Elementor
- ✅ Teste em navegação privada (sem cache)
- ✅ Limpe cache do WordPress

### Valores padrão incorretos
- Edite a seção `<!-- VALORES PADRÃO -->` no arquivo HTML
- Procure por `document.getElementById('sim-input-...')` e altere `.value`

---

## 📝 Notas Importantes

⚠️ **Esta é uma simulação** — Os valores calculados são estimativas e podem variar conforme:
- Flutuações das taxas de juros
- Alterações nas condições de financiamento
- Mudanças na legislação fiscal japonesa

Sempre consulte o banco ou instituição financeira para valores oficiais.

---

## 📄 Licença

Desenvolvido para uso interno no projeto VISION (2026).

---

## 🔗 Referências

- Documentação de Design: `docs/superpowers/specs/2026-05-28-simulador-financiamento-design.md`
- Plano de Implementação: `docs/superpowers/plans/2026-05-28-simulador-financiamento.md`
- Template Excel Original: `data/template.xlsx`

---

**Última atualização:** 28/05/2026  
**Versão:** 1.0
