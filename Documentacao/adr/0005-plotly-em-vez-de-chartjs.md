---
adr: 005
title: "ADR-005 — Plotly em vez de Chart.js"
status: Revogada
substituida_por: ADR-016
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - graficos
---

# ADR-005 — Plotly em vez de Chart.js

> ### 🔄 Status após o pivô v4.0
> ****Revogada** (2026-09-02)**
>
> Esta ADR foi revogada, não substituída. Seu argumento central era literalmente eliminar JavaScript de charting e manter os gráficos 100% em Python. Com a adoção do Next.js, escrever JavaScript deixou de ser evitável, e a premissa da decisão desapareceu. A escolha de biblioteca de gráficos foi refeita do zero na ADR-016.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-17 (decisao herdada da v3.4 original)
**Status**: Aprovada

## Contexto

Versoes anteriores usavam Chart.js (JavaScript) ou Metabase (ferramenta BI separada). A v3.4 consolidou em Plotly.

## Decisao

**Plotly** — graficos gerados 100% no backend (Python), sem JavaScript de charting. Os graficos sao renderizados como HTML/JSON e injetados na pagina via HTMX.

## Motivos

- Dev nao precisa escrever JavaScript para graficos
- Plotly gera graficos interativos (zoom, hover, filtro) nativamente
- Consistencia: mesmo ecossistema Python do restante do projeto
- Eliminacao de Metabase como dependencia separada

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-004](./0004-cron-em-vez-de-celery.md) | [Índice de ADRs](./README.md) | [ADR-006](./0006-playwright-apenas-na-fase-5.md) |
