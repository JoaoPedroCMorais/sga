# Blueprint de Arquitetura — SGA v4.0 (API-First)

> Governança de Dados e Engenharia de Sistemas
> Versão: 4.0 | Atualizado em: 2026-09-02
> Substitui: `Cerebro/_arquivoV3_django/Foundation/blueprint_v3_4_revisado.md`

---

## Visão em Camadas

```
┌───────────────────────────────────────────────────────────────┐
│  06. CAMADA DE CLIENTES                                       │
│  Next.js 15 (App Router) + React 19 + TypeScript              │
│  Tailwind CSS + shadcn/ui | TanStack Query + Table            │
│  Recharts (dashboards) | React Hook Form + Zod                │
│  ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─   │
│  [Trabalho futuro: React Native / Flutter — mesma API]        │
├───────────────────────────────────────────────────────────────┤
│  05. CAMADA DE CONTRATO  ◄── NOVA NA v4.0                     │
│  OpenAPI 3.1 gerado pelo FastAPI (/openapi.json)              │
│  openapi-typescript → packages/api-types                      │
│  Versionamento de rota: /api/v1/                              │
│  Swagger UI (/docs) | ReDoc (/redoc)                          │
├───────────────────────────────────────────────────────────────┤
│  04. CAMADA DE APLICAÇÃO (FastAPI + Uvicorn)                  │
│  routers/ → dependências de autorização → services/           │
│                                        → repositories/        │
│  Authlib (OAuth2 Google) | PyJWT | SQLModel                   │
│  WeasyPrint + Matplotlib (geração de PDF)                     │
├───────────────────────────────────────────────────────────────┤
│  03. CAMADA DE PROCESSAMENTO (ETL e Otimização)               │
│  Pandas + openpyxl | Typer (scripts CLI)                      │
│  Railway Cron (prod) / APScheduler (dev)                      │
│  OR-Tools CP-SAT — executado FORA do event loop               │
├───────────────────────────────────────────────────────────────┤
│  02. CAMADA DE VALIDAÇÃO (Data Integrity)                     │
│  Pydantic v2 — fronteira HTTP                                 │
│  Pandera — fronteira ETL                                      │
│  Logging centralizado: rejeição rastreável (Sentry)           │
├───────────────────────────────────────────────────────────────┤
│  01. CAMADA DE EXTRAÇÃO (Ingestão)                            │
│  EvalBee (.xlsx) | Google Sheets (API v4)                     │
│  Google Classroom (API REST)                                  │
├───────────────────────────────────────────────────────────────┤
│  00. CAMADA DE PERSISTÊNCIA E AUDITORIA                       │
│  PostgreSQL 16 — SSOT (Railway em prod, Docker em dev)        │
│  Triggers PL/pgSQL → audit_log (append-only)                  │
│  Filesystem local (Fases 0-4) / Supabase S3 (Fase 5)          │
└───────────────────────────────────────────────────────────────┘
```

**Diferença estrutural em relação à v3.4:** o monolito tinha cinco camadas e a apresentação
era produzida pela própria camada de aplicação (Django Templates). A v4.0 tem seis camadas,
e a camada 05 (Contrato) é a fronteira formal entre servidor e clientes. É ela que permite
que a camada 06 seja substituída ou multiplicada sem tocar nas camadas 00-04 — o objetivo
declarado do pivô.

---

## 00. Camada de Persistência e Auditoria

| Componente | Tecnologia | Função |
|---|---|---|
| Banco (prod) | PostgreSQL 16 (Railway managed) | Single Source of Truth |
| Banco (dev) | PostgreSQL 16 (Docker Compose) | Paridade total com produção |
| Migrations | Alembic | Sistema único de evolução de schema |
| Auditoria (banco) | Triggers PL/pgSQL → `audit_log` | Rede de segurança imutável |
| Storage (Fases 0-4) | Filesystem local | Justificativas, atestados |
| Storage (Fase 5) | Supabase Storage (S3-compatible) via boto3 | Produção |

**Por que o SQLite foi aposentado.** A auditoria da v4.0 depende de triggers PL/pgSQL, que
não existem no SQLite. Manter SQLite em desenvolvimento criaria um ambiente onde a garantia
central do Princípio #5 simplesmente não roda — bugs de auditoria só apareceriam em
produção. Ver ADR-018.

---

## 01. Camada de Extração (Ingestão de Fontes)

| Fonte | Formato | Dados |
|---|---|---|
| EvalBee | .xlsx | Simulados, gabaritos, respostas dos alunos |
| Google Sheets | API v4 | Frequência manual, redações |
| Google Classroom | API REST | Notas, prazos, entregas |

Todas as fontes passam obrigatoriamente pela Camada 02 antes de atingir o banco.

---

## 02. Camada de Validação (Data Integrity)

A v4.0 tem **duas fronteiras de entrada**, e cada uma tem sua ferramenta:

| Fronteira | Ferramenta | Momento | Falha resulta em |
|---|---|---|---|
| HTTP | Pydantic v2 (via SQLModel) | Antes de o payload chegar ao router | `422 Unprocessable Entity` automático |
| ETL | Pandera (`pa.DataFrameSchema`) | Antes de o DataFrame ser processado | Pipeline interrompido + log no Sentry |

Nenhum dado inválido atinge o PostgreSQL. Nenhuma rejeição é silenciosa.

---

## 03. Camada de Processamento (ETL e Otimização)

| Componente | Função |
|---|---|
| Pandas + openpyxl | Transformação e normalização de planilhas complexas |
| Pandera | Validação pós-transformação |
| Typer | Scripts CLI (substituem os management commands do Django) |
| Railway Cron (prod) / APScheduler (dev) | Agendamento de extração e sincronização |
| SQLModel | Persistência via `session.add_all()` / `bulk_insert_mappings()` |
| OR-Tools (CP-SAT) | Solver de grade horária |

### Restrição crítica — trabalho bloqueante e o event loop

O Uvicorn executa um event loop assíncrono de thread única por worker. Uma operação
bloqueante e CPU-bound executada dentro de um endpoint `async def` **paralisa todas as
requisições daquele worker** até terminar.

No monolito Django/WSGI esse problema não existia: cada requisição ocupava um worker
próprio e síncrono. É um risco novo, introduzido pelo pivô.

Duas operações do SGA são bloqueantes e CPU-bound:

| Operação | Duração típica | Tratamento obrigatório |
|---|---|---|
| Solver CP-SAT (grade horária) | 10-60 s | `BackgroundTasks` + endpoint de consulta de status |
| Pipeline EvalBee (Pandas + WeasyPrint) | 5-120 s | `BackgroundTasks` ou script Typer via Cron |

Regra: nenhuma chamada a `solver.Solve()`, a Pandas sobre planilha inteira ou a WeasyPrint
ocorre diretamente no corpo de um endpoint `async def`. Ver ADR-015.

---

## 04. Camada de Aplicação (FastAPI)

### Fluxo de uma requisição

```
Requisição HTTP
      │
      ▼
CORSMiddleware ─────────────► origem permitida?
      │
      ▼
Dependência de autenticação ─► JWT válido no cookie httpOnly / header Bearer?
      │                        (retorna o usuário autenticado)
      ▼
Dependência de autorização ──► require_role("COORDENADOR", "PROFESSOR")
      │                        (403 se o perfil não consta)
      ▼
Router ──────────────────────► valida o payload (Pydantic) e monta o caso de uso
      │
      ▼
Service ─────────────────────► regra de negócio (não conhece HTTP)
      │
      ▼
Repository ──────────────────► APLICA O FILTRO POR VÍNCULO e executa a consulta
      │                        (404 se o objeto existe mas não pertence ao usuário)
      ▼
SQLModel / SQLAlchemy ───────► listener before_flush grava em audit_log
      │
      ▼
PostgreSQL ──────────────────► trigger PL/pgSQL grava em audit_log (rede de segurança)
      │
      ▼
response_model (Pydantic) ───► serialização + entrada no contrato OpenAPI
```

### Responsabilidade de cada camada de código

| Diretório | Responsabilidade | Nunca faz |
|---|---|---|
| `routers/` | Traduzir HTTP em chamada de caso de uso; declarar `response_model` | Conter regra de negócio ou consulta ao banco |
| `services/` | Regra de negócio; orquestração; solver; ETL; PDF | Importar objetos de request/response |
| `repositories/` | Consultas ao banco **com o filtro de permissão aplicado** | Retornar dados sem filtro por vínculo |
| `models/` | Tabelas (`table=True`) | Conter lógica de aplicação |
| `schemas/` | Contratos de entrada e saída (`table=False`) | Ser usados como tabela |
| `core/` | Configuração, segurança, dependências compartilhadas | Conhecer domínio acadêmico |

**Regra herdada da v3.4 e mantida:** `services/` nunca importa de `routers/`. A direção da
dependência é sempre router → service → repository.

### Padrão de autorização (substitui o `BaseFilteredView` da v3.4)

```python
# core/security.py
def require_role(*allowed: Role):
    def dependency(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed:
            raise HTTPException(status_code=403, detail="Acesso negado")
        return user
    return dependency


# repositories/student.py
async def list_students_for(session: AsyncSession, user: User) -> Sequence[Student]:
    """Aplica o filtro por vínculo. Permissão padrão: negar."""
    stmt = select(Student)

    if user.role == Role.COORDENADOR:
        pass                                              # vê tudo
    elif user.role == Role.PROFESSOR:
        stmt = stmt.join(ClassGroup).where(ClassGroup.teachers.any(id=user.id))
    elif user.role == Role.MONITOR:
        stmt = stmt.join(ClassGroup).where(ClassGroup.monitors.any(id=user.id))
    elif user.role == Role.ALUNO:
        stmt = stmt.where(Student.user_id == user.id)
    else:
        return []                                         # NEGAR por padrão

    return (await session.exec(stmt)).all()
```

O `require_role` protege a **rota**; o repositório protege o **objeto**. As duas camadas são
obrigatórias — a primeira sozinha não impede IDOR (Princípio #4).

---

## 05. Camada de Contrato (nova na v4.0)

```
apps/api/src/sga_api/models/    (SQLModel, Python)
            │
            ▼  FastAPI introspecta os response_model
    GET /openapi.json           (OpenAPI 3.1)
            │
            ▼  openapi-typescript
    packages/api-types/         (tipos TypeScript)
            │
            ▼  importado por
    apps/web/src/lib/api/       (client tipado + hooks TanStack Query)
```

| Garantia | Como é obtida |
|---|---|
| Frontend nunca lê um campo que o backend não expõe | `tsc --noEmit` quebra na compilação |
| Contrato não regride sem alarme | CI regenera os tipos e falha se divergirem do commit |
| Cliente mobile futuro não é quebrado por deploy | Versionamento em `/api/v1/` |
| Documentação nunca desatualiza | Swagger gerado do código, não escrito à mão |

Ver Princípio #8 e ADR-017.

---

## 06. Camada de Clientes

### Cliente web (escopo desta versão)

| Componente | Tecnologia | Função |
|---|---|---|
| Framework | Next.js 15 (App Router) | Roteamento, SSR/RSC, build |
| Estilo | Tailwind CSS + shadcn/ui | Design system utilitário, mobile-first |
| Estado de servidor | TanStack Query v5 | Cache, revalidação, optimistic updates |
| Tabelas | TanStack Table v8 | Base do `<DataTable />` genérico |
| Formulários | React Hook Form + Zod | Base do `<CrudForm />` genérico |
| Gráficos | Recharts | Dashboards a partir de JSON agregado da API |

### Os dois componentes que sustentam o console administrativo

A perda do Django Admin é o maior custo do pivô (ver `migracao_v3_para_v4.md`). A mitigação
arquitetural é não construir oito telas independentes, mas dois componentes genéricos dos
quais as telas são derivadas:

```
<DataTable />   TanStack Table + paginação, ordenação e busca server-side.
                Configurado por um objeto de definição de colunas por entidade.
                Equivale ao list_display / search_fields / list_filter do Django Admin.

<CrudForm />    React Hook Form + schema Zod derivado do OpenAPI.
                Renderiza os campos a partir do schema da entidade.
                Equivale ao ModelForm do Django Admin.
```

Com os dois prontos, cada nova entidade administrativa custa aproximadamente um dia de
trabalho (um arquivo de configuração de colunas e uma rota), e não uma semana. Ver ADR-014
e a Fase 1 do `roadmap.md`.

### Fluxo de interatividade (substitui o fluxo HTMX da v3.4)

```
[Navegador]
    │
    ├── Navegação ──────► Next.js App Router ──► RSC busca dados na API ──► HTML
    │
    └── Interação ──────► TanStack Query mutation ──► POST /api/v1/... ──► JSON
                                │
                                ├── optimistic update (UI responde antes da rede)
                                └── invalidate query (revalidação em segundo plano)
```

O `hx-post` + `hx-swap` da v3.4 é substituído por mutation com optimistic update. Para o
caso de uso mais sensível — o monitor fazendo chamada em 3G instável — o resultado é
superior: a interface responde imediatamente e a sincronização ocorre em segundo plano,
com rollback automático em caso de falha.

O polling `hx-trigger="every 5s"` do painel da coordenação é substituído por
`refetchInterval` do TanStack Query na Fase 2, com avaliação de Server-Sent Events como
evolução possível.

---

## Topologia de Implantação

```
                         ┌──────────────────────┐
   Navegador ──────────► │  sga-web (Railway)   │
   (e mobile futuro)     │  Next.js / Node      │
          │              └──────────┬───────────┘
          │                         │ (RSC / server actions)
          │                         ▼
          │              ┌──────────────────────┐
          └────────────► │  sga-api (Railway)   │
            /api/v1/*    │  FastAPI / Uvicorn   │
                         └──────────┬───────────┘
                                    │
                         ┌──────────▼───────────┐    ┌──────────────────┐
                         │ PostgreSQL 16        │    │ Supabase Storage │
                         │ (Railway managed)    │    │ (Fase 5)         │
                         └──────────────────────┘    └──────────────────┘

                         Sentry ◄── ambos os serviços
                         Railway Cron ──► scripts Typer no serviço sga-api
```

**Consequências operacionais da separação em dois serviços:**

| Aspecto | Cuidado exigido |
|---|---|
| CORS | Origem restrita ao domínio de `sga-web`; nunca `*` |
| Cookies | `SameSite=Lax` e `Secure`; domínio compartilhado ou proxy reverso |
| Variáveis de ambiente | Duplicadas em dois serviços; `NEXT_PUBLIC_API_URL` no web |
| Deploy | Ordem importa: migration → API → web |
| Observabilidade | Dois projetos no Sentry, correlacionados por trace id |

---

## Referências

- `stack.md` — pilha tecnológica canônica
- `principios.md` — os 8 princípios
- `decisoes_arquiteturais.md` — ADR-001 a ADR-018
- `diretorios.md` — mapeamento das camadas para pastas
