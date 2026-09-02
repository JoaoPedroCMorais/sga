# Decisões Arquiteturais (ADRs) — SGA

> Registro formal e cumulativo das decisões de arquitetura do projeto.
> Um arquivo por decisão, no padrão ADR (Michael Nygard).
> Atualizado em: 2026-09-02

---

## Como este registro funciona

Este é um **log append-only**. Decisões nunca são apagadas — quando deixam de valer, o
arquivo recebe um status no frontmatter e um bloco explicando o que a substituiu. O texto
original é preservado sem alteração.

Essa política existe por três razões: a rastreabilidade exigida pela banca de Iniciação
Científica, a possibilidade de auditar o raciocínio que levou a cada mudança, e o fato de
que uma decisão revogada frequentemente contém o argumento que impede que o erro oposto
seja cometido no futuro.

| Status | Significado |
|---|---|
| **Aprovada** | Vigente |
| **Substituída** | O problema continua existindo; a solução mudou |
| **Revogada** | A premissa que motivava a decisão deixou de existir |
| **Obsoleta** | A decisão perdeu objeto (o caso de uso desapareceu) |
| **Mantida** | Sobreviveu ao pivô, com ou sem adaptação |

---

## Parte I — Era Django (v3.4) · maio de 2026

| ADR | Título | Status |
|---|---|---|
| [001](./0001-django-orm-em-vez-de-sqlalchemy.md) | Django ORM em vez de SQLAlchemy | 🔄 Substituída pela 009 |
| [002](./0002-django-groups-em-vez-de-guardian.md) | Django Groups em vez de django-guardian | 🔄 Substituída pela 011 |
| [003](./0003-storage-filesystem-local-e-supabase-s3.md) | Filesystem local (dev) + Supabase Storage S3 (prod) | ✅ Mantida |
| [004](./0004-cron-em-vez-de-celery.md) | django-crontab + Railway Cron em vez de Celery | ✅ Mantida em espírito |
| [005](./0005-plotly-em-vez-de-chartjs.md) | Plotly em vez de Chart.js | ❌ Revogada |
| [006](./0006-playwright-apenas-na-fase-5.md) | Playwright apenas na Fase 5 | ✅ Mantida e reforçada |
| [007](./0007-excecao-alpinejs-no-modulo-de-chamada.md) | Exceção controlada — Alpine.js na Chamada | ⚪ Obsoleta |

## Parte II — Pivô API-First (v4.0) · setembro de 2026

| ADR | Título | Peso |
|---|---|---|
| [008](./0008-pivo-para-arquitetura-api-first.md) | Pivô para arquitetura API-First | 🔴 **decisão-mãe** |
| [009](./0009-sqlmodel-como-orm-e-validacao.md) | SQLModel como ORM e validação unificada | 🔴 estrutural |
| [010](./0010-alembic-como-sistema-unico-de-migrations.md) | Alembic como sistema único de migrations | 🔴 estrutural |
| [011](./0011-rbac-por-dependencias-e-filtro-no-repositorio.md) | RBAC por dependências + filtro no repositório | 🔴 segurança |
| [012](./0012-auditoria-hibrida-listeners-e-triggers.md) | Auditoria híbrida: listeners + triggers PL/pgSQL | 🔴 segurança |
| [013](./0013-fastapi-como-unico-authorization-server.md) | FastAPI como único Authorization Server | 🔴 segurança |
| [014](./0014-console-nextjs-com-sqladmin-como-ponte.md) | Console em Next.js + SQLAdmin como ponte | 🔴 produto |
| [015](./0015-trabalho-bloqueante-fora-do-event-loop.md) | Trabalho bloqueante fora do event loop | 🟡 operação |
| [016](./0016-recharts-como-biblioteca-de-graficos.md) | Recharts como biblioteca de gráficos | 🟡 frontend |
| [017](./0017-openapi-como-fonte-dos-tipos-typescript.md) | Contrato OpenAPI como fonte dos tipos TS | 🟡 integração |
| [018](./0018-postgresql-em-dev-via-docker.md) | PostgreSQL em dev via Docker | 🟡 infraestrutura |

---

## Por onde começar

| Se você quer... | Leia |
|---|---|
| Entender o projeto inteiro em uma decisão | [ADR-008](./0008-pivo-para-arquitetura-api-first.md) |
| Escrever um endpoint sem abrir brecha de segurança | [ADR-011](./0011-rbac-por-dependencias-e-filtro-no-repositorio.md) |
| Entender por que o SQLite foi aposentado | [ADR-012](./0012-auditoria-hibrida-listeners-e-triggers.md) → [ADR-018](./0018-postgresql-em-dev-via-docker.md) |
| Saber por que não usamos NextAuth direto no Google | [ADR-013](./0013-fastapi-como-unico-authorization-server.md) |
| Evitar derrubar o sistema com o solver | [ADR-015](./0015-trabalho-bloqueante-fora-do-event-loop.md) |
| Defender o pivô perante a banca | [ADR-008](./0008-pivo-para-arquitetura-api-first.md) + `../migracao_v3_para_v4.md` |

---

## Como criar uma ADR nova

1. Próximo número livre, com quatro dígitos e slug descritivo:
   `Documentacao/adr/0019-titulo-curto.md`
2. Frontmatter obrigatório:

```yaml
---
adr: 019
title: "ADR-019 — Título"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - <domínio>
---
```

3. Estrutura do corpo:

```markdown
# ADR-019 — Título

**Data**: AAAA-MM-DD
**Status**: Aprovada
**Substitui**: (se aplicável)
**Decisores**: Coordenador de IC + Dev

## Contexto
## Problema
## Alternativas Consideradas   (tabela com prós e contras)
## Decisão
## Consequências
## Cláusula de Revisão   (obrigatória para andaimes temporários)

## Navegação
```

4. Acrescentar a linha na tabela deste índice
5. Atualizar `Cerebro/Registro de Atualizações.md`

> [!important] Nunca apague uma ADR
> Quando uma decisão deixa de valer, altere o `status` no frontmatter, acrescente um bloco
> explicando o que mudou no contexto, e mantenha o texto original intacto. A banca avalia o
> **raciocínio no contexto em que a decisão foi tomada**, não a permanência dela.

---

## Andaime com prazo

> ⚠️ A [ADR-014](./0014-console-nextjs-com-sqladmin-como-ponte.md) autoriza o SQLAdmin como
> ponte temporária, com **remoção obrigatória ao fim da Fase 2**. Estender exige nova ADR —
> não pode ocorrer por omissão.

---

## Documentos relacionados

| Documento | Conteúdo |
|---|---|
| `../principios.md` | Os 8 princípios que estas decisões aplicam |
| `../stack.md` | O resultado destas decisões, em forma de pilha tecnológica |
| `../blueprint.md` | Como as decisões se compõem em camadas |
| `../migracao_v3_para_v4.md` | Registro do pivô e nota metodológica sobre revisão de decisões |
