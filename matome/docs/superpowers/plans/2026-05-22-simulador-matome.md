# Simulador MATOME — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Criar `matome/index.html` — simulador de consolidação de dívidas (wizard 3 telas) com cálculo PMT automático, máscara ¥, responsivo mobile-first e geração de PDF via Print CSS.

**Architecture:** Arquivo HTML único com CSS e JS inline. Estado global em objeto `state`. Cada tela é uma `<div class="tela">` — visibilidade controlada por JS. Render functions atualizam o DOM ao vivo conforme o usuário digita.

**Tech Stack:** HTML5, CSS3 (custom properties, grid, media queries), Vanilla JS (ES6+), `window.print()` para PDF.

---

## Estrutura de Arquivos

```
matome/
└── index.html   ← único arquivo entregável
```

---

## Task 1: HTML skeleton + CSS completo

**Files:**
- Create: `matome/index.html`

- [ ] **Step 1: Criar o arquivo com estrutura base**

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MATOME — Simulador de Consolidação de Dívidas</title>
<style>
/* ── RESET E VARIÁVEIS ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
:root {
  --bg: #f5f3ef;
  --dark: #2d2d2d;
  --gold: #c9a84c;
  --text: #2d2d2d;
  --label: #888;
  --border: #d0c8b8;
  --divider: #e0d8c8;
  --before-bg: #fff5f5;
  --before-border: #f0c0c0;
  --before-color: #cc0000;
  --after-bg: #f5fff8;
  --after-border: #a0d8b0;
  --after-color: #006600;
}
body { font-family: 'Segoe UI', sans-serif; background: var(--bg); color: var(--text); min-height: 100vh; }

/* ── HEADER ── */
.header { background: var(--dark); border-bottom: 3px solid var(--gold); padding: 16px 24px; }
.logo { font-size: 24px; font-weight: 300; color: #fff; letter-spacing: 5px; text-transform: uppercase; }
.logo strong { font-weight: 900; color: var(--gold); }
.tagline { font-size: 10px; color: #888; letter-spacing: 1.5px; margin-top: 3px; }

/* ── STEPS ── */
.steps { display: flex; background: #fff; border-bottom: 1px solid var(--divider); position: sticky; top: 0; z-index: 10; }
.step { flex: 1; padding: 12px 6px; text-align: center; font-size: 10px; color: #aaa; border-bottom: 3px solid transparent; letter-spacing: 0.5px; text-transform: uppercase; line-height: 1.4; transition: all 0.2s; cursor: default; }
.step.active { color: var(--dark); border-bottom-color: var(--gold); font-weight: 700; }
.step.done { color: var(--gold); }

/* ── TELAS ── */
.tela { display: none; }
.tela.active { display: block; }

/* ── CONTAINER ── */
.container { max-width: 660px; margin: 0 auto; padding: 28px 20px; }

/* ── SECTION TITLE ── */
.sec-title {
  font-size: 10px; font-weight: 700; color: var(--gold);
  letter-spacing: 2px; text-transform: uppercase;
  border-bottom: 1px solid var(--divider); padding-bottom: 8px; margin-bottom: 18px;
}

/* ── FIELD GROUP ── */
.field-group { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; margin-bottom: 24px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { font-size: 11px; color: var(--label); line-height: 1.4; }
.field label em { font-style: normal; color: #bbb; font-size: 10px; display: block; }
.field input, .field select {
  padding: 10px 0; border: none; border-bottom: 1.5px solid var(--border);
  background: transparent; font-size: 15px; font-weight: 600; color: var(--text); width: 100%;
  border-radius: 0; -webkit-appearance: none;
}
.field input:focus, .field select:focus { outline: none; border-bottom-color: var(--gold); }
.field input[type="date"] { font-weight: 400; font-size: 14px; }
.field select { cursor: pointer; background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='8' viewBox='0 0 12 8'%3E%3Cpath fill='%23888' d='M6 8L0 0h12z'/%3E%3C/svg%3E"); background-repeat: no-repeat; background-position: right 4px center; padding-right: 20px; }

/* ── TOTAL BOX ── */
.total-box {
  display: flex; justify-content: space-between; align-items: center;
  border: 1px solid var(--gold); border-radius: 4px;
  padding: 12px 16px; background: #fffdf7; margin-bottom: 24px; flex-wrap: wrap; gap: 6px;
}
.total-box .lbl { font-size: 11px; color: var(--label); letter-spacing: 1px; text-transform: uppercase; }
.total-box .val { font-size: 20px; font-weight: 700; }

/* ── CALC BOX ── */
.calc-box { background: var(--dark); border-radius: 4px; padding: 16px 18px; margin-bottom: 24px; }
.calc-title { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; }
.calc-line { display: flex; justify-content: space-between; align-items: baseline; font-size: 13px; padding: 4px 0; color: #ccc; gap: 8px; }
.calc-line .ck { flex: 1; }
.calc-line .cv { white-space: nowrap; }
.calc-line .plus { color: #666; margin-right: 6px; }
.calc-line.sum { border-top: 1px solid #444; margin-top: 6px; padding-top: 10px; }
.calc-line.sum .ck { color: #fff; font-weight: 700; }
.calc-line.sum .cv { color: var(--gold); font-size: 16px; font-weight: 800; }
.calc-line.pmt { border-top: none; margin-top: 2px; padding-top: 4px; }
.calc-line.pmt .ck { color: #aaa; font-weight: 400; font-size: 12px; }
.calc-line.pmt .cv { color: var(--gold); font-size: 18px; font-weight: 900; }

/* ── BUTTON ── */
.btn {
  width: 100%; padding: 14px; background: var(--dark); border: none;
  border-radius: 4px; font-size: 13px; font-weight: 700; color: var(--gold);
  cursor: pointer; letter-spacing: 3px; text-transform: uppercase; touch-action: manipulation;
  transition: background 0.2s;
}
.btn:hover { background: #3d3d3d; }
.btn.secondary { background: transparent; border: 1px solid var(--border); color: var(--label); letter-spacing: 1px; margin-bottom: 10px; }
.btn.secondary:hover { border-color: var(--dark); color: var(--dark); }

/* ── RESULT ── */
.result-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 20px; }
.result-col { border-radius: 4px; padding: 14px; }
.result-col.before { background: var(--before-bg); border: 1px solid var(--before-border); }
.result-col.after  { background: var(--after-bg);  border: 1px solid var(--after-border); }
.col-title { font-size: 10px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; margin-bottom: 10px; padding-bottom: 8px; border-bottom: 1px solid; }
.result-col.before .col-title { color: var(--before-color); border-color: var(--before-border); }
.result-col.after  .col-title { color: var(--after-color);  border-color: var(--after-border); }
.result-row { display: flex; justify-content: space-between; padding: 3px 0; font-size: 12px; gap: 4px; }
.result-row .ri { color: #555; flex: 1; }
.result-row .ra { font-weight: 600; white-space: nowrap; }
.result-row.tr { border-top: 1px solid #ccc; margin-top: 6px; padding-top: 8px; font-weight: 700; }
.result-row.note { font-size: 10px; color: #999; font-style: italic; }
.result-row.zero .ra { color: var(--after-color); }

/* ── ECONOMY BOX ── */
.eco-box { background: var(--dark); border-radius: 4px; padding: 22px 16px; text-align: center; margin-bottom: 20px; }
.eco-box .eco-lbl { font-size: 10px; color: #888; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 6px; }
.eco-box .eco-big { font-size: 30px; font-weight: 900; color: var(--gold); line-height: 1.2; }
.eco-box .eco-sub { font-size: 12px; color: #aaa; margin-top: 8px; line-height: 1.8; }

/* ── PDF PRINT HEADER ── */
.pdf-header { display: none; }

/* ── RESPONSIVE ── */
@media (max-width: 480px) {
  .header { padding: 14px 16px; }
  .logo { font-size: 20px; letter-spacing: 3px; }
  .step { font-size: 9px; padding: 10px 4px; }
  .container { padding: 20px 16px; }
  .field-group { grid-template-columns: 1fr; gap: 14px; }
  .result-grid { grid-template-columns: 1fr; }
  .eco-box .eco-big { font-size: 24px; }
  .calc-line { font-size: 12px; }
  .calc-line.sum .cv { font-size: 14px; }
  .calc-line.pmt .cv { font-size: 16px; }
}
@media (min-width: 481px) and (max-width: 768px) {
  .result-grid { grid-template-columns: 1fr; }
}

/* ── PRINT / PDF ── */
@media print {
  body { background: #fff; }
  .steps, .btn, .header { display: none !important; }
  .tela { display: block !important; }
  .pdf-header { display: block; border-bottom: 3px solid var(--gold); padding-bottom: 16px; margin-bottom: 24px; }
  .pdf-logo { font-size: 28px; font-weight: 300; letter-spacing: 6px; text-transform: uppercase; color: var(--dark); }
  .pdf-logo strong { font-weight: 900; color: var(--gold); }
  .pdf-tagline { font-size: 10px; color: #888; letter-spacing: 2px; margin-top: 3px; }
  .pdf-client { font-size: 13px; color: #555; margin-top: 8px; }
  .tela-1-content, .tela-2-content { display: none; }
  .result-grid { grid-template-columns: 1fr 1fr !important; }
  .calc-box { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .eco-box  { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .result-col.before { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .result-col.after  { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .pdf-footer { margin-top: 24px; font-size: 10px; color: #bbb; text-align: center; border-top: 1px solid #eee; padding-top: 12px; }
}
</style>
</head>
<body>

<div class="header">
  <div class="logo"><strong>MATOME</strong></div>
  <div class="tagline">まとめ · SOLUCIONANDO SUA DÍVIDA NO JAPÃO 🇯🇵</div>
</div>

<div class="steps">
  <div class="step active" id="step1">① Situação Atual</div>
  <div class="step"        id="step2">② Proposta</div>
  <div class="step"        id="step3">③ Resultado</div>
</div>

<!-- TELA 1 -->
<div class="tela active" id="tela1">
  <div class="container tela-1-content">
    <!-- campos serão adicionados nas próximas tasks -->
  </div>
</div>

<!-- TELA 2 -->
<div class="tela" id="tela2">
  <div class="container tela-2-content">
  </div>
</div>

<!-- TELA 3 -->
<div class="tela" id="tela3">
  <!-- PDF header (visível só no print) -->
  <div class="pdf-header container">
    <div class="pdf-logo"><strong>MATOME</strong></div>
    <div class="pdf-tagline">まとめ · SOLUCIONANDO SUA DÍVIDA NO JAPÃO 🇯🇵</div>
    <div class="pdf-client" id="pdf-client-info"></div>
  </div>
  <div class="container">
  </div>
  <div class="pdf-footer container">Simulação gerada pelo Simulador MATOME · Valores ilustrativos sujeitos à análise de crédito</div>
</div>

<script>
// JS será adicionado nas próximas tasks
</script>
</body>
</html>
```

- [ ] **Step 2: Abrir no browser e verificar**

Abrir `matome/index.html` no browser. Verificar:
- Header preto com borda dourada aparece
- Steps "① Situação Atual" está ativo (cor escura)
- Página em branco abaixo (normal — campos ainda não adicionados)
- DevTools → mobile 375px: header não quebra

- [ ] **Step 3: Commit**

```bash
git -C "C:\Users\hiros\Mirai\matome" init
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: HTML skeleton + CSS completo MATOME"
```

---

## Task 2: JS — utilitários (formatYen, parseYen, calcPMT, estado global)

**Files:**
- Modify: `matome/index.html` — bloco `<script>`

- [ ] **Step 1: Adicionar estado global e funções utilitárias no `<script>`**

Substituir o comentário `// JS será adicionado...` por:

```js
// ── ESTADO GLOBAL ──────────────────────────────────────────
const state = {
  // Tela 1 — cliente
  nome: '', idade: '', data: '',
  // Tela 1 — parcelas mensais
  financiamento: 0, carro: 0, cartao: 0, luz: 0, gas: 0, outros: 0,
  // Tela 1 — saldos devedores
  residuoCasa: 0, residuoCarro: 0, residuoCartao: 0,
  // Tela 2 — orçamentos
  reforma: 0, exterior: 0, solar: 0, outrasObras: 0,
  // Tela 2 — condições
  taxa: 1.5, prazo: 35
};

// ── FORMATAÇÃO ¥ ───────────────────────────────────────────
function parseYen(str) {
  if (!str) return 0;
  return parseInt(String(str).replace(/[¥\s\.]/g, ''), 10) || 0;
}

function formatYen(n) {
  const v = Math.round(n);
  if (!v) return '';
  return '¥ ' + v.toString().replace(/\B(?=(\d{3})+(?!\d))/g, '.');
}

function maskInput(el) {
  const raw = parseYen(el.value);
  el.value = formatYen(raw);
}

function bindYenInputs(container) {
  container.querySelectorAll('input[data-yen]').forEach(el => {
    el.addEventListener('blur', () => maskInput(el));
    el.addEventListener('focus', () => {
      const raw = parseYen(el.value);
      el.value = raw ? raw : '';
    });
    el.addEventListener('input', () => {
      // remove não-numéricos para evitar lixo enquanto digita
      el.value = el.value.replace(/[^\d]/g, '');
    });
  });
}

// ── PMT (Sistema Price) ────────────────────────────────────
function calcPMT(principal, annualRatePct, years) {
  if (!principal || !years) return 0;
  const r = annualRatePct / 12 / 100;
  const n = years * 12;
  if (r === 0) return Math.round(principal / n);
  return Math.round(principal * (r * Math.pow(1 + r, n)) / (Math.pow(1 + r, n) - 1));
}

// ── NAVEGAÇÃO WIZARD ───────────────────────────────────────
function goTo(n) {
  document.querySelectorAll('.tela').forEach(t => t.classList.remove('active'));
  document.getElementById('tela' + n).classList.add('active');
  document.querySelectorAll('.step').forEach((s, i) => {
    s.classList.remove('active', 'done');
    if (i + 1 < n) s.classList.add('done');
    else if (i + 1 === n) s.classList.add('active');
  });
  window.scrollTo({ top: 0, behavior: 'smooth' });
}
```

- [ ] **Step 2: Testar no console do browser**

Abrir DevTools → Console e executar:

```js
// Deve retornar '¥ 15.000.000'
console.assert(formatYen(15000000) === '¥ 15.000.000', 'formatYen falhou');

// Deve retornar 15000000
console.assert(parseYen('¥ 15.000.000') === 15000000, 'parseYen falhou');

// PMT: ¥22.200.000 / 35 anos / 1.5% ≈ ¥68.406
const pmt = calcPMT(22200000, 1.5, 35);
console.assert(pmt > 60000 && pmt < 75000, 'calcPMT fora do esperado: ' + pmt);

console.log('✅ Utilitários OK — PMT calculado:', formatYen(pmt));
```

Resultado esperado no console: `✅ Utilitários OK — PMT calculado: ¥ 68.406` (valor aproximado)

- [ ] **Step 3: Commit**

```bash
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: utilitários JS (formatYen, parseYen, calcPMT, estado, navegação)"
```

---

## Task 3: Tela 1 — campos + total ao vivo

**Files:**
- Modify: `matome/index.html` — `<div class="container tela-1-content">`

- [ ] **Step 1: Preencher o HTML da Tela 1**

Substituir o conteúdo de `<div class="container tela-1-content">` por:

```html
<div class="sec-title">① Dados do cliente · お客様情報</div>
<div class="field-group">
  <div class="field">
    <label>Nome <em>お名前</em></label>
    <input type="text" id="f-nome" placeholder="Yamamoto Hiroshi">
  </div>
  <div class="field">
    <label>Idade <em>年齢</em></label>
    <input type="number" id="f-idade" placeholder="35" min="18" max="99">
  </div>
  <div class="field" style="grid-column:1/-1">
    <label>Data da simulação <em>シミュレーション日</em></label>
    <input type="date" id="f-data">
  </div>
</div>

<div class="sec-title">Parcelas mensais atuais · 現在の月額支出</div>
<div class="field-group">
  <div class="field">
    <label>住宅ローン <em>Financiamento da casa</em></label>
    <input type="text" id="f-financiamento" data-yen placeholder="¥ 90.000">
  </div>
  <div class="field">
    <label>車ローン <em>Carro</em></label>
    <input type="text" id="f-carro" data-yen placeholder="¥ 40.000">
  </div>
  <div class="field">
    <label>クレジット <em>Cartão de crédito</em></label>
    <input type="text" id="f-cartao" data-yen placeholder="¥ 30.000">
  </div>
  <div class="field">
    <label>電気代 <em>Conta de luz</em></label>
    <input type="text" id="f-luz" data-yen placeholder="¥ 20.000">
  </div>
  <div class="field">
    <label>ガス代 <em>Conta de gás</em></label>
    <input type="text" id="f-gas" data-yen placeholder="¥ 15.000">
  </div>
  <div class="field">
    <label>その他 <em>Outros</em></label>
    <input type="text" id="f-outros" data-yen placeholder="¥ 0">
  </div>
</div>

<div class="total-box">
  <span class="lbl">Total mensal atual · 現在の月額合計</span>
  <span class="val" id="total-atual">¥ 0</span>
</div>

<div class="sec-title">Saldo devedor · 残債合計</div>
<div class="field-group">
  <div class="field">
    <label>残債 住宅ローン <em>Saldo devedor casa</em></label>
    <input type="text" id="f-res-casa" data-yen placeholder="¥ 15.000.000">
  </div>
  <div class="field">
    <label>残債 車ローン <em>Saldo devedor carro</em></label>
    <input type="text" id="f-res-carro" data-yen placeholder="¥ 2.000.000">
  </div>
  <div class="field">
    <label>残債 クレジット <em>Saldo cartão</em></label>
    <input type="text" id="f-res-cartao" data-yen placeholder="¥ 500.000">
  </div>
</div>

<button class="btn" onclick="avancarParaTela2()">Próximo →</button>
```

- [ ] **Step 2: Adicionar JS da Tela 1 no `<script>` (após o código da Task 2)**

```js
// ── TELA 1 ────────────────────────────────────────────────
function initTela1() {
  // data de hoje como default
  document.getElementById('f-data').value = new Date().toISOString().split('T')[0];

  // máscara ¥ em todos os inputs data-yen da tela 1
  bindYenInputs(document.getElementById('tela1'));

  // total ao vivo: dispara em qualquer mudança nos 6 campos mensais
  const mensaisIds = ['f-financiamento','f-carro','f-cartao','f-luz','f-gas','f-outros'];
  mensaisIds.forEach(id => {
    document.getElementById(id).addEventListener('input', atualizarTotalAtual);
    document.getElementById(id).addEventListener('blur',  atualizarTotalAtual);
  });
}

function atualizarTotalAtual() {
  const ids = ['f-financiamento','f-carro','f-cartao','f-luz','f-gas','f-outros'];
  const total = ids.reduce((sum, id) => sum + parseYen(document.getElementById(id).value), 0);
  document.getElementById('total-atual').textContent = formatYen(total) || '¥ 0';
}

function lerTela1() {
  state.nome          = document.getElementById('f-nome').value.trim();
  state.idade         = document.getElementById('f-idade').value;
  state.data          = document.getElementById('f-data').value;
  state.financiamento = parseYen(document.getElementById('f-financiamento').value);
  state.carro         = parseYen(document.getElementById('f-carro').value);
  state.cartao        = parseYen(document.getElementById('f-cartao').value);
  state.luz           = parseYen(document.getElementById('f-luz').value);
  state.gas           = parseYen(document.getElementById('f-gas').value);
  state.outros        = parseYen(document.getElementById('f-outros').value);
  state.residuoCasa   = parseYen(document.getElementById('f-res-casa').value);
  state.residuoCarro  = parseYen(document.getElementById('f-res-carro').value);
  state.residuoCartao = parseYen(document.getElementById('f-res-cartao').value);
}

function avancarParaTela2() {
  lerTela1();
  goTo(2);
  atualizarCalcBox();
}

// inicializar ao carregar
document.addEventListener('DOMContentLoaded', initTela1);
```

- [ ] **Step 3: Verificar no browser**

1. Abrir `index.html`
2. Digitar `90000` no campo 住宅ローン → clicar fora → deve mostrar `¥ 90.000`
3. Digitar nos 6 campos de parcelas mensais → "Total mensal atual" deve somar em tempo real
4. Clicar "Próximo →" → deve ir para a Tela 2 (em branco por enquanto) e steps deve mostrar ① como done, ② como active

- [ ] **Step 4: Commit**

```bash
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: tela 1 campos + máscara ¥ + total ao vivo"
```

---

## Task 4: Tela 2 — orçamentos + PMT ao vivo

**Files:**
- Modify: `matome/index.html` — `<div class="container tela-2-content">`

- [ ] **Step 1: Preencher HTML da Tela 2**

Substituir o conteúdo de `<div class="container tela-2-content">` por:

```html
<div class="sec-title">② Orçamentos adicionais · 追加工事費用</div>
<div class="field-group">
  <div class="field">
    <label>リフォーム <em>Reforma</em></label>
    <input type="text" id="f-reforma" data-yen placeholder="¥ 2.000.000">
  </div>
  <div class="field">
    <label>外構工事 <em>Área externa</em></label>
    <input type="text" id="f-exterior" data-yen placeholder="¥ 1.500.000">
  </div>
  <div class="field">
    <label>太陽光発電 <em>Painel solar</em></label>
    <input type="text" id="f-solar" data-yen placeholder="¥ 1.200.000">
  </div>
  <div class="field">
    <label>その他工事 <em>Outras obras</em></label>
    <input type="text" id="f-outras-obras" data-yen placeholder="¥ 0">
  </div>
</div>

<div class="sec-title">Condições do novo financiamento · 新ローン条件</div>
<div class="field-group">
  <div class="field">
    <label>金利 <em>Taxa de juros ao ano (%)</em></label>
    <input type="number" id="f-taxa" value="1.5" min="0.1" max="20" step="0.1">
  </div>
  <div class="field">
    <label>返済期間 <em>Prazo do financiamento</em></label>
    <select id="f-prazo">
      <option value="35">35 anos</option>
      <option value="30">30 anos</option>
      <option value="25">25 anos</option>
      <option value="20">20 anos</option>
    </select>
  </div>
</div>

<div class="calc-box">
  <div class="calc-title">Total a financiar · 融資総額（自動計算）</div>
  <div class="calc-line"><span class="ck">残債 合計 <em style="color:#555;font-size:11px">(dívidas consolidadas)</em></span><span class="cv" id="calc-residuo">¥ 0</span></div>
  <div class="calc-line"><span class="ck"><span class="plus">+</span>リフォーム</span><span class="cv" id="calc-reforma">¥ 0</span></div>
  <div class="calc-line"><span class="ck"><span class="plus">+</span>外構工事</span><span class="cv" id="calc-exterior">¥ 0</span></div>
  <div class="calc-line"><span class="ck"><span class="plus">+</span>太陽光発電</span><span class="cv" id="calc-solar">¥ 0</span></div>
  <div class="calc-line"><span class="ck"><span class="plus">+</span>その他工事</span><span class="cv" id="calc-outras-obras">¥ 0</span></div>
  <div class="calc-line sum">
    <span class="ck">TOTAL A FINANCIAR</span>
    <span class="cv" id="calc-total">¥ 0</span>
  </div>
  <div class="calc-line pmt">
    <span class="ck" id="calc-pmt-label">Nova parcela mensal · 35 anos · 1,5%</span>
    <span class="cv" id="calc-pmt">¥ 0</span>
  </div>
</div>

<button class="btn secondary" onclick="goTo(1)">← Voltar</button>
<button class="btn" onclick="avancarParaTela3()">Ver resultado →</button>
```

- [ ] **Step 2: Adicionar JS da Tela 2 no `<script>`**

```js
// ── TELA 2 ────────────────────────────────────────────────
function initTela2() {
  bindYenInputs(document.getElementById('tela2'));

  const orcIds = ['f-reforma','f-exterior','f-solar','f-outras-obras'];
  orcIds.forEach(id => {
    document.getElementById(id).addEventListener('input', atualizarCalcBox);
    document.getElementById(id).addEventListener('blur',  atualizarCalcBox);
  });
  document.getElementById('f-taxa').addEventListener('input',  atualizarCalcBox);
  document.getElementById('f-prazo').addEventListener('change', atualizarCalcBox);
}

function atualizarCalcBox() {
  // Ler orçamentos
  state.reforma      = parseYen(document.getElementById('f-reforma').value);
  state.exterior     = parseYen(document.getElementById('f-exterior').value);
  state.solar        = parseYen(document.getElementById('f-solar').value);
  state.outrasObras  = parseYen(document.getElementById('f-outras-obras').value);
  state.taxa         = parseFloat(document.getElementById('f-taxa').value) || 1.5;
  state.prazo        = parseInt(document.getElementById('f-prazo').value) || 35;

  const residuo = state.residuoCasa + state.residuoCarro + state.residuoCartao;
  const total   = residuo + state.reforma + state.exterior + state.solar + state.outrasObras;
  const pmt     = calcPMT(total, state.taxa, state.prazo);

  document.getElementById('calc-residuo').textContent     = formatYen(residuo) || '¥ 0';
  document.getElementById('calc-reforma').textContent     = formatYen(state.reforma) || '¥ 0';
  document.getElementById('calc-exterior').textContent    = formatYen(state.exterior) || '¥ 0';
  document.getElementById('calc-solar').textContent       = formatYen(state.solar) || '¥ 0';
  document.getElementById('calc-outras-obras').textContent= formatYen(state.outrasObras) || '¥ 0';
  document.getElementById('calc-total').textContent       = formatYen(total) || '¥ 0';
  document.getElementById('calc-pmt').textContent         = formatYen(pmt) || '¥ 0';
  document.getElementById('calc-pmt-label').textContent   =
    `Nova parcela mensal · ${state.prazo} anos · ${state.taxa.toFixed(1).replace('.',',')}%`;
}

function lerTela2() {
  state.reforma     = parseYen(document.getElementById('f-reforma').value);
  state.exterior    = parseYen(document.getElementById('f-exterior').value);
  state.solar       = parseYen(document.getElementById('f-solar').value);
  state.outrasObras = parseYen(document.getElementById('f-outras-obras').value);
  state.taxa        = parseFloat(document.getElementById('f-taxa').value) || 1.5;
  state.prazo       = parseInt(document.getElementById('f-prazo').value) || 35;
}

function avancarParaTela3() {
  lerTela2();
  renderTela3();
  goTo(3);
}

document.addEventListener('DOMContentLoaded', initTela2);
```

- [ ] **Step 3: Verificar no browser**

1. Preencher Tela 1 → clicar Próximo
2. Na Tela 2: digitar valores em reforma, exterior, solar
3. A caixa escura deve atualizar em tempo real: residuo + orçamentos = total → nova parcela
4. Mudar o prazo para 20 anos → parcela deve aumentar
5. Mudar taxa para 2% → parcela deve aumentar
6. Label da parcela deve atualizar: "Nova parcela mensal · 20 anos · 2,0%"

- [ ] **Step 4: Commit**

```bash
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: tela 2 orçamentos + cálculo PMT ao vivo"
```

---

## Task 5: Tela 3 — resultado + economia

**Files:**
- Modify: `matome/index.html` — `<div class="container">` da Tela 3

- [ ] **Step 1: Preencher HTML da Tela 3 (esqueleto com IDs)**

Substituir o `<div class="container">` vazio da Tela 3 por:

```html
<div class="container">
  <div class="sec-title" id="result-title">③ Resultado</div>

  <div class="result-grid">
    <div class="result-col before">
      <div class="col-title">❌ Situação Atual · 現状</div>
      <div class="result-row"><span class="ri">住宅ローン</span><span class="ra" id="r-financiamento">—</span></div>
      <div class="result-row"><span class="ri">車ローン</span><span class="ra" id="r-carro">—</span></div>
      <div class="result-row"><span class="ri">クレジット</span><span class="ra" id="r-cartao">—</span></div>
      <div class="result-row"><span class="ri">電気代</span><span class="ra" id="r-luz">—</span></div>
      <div class="result-row"><span class="ri">ガス代</span><span class="ra" id="r-gas">—</span></div>
      <div class="result-row" id="r-outros-row"><span class="ri">その他</span><span class="ra" id="r-outros">—</span></div>
      <div class="result-row tr"><span class="ri">TOTAL</span><span class="ra" id="r-total-antes" style="color:var(--before-color);font-size:15px">—</span></div>
    </div>
    <div class="result-col after">
      <div class="col-title">✅ Com MATOME · まとめ後</div>
      <div class="result-row"><span class="ri">新ローン <em id="r-prazo-label" style="font-size:10px;color:#888"></em></span><span class="ra" id="r-nova-parcela">—</span></div>
      <div class="result-row zero"><span class="ri">電気代 <em id="r-solar-label" style="font-size:10px;color:#888"></em></span><span class="ra" id="r-luz-depois">—</span></div>
      <div class="result-row zero"><span class="ri">ガス代</span><span class="ra" id="r-gas-depois" style="color:var(--after-color)">¥ 0</span></div>
      <div class="result-row note"><span>車・クレジット: roukin に統合済</span></div>
      <div class="result-row tr"><span class="ri">TOTAL</span><span class="ra" id="r-total-depois" style="color:var(--after-color);font-size:15px">—</span></div>
    </div>
  </div>

  <div class="eco-box">
    <div class="eco-lbl">Economia mensal · 月の節約額</div>
    <div class="eco-big" id="eco-mensal">—</div>
    <div class="eco-sub" id="eco-sub">—</div>
  </div>

  <div id="proposta-resumo" style="margin-bottom:20px;font-size:12px;color:#888;line-height:1.8;border:1px solid var(--divider);border-radius:4px;padding:12px 14px;">
    <!-- resumo da proposta preenchido por JS -->
  </div>

  <button class="btn secondary" onclick="goTo(2)">← Voltar</button>
  <button class="btn" onclick="gerarPDF()">📄 Gerar PDF personalizado</button>
</div>
```

- [ ] **Step 2: Adicionar `renderTela3()` e `gerarPDF()` no `<script>`**

```js
// ── TELA 3 ────────────────────────────────────────────────
function renderTela3() {
  const totalAntes  = state.financiamento + state.carro + state.cartao +
                      state.luz + state.gas + state.outros;
  const residuo     = state.residuoCasa + state.residuoCarro + state.residuoCartao;
  const totalFinanc = residuo + state.reforma + state.exterior + state.solar + state.outrasObras;
  const novaParcela = calcPMT(totalFinanc, state.taxa, state.prazo);
  const luzDepois   = state.solar > 0 ? 0 : state.luz;
  const totalDepois = novaParcela + luzDepois; // gás = 0 (all-electric assumido)
  const econMensal  = totalAntes - totalDepois;
  const econAnual   = econMensal * 12;
  const econ10      = econMensal * 120;

  // título com nome do cliente
  const nomeLabel = state.nome ? ` · ${state.nome}` : '';
  const idadeLabel = state.idade ? `, ${state.idade} anos` : '';
  document.getElementById('result-title').textContent = `③ Resultado${nomeLabel}${idadeLabel}`;

  // coluna ANTES
  document.getElementById('r-financiamento').textContent = formatYen(state.financiamento) || '¥ 0';
  document.getElementById('r-carro').textContent         = formatYen(state.carro)         || '¥ 0';
  document.getElementById('r-cartao').textContent        = formatYen(state.cartao)        || '¥ 0';
  document.getElementById('r-luz').textContent           = formatYen(state.luz)           || '¥ 0';
  document.getElementById('r-gas').textContent           = formatYen(state.gas)           || '¥ 0';

  const outrosRow = document.getElementById('r-outros-row');
  if (state.outros > 0) {
    document.getElementById('r-outros').textContent = formatYen(state.outros);
    outrosRow.style.display = '';
  } else {
    outrosRow.style.display = 'none';
  }
  document.getElementById('r-total-antes').textContent = formatYen(totalAntes);

  // coluna DEPOIS
  document.getElementById('r-prazo-label').textContent =
    `(${state.prazo} anos · ${state.taxa.toFixed(1).replace('.',',')}%)`;
  document.getElementById('r-nova-parcela').textContent = formatYen(novaParcela);
  document.getElementById('r-solar-label').textContent  = state.solar > 0 ? '(painel solar)' : '';
  document.getElementById('r-luz-depois').textContent   = formatYen(luzDepois) || '¥ 0';
  document.getElementById('r-gas-depois').textContent   = '¥ 0';
  document.getElementById('r-total-depois').textContent = formatYen(totalDepois);

  // economia
  document.getElementById('eco-mensal').textContent = formatYen(econMensal) + ' / mês';
  document.getElementById('eco-sub').innerHTML =
    formatYen(econAnual) + ' por ano<br>' + formatYen(econ10) + ' em 10 anos';

  // resumo da proposta
  const dataFmt = state.data ? new Date(state.data + 'T12:00').toLocaleDateString('pt-BR') : '—';
  document.getElementById('proposta-resumo').innerHTML =
    `<strong>Proposta MATOME</strong> · ${dataFmt}<br>` +
    `Total financiado: ${formatYen(totalFinanc)} &nbsp;|&nbsp; Prazo: ${state.prazo} anos &nbsp;|&nbsp; Taxa: ${state.taxa.toFixed(1).replace('.',',')}% a.a.<br>` +
    (state.reforma   > 0 ? `Reforma: ${formatYen(state.reforma)} &nbsp;` : '') +
    (state.exterior  > 0 ? `Área externa: ${formatYen(state.exterior)} &nbsp;` : '') +
    (state.solar     > 0 ? `Painel solar: ${formatYen(state.solar)}` : '');

  // PDF header
  document.getElementById('pdf-client-info').textContent =
    `${state.nome}${state.idade ? ', ' + state.idade + ' anos' : ''} · Simulação: ${dataFmt}`;
}

function gerarPDF() {
  window.print();
}
```

- [ ] **Step 3: Verificar no browser**

1. Preencher Tela 1 completamente
2. Preencher Tela 2 com valores e clicar "Ver resultado"
3. Tela 3 deve mostrar:
   - Nome e idade no título
   - Coluna ANTES com todas as parcelas
   - Coluna DEPOIS com nova parcela + luz ¥0 se solar > 0
   - Caixa de economia com valores calculados
   - Resumo da proposta com data formatada

- [ ] **Step 4: Commit**

```bash
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: tela 3 resultado + cálculo de economia"
```

---

## Task 6: PDF via Print CSS

**Files:**
- Modify: `matome/index.html` — CSS `@media print` (já presente no skeleton) + função `gerarPDF()`

- [ ] **Step 1: Ajustar o CSS `@media print` para layout de relatório**

No bloco `@media print` já existente, confirmar/ajustar para:

```css
@media print {
  @page { margin: 15mm 20mm; size: A4 portrait; }
  body { background: #fff; font-size: 12px; }

  /* ocultar elementos de navegação */
  .steps, .btn, .header, .tela-1-content, .tela-2-content, .btn.secondary { display: none !important; }

  /* mostrar todas as telas no print */
  .tela { display: block !important; }

  /* PDF header */
  .pdf-header { display: block !important; page-break-after: avoid; }
  .pdf-logo { font-size: 24px; font-weight: 300; letter-spacing: 5px; text-transform: uppercase; color: #2d2d2d; }
  .pdf-logo strong { font-weight: 900; color: #c9a84c; }
  .pdf-tagline { font-size: 9px; color: #888; letter-spacing: 2px; margin-top: 3px; }
  .pdf-client { font-size: 12px; color: #555; margin-top: 8px; }

  /* resultado em 2 colunas mesmo no print */
  .result-grid { grid-template-columns: 1fr 1fr !important; gap: 12px; }

  /* garantir cores no print */
  .calc-box  { -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #2d2d2d !important; }
  .eco-box   { -webkit-print-color-adjust: exact; print-color-adjust: exact; background: #2d2d2d !important; }
  .result-col.before { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
  .result-col.after  { -webkit-print-color-adjust: exact; print-color-adjust: exact; }

  /* footer */
  .pdf-footer { display: block !important; margin-top: 20px; font-size: 9px; color: #bbb; text-align: center; border-top: 1px solid #eee; padding-top: 10px; }
}
```

- [ ] **Step 2: Testar geração de PDF**

1. Preencher simulação completa e chegar na Tela 3
2. Clicar "Gerar PDF personalizado"
3. Na janela de impressão do browser:
   - Selecionar "Salvar como PDF"
   - Ativar "Gráficos de fundo" / "Background graphics" nas opções
4. Verificar que o PDF contém:
   - Header MATOME com borda dourada
   - Nome e data do cliente
   - Comparativo antes/depois
   - Caixa de economia escura com texto dourado
   - Rodapé discreto
   - Steps e botões NÃO aparecem

- [ ] **Step 3: Commit**

```bash
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: geração de PDF via print CSS"
```

---

## Task 7: Polimento final + testes mobile

**Files:**
- Modify: `matome/index.html`

- [ ] **Step 1: Verificar responsividade mobile**

No browser, abrir DevTools → Toggle device toolbar → iPhone SE (375×667):

Checklist:
- [ ] Tela 1: campos em coluna única, sem overflow horizontal
- [ ] Total box: valor não quebra para segunda linha
- [ ] Tela 2: calc box legível, valores não cortados
- [ ] Tela 3: colunas ANTES/DEPOIS empilhadas verticalmente
- [ ] Botões com área de toque adequada (≥44px de altura)

- [ ] **Step 2: Adicionar `inputmode="numeric"` nos inputs ¥ para teclado numérico no mobile**

Em todos os `<input type="text" data-yen>`, adicionar o atributo `inputmode="numeric"`:

```html
<input type="text" id="f-financiamento" data-yen inputmode="numeric" placeholder="¥ 90.000">
```

Repetir para todos os 12 inputs `data-yen`.

- [ ] **Step 3: Verificar fluxo completo**

Preencher uma simulação exemplo completa e validar:

| Campo | Valor de teste |
|-------|---------------|
| Nome | Tanaka Silva |
| Idade | 42 |
| 住宅ローン | 85.000 |
| 車ローン | 35.000 |
| クレジット | 25.000 |
| 電気代 | 18.000 |
| ガス代 | 12.000 |
| 残債 casa | 12.000.000 |
| 残債 carro | 1.800.000 |
| 残債 cartão | 400.000 |
| リフォーム | 1.500.000 |
| 外構工事 | 800.000 |
| 太陽光発電 | 1.000.000 |
| Taxa | 1.5% |
| Prazo | 35 anos |

Resultado esperado:
- Total atual: ¥ 175.000
- Total financiar: ¥ 17.500.000
- Nova parcela: ~¥ 53.900 (PMT de ¥17.500.000 / 1.5% / 35 anos)
- Luz depois: ¥ 0 (solar > 0)
- Total depois: ~¥ 53.900
- Economia: ~¥ 121.100/mês

- [ ] **Step 4: Commit final**

```bash
git -C "C:\Users\hiros\Mirai\matome" add index.html
git -C "C:\Users\hiros\Mirai\matome" commit -m "feat: polimento mobile + inputmode numérico + validação fluxo completo"
```

---

## Revisão do Spec

| Requisito | Task |
|-----------|------|
| Wizard 3 telas | Task 1 (skeleton), Tasks 3–5 |
| 18 campos editáveis (nome, idade, data + 15 ¥) | Tasks 3–4 |
| Máscara ¥ com pontos | Task 2 |
| Total mensal ao vivo | Task 3 |
| Cálculo PMT automático | Tasks 2 + 4 |
| Caixa de cálculo ao vivo (Tela 2) | Task 4 |
| Resultado antes/depois | Task 5 |
| Economia mensal/anual/10 anos | Task 5 |
| Luz ¥0 quando solar > 0 | Task 5 |
| PDF branded via Print CSS | Task 6 |
| Mobile-first responsive | Tasks 1 + 7 |
| `inputmode="numeric"` mobile | Task 7 |
