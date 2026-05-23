# Simulador MATOME — Design Spec
**Data:** 2026-05-22  
**Projeto:** `Mirai/matome/`  
**Entregável:** Arquivo `index.html` único, hospedável online, mobile-first

---

## 1. Visão Geral

Simulador de consolidação de dívidas (まとめ) para brasileiros no Japão com casa própria financiada. O usuário informa suas despesas mensais e saldos devedores; o corretor informa orçamentos de obras e condições do novo roukin; o sistema calcula a nova parcela mensal e exibe o comparativo antes/depois. Ao final, gera um PDF personalizado com branding MATOME.

**Público:** corretores com clientes (desktop) e clientes sozinhos (mobile).  
**Distribuição:** hospedado online (URL fixa). Arquivo HTML + CSS + JS sem dependências externas — exceto biblioteca de PDF.  
**Idioma:** Português brasileiro. Termos em kanji com tradução em parênteses. Valores em ¥ sem decimais, com ponto a cada 3 casas (ex: ¥ 15.000.000).

---

## 2. Estilo Visual

**Tema:** Elegante / Japonês  
- Fundo: `#f5f3ef` (off-white quente)  
- Header: `#2d2d2d` (preto) com borda inferior `#c9a84c` (dourado)  
- Acento primário: `#c9a84c` (dourado)  
- Texto: `#2d2d2d`  
- Labels: `#888`  
- Inputs: borda inferior apenas, sem box  
- Botão: fundo `#2d2d2d`, texto `#c9a84c`, uppercase, letter-spacing  

---

## 3. Fluxo — Wizard 3 Telas

### Tela 1 — Situação Atual

**Seção: Dados do cliente (お客様情報)**
| Campo | Tipo | Default |
|-------|------|---------|
| Nome (お名前) | text | — |
| Idade (年齢) | number | — |
| Data da simulação (シミュレーション日) | date | hoje (auto) |

**Seção: Parcelas mensais atuais (現在の月額支出)**
| Campo | Tipo |
|-------|------|
| 住宅ローン — Financiamento da casa | ¥ number |
| 車ローン — Carro | ¥ number |
| クレジット — Cartão de crédito | ¥ number |
| 電気代 — Conta de luz | ¥ number |
| ガス代 — Conta de gás | ¥ number |
| その他 — Outros | ¥ number |

→ **Total mensal atual** calculado em tempo real (soma dos 6 campos).

**Seção: Saldo devedor (残債合計)**
| Campo | Tipo |
|-------|------|
| 残債 住宅ローン — Saldo devedor casa | ¥ number |
| 残債 車ローン — Saldo devedor carro | ¥ number |
| 残債 クレジット — Saldo cartão | ¥ number |

---

### Tela 2 — Proposta MATOME (まとめプラン)

**Seção: Orçamentos adicionais (追加工事費用)**
| Campo | Tipo |
|-------|------|
| リフォーム — Reforma | ¥ number |
| 外構工事 — Área externa | ¥ number |
| 太陽光発電 — Painel solar | ¥ number |
| その他工事 — Outras obras | ¥ number |

**Seção: Condições do novo financiamento (新ローン条件)**
| Campo | Tipo | Opções |
|-------|------|--------|
| 金利 — Taxa de juros ao ano | % number | default 1.5 |
| 返済期間 — Prazo | select | 20, 25, 30, 35 anos |

**Caixa de cálculo automático (escura):**
- Residual total = Σ(saldos devedores T1)
- Total a financiar = residual + reforma + exterior + solar + outras obras
- Nova parcela = PMT(taxa_mensal, meses, total) usando fórmula de amortização Price
- Mostrado em tempo real conforme campos são preenchidos

---

### Tela 3 — Resultado

**Comparativo lado a lado:**
- Coluna ANTES (vermelho): lista as 6 parcelas mensais atuais + total
- Coluna DEPOIS (verde): nova parcela roukin + luz ¥0 (solar) + gás ¥0 (elétrico) + nota "carro e cartão consolidados" + total

**Caixa de economia (fundo escuro, dourado):**
- Economia mensal = Total atual − Nova parcela
- Economia anual = × 12
- Economia em 10 anos = × 120

**Botão:** Gerar PDF personalizado

---

## 4. Geração de PDF

**Método:** Print CSS (`@media print`) + `window.print()`  
- Zero dependências externas  
- PDF fiel ao estilo visual (preto/dourado)  
- Ao clicar "Gerar PDF", oculta header de navegação e steps, exibe cabeçalho MATOME com nome do cliente e data, imprime resultado completo  

**Conteúdo do PDF:**
1. Cabeçalho: logo MATOME + slogan + nome do cliente + data da simulação
2. Resumo do cliente: nome, idade, data
3. Tabela situação atual (despesas mensais)
4. Tabela proposta MATOME (orçamentos + condições)
5. Comparativo antes/depois
6. Destaque da economia (mensal / anual / 10 anos)
7. Rodapé discreto

---

## 5. Formatação de Valores

- Máscara de entrada: ao digitar, formatar automaticamente com ponto a cada 3 dígitos (ex: `15000000` → `¥ 15.000.000`)
- Sem casas decimais
- Cálculo interno usa parseInt removendo formatação
- Fórmula PMT: `P × [r(1+r)^n] / [(1+r)^n − 1]`  
  onde `r = taxa_anual / 12 / 100`, `n = prazo_anos × 12`

---

## 6. Responsividade

| Breakpoint | Layout |
|------------|--------|
| ≤480px (mobile) | campos em 1 coluna, resultado empilhado |
| 481–768px (tablet) | campos em 2 colunas, resultado empilhado |
| ≥769px (desktop) | campos em 2 colunas, resultado lado a lado |

---

## 7. Estrutura de Arquivos

```
matome/
├── index.html        # tudo em um único arquivo (HTML + CSS + JS inline)
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-05-22-simulador-matome-design.md
```

---

## 8. Fora do Escopo

- Backend / banco de dados
- Autenticação
- Flat / マンション (apenas casa própria 一戸建て)
- Versão em japonês
- Cálculo de score de crédito
