---
adr: 016
title: "ADR-016 — Recharts como Biblioteca de Gráficos"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - graficos
  - frontend
---

# ADR-016 — Recharts como Biblioteca de Gráficos

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: ADR-005 (revogada)
**Decisores**: Coordenador de IC + Dev

## Contexto

A ADR-005 escolhera Plotly com um argumento explícito: gráficos gerados 100% no backend em
Python, sem JavaScript de charting, renderizados como HTML e injetados via HTMX.

## Problema

**A premissa da ADR-005 deixou de existir.** Com o Next.js, escrever JavaScript não é mais
evitável — é a linguagem da camada de apresentação. O argumento "o dev não precisa escrever
JavaScript para gráficos" perdeu sentido, e com ele toda a base da decisão anterior. A
escolha precisa ser refeita do zero, não adaptada.

Muda também a natureza do dado trafegado: em vez de o backend devolver HTML de um gráfico
pronto, ele passa a devolver **JSON agregado**, e o cliente decide como desenhar. Isso é
consequência direta do Princípio #8 — o contrato expõe dados, não apresentação.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| `react-plotly.js` | Continuidade conceitual; muito poderoso; zoom e pan científicos | ~1 MB no bundle; API imperativa que destoa do React; estilização difícil de casar com Tailwind |
| **Recharts** (adotada) | Componentes React declarativos; leve; combina bem com Tailwind e shadcn/ui; curva de aprendizado curta | Menos recursos para gráficos científicos complexos |
| Chart.js + react-chartjs-2 | Popular; leve | API imperativa via canvas; acessibilidade pior; **proibido desde a v3.4** |
| Visx / D3 | Controle total | Curva de aprendizado alta; excesso de código para gráficos simples |
| Manter Plotly server-side gerando imagens | Sem JS de charting | Perde interatividade; contraria o Princípio #8 |

## Decisão

**Adotar Recharts** como biblioteca única de gráficos do cliente web.

Regra de contrato: os endpoints de dashboard retornam **JSON agregado** — séries de dados
prontas para plotagem, agregadas no PostgreSQL — e nunca HTML, imagem ou configuração de
gráfico. Exemplo: `GET /api/v1/dashboards/exam/{id}/accuracy-by-room` devolve
`[{room: "Sala 1", accuracy: 0.72}, ...]`.

**Matplotlib permanece no backend**, exclusivamente para gráficos estáticos embarcados nos
boletins em PDF gerados por WeasyPrint. São contextos distintos: PDF é imagem, dashboard é
interação.

## Consequências

- A agregação passa a ser responsabilidade explícita do backend (SQL/SQLModel), o que é
  desejável: agregar 90 alunos no cliente seria desperdício de banda e bateria
- Gráficos ficam consistentes com o design system (Tailwind + shadcn/ui)
- Se surgir necessidade de visualização científica complexa (heatmaps densos, 3D), avaliar
  `react-plotly.js` pontualmente naquela tela, com extensão desta ADR — nunca em silêncio

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-015](./0015-trabalho-bloqueante-fora-do-event-loop.md) | [Índice de ADRs](./README.md) | [ADR-017](./0017-openapi-como-fonte-dos-tipos-typescript.md) |
