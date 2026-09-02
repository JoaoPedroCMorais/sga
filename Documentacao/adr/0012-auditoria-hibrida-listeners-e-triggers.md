---
adr: 012
title: "ADR-012 — Auditoria Híbrida — Listeners SQLAlchemy e Triggers PL/pgSQL"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - auditoria
  - seguranca
---

# ADR-012 — Auditoria Híbrida — Listeners SQLAlchemy e Triggers PL/pgSQL

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: a implementação do Princípio #5 baseada em django-pghistory
**Decisores**: Coordenador de IC + Dev

## Contexto

O Princípio #5 (Auditoria Total) exige registro imutável de quem alterou o quê e quando. Na
v3.4 esse princípio era realizado inteiramente pelo `django-pghistory`, que instala triggers
no PostgreSQL e grava eventos em tabelas dedicadas. Os modelos `ClassGroup`, `Student`,
`AttendanceRecord` e `AbsenceJustification` já estavam rastreados.

## Problema

**Não existe equivalente maduro do django-pghistory para SQLModel.** As opções do ecossistema
SQLAlchemy foram avaliadas e nenhuma é substituto direto:

| Biblioteca | Avaliação |
|---|---|
| `sqlalchemy-continuum` | Histórico de manutenção irregular; suporte a async problemático; acoplada a padrões de sessão que o FastAPI não usa |
| `sqlalchemy-history` | Fork mais recente do continuum; menos maduro; base de usuários pequena |
| Implementação própria | Exige decidir explicitamente o nível da garantia |

Registra-se com honestidade: **esta é a maior perda técnica do pivô.** O pghistory oferecia
imutabilidade garantida pelo banco, com configuração de uma linha por modelo.

## Alternativas Consideradas

| Opção | Garantia | Prós | Contras |
|---|---|---|---|
| A. Apenas listeners SQLAlchemy | Nível de aplicação | 100% Python; testável; registro rico (usuário, IP, endpoint) | Qualquer escrita que não passe pela sessão da aplicação escapa: `bulk_insert`, script de manutenção, acesso direto ao banco |
| B. Apenas triggers PL/pgSQL | Nível de banco | Imutabilidade real; equivalente ao pghistory | Não captura contexto de aplicação (qual usuário HTTP, qual endpoint); exige SQL bruto |
| **C. Híbrida** (adotada) | Ambos | Cobre os dois flancos; o contexto rico vem da aplicação e a garantia vem do banco | Duas implementações a manter; possibilidade de registro duplicado a ser tratada |

## Decisão

**Adotar a estratégia híbrida (opção C)**, em duas camadas:

**Camada de aplicação** — listener `before_flush` do SQLAlchemy grava em `audit_log` o
registro rico: `actor_id`, `actor_role`, `ip`, `endpoint`, `entity`, `entity_id`, `action`,
`changes` (JSONB com o diff), `occurred_at`, `source='app'`.

**Camada de banco** — triggers `AFTER INSERT/UPDATE/DELETE` nas entidades críticas gravam em
`audit_log` com `source='db'`, capturando `row_to_json(OLD)` e `row_to_json(NEW)`. Os
triggers são criados em migration Alembic e versionados em git.

Entidades cobertas pelas duas camadas: `User`, `Student`, `ClassGroup`, `AttendanceRecord`,
`AbsenceJustification`.

**Imutabilidade da tabela:** `audit_log` é append-only. Nenhum endpoint expõe UPDATE ou
DELETE sobre ela. Em produção, o usuário de aplicação recebe apenas `INSERT` e `SELECT` na
tabela; `UPDATE`/`DELETE` são revogados via `REVOKE`.

**Consulta:** router `audit` estritamente read-only, acessível apenas ao perfil Coordenador.

## Consequências

- **Exceção formal ao Princípio #6** (SQL bruto), delimitada a migrations Alembic. Registrada
  na redação do próprio princípio.
- **O SQLite deixa de ser viável em desenvolvimento** (ADR-018): sem triggers PL/pgSQL, a
  camada de garantia simplesmente não roda em dev, e bugs de auditoria só apareceriam em
  produção.
- Registro duplicado é esperado e desejado — as duas fontes são distinguidas por `source` e
  correlacionadas na consulta. Divergência entre elas é sinal de escrita que escapou da
  aplicação, e é exatamente o que se quer detectar.
- Testes de auditoria exigem PostgreSQL real, não banco em memória.

## Comparação honesta com a v3.4

| Aspecto | v3.4 (pghistory) | v4.0 (híbrida) |
|---|---|---|
| Imutabilidade | Garantida pelo banco | Garantida pelo banco (triggers) |
| Contexto de aplicação | Limitado (via middleware do pghistory) | Rico (usuário, IP, endpoint, motivo) |
| Esforço de implementação | Uma linha por modelo | Listener + trigger + migration + testes |
| Risco de erro de implementação | Baixo (biblioteca madura) | **Médio — código próprio** |

O risco residual é reconhecido: código de auditoria escrito no projeto é menos testado em
campo que uma biblioteca consolidada. A mitigação é cobertura de testes específica para os
cinco modelos críticos, incluindo teste que confirma que uma escrita fora da sessão da
aplicação ainda é capturada pelo trigger.

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-011](./0011-rbac-por-dependencias-e-filtro-no-repositorio.md) | [Índice de ADRs](./README.md) | [ADR-013](./0013-fastapi-como-unico-authorization-server.md) |
