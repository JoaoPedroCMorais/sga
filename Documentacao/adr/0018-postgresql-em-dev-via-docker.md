---
adr: 018
title: "ADR-018 — PostgreSQL em Desenvolvimento via Docker (Aposentadoria do SQLite)"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - infraestrutura
  - postgresql
---

# ADR-018 — PostgreSQL em Desenvolvimento via Docker (Aposentadoria do SQLite)

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Coordenador de IC + Dev

## Contexto

Desde a v3.1, o SGA usava SQLite em desenvolvimento e PostgreSQL em produção, com a
justificativa de "zero configuração" para o ambiente local.

## Problema

A ADR-012 estabeleceu que a garantia de imutabilidade da auditoria depende de **triggers
PL/pgSQL**. O SQLite não os suporta na mesma forma, e não possui `JSONB`, `row_to_json()`
nem os tipos usados pelo `audit_log`.

Manter SQLite em desenvolvimento significaria que a camada mais crítica do Princípio #5
**não roda no ambiente onde o código é escrito e testado**. Bugs de auditoria só apareceriam
em produção, exatamente onde são mais caros e onde há dados reais de alunos.

Há ainda diferenças conhecidas que já mordem antes disso: SQLite não tem tipos `Enum`
nativos, é permissivo com tipagem, trata constraints e transações de forma distinta, e não
suporta `ON CONFLICT` com a mesma semântica usada no upsert da chamada.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Manter SQLite em dev | Zero configuração | Auditoria não testável localmente; divergência de tipos e constraints; contraria a paridade dev/prod |
| SQLite em dev + Postgres só no CI | Setup local leve | O desenvolvedor descobre a quebra no CI, não ao escrever; pior ciclo de feedback |
| **PostgreSQL 16 via Docker Compose** (adotada) | Paridade total; auditoria testável; um comando para subir | Exige Docker instalado; consumo de memória no ambiente local |

## Decisão

**Aposentar o SQLite do projeto.** O desenvolvimento local usa PostgreSQL 16 em contêiner,
subido por `docker compose up -d`, com a mesma versão maior utilizada em produção no Railway.

Os testes automatizados usam PostgreSQL real (schema dedicado ou testcontainers), não banco
em memória, porque precisam exercitar triggers e constraints reais.

## Consequências

- Uma dependência nova no ambiente de desenvolvimento: Docker
- Paridade dev/produção: constraints, tipos, transações e triggers se comportam igual
- Os testes ficam mais lentos que com banco em memória — trade-off aceito em favor de
  fidelidade, dado que a suíte é pequena na escala do projeto
- A menção a "SQLite (dev)" nos documentos anteriores fica formalmente revogada

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-017](./0017-openapi-como-fonte-dos-tipos-typescript.md) | [Índice de ADRs](./README.md) | — |
