---
adr: 010
title: "ADR-010 — Alembic como Sistema Único de Migrations"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - migrations
  - alembic
---

# ADR-010 — Alembic como Sistema Único de Migrations

**Data**: 2026-09-02
**Status**: Aprovada
**Relacionada**: ADR-001 (que proibia Alembic), ADR-009
**Decisores**: Dev

## Contexto

A v3.4 listava Alembic entre as tecnologias proibidas. O motivo, registrado na ADR-001, era
específico: *"Django Migrations e Alembic são dois sistemas de migração de schema
concorrentes. Mantê-los sincronizados é fonte garantida de bugs."*

## Problema

Com a remoção do Django, não há mais Django Migrations. O SQLModel não possui sistema de
migração próprio. Sem Alembic, a evolução de schema seria manual — inaceitável para um
sistema com auditoria e dados reais de alunos.

## Decisão

**Adotar Alembic como sistema único de migrations**, configurado com
`target_metadata = SQLModel.metadata`.

Convenções obrigatórias:

1. Toda migration é gerada com `alembic revision --autogenerate` e **revisada manualmente
   antes do commit**. O autogenerate não detecta renomeações nem alterações de tipo com
   segurança.
2. Toda migration tem `downgrade()` implementado. Migration sem downgrade não passa em
   review.
3. Triggers e funções PL/pgSQL da auditoria (ADR-012) vivem em migrations, com `op.execute()`.
4. Migrations rodam antes do deploy da API, nunca depois (ver topologia em `blueprint.md`).
5. As migrations do Django (7 arquivos em `academic/`, `attendance/`, `users/`) são
   descartadas. O banco de desenvolvimento é recriado do zero na Fase 0; não há dados de
   produção a preservar nesta etapa.

## Consequências

- A proibição da v3.4 é formalmente levantada, com o registro do motivo
- Um único histórico linear de schema, versionado em git
- Risco conhecido: `--autogenerate` com PostgreSQL e SQLModel ocasionalmente produz diffs
  espúrios em tipos `Enum` — daí a exigência de revisão manual

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-009](./0009-sqlmodel-como-orm-e-validacao.md) | [Índice de ADRs](./README.md) | [ADR-011](./0011-rbac-por-dependencias-e-filtro-no-repositorio.md) |
