---
adr: 006
title: "ADR-006 — Playwright Apenas na Fase 5"
status: Mantida
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - testes
---

# ADR-006 — Playwright Apenas na Fase 5

> ### 🔄 Status após o pivô v4.0
> ****Mantida e reforçada** (2026-09-02)**
>
> A decisão de adiar Playwright para a Fase 5 continua correta e ganha força: uma interface React em construção é ainda mais instável para testes E2E do que templates Django eram. A pirâmide de testes da v4.0 acrescenta Vitest na camada de componente.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-17
**Status**: Aprovada

## Contexto

O roadmap menciona pytest-django + Playwright para testes.

## Decisao

- **Fases 1-4**: Apenas pytest-django (testes de model, view, API, permissao)
- **Fase 5**: Adicionar Playwright para 10 testes E2E criticos

## Motivos

- Testes E2E em frontend instavel (Fases 1-3) quebram constantemente e geram retrabalho
- pytest-django cobre model layer, permissions, e API — que e onde a maioria dos bugs vive
- Playwright tem curva de aprendizado propria (browsers, selectors, waits)
- O roadmap v3.4 ja previa "10 testes E2E criticos" na Fase 5 — alinhado

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-005](./0005-plotly-em-vez-de-chartjs.md) | [Índice de ADRs](./README.md) | [ADR-007](./0007-excecao-alpinejs-no-modulo-de-chamada.md) |
