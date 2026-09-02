# Decisões Arquiteturais (ADRs) — SGA

> **As ADRs foram divididas em um arquivo por decisão.**
> Elas vivem em [`adr/`](./adr/) — este documento é o ponto de entrada.
> Atualizado em: 2026-09-02

---

## 📁 Onde estão as ADRs

```
Documentacao/adr/
├── README.md                                        ← índice completo, com política
├── 0001-django-orm-em-vez-de-sqlalchemy.md
├── 0002-django-groups-em-vez-de-guardian.md
├── ...
└── 0018-postgresql-em-dev-via-docker.md
```

👉 **[Abrir o índice completo de ADRs](./adr/README.md)**

Uma cópia consolidada do documento anterior (todas as 18 ADRs num arquivo único, como estava
até 02/09/2026) ficou preservada em
[`_arquivo_v3_4/decisoes_arquiteturais_consolidado_20260902.md`](./_arquivo_v3_4/decisoes_arquiteturais_consolidado_20260902.md),
para consulta contínua ou upload em ferramentas de IA.

---

## Índice rápido

### Parte I — Era Django (v3.4) · maio de 2026

| ADR | Título | Status |
|---|---|---|
| [001](./adr/0001-django-orm-em-vez-de-sqlalchemy.md) | Django ORM em vez de SQLAlchemy | 🔄 Substituída pela 009 |
| [002](./adr/0002-django-groups-em-vez-de-guardian.md) | Django Groups em vez de django-guardian | 🔄 Substituída pela 011 |
| [003](./adr/0003-storage-filesystem-local-e-supabase-s3.md) | Filesystem local (dev) + Supabase S3 (prod) | ✅ Mantida |
| [004](./adr/0004-cron-em-vez-de-celery.md) | Cron em vez de Celery | ✅ Mantida em espírito |
| [005](./adr/0005-plotly-em-vez-de-chartjs.md) | Plotly em vez de Chart.js | ❌ Revogada |
| [006](./adr/0006-playwright-apenas-na-fase-5.md) | Playwright apenas na Fase 5 | ✅ Mantida |
| [007](./adr/0007-excecao-alpinejs-no-modulo-de-chamada.md) | Exceção Alpine.js na Chamada | ⚪ Obsoleta |

### Parte II — Pivô API-First (v4.0) · setembro de 2026

| ADR | Título | Peso |
|---|---|---|
| [008](./adr/0008-pivo-para-arquitetura-api-first.md) | Pivô para arquitetura API-First | 🔴 decisão-mãe |
| [009](./adr/0009-sqlmodel-como-orm-e-validacao.md) | SQLModel como ORM e validação | 🔴 |
| [010](./adr/0010-alembic-como-sistema-unico-de-migrations.md) | Alembic como migrations | 🔴 |
| [011](./adr/0011-rbac-por-dependencias-e-filtro-no-repositorio.md) | RBAC em duas camadas | 🔴 segurança |
| [012](./adr/0012-auditoria-hibrida-listeners-e-triggers.md) | Auditoria híbrida | 🔴 segurança |
| [013](./adr/0013-fastapi-como-unico-authorization-server.md) | FastAPI como único Auth Server | 🔴 segurança |
| [014](./adr/0014-console-nextjs-com-sqladmin-como-ponte.md) | Console Next.js + SQLAdmin | 🔴 produto |
| [015](./adr/0015-trabalho-bloqueante-fora-do-event-loop.md) | Bloqueante fora do event loop | 🟡 |
| [016](./adr/0016-recharts-como-biblioteca-de-graficos.md) | Recharts | 🟡 |
| [017](./adr/0017-openapi-como-fonte-dos-tipos-typescript.md) | OpenAPI gera os tipos TS | 🟡 |
| [018](./adr/0018-postgresql-em-dev-via-docker.md) | PostgreSQL em dev via Docker | 🟡 |

---

## Política do registro

**Log append-only.** Decisões nunca são apagadas — quando deixam de valer, o arquivo recebe
um status no frontmatter e um bloco explicando o que mudou no contexto. O texto original
fica intacto.

Motivo: a banca de IC avalia o **raciocínio no contexto em que a decisão foi tomada**, não a
permanência dela. Reverter porque o contexto mudou é prática de engenharia; reverter porque
o raciocínio era falho é correção de erro — e o registro precisa distinguir os dois casos.

Instruções completas para criar uma ADR nova: [`adr/README.md`](./adr/README.md).

---

## Documentos relacionados

- [`principios.md`](./principios.md) — os 8 princípios que estas decisões aplicam
- [`stack.md`](./stack.md) — o resultado destas decisões
- [`blueprint.md`](./blueprint.md) — como elas se compõem em camadas
- [`migracao_v3_para_v4.md`](./migracao_v3_para_v4.md) — o pivô e a nota metodológica
