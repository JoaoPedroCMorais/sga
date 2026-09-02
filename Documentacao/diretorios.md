# Especificação de Diretórios — SGA v4.0 (Monorepo)

> Documento de uso interno: controle de implementação de arquitetura.
> Versão: 4.0 | Atualizado em: 2026-09-02
> Substitui: `_arquivo_v3_4/diretorios_v3_4_revisado.md`

---

## Por que monorepo

| Alternativa | Avaliação |
|---|---|
| Dois repositórios (api e web) | Separação limpa, mas a geração de tipos do OpenAPI passa a exigir publicação de pacote ou submodule; uma alteração de contrato vira dois PRs em dois repositórios |
| **Monorepo** (adotado) | Uma alteração de contrato é um commit atômico que já contém backend, tipos gerados e frontend; CI valida os dois lados juntos; para desenvolvedor solo, elimina sobrecarga de coordenação |

O Princípio #8 (o contrato de API é a fronteira) só é verificável em CI de forma barata se
backend e frontend estiverem no mesmo commit.

---

## Estrutura Completa

```
sga/
│
├── apps/
│   │
│   ├── api/                                # Backend FastAPI
│   │   ├── src/sga_api/
│   │   │   ├── __init__.py
│   │   │   ├── main.py                     # instância FastAPI, middlewares, CORS, routers
│   │   │   │
│   │   │   ├── core/                       # infraestrutura transversal
│   │   │   │   ├── config.py               # pydantic-settings (variáveis de ambiente)
│   │   │   │   ├── security.py             # JWT, require_role(), get_current_user()
│   │   │   │   ├── oauth.py                # Authlib — fluxo Google (ADR-013)
│   │   │   │   └── exceptions.py           # handlers de exceção padronizados
│   │   │   │
│   │   │   ├── db/
│   │   │   │   ├── session.py              # engine assíncrona, get_session()
│   │   │   │   └── listeners.py            # auditoria nível aplicação (ADR-012)
│   │   │   │
│   │   │   ├── models/                     # SQLModel table=True — o schema do banco
│   │   │   │   ├── user.py                 # User (role, email como identificador)
│   │   │   │   ├── academic.py             # Student, Teacher, Subject, ClassGroup
│   │   │   │   ├── attendance.py           # AttendanceRecord, AbsenceJustification
│   │   │   │   ├── schedule.py             # Schedule, TimeSlot, Availability
│   │   │   │   ├── assessment.py           # Exam, ExamResult, Question
│   │   │   │   ├── audit.py                # AuditLog (append-only)
│   │   │   │   └── job.py                  # Job (status de tarefas longas — ADR-015)
│   │   │   │
│   │   │   ├── schemas/                    # SQLModel table=False — contratos de I/O
│   │   │   │   ├── user.py                 # UserCreate, UserRead, UserUpdate
│   │   │   │   ├── academic.py
│   │   │   │   ├── attendance.py
│   │   │   │   ├── schedule.py
│   │   │   │   ├── assessment.py
│   │   │   │   └── dashboard.py            # séries agregadas para os gráficos
│   │   │   │
│   │   │   ├── routers/                    # camada HTTP — um arquivo por domínio
│   │   │   │   ├── auth.py                 # login, callback, refresh, logout, me
│   │   │   │   ├── users.py
│   │   │   │   ├── academic.py
│   │   │   │   ├── attendance.py
│   │   │   │   ├── schedules.py
│   │   │   │   ├── assessments.py
│   │   │   │   ├── dashboards.py
│   │   │   │   ├── jobs.py
│   │   │   │   └── audit.py                # READ-ONLY, exclusivo do Coordenador
│   │   │   │
│   │   │   ├── repositories/               # ◄ ONDE VIVE O FILTRO DE PERMISSÃO
│   │   │   │   ├── base.py
│   │   │   │   ├── student.py
│   │   │   │   ├── class_group.py
│   │   │   │   ├── attendance.py
│   │   │   │   └── assessment.py
│   │   │   │
│   │   │   ├── services/                   # regra de negócio — não conhece HTTP
│   │   │   │   ├── solver.py               # CP-SAT (portado de gerar_grade.py)
│   │   │   │   ├── swap_suggester.py       # sugestão de trocas de aula
│   │   │   │   ├── evalbee_pipeline.py     # ETL (portado de gerar_estatisticas.py)
│   │   │   │   ├── pdf_generator.py        # boletins — WeasyPrint + Matplotlib
│   │   │   │   └── aggregations.py         # séries dos dashboards
│   │   │   │
│   │   │   ├── validation/                 # schemas Pandera (fronteira ETL)
│   │   │   │   ├── evalbee_schema.py
│   │   │   │   ├── students_import_schema.py
│   │   │   │   └── sheets_schema.py
│   │   │   │
│   │   │   ├── admin/                      # ⚠️ SQLAdmin — TEMPORÁRIO, remover na Fase 2
│   │   │   │   └── setup.py                #    cláusula de remoção na ADR-014
│   │   │   │
│   │   │   ├── templates/                  # Jinja2 — único uso server-side (PDF)
│   │   │   │   └── report_card.html
│   │   │   │
│   │   │   └── cli/                        # scripts Typer (substituem management commands)
│   │   │       ├── sync_classroom.py
│   │   │       ├── process_evalbee.py
│   │   │       └── seed.py
│   │   │
│   │   ├── alembic/
│   │   │   ├── env.py                      # target_metadata = SQLModel.metadata
│   │   │   └── versions/                   # inclui triggers PL/pgSQL (ADR-012)
│   │   │
│   │   ├── tests/
│   │   │   ├── conftest.py                 # fixtures: sessão, PostgreSQL de teste, usuários
│   │   │   ├── factories/                  # polyfactory
│   │   │   ├── test_models/
│   │   │   ├── test_repositories/          # ◄ testes de filtro por vínculo
│   │   │   ├── test_routers/               # httpx.AsyncClient + ASGITransport
│   │   │   ├── test_permissions/           # ◄ 4 perfis + testes de IDOR
│   │   │   ├── test_audit/                 # ◄ inclui escrita fora da sessão da aplicação
│   │   │   └── test_services/
│   │   │
│   │   ├── pyproject.toml                  # uv, Ruff, mypy, pytest
│   │   ├── alembic.ini
│   │   └── CLAUDE.md                       # diretrizes específicas do backend
│   │
│   └── web/                                # Frontend Next.js
│       ├── src/
│       │   ├── app/
│       │   │   ├── layout.tsx
│       │   │   ├── (auth)/                 # rotas públicas
│       │   │   │   ├── login/
│       │   │   │   └── callback/
│       │   │   │
│       │   │   ├── (admin)/                # ◄ CONSOLE — substitui o Django Admin
│       │   │   │   ├── layout.tsx          # sidebar + guarda de rota por perfil
│       │   │   │   ├── usuarios/
│       │   │   │   ├── alunos/             # inclui importação em lote
│       │   │   │   ├── turmas/
│       │   │   │   ├── professores/
│       │   │   │   ├── disciplinas/
│       │   │   │   └── auditoria/          # read-only
│       │   │   │
│       │   │   └── (app)/                  # uso cotidiano
│       │   │       ├── chamada/            # mobile-first
│       │   │       ├── ficha/[id]/
│       │   │       ├── justificativas/
│       │   │       ├── grade/
│       │   │       ├── simulados/
│       │   │       └── dashboards/
│       │   │
│       │   ├── components/
│       │   │   ├── ui/                     # shadcn/ui (copiado para o repo)
│       │   │   ├── data-table/             # ◄ <DataTable /> genérico (ADR-014)
│       │   │   ├── crud-form/              # ◄ <CrudForm /> genérico (ADR-014)
│       │   │   ├── charts/                 # wrappers Recharts (ADR-016)
│       │   │   └── attendance/             # componentes da chamada
│       │   │
│       │   ├── lib/
│       │   │   ├── api/
│       │   │   │   ├── client.ts           # fetch com credenciais e refresh
│       │   │   │   └── hooks/              # hooks TanStack Query por domínio
│       │   │   ├── auth.ts                 # leitura de sessão, guarda de rota
│       │   │   └── schemas/                # schemas Zod derivados do OpenAPI
│       │   │
│       │   └── config/
│       │       └── entities/               # ◄ definição de colunas e campos por entidade
│       │           ├── student.ts          #    é isto que faz uma tela nova custar 1 dia
│       │           ├── class-group.ts
│       │           └── user.ts
│       │
│       ├── tests/                          # Vitest + Testing Library
│       ├── e2e/                            # Playwright — apenas Fase 5 (ADR-006)
│       ├── package.json
│       ├── tailwind.config.ts
│       ├── tsconfig.json                   # strict: true
│       └── CLAUDE.md                       # diretrizes específicas do frontend
│
├── packages/
│   └── api-types/                          # ◄ GERADO — nunca editado à mão (ADR-017)
│       ├── schema.d.ts                     # saída do openapi-typescript
│       └── package.json
│
├── Documentacao/                           # ◄ SSOT DOCUMENTAL
│   ├── stack.md
│   ├── principios.md
│   ├── blueprint.md
│   ├── decisoes_arquiteturais.md
│   ├── roadmap.md
│   ├── diretorios.md                       # este arquivo
│   ├── migracao_v3_para_v4.md
│   └── _arquivo_v3_4/                      # congelado — documentação da era Django
│
├── Cerebro/                                # vault Obsidian — apenas LÊ de Documentacao/
│
├── scripts/
│   └── generate-types.sh                   # openapi.json → packages/api-types
│
├── .github/workflows/
│   ├── api.yml                             # ruff + mypy + pytest
│   ├── web.yml                             # eslint + tsc + vitest
│   └── contract.yml                        # ◄ falha se os tipos gerados divergirem
│
├── docker-compose.yml                      # PostgreSQL 16 local (ADR-018)
├── pnpm-workspace.yaml
├── .env.example
├── .gitignore
├── CLAUDE.md                               # diretrizes gerais do projeto
└── README.md
```

---

## Regras de Organização

### Direção das dependências (backend)

```
routers/  →  services/  →  repositories/  →  models/
    │                           │
    └──────► schemas/ ◄─────────┘
```

| Regra | Verificação |
|---|---|
| `services/` **nunca** importa de `routers/` | Regra herdada da v3.4 e mantida |
| `services/` nunca recebe objetos `Request` ou `Response` | Regra de negócio não conhece HTTP |
| `routers/` nunca executa `select()` diretamente | Todo acesso ao banco passa por repositório |
| `repositories/` **sempre** recebe o usuário autenticado | É onde o Princípio #4 é aplicado |
| `models/` (`table=True`) nunca é usado como `response_model` | Evita vazamento de campo sensível |

### Responsabilidade por diretório (backend)

| Diretório | Contém | Nunca contém |
|---|---|---|
| `core/` | Configuração, segurança, dependências transversais | Conhecimento do domínio acadêmico |
| `models/` | Definição de tabelas | Lógica de aplicação |
| `schemas/` | Contratos de entrada e saída | `table=True` |
| `routers/` | Tradução HTTP ↔ caso de uso; `response_model` obrigatório | Regra de negócio; consulta ao banco |
| `repositories/` | Consultas com filtro de permissão | Regra de negócio |
| `services/` | Regra de negócio, solver, ETL, PDF | Importações de HTTP |
| `validation/` | Schemas Pandera | Validação de payload HTTP (isso é Pydantic) |
| `cli/` | Scripts Typer para Cron e manutenção | Endpoints |

### Organização do frontend

| Diretório | Regra |
|---|---|
| `app/(admin)/` | Toda rota exige perfil Coordenador na guarda de layout |
| `app/(app)/` | Guarda por perfil declarada por rota |
| `components/ui/` | shadcn/ui — copiado para o repositório, não instalado como dependência |
| `components/data-table/`, `crud-form/` | Genéricos e reutilizáveis; nunca contêm regra de uma entidade específica |
| `config/entities/` | Onde vive a especificidade de cada entidade (colunas, campos, labels) |
| `lib/api/` | Único lugar que fala com a API; usa exclusivamente os tipos de `packages/api-types` |
| `packages/api-types/` | **Gerado. Editar à mão é violação do Princípio #8** |

### Convenção de nomes

| Contexto | Convenção | Exemplo |
|---|---|---|
| Módulos Python | `snake_case` | `evalbee_pipeline.py` |
| Modelos e schemas | `PascalCase` | `AttendanceRecord`, `StudentRead` |
| Rotas da API | `kebab-case`, plural, com `/api/v1/` | `/api/v1/attendance-records` |
| Arquivos React | `kebab-case` | `data-table.tsx` |
| Componentes React | `PascalCase` | `<DataTable />` |
| Rotas do Next.js | `kebab-case`, **em português** (é interface de usuário) | `/alunos`, `/chamada` |

**Observação sobre idioma:** o código, os modelos e as rotas da API são escritos em inglês; a
interface e as rotas do frontend, em português, porque são vistas pelos usuários do CAAI. As
mensagens de erro retornadas pela API são em português, pois são exibidas ao usuário final.

### Arquivos temporários com data de remoção

| Caminho | Remoção prevista | Referência |
|---|---|---|
| `apps/api/src/sga_api/admin/` | Fim da Fase 2 | ADR-014 |

Nenhum outro andaime temporário é permitido sem ADR que declare a data de remoção.

---

## Migração da Estrutura Django

| Estrutura v3.4 | Destino v4.0 |
|---|---|
| `users/models.py` | `apps/api/src/sga_api/models/user.py` |
| `academic/models.py` | `apps/api/src/sga_api/models/academic.py` |
| `attendance/models.py` | `apps/api/src/sga_api/models/attendance.py` |
| `attendance/views.py` | Dividido em `routers/attendance.py` + `repositories/attendance.py` |
| `*/admin.py` | `app/(admin)/` no Next.js (e `admin/setup.py` temporário) |
| `templates/*.html` | `apps/web/src/app/` |
| `*/tests/` | `apps/api/tests/` |
| `config/settings.py` | `core/config.py` (pydantic-settings) |
| `*/migrations/` | Descartadas — Alembic recomeça (ADR-010) |
| `manage.py` | `cli/` com Typer |

---

## Referências

- `blueprint.md` — camadas arquiteturais mapeadas nestes diretórios
- `stack.md` — tecnologias de cada camada
- `decisoes_arquiteturais.md` — ADRs que justificam estas separações
