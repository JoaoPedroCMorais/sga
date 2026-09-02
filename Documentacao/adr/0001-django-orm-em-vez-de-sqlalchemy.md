---
adr: 001
title: "ADR-001 — Django ORM em vez de SQLAlchemy"
status: Substituída
substituida_por: ADR-009
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - orm
  - django
---

# ADR-001 — Django ORM em vez de SQLAlchemy

> ### 🔄 Status após o pivô v4.0
> ****Substituída pela ADR-009** (2026-09-02)**
>
> O pivô arquitetural eliminou as quatro dependências que fundamentavam esta decisão (django-pghistory, django-allauth, DRF e Django Admin). Sem elas, os argumentos de incompatibilidade deixam de se aplicar. O SQLAlchemy retorna ao projeto sob a forma de SQLModel. **Esta ADR não estava incorreta**: ela era válida no contexto em que foi tomada, e o contexto mudou por decisão do Coordenador de IC.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-17
**Status**: Aprovada
**Decisores**: Dev + Coordenador de IC

## Contexto

A versao anterior da arquitetura (v3.1 a v3.4 original) especificava SQLAlchemy como ORM para garantir o Principio #6 (Codigo Agnostico de Banco). A intencao era evitar SQL direto (raw queries).

## Problema

SQLAlchemy e incompativel com o ecossistema Django escolhido:

- **django-pghistory** registra mudancas via Django Migrations e Django signals. Nao detecta alteracoes feitas via SQLAlchemy.
- **django-allauth** define models (SocialAccount, EmailAddress) com Django ORM. Nao interopera com SQLAlchemy.
- **DRF ModelSerializer** espera Django Models. Serializar SQLAlchemy Models exige adaptadores manuais.
- **Django Admin** espera Django Models. SQLAlchemy Models nao aparecem no Admin.
- **Django Migrations e Alembic** sao dois sistemas de migracao de schema concorrentes. Mante-los sincronizados e fonte garantida de bugs.

Nenhum projeto Django de sucesso conhecido (Wagtail, Zulip, Saleor, Taiga, Django Oscar) usa SQLAlchemy em paralelo com Django ORM.

## Alternativas Consideradas

| Opcao | Pros | Contras |
|---|---|---|
| SQLAlchemy + Alembic (status quo) | ORM poderoso, expressivo | Incompativel com stack Django; dois ORMs, duas migracoes |
| Django ORM exclusivo | Compativel com toda a stack; zero config extra; built-in | Menos expressivo que SQLAlchemy para queries complexas (mitigavel com `annotate`, `Subquery`, `F()`) |
| Abandonar Django, usar Flask + SQLAlchemy | SQLAlchemy nativo | Perde TODO o ecossistema (allauth, pghistory, Admin, DRF, etc.) |

## Decisao

**Usar Django ORM exclusivamente.** Reescrever Principio #6:

> "Codigo Agnostico de Banco — Django ORM, nunca raw SQL"

O Django ORM ja e database-agnostic (suporta PostgreSQL, MySQL, SQLite, Oracle). O principio original esta preservado; o meio de implementacao mudou.

## Consequencias

- Remover SQLAlchemy e Alembic das dependencias
- Todas as queries passam pelo Django ORM
- Migrations gerenciadas exclusivamente por `python manage.py makemigrations/migrate`
- Para queries complexas: usar `annotate()`, `Subquery()`, `F()`, `Q()`, `Window()` — nao raw SQL

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| — | [Índice de ADRs](./README.md) | [ADR-002](./0002-django-groups-em-vez-de-guardian.md) |
