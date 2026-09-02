# Decisoes Arquiteturais (ADRs) — SGA v3.4

> Cada decisao e registrada com data, contexto, alternativas e justificativa.
> Formato inspirado nos ADRs (Architecture Decision Records) de projetos como Zulip e Wagtail.
> Atualizado em: 2026-05-17

---

## ADR-001: Django ORM em vez de SQLAlchemy

**Data**: 2026-05-17
**Status**: Aprovada
**Decisores**: Dev + Coordenador de IC

### Contexto

A versao anterior da arquitetura (v3.1 a v3.4 original) especificava SQLAlchemy como ORM para garantir o Principio #6 (Codigo Agnostico de Banco). A intencao era evitar SQL direto (raw queries).

### Problema

SQLAlchemy e incompativel com o ecossistema Django escolhido:

- **django-pghistory** registra mudancas via Django Migrations e Django signals. Nao detecta alteracoes feitas via SQLAlchemy.
- **django-allauth** define models (SocialAccount, EmailAddress) com Django ORM. Nao interopera com SQLAlchemy.
- **DRF ModelSerializer** espera Django Models. Serializar SQLAlchemy Models exige adaptadores manuais.
- **Django Admin** espera Django Models. SQLAlchemy Models nao aparecem no Admin.
- **Django Migrations e Alembic** sao dois sistemas de migracao de schema concorrentes. Mante-los sincronizados e fonte garantida de bugs.

Nenhum projeto Django de sucesso conhecido (Wagtail, Zulip, Saleor, Taiga, Django Oscar) usa SQLAlchemy em paralelo com Django ORM.

### Alternativas Consideradas

| Opcao | Pros | Contras |
|---|---|---|
| SQLAlchemy + Alembic (status quo) | ORM poderoso, expressivo | Incompativel com stack Django; dois ORMs, duas migracoes |
| Django ORM exclusivo | Compativel com toda a stack; zero config extra; built-in | Menos expressivo que SQLAlchemy para queries complexas (mitigavel com `annotate`, `Subquery`, `F()`) |
| Abandonar Django, usar Flask + SQLAlchemy | SQLAlchemy nativo | Perde TODO o ecossistema (allauth, pghistory, Admin, DRF, etc.) |

### Decisao

**Usar Django ORM exclusivamente.** Reescrever Principio #6:

> "Codigo Agnostico de Banco — Django ORM, nunca raw SQL"

O Django ORM ja e database-agnostic (suporta PostgreSQL, MySQL, SQLite, Oracle). O principio original esta preservado; o meio de implementacao mudou.

### Consequencias

- Remover SQLAlchemy e Alembic das dependencias
- Todas as queries passam pelo Django ORM
- Migrations gerenciadas exclusivamente por `python manage.py makemigrations/migrate`
- Para queries complexas: usar `annotate()`, `Subquery()`, `F()`, `Q()`, `Window()` — nao raw SQL

---

## ADR-002: Django Groups em vez de django-guardian

**Data**: 2026-05-17
**Status**: Aprovada (revisavel na Fase 2)
**Decisores**: Dev + Coordenador de IC

### Contexto

O SGA tem 4 perfis fixos de acesso (Coordenador, Professor, Monitor, Aluno). A versao original especificava django-guardian para permissoes object-level.

### Problema

django-guardian brilha quando permissoes sao atribuidas por objeto individual (ex: "Prof. X pode ver a Turma Y especifica"). No SGA:

- **Coordenador** ve tudo — nao precisa de permissao por objeto
- **Professor** ve todas as turmas onde leciona — determinado pelo vinculo `ClassGroup.teachers`, nao por permissao atribuida
- **Monitor** ve a turma onde faz chamada — determinado pelo vinculo `ClassGroup.monitors`
- **Aluno** ve apenas seus proprios dados — filtro `student__user=request.user`

Em todos os casos, o acesso e determinado pelo **vinculo no model**, nao por uma permissao atribuida separadamente. django-guardian adicionaria uma camada de indireção desnecessaria.

### Alternativas Consideradas

| Opcao | Pros | Contras |
|---|---|---|
| django-guardian (status quo) | Flexivel, granular | Overhead para 4 perfis fixos; mais uma tabela de permissoes; curva de aprendizado |
| Django Groups + queryset filters | Simples, nativo, zero dependencia extra | Menos flexivel se surgir caso de permissao ad-hoc |
| Custom permission backend | Maximo controle | Mais codigo para manter |

### Decisao

**Usar Django Groups + filtros no queryset.** Padrao:

```python
def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='coordenador').exists():
        return self.model.objects.all()
    if user.groups.filter(name='professor').exists():
        return self.model.objects.filter(class_group__teachers=user)
    # ... etc
    return self.model.objects.none()
```

### Clausula de Revisao

Se durante a Fase 2-3 surgir um caso concreto onde permissao por objeto individual e necessaria (ex: "Prof. X pode ver ESTA turma mas nao AQUELA, mesmo lecionando em ambas"), reavaliar a inclusao de django-guardian pontualmente no app afetado.

---

## ADR-003: Filesystem Local (dev) + Supabase Storage S3 (prod)

**Data**: 2026-05-17
**Status**: Aprovada
**Decisores**: Dev + Coordenador de IC

### Contexto

O blueprint v3.4 original especificava Supabase Storage para todas as fases. A analise arquitetural identificou que nas fases iniciais o filesystem local basta, mas o coordenador de IC orientou manter Supabase Storage para producao.

### Decisao

**Fases 1-4**: Filesystem local (`media/`) servido por WhiteNoise ou Django em dev. Zero config extra. Acelera o MVP sem dependencia de servico externo.

**Fase 5 (producao)**: Supabase Storage via endpoint S3-compatible + `django-storages`. Motivos:
- Supabase agora oferece endpoint S3-compatible, entao `django-storages` funciona nativamente
- Migracao trivial: mudar `DEFAULT_FILE_STORAGE` no `production.py`
- Alinhamento com orientacao do coordenador de IC
- Gratuito ate 1GB (suficiente para o volume do SGA)

---

## ADR-004: django-crontab + Railway Cron Jobs em vez de Celery

**Data**: 2026-05-17
**Status**: Aprovada

### Contexto

Versoes anteriores especificavam Celery + Redis para tasks assincronas. A v3.4 simplificou para django-crontab.

### Problema

Celery + Redis exige:
- Servidor Redis rodando continuamente (~$5/mes no Railway)
- Worker Celery rodando como processo separado
- Configuracao de broker, result backend, serializer
- Debugging de tasks distribuidas e muito mais complexo que codigo sincrono

Para a escala do SGA (~90 alunos), nenhuma task justifica essa complexidade.

### Decisao

- **Dev local**: django-crontab para agendamento
- **Producao (Railway)**: Railway Cron Jobs executando management commands Django
- **Se surgir necessidade de task async com feedback** (ex: barra de progresso no upload de simulado): avaliar Django-Q2 (usa PostgreSQL como broker, sem Redis)

### Consequencias

- Nao usar Redis em nenhuma fase
- Pipeline EvalBee roda como management command: `python manage.py process_evalbee <arquivo.xlsx>`
- Sync Classroom roda via cron: `python manage.py sync_classroom` (agendado diariamente)

---

## ADR-005: Plotly em vez de Chart.js

**Data**: 2026-05-17 (decisao herdada da v3.4 original)
**Status**: Aprovada

### Contexto

Versoes anteriores usavam Chart.js (JavaScript) ou Metabase (ferramenta BI separada). A v3.4 consolidou em Plotly.

### Decisao

**Plotly** — graficos gerados 100% no backend (Python), sem JavaScript de charting. Os graficos sao renderizados como HTML/JSON e injetados na pagina via HTMX.

### Motivos

- Dev nao precisa escrever JavaScript para graficos
- Plotly gera graficos interativos (zoom, hover, filtro) nativamente
- Consistencia: mesmo ecossistema Python do restante do projeto
- Eliminacao de Metabase como dependencia separada

---

## ADR-006: Playwright Apenas na Fase 5

**Data**: 2026-05-17
**Status**: Aprovada

### Contexto

O roadmap menciona pytest-django + Playwright para testes.

### Decisao

- **Fases 1-4**: Apenas pytest-django (testes de model, view, API, permissao)
- **Fase 5**: Adicionar Playwright para 10 testes E2E criticos

### Motivos

- Testes E2E em frontend instavel (Fases 1-3) quebram constantemente e geram retrabalho
- pytest-django cobre model layer, permissions, e API — que e onde a maioria dos bugs vive
- Playwright tem curva de aprendizado propria (browsers, selectors, waits)
- O roadmap v3.4 ja previa "10 testes E2E criticos" na Fase 5 — alinhado
