# Simulador ao Vivo do Autônomo — Protótipo HTML

**Data:** 2026-08-09
**Status:** Aprovado para implementação
**Substitui:** `2026-08-09-cassino-leao-japones-design.md` (conceito de cassino
abandonado — ver nota de status naquele arquivo)

## Contexto

Abertura interativa para uma palestra sobre iDeCo voltada a autônomos
brasileiros no Japão (Categoria 1 / jiei-gyō). Antes de apresentar o
simulador real de iDeCo (`casapropriajp.com/ideco-2026`), a ideia é abrir com
uma mini-simulação financeira interativa que faz a plateia sentir o imposto
saindo do lucro e depois sentir o efeito do abatimento fiscal — sem usar
estética de jogo de azar (cassino, roleta, cartas, fichas), que soa deslocada
num contexto de planejamento financeiro sério.

Este documento cobre apenas o **protótipo**: uma página HTML autocontida que
simula a experiência de UMA pessoa participando pelo celular, para o
palestrante testar o fluxo e o timing sozinho antes de decidir construir a
versão multiplayer real.

## Por que não parecer com o simulador real

O simulador real (`casapropriajp.com/ideco-2026`) já tem identidade visual
forte e deliberadamente "séria": fundo escuro quase preto, texto bege claro,
fonte Archivo, nomenclatura de seções estilo terminal (`entrada.exe`,
`resultado.exe`, `comparacao.exe`). Este protótipo deve ser visualmente **o
oposto** — claro, arredondado, acolhedor — para que a transição do jogo para
o simulador real (claro → escuro, lúdico → denso) reforce na prática a fala
"agora vamos sair do fictício e ver seu valor REAL". O protótipo não deve
usar fundo escuro, fonte Archivo, nem nomenclatura ".exe"/terminal.

## Objetivo

Dar ao palestrante algo clicável, envolvente e pessoal — não um formulário
genérico — que reproduza a sequência emocional do jogo (imposto tira →
escolha → recuperação → comparação → transição para o simulador real),
usando técnicas de engajamento de produto financeiro (personalização,
animação de contagem, número de impacto) em vez de mecânica de jogo de azar.

## Fora de escopo

- Multiplayer real / sincronização entre celulares
- QR code funcional (será só um placeholder visual)
- Integração com Kahoot, Mentimeter ou qualquer ferramenta terceira
- Persistência de dados entre sessões ou entre jogadores reais
- Prova social ao vivo (contador incremental de "pessoas participando agora")
  — descartada explicitamente pelo usuário
- Cálculo real de faixas de imposto japonesas — os números são ilustrativos,
  gerados por uma fórmula simplificada fixa, não uma calculadora fiscal real
- Pacing controlado pelo host (ver "Notas para versão futura" abaixo)

## Personalização por faixa de renda

Em vez de um exemplo fixo igual para todo mundo, a tela de entrada oferece um
seletor rápido (toque, sem digitar) de lucro mensal ilustrativo:

- ¥200.000/mês
- ¥300.000/mês (padrão pré-selecionado)
- ¥500.000/mês
- ¥800.000/mês

**Os números não são mais uma fórmula percentual inventada** (a primeira
versão usava -25%/+25% fixos, que gerava valores irrealistas — ex.:
¥1,2 milhão/ano de diferença, quase 10x o valor real). Em vez disso, cada
faixa usa uma tabela de valores calibrados consultando o próprio simulador
real (`casapropriajp.com/ideco-2026`), Categoria 1, aporte máximo de
¥68.000/mês, idade 42, retorno 3% a.a. — os mesmos parâmetros padrão da
ferramenta oficial:

| Lucro mensal | Imposto obrigatório/mês (sem iDeCo) | % efetiva real | Economia com iDeCo máximo/mês |
|---|---|---|---|
| ¥200.000 | ¥16.000 | 8,0% | ¥10.000 |
| ¥300.000 | ¥31.000 | 10,3% | ¥11.000 |
| ¥500.000 | ¥88.000 | 17,6% | ¥21.000 |
| ¥800.000 | ¥184.000 | 23,0% | ¥23.000 |

```js
const DADOS_POR_FAIXA = {
  200000: { impostoObrigatorio: 16000, economiaIdeco: 10000 },
  300000: { impostoObrigatorio: 31000, economiaIdeco: 11000 },
  500000: { impostoObrigatorio: 88000, economiaIdeco: 21000 },
  800000: { impostoObrigatorio: 184000, economiaIdeco: 23000 },
};

function simular(lucro) {
  const dados = DADOS_POR_FAIXA[lucro];
  const saldoAposImposto = lucro - dados.impostoObrigatorio;
  const cenarioA = saldoAposImposto; // sem planejamento: nada muda, o imposto continua
  const cenarioB = saldoAposImposto + dados.economiaIdeco; // com iDeCo: recupera a economia
  const diferencaMensal = dados.economiaIdeco;
  const diferencaAnual = diferencaMensal * 12;
  return { lucro, impostoObrigatorio: dados.impostoObrigatorio, saldoAposImposto, cenarioA, cenarioB, diferencaMensal, diferencaAnual };
}
```

Note que `cenarioA` (sem planejamento) é numericamente igual a
`saldoAposImposto` — não há uma "segunda perda" inventada. A mensagem desse
cenário é "nada muda, você continua pagando esse imposto todo mês", não uma
perda adicional fictícia.

Exemplo com o valor padrão (¥300.000): imposto obrigatório ¥31.000 → saldo
¥269.000 → cenário sem planejamento ¥269.000 (inalterado) vs. cenário com
iDeCo ¥280.000 → diferença de ¥11.000/mês (≈ **¥132.000/ano**), consistente
com a economia anual real de ¥128.872 mostrada pelo simulador oficial para
esse mesmo perfil.

## Fluxo de telas

1. **Entrada** — QR code (placeholder) + seletor de faixa de renda (4
   opções, toque único) + campo de nome + botão "Simular meu lucro".
2. **Desconto obrigatório** — botão "Calcular meu desconto obrigatório"; uma
   barra de progresso anima de 100% para 75% enquanto o valor do lucro **conta
   visivelmente** (efeito hodômetro/taxímetro, não troca instantânea) de
   `lucro` até `saldoAposImposto`, com o texto explicando Shotoku-zei/Jumin-zei.
   Som e vibração de "queda" acompanham a contagem.
3. **Comparação de cenários** — dois cards lado a lado, estilo comparação de
   planos (não cartas de baralho): "Sem planejamento tributário" vs. "Com
   iDeCo ativado". Ao tocar em um, o valor conta (hodômetro) de
   `saldoAposImposto` até o resultado daquele cenário (`cenarioA` ou
   `cenarioB`), com som/vibração de perda ou ganho conforme o caso.
4. **Resultado comparativo** — mostra lado a lado os dois cenários
   (`cenarioA` e `cenarioB`, mesmo que só um tenha sido "escolhido"), com a
   diferença mensal em destaque e, maior ainda, a **diferença anualizada**
   (`diferencaAnual`) — esse é o número de impacto que deve ficar na cabeça
   de quem está assistindo.
5. **Como você se compara** — tabela simples (sem troféu/flourish de
   "ranking de jogo") com o jogador ao lado de 3 participantes fictícios
   fixos, todos calculados a partir do mesmo `saldoAposImposto` do jogador
   para ficar comparável em qualquer faixa de renda escolhida:
   - Tanaka_Kojin — ativou iDeCo com aporte máximo (`sim.cenarioB`)
   - Silva_Autonomo — ativou iDeCo com aporte menor (`sim.saldoAposImposto + 60%` da economia)
   - Kenji_Design — ainda não decidiu (`sim.cenarioA`, igual ao saldo sem planejamento)
   Ordenado do maior para o menor saldo.
6. **Transição/CTA** — fala do palestrante adaptada para citar o valor anual
   real calculado (`diferencaAnual`) em vez de fichas fictícias, com botão
   real "Ver meu valor real →" linkando para
   `https://casapropriajp.com/ideco-2026`. Botão "Simular de novo" reinicia o
   fluxo.

## Feedback sensorial

- Efeitos sonoros curtos sintetizados via Web Audio API (sem arquivos
  externos): um tom neutro de queda (desconto obrigatório / cenário sem
  planejamento) e um tom neutro de ganho (cenário com iDeCo) — nada de som de
  caça-níquel ou "cha-ching" de cassino.
- `navigator.vibrate()` nos mesmos momentos, em dispositivos móveis (no-op
  silencioso em desktop).
- Botão de mudo no canto da tela.
- Animação de contagem numérica (hodômetro) descrita acima, sincronizada com
  o som/vibração.

## Estilo visual

Paleta sóbria e clara: branco/creme como fundo, azul-marinho para texto e
elementos estruturais, dourado usado só como destaque discreto em números de
impacto — nunca neon, nunca fundo escuro. Cantos arredondados, sombras
suaves. Sem mascote de leão-cassino. Pode manter uma referência bem discreta
e opcional ao "Leão" (gíria brasileira pro Fisco) como um ícone pequeno e
simples na tela de desconto obrigatório — não é essencial; se ficar
deslocado na implementação, pode ser removido sem impacto no resto do design.
Tipografia diferente da Archivo usada pelo simulador real (usar uma fonte de
sistema padrão, ex. `system-ui`/`Hiragino Sans`/`Yu Gothic`).

## Toggle Celular / Telão

Um botão discreto no canto da tela alterna entre duas apresentações visuais
do mesmo estado: **Visão Celular** (padrão, layout vertical compacto) e
**Visão Telão** (números grandes, resultado comparativo em destaque) — para
o palestrante ensaiar como ficaria projetado. Puramente uma troca de
layout/CSS sobre o mesmo estado, sem duplicar lógica.

## Arquitetura técnica

- Um único arquivo HTML autocontido (`simulador-ao-vivo-autonomo.html`), CSS
  e JS inline, sem dependências externas, sem build step.
- `simular(lucro)` e as funções de montagem da tabela de comparação são
  puras (sem DOM), testáveis via Node.
- Máquina de estados simples em JS puro controlando a tela atual e os
  valores calculados.
- Animação de contagem numérica via `requestAnimationFrame` ou
  `setInterval`, sem bibliotecas externas.
- Nenhuma chamada de rede, nenhum armazenamento persistente.

## Notas para versão futura (fora de escopo deste protótipo)

Quando for construir a versão multiplayer real para a plateia inteira, o
pacing de cada rodada deve ser controlado pelo apresentador (host avança a
rodada para todos), não por cada participante individualmente. Nesse
contexto, a prova social ao vivo (item descartado aqui por ser simulada num
protótipo solo) pode fazer sentido de novo, já que os números seriam reais
(quantidade real de pessoas na sala que já escolheram o cenário com iDeCo).
Isso não afeta o protótipo atual.
