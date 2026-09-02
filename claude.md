# DIRETRIZES DE DESENVOLVIMENTO — SGA v4.0 (API-First)

> Fonte única de verdade para decisões técnicas do projeto.
> Documentação detalhada em `Documentacao/`.
> Versão: 4.0 | Atualizado em: 2026-09-02

---

## 1. Regras de Comportamento (Cinto de Segurança)

- **NUNCA** apague arquivos, rode `alembic upgrade` contra produção ou execute `docker compose down -v` sem me pedir permissão antes.
- Se eu pedir algo que fira os princípios do projeto ou uma ADR vigente, **me avise antes de executar** e cite a ADR.
- Antes de refatorar, faça perguntas de esclarecimento se tiver menos de 95% de certeza.
- Responda sempre em **português brasileiro**.
- Código deve ser **completo e funcional** — nunca use `...` ou `# resto do código aqui`.
- Ao propor uma dependência nova, justifique contra o Princípio #2 (Simplicidade Primeiro).

---

## 2. Stack Definitiva

Documento canônico: `Documentacao/stack.md`. Resumo operacional:

### Backend (`apps/api/`)
- **Framework:** FastAPI + Uvicorn (ASGI)
- **ORM e validação:** SQLModel (SQLAlchemy 2.0 + Pydantic v2). **NÃO use Django ORM.**
- **Migrations:** Alembic — sistema único
- **Banco (dev e prod):** PostgreSQL 16. **SQLite foi aposentado** (ADR-018)
- **Pacotes:** uv
- **Agendamento:** APScheduler (dev) / Railway Cron (prod)
- **PDF:** WeasyPrint + Matplotlib + Jinja2
- **CLI:** Typer

### Autenticação e Permissões
- **Authorization Server:** FastAPI + Authlib (OAuth2 Google, domínio institucional). **Único emissor de credenciais** (ADR-013)
- **Tokens:** JWT 15 min + refresh 7 dias, em cookie `httpOnly` no web e `Bearer` no mobile
- **RBAC:** `require_role()` na rota **+** filtro por vínculo no repositório (ADR-011)
- **4 perfis:** Coordenador, Professor, Monitor, Aluno
- **Padrão de acesso: NEGAR**
- **Auditoria:** listeners SQLAlchemy + triggers PL/pgSQL (ADR-012)

### Frontend (`apps/web/`)
- **Framework:** Next.js 15 (App Router) + React 19 + TypeScript `strict`
- **CSS:** Tailwind CSS + shadcn/ui
- **Estado de servidor:** TanStack Query v5
- **Tabelas:** TanStack Table v8 | **Formulários:** React Hook Form + Zod
- **Gráficos:** Recharts (ADR-016). **NÃO use Chart.js nem Plotly**
- **Pacotes:** pnpm (workspaces)

### Contrato
- OpenAPI 3.1 nativo do FastAPI → `openapi-typescript` → `packages/api-types`
- **Nenhum tipo da API é escrito à mão em TypeScript** (Princípio #8, ADR-017)

### Testes e Qualidade
- **API:** pytest + pytest-asyncio + `httpx.AsyncClient` + polyfactory, contra PostgreSQL real
- **Web:** Vitest + Testing Library | **E2E:** Playwright apenas na Fase 5 (ADR-006)
- **Linters:** Ruff (Python) | ESLint + Prettier (TS)
- **Tipos:** mypy | `tsc --noEmit`

---

## 3. Padrões de Código

### Python
- **Type hints obrigatórios** em todas as funções.
- **N+1 queries: ESTRITAMENTE PROIBIDO.** Use `selectinload()` / `joinedload()` em listagens.
- Todo endpoint declara **`response_model` explícito**. Sem isso, o contrato fica vazio e o code review rejeita.
- Modelos `table=True` **nunca** são usados como `response_model` — sempre existe um schema `...Read`.
- Imports: stdlib → terceiros → local. Sem imports não utilizados.
- Docstrings estilo Google em funções públicas.
- Nada de `print()` — use o logger configurado.

### TypeScript
- `strict: true`. **`any` é proibido**; use `unknown` e refine.
- Componentes de servidor por padrão; `"use client"` apenas quando houver estado ou evento.
- Toda chamada à API passa por `lib/api/` e usa os tipos de `packages/api-types`.
- Nada de `fetch` solto em componente — use os hooks do TanStack Query.
- Nenhuma regra de negócio no cliente. O frontend não é mecanismo de segurança.

---

## 4. Arquitetura de Camadas (backend)

```
routers/  →  services/  →  repositories/  →  models/
```

| Regra | Obrigatoriedade |
|---|---|
| `services/` nunca importa de `routers/` | Absoluta |
| `services/` nunca recebe `Request`/`Response` | Absoluta |
| `routers/` nunca executa `select()` direto | Absoluta |
| `repositories/` sempre recebe o usuário autenticado | Absoluta — é onde o Princípio #4 vive |

---

## 5. Permissões — o padrão obrigatório

```python
# Camada 1 — a rota protege o endpoint
@router.get("/students", response_model=list[StudentRead])
async def list_students(
    user: User = Depends(require_role(Role.COORDENADOR, Role.PROFESSOR, Role.MONITOR)),
    session: AsyncSession = Depends(get_session),
):
    return await student_repo.list_for(session, user)


# Camada 2 — o repositório protege o objeto
async def list_for(session: AsyncSession, user: User) -> Sequence[Student]:
    stmt = select(Student)
    if user.role == Role.COORDENADOR:
        pass
    elif user.role == Role.PROFESSOR:
        stmt = stmt.join(ClassGroup).where(ClassGroup.teachers.any(id=user.id))
    elif user.role == Role.MONITOR:
        stmt = stmt.join(ClassGroup).where(ClassGroup.monitors.any(id=user.id))
    elif user.role == Role.ALUNO:
        stmt = stmt.where(Student.user_id == user.id)
    else:
        return []                      # NEGAR por padrão
    return (await session.exec(stmt)).all()
```

**As duas camadas são obrigatórias.** A primeira sozinha não impede IDOR.
Consulta de objeto individual que não pertence ao usuário retorna **404**, não 403 — um 403
confirmaria a existência do recurso.

---

## 6. Os 8 Princípios Invioláveis

1. **SSOT** — Todo dado oficial no PostgreSQL. O frontend não é fonte de verdade.
2. **Simplicidade Primeiro** — A solução mais simples que funcione.
3. **Validação na Entrada** — Pydantic na fronteira HTTP, Pandera na fronteira ETL.
4. **Permissão Padrão é Negar** — Acesso explícito, verificado por objeto.
5. **Auditoria Total** — Quem, quando, o quê — imutável, em duas camadas.
6. **Código Agnóstico de Banco** — SQLModel/SQLAlchemy Core, nunca raw SQL em tempo de requisição.
7. **Entregue Valor Cedo** — Cada fase entrega algo usável.
8. **O Contrato de API é a Fronteira** — OpenAPI gera os tipos do frontend.

Detalhamento em `Documentacao/principios.md`.

---

## 7. Regras de Negócio do CAAI (não negociáveis)

| Regra | Implementação |
|---|---|
| **Dupla chamada diária** | `UNIQUE(student_id, date, period)`, `period ∈ {BEFORE_BREAK, AFTER_BREAK}` |
| **Correção sem duplicação** | `INSERT ... ON CONFLICT DO UPDATE` |
| **4 perfis de acesso** | Coordenador, Professor, Monitor, Aluno |
| **Grade horária por CP-SAT** | OR-Tools, executado fora do event loop |
| **Auditoria imutável** | `audit_log` append-only, sem endpoint de UPDATE ou DELETE |

---

## 8. Trabalho Bloqueante — regra crítica

**Nunca** chame `solver.Solve()`, Pandas sobre planilha inteira ou WeasyPrint dentro do corpo
de um endpoint `async def`. Isso trava o event loop e paralisa todas as requisições do worker.

Padrão obrigatório: `BackgroundTasks` + registro em `job` + resposta **202 Accepted** com
`job_id` + endpoint de consulta de status. Ver ADR-015.

---

## 9. O Que NÃO Usar

| NÃO usar | Usar em vez disso | Motivo |
|---|---|---|
| Django, DRF, Django ORM | FastAPI + SQLModel | ADR-008, ADR-009 |
| SQLite | PostgreSQL 16 via Docker | ADR-018 — triggers de auditoria |
| Raw SQL em tempo de requisição | SQLModel / SQLAlchemy Core | Princípio #6 (exceção: triggers em migration) |
| Celery + Redis | `BackgroundTasks` + tabela `job` + Railway Cron | ADR-004, ADR-015 |
| Chart.js, Plotly | Recharts | ADR-016 |
| NextAuth autenticando direto no Google | FastAPI como Authorization Server | ADR-013 |
| Tipos TS escritos à mão para a API | `openapi-typescript` | ADR-017, Princípio #8 |
| `any` no TypeScript | `unknown` + refinamento | Padrão de código |
| Modelo `table=True` como `response_model` | Schema `...Read` | Vazamento de campo sensível |
| Alpine.js, HTMX, Bootstrap | React + Tailwind | ADR-008; ADR-007 obsoleta |

---

## 10. Andaimes Temporários

| Item | Remoção prevista | ADR |
|---|---|---|
| `apps/api/src/sga_api/admin/` (SQLAdmin) | **Fim da Fase 2** | ADR-014 |

Estender o prazo exige nova ADR. Não pode ocorrer por omissão.

---

## 11. Documentação do Projeto

`Documentacao/` é a **fonte única de verdade documental**. O vault Obsidian (`Cerebro/`)
apenas lê de lá; nunca mantém cópia paralela.

| Arquivo | Conteúdo |
|---|---|
| `stack.md` | Pilha tecnológica canônica |
| `principios.md` | Os 8 princípios |
| `blueprint.md` | Arquitetura em camadas |
| `decisoes_arquiteturais.md` | ADR-001 a ADR-018 |
| `roadmap.md` | Cronograma, entregas e riscos |
| `diretorios.md` | Estrutura do monorepo |
| `migracao_v3_para_v4.md` | Registro do pivô arquitetural |
| `_arquivo_v3_4/` | Documentação congelada da era Django |
