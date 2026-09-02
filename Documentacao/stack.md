# Stack Definitiva — SGA v4.0 (API-First)

> Documento canônico da pilha tecnológica do SGA.
> Qualquer divergência em outros documentos deve ser resolvida em favor DESTE arquivo.
> Versão: 4.0 | Atualizado em: 2026-09-02
> Substitui: `_arquivo_v3_4/stack_definitiva_v3_4_revisada.md`

---

## Visão Geral

Sistema de Gerenciamento Acadêmico (SGA) para o curso preparatório CAAI.

| Dimensão | Valor |
|---|---|
| Escala | ~90 alunos, ~20 professores, 3 salas, 4 perfis de acesso |
| Execução | Desenvolvedor solo com auxílio de IAs + orientação do Coordenador de IC |
| Arquitetura | **API-First desacoplada** (cliente web e API independentes) |
| Timeline | 10-11 meses, 6 fases (Fase 0 a Fase 5) |
| Clientes previstos | Web (Next.js) na v4.0; Mobile (React Native/Flutter) em trabalho futuro |

**Razão da arquitetura desacoplada:** permitir que múltiplos clientes (web, mobile, e
eventuais integrações institucionais) consumam a mesma API sem duplicação de regra de
negócio. Ver ADR-008.

---

## Pilha Tecnológica Definitiva

### Backend — API

| Componente | Tecnologia | Versão | Notas |
|---|---|---|---|
| Framework | FastAPI | 0.115+ | Async, OpenAPI nativo |
| Servidor ASGI | Uvicorn | 0.32+ | `--workers` em produção |
| ORM e Modelos | **SQLModel** | 0.0.22+ | SQLAlchemy 2.0 + Pydantic v2 unificados |
| Validação HTTP | Pydantic | v2 | Embutido no SQLModel |
| Migrations | **Alembic** | 1.13+ | Único sistema de migração do projeto |
| Banco (dev) | **PostgreSQL 16 via Docker Compose** | 16 | Paridade com produção (ADR-018) |
| Banco (prod) | PostgreSQL | 16 (Railway managed) | SSOT |
| Driver | psycopg | 3.x | Suporte async |
| Configuração | pydantic-settings | 2.x | Variáveis de ambiente tipadas |
| Gerenciador de pacotes | **uv** | latest | Substitui pip/venv; lockfile determinístico |

### Autenticação e Autorização

| Componente | Tecnologia | Notas |
|---|---|---|
| Authorization Server | **FastAPI + Authlib** | Único emissor de credenciais do sistema (ADR-013) |
| Provedor de identidade | Google OAuth2 | Restrito ao domínio institucional |
| Tokens | PyJWT | Access token 15 min + refresh token 7 dias |
| Transporte do token | Cookie `httpOnly`, `Secure`, `SameSite=Lax` | Web. Mobile usa `Authorization: Bearer` |
| Hash (contas locais de fallback) | passlib + argon2 | Apenas para contas de serviço/seed |
| RBAC | Dependências FastAPI + filtros no repositório | 4 perfis fixos (ADR-011) |
| Auditoria | **Listeners SQLAlchemy + triggers PL/pgSQL** | Estratégia híbrida (ADR-012) |

> **Regra estrutural:** o Next.js **não** autentica contra o Google. Ele autentica contra o
> FastAPI. Se NextAuth (Auth.js) for utilizado, é exclusivamente como cliente OIDC apontando
> para o próprio backend do SGA. Ver ADR-013.

### Frontend Web

| Componente | Tecnologia | Versão | Notas |
|---|---|---|---|
| Framework | **Next.js** | 15+ (App Router) | React Server Components onde couber |
| Runtime | React | 19 | — |
| Linguagem | TypeScript | 5.x | `strict: true` obrigatório |
| CSS | **Tailwind CSS** | 4.x | Utility-first, mobile-first |
| Componentes | shadcn/ui | latest | Copiados para o repo, não instalados como dependência |
| Estado de servidor | TanStack Query | v5 | Cache, revalidação, optimistic updates |
| Tabelas | TanStack Table | v8 | Base do `<DataTable />` genérico |
| Formulários | React Hook Form + Zod | latest | Schemas Zod derivados do OpenAPI |
| Gráficos | **Recharts** | 2.x | Substitui o Plotly server-side (ADR-016) |
| Gerenciador de pacotes | pnpm | 9.x | Workspaces do monorepo |

### Contrato de API

| Componente | Tecnologia | Notas |
|---|---|---|
| Especificação | OpenAPI 3.1 | Gerado automaticamente pelo FastAPI |
| Documentação interativa | Swagger UI (`/docs`) + ReDoc (`/redoc`) | Nativo, sem configuração |
| Geração de tipos | **openapi-typescript** | Gera `packages/api-types` |
| Verificação no CI | Diff do tipo gerado vs. commitado | Build falha se divergir (Princípio #8) |
| Versionamento | Prefixo de rota `/api/v1/` | Protege clientes mobile futuros |

### ETL, Validação e Otimização

| Componente | Tecnologia | Notas |
|---|---|---|
| Processamento de dados | Pandas + openpyxl | ETL de planilhas EvalBee e Google Sheets |
| Validação de schema | **Pandera** | Mantido da v3.4 — valida DataFrames antes de processar |
| Otimização (grade horária) | Google OR-Tools (CP-SAT) | **Executado fora do event loop** (ADR-015) |
| Scripts CLI | Typer | Substitui os management commands do Django |
| Agendamento (dev) | APScheduler | Processo único, nunca com múltiplos workers |
| Agendamento (prod) | **Railway Cron Jobs** | Chama script Typer ou endpoint protegido |

### Documentos e Relatórios

| Componente | Tecnologia | Notas |
|---|---|---|
| PDF (boletins, relatórios) | WeasyPrint | HTML/CSS para PDF, executado no FastAPI |
| Gráficos em PDF | Matplotlib | Gráficos estáticos embarcados |
| Templates de PDF | Jinja2 | Único uso remanescente de template server-side |

### Infraestrutura e Deploy

| Componente | Tecnologia | Notas |
|---|---|---|
| Orquestração local | Docker Compose | PostgreSQL 16 + serviços auxiliares |
| Deploy | Railway | **2 serviços**: `sga-api` e `sga-web` + PostgreSQL managed |
| Storage (Fases 0-4) | Filesystem local | Volume baixo, sem dependência externa |
| Storage (Fase 5) | Supabase Storage (S3-compatible) via boto3 | Gratuito até 1 GB (ADR mantida da v3.4) |
| Monitoramento | Sentry | SDK do FastAPI + SDK do Next.js |
| CORS | `CORSMiddleware` do FastAPI | Origem restrita ao domínio do frontend |

### Testes e Qualidade

| Camada | Tecnologia | Quando |
|---|---|---|
| API — unit e integração | pytest + pytest-asyncio | Fases 0-5 (desde o início) |
| API — cliente HTTP de teste | `httpx.AsyncClient` + `ASGITransport` | Substitui o test client do Django |
| API — factories | polyfactory | Geração de dados de teste a partir dos modelos |
| API — banco de teste | PostgreSQL efêmero (testcontainers ou schema dedicado) | Triggers precisam de Postgres real |
| Web — unit e componente | Vitest + Testing Library | Fases 1-5 |
| E2E | **Playwright** | Apenas Fase 5 (10 testes críticos) — ADR-006 mantida |
| Linter/Formatter (Python) | Ruff | `ruff check .` e `ruff format .` |
| Linter/Formatter (TS) | ESLint + Prettier | `eslint .` e `prettier --check .` |
| Tipagem estática | mypy (Python) + `tsc --noEmit` (TS) | Obrigatório no CI |
| CI | GitHub Actions | Dois jobs paralelos: `api` e `web` |

---

## Os 4 Perfis de Acesso (RBAC)

Regra de negócio do CAAI — **inalterada pelo pivô**.

| Perfil | Acesso | Implementação v4.0 |
|---|---|---|
| **Coordenador** | Tudo (dados, relatórios, configuração, gestão de usuários, auditoria) | `require_role("COORDENADOR")` — repositório sem filtro |
| **Professor** | Suas turmas (notas, frequência, ocorrências, solicitação de troca) | Filtro: `ClassGroup.teachers.any(id=user.id)` |
| **Monitor** | Realizar chamada, histórico da sua turma | Filtro: `ClassGroup.monitors.any(id=user.id)` |
| **Aluno** | Consulta própria (notas, boletim, frequência, materiais, justificar faltas) | Filtro: `Student.user_id == user.id` |

Permissão padrão: **NEGAR**. A verificação ocorre no endpoint, por objeto — nunca apenas na
rota do frontend. Ver Princípio #4 e ADR-011.

---

## Regras de Negócio Preservadas do CAAI

O pivô arquitetural **não altera nenhuma regra de negócio**. As seguintes permanecem
integralmente válidas:

| Regra | Descrição | Implementação v4.0 |
|---|---|---|
| **Dupla chamada diária** | Uma chamada antes e outra depois do intervalo, para detectar evasão | `UNIQUE(student_id, date, period)` com `period ∈ {BEFORE_BREAK, AFTER_BREAK}` |
| **Correção sem duplicação** | O monitor pode corrigir um clique errado sem gerar registro duplicado | `INSERT ... ON CONFLICT DO UPDATE` (upsert) no repositório |
| **4 perfis de acesso** | Coordenador, Professor, Monitor, Aluno | Tabela acima |
| **Grade horária por CP-SAT** | Alocação otimizada de aulas em 3 salas | OR-Tools em worker separado (ADR-015) |
| **Auditoria e rastreabilidade** | Toda alteração registrada de forma imutável | Estratégia híbrida (ADR-012) |

---

## Fontes de Dados Externas

| Fonte | Formato | Uso |
|---|---|---|
| EvalBee | .xlsx | Simulados e gabaritos |
| Google Sheets | API v4 | Frequência e redações |
| Google Classroom | API REST | Notas e prazos |

Todas passam por validação Pandera antes de atingir o PostgreSQL (Princípio #3).

---

## O Que Foi REMOVIDO — v4.0 (pivô de 2026-09-02)

| Removido | Substituto | ADR |
|---|---|---|
| **Django 5** | FastAPI + Uvicorn | ADR-008 |
| **Django REST Framework** | FastAPI (roteamento e serialização nativos) | ADR-008 |
| **Django ORM** | SQLModel | ADR-009 |
| **Django Migrations** | Alembic | ADR-010 |
| **Django Admin** | Console em Next.js + SQLAdmin como ponte temporária | ADR-014 |
| **django-allauth** | Authlib no FastAPI | ADR-013 |
| **djangorestframework-simplejwt** | PyJWT + cookie httpOnly | ADR-013 |
| **Django Groups + queryset filters** | Dependências FastAPI + filtros no repositório | ADR-011 |
| **django-pghistory** | Listeners SQLAlchemy + triggers PL/pgSQL | ADR-012 |
| **django-crontab** | APScheduler (dev) + Railway Cron (prod) | ADR-013 da v3.4, adaptada |
| **Django Templates** | Next.js (App Router) | ADR-008 |
| **Bootstrap 5** | Tailwind CSS + shadcn/ui | ADR-008 |
| **HTMX** | React (estado e fetch nativos) | ADR-008 |
| **Alpine.js** (exceção da ADR-007) | React — a exceção deixou de ser necessária | ADR-007 obsoleta |
| **Plotly server-side** | Recharts consumindo JSON agregado da API | ADR-016 |
| **django-crispy-forms** | React Hook Form + Zod | ADR-008 |
| **django-tables2** | TanStack Table | ADR-008 |
| **drf-spectacular** | OpenAPI nativo do FastAPI | ADR-017 |
| **django-storages** | boto3 direto | ADR-008 |
| **pytest-django** | pytest + httpx AsyncClient | ADR-008 |
| **SQLite (dev)** | PostgreSQL 16 via Docker Compose | ADR-018 |

## O Que Continua REMOVIDO — herdado da v3.4

| Removido | Motivo | Situação após o pivô |
|---|---|---|
| **Celery + Redis** | Escala não justifica broker dedicado e worker separado | **Continua proibido.** O `BackgroundTasks` do FastAPI e o Railway Cron cobrem o necessário. A natureza assíncrona do FastAPI aumenta a tentação de reintroduzir Celery — resistir |
| **Prefect 2** | Orquestrador de ETL enterprise, desproporcional para ~90 alunos | Continua proibido. Scripts Typer bastam |
| **django-guardian** | Permissões object-level para 4 perfis determinísticos | Irrelevante (não há Django). O conceito equivalente — biblioteca de ACL por objeto — permanece desnecessário |
| **Metabase** | Ferramenta de BI separada | Continua proibido. Dashboards nativos em Recharts |
| **Chart.js** | — | Continua proibido. Recharts é a escolha única (ADR-016) |
| **Flutter (nesta versão)** | Fora do escopo da IC | Permanece fora do escopo entregável, mas a arquitetura v4.0 existe justamente para viabilizá-lo depois |

## O Que Voltou a Ser PERMITIDO

Duas tecnologias estavam explicitamente proibidas na v3.4 e retornam com o pivô. O registro
é obrigatório para rastreabilidade acadêmica:

| Tecnologia | Status v3.4 | Status v4.0 | Justificativa |
|---|---|---|---|
| **SQLAlchemy** (via SQLModel) | Proibido (ADR-001) | **Permitido e obrigatório** | Os quatro argumentos da ADR-001 dependiam de pghistory, allauth, DRF e Django Admin — todos eliminados pelo pivô. Ver ADR-009 |
| **Alembic** | Proibido (ADR-001) | **Permitido e obrigatório** | O argumento era "dois sistemas de migração concorrentes". Sem Django Migrations, o Alembic passa a ser o sistema único. Ver ADR-010 |
| **React / Next.js** | Removido do escopo (v3.4) | **Núcleo da camada de apresentação** | Ver ADR-008 |

---

## Referências

- `principios.md` — os 8 princípios que fundamentam estas escolhas
- `blueprint.md` — arquitetura em camadas
- `decisoes_arquiteturais.md` — ADR-001 a ADR-018
- `diretorios.md` — estrutura do monorepo
- `roadmap.md` — cronograma de implementação
