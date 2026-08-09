# Cassino do Leão Japonês — Protótipo HTML

**Data:** 2026-08-09
**Status:** SUBSTITUÍDO — o usuário decidiu abandonar a estética de cassino/aposta
por algo mais sóbrio e realista. Ver
`2026-08-09-simulador-ao-vivo-autonomo-design.md` para o design atual.

## Contexto

Abertura lúdica para uma palestra sobre iDeCo voltada a autônomos brasileiros no
Japão (Categoria 1 / jiei-gyō). Antes de apresentar o simulador real de iDeCo
(`casapropriajp.com/ideco-2026`), a ideia é abrir com um mini-jogo estilo cassino
que faz a plateia "sentir" o imposto sumindo e depois sentir o efeito do
abatimento fiscal, tudo com fichas fictícias.

Este documento cobre apenas o **protótipo**: uma página HTML autocontida que
simula a experiência de UM celular de participante, para o palestrante testar
o fluxo e o timing sozinho antes de decidir construir a versão multiplayer real
(Kahoot/Mentimeter/ferramenta própria).

## Objetivo

Dar ao palestrante algo clicável que reproduza fielmente a sequência emocional
do jogo (perder fichas → escolher → recuperar fichas → ver ranking → transição
para o simulador real), servindo de base de validação antes do investimento
numa versão multiplayer.

## Fora de escopo

- Multiplayer real / sincronização entre celulares
- QR code funcional (será só um placeholder visual)
- Integração com Kahoot, Mentimeter ou qualquer ferramenta terceira
- Persistência de dados entre sessões ou entre jogadores reais
- Pacing controlado pelo host (ver "Notas para versão futura" abaixo)

## Fluxo de telas

1. **Entrada** — QR code (placeholder) + campo de nome + botão "Receber 100
   Fichas de Lucro". Saldo inicial: 100 fichas.
2. **Rodada 1 — Roleta do Imposto** — botão "Girar a Roleta do Imposto",
   animação de roleta, resultado fixo: **-25 fichas** (mensagem sobre
   Shotoku-zei/Jumin-zei). Saldo: 100 → 75.
3. **Rodada 2 — Escolha da Carta** — duas cartas clicáveis:
   - **Carta A** (tradicional): **-15 fichas**. Saldo: 75 → 60.
   - **Carta B** (ativar iDeCo): **+20 fichas**. Saldo: 75 → 95.
   No momento da revelação de cada carta, mostrar imediatamente o equivalente
   em ienes reais (1 ficha = ¥10.000), ex.: "+20 fichas ≈ ¥200.000 reais no
   seu bolso" — a ponte fichas→ienes acontece aqui, no pico emocional, não só
   no final.
4. **Ranking** — mostra "Saldo Final de Fichas" (métrica única, sem termos
   ambíguos como "fichas salvas"). Lista o jogador em destaque ao lado de 3
   participantes fictícios fixos (dados flavor, não precisam ser derivados da
   fórmula do jogo — só precisam ser plausíveis e nunca ultrapassar o máximo
   possível de 95 fichas):
   - Tanaka_Kojin — 95
   - Silva_Autonomo — 93
   - Kenji_Design — 91
   Ordenado do maior para o menor saldo.
5. **Transição / CTA** — texto da fala de transição do palestrante (fornecido
   pelo usuário) + botão real "Ver meu valor real →" linkando diretamente para
   `https://casapropriajp.com/ideco-2026` (sem depender de o público digitar a
   URL de cor).

Botão "Jogar de novo" disponível na tela de ranking/transição para reiniciar o
fluxo (reseta saldo para 100).

## Toggle Celular / Telão

Um botão discreto no canto da tela alterna entre duas apresentações visuais do
mesmo estado do jogo:
- **Visão Celular** (padrão): layout vertical compacto, como descrito acima.
- **Visão Telão**: mesma lógica de estado, mas com números grandes e o
  ranking em destaque — para o palestrante ensaiar como ficaria projetado.

O toggle não duplica lógica de jogo; é puramente uma troca de layout/CSS sobre
o mesmo estado.

## Feedback sensorial

- Efeitos sonoros curtos sintetizados via Web Audio API (sem arquivos de áudio
  externos, mantendo o arquivo autocontido) nos momentos de: girar roleta,
  perder fichas, ganhar fichas (som tipo "cha-ching").
- `navigator.vibrate()` nos momentos de perda/ganho em dispositivos móveis
  (no-op silencioso em desktop/navegadores sem suporte).
- Botão de mudo no canto da tela para desligar o som durante testes.

## Estilo visual

Tema "japonês moderno + cassino": paleta vermelho e dourado, padrão sutil tipo
washi de fundo, um leão (shishi) estilizado como mascote/ícone recorrente
(SVG inline, sem imagens externas), fichas com efeito de brilho dourado,
números em tipografia bold/grande para os valores de fichas.

## Arquitetura técnica

- Um único arquivo HTML autocontido (CSS + JS inline, sem dependências
  externas, sem build step).
- Máquina de estados simples em JS puro controlando a tela atual e o saldo de
  fichas.
- Todas as animações via CSS transitions/keyframes.
- Nenhuma chamada de rede, nenhum armazenamento persistente (localStorage não
  é necessário — cada reload começa do zero).

## Notas para versão futura (fora de escopo deste protótipo)

Quando for construir a versão multiplayer real para a plateia inteira, o
pacing de cada rodada deve ser controlado pelo apresentador (host avança a
rodada para todos), não por cada participante individualmente — senão o
efeito de "todo mundo vendo o placar cair junto no telão" se perde com
participantes em ritmos diferentes. Isso não afeta o protótipo atual, que é
de uso solo.
