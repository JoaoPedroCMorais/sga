# DIRETRIZES DE DESENVOLVIMENTO DO SGA v3.4 REVISADA

> Este arquivo e a fonte unica de verdade para decisoes tecnicas do projeto.
> Documentacao detalhada em: `SGA - Doc/Documentacao/v3.4 Revisada/`

---

## 1. Regras de Comportamento (Cinto de Seguranca)

- **NUNCA** apague arquivos ou rode `migrate` sem me pedir permissao antes.
- Se eu pedir algo que fira os principios do Django, me avise e sugira a melhor pratica.
- Antes de refatorar, faca perguntas de esclarecimento se tiver menos de 95% de certeza.
- Responda sempre em **portugues brasileiro**.
- Codigo deve ser **completo e funcional** — nunca use `...` ou `# resto do codigo aqui`.

---

## 2. Stack Definitiva

### Backend
- **Framework:** Django 5 + DRF (Django REST Framework)
- **ORM:** Django ORM exclusivamente. **NAO USE SQLAlchemy.** Nunca raw SQL.
- **Banco (dev):** SQLite
- **Banco (prod):** PostgreSQL 15+ (Railway)
- **Agendamento:** django-crontab
- **Auditoria:** django-pghistory (triggers PostgreSQL, logs imutaveis)

### Auth e Permissoes
- **Auth:** django-allauth (Google OAuth2, restrito ao dominio institucional)
- **Permissoes:** Django Groups + queryset filters. **NAO USE django-guardian.**
- **4 perfis:** Coordenador, Professor, Monitor, Aluno
- **Padrao de acesso: NEGAR.** Se nao foi concedido, esta negado.

### Frontend
- **Templates:** Django Templates (server-side rendering). **Zero SPAs (React/Vue).**
- **CSS:** Bootstrap 5 (mobile-first)
- **Interatividade:** HTMX (atualizacoes parciais sem JS customizado)
- **Graficos/BI:** Plotly (100% Python, renderizado no backend)
- **Formularios:** django-crispy-forms + crispy-bootstrap5
- **Tabelas:** django-tables2

### ETL e Dados
- **Processamento:** Pandas + openpyxl
- **Validacao:** Pandera (schemas obrigatorios antes de processar)
- **Otimizacao:** Google OR-Tools (CP-SAT) para grade horaria

### Infra e Deploy
- **Deploy:** Railway (PostgreSQL managed)
- **Storage (dev):** Filesystem local
- **Storage (prod):** Supabase Storage (S3-compatible) + django-storages
- **Monitoramento:** Sentry
- **PDF:** WeasyPrint + Matplotlib

### Testes e Qualidade
- **Testes:** pytest-django (Playwright apenas na Fase 5 para E2E)
- **Linter:** Ruff (`ruff check .` e `ruff format .`)
- **Docs API:** drf-spectacular (Swagger/OpenAPI)

---

## 3. Padroes de Codigo

- **Typing:** Type Hints em todas as funcoes (`def get_student(student_id: int) -> Student:`).
- **N+1 Queries:** ESTRITAMENTE PROIBIDO. Sempre use `select_related` e `prefetch_related` em listagens.
- **Linter:** O codigo deve passar em `ruff check .` e `ruff format .`.
- **Testes:** pytest-django. Cada feature critica tem teste correspondente.
- **Imports:** stdlib → third-party → local. Organizados e sem imports nao utilizados.
- **Docstrings:** Google style em funcoes publicas.
- **Admin:** Contagens em `list_display` devem usar `annotate()`, nunca `obj.related.count()`.

---

## 4. Permissoes (RBAC sem django-guardian)

Acesso padrao e NEGAR. Filtrar QuerySets pelo perfil do usuario:

```python
# Padrao para TODAS as views
class BaseFilteredView(LoginRequiredMixin, View):
    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name='coordenador').exists():
            return self.model.objects.all()
        if user.groups.filter(name='professor').exists():
            return self.model.objects.filter(class_group__teachers=user)
        if user.groups.filter(name='monitor').exists():
            return self.model.objects.filter(class_group__monitors=user)
        if user.groups.filter(name='aluno').exists():
            return self.model.objects.filter(student__user=user)
        return self.model.objects.none()
```

---

## 5. 7 Principios Inviolaveis

1. **SSOT** — Todo dado oficial no PostgreSQL.
2. **Simplicidade Primeiro** — Solucao mais simples que funcione.
3. **Validacao na Entrada** — Pandera antes de processar.
4. **Permissao Padrao e Negar** — Acesso explicito.
5. **Auditoria Total** — Quem, quando, o que (imutavel via django-pghistory).
6. **Codigo Agnostico de Banco** — Django ORM, nunca raw SQL.
7. **Entregue Valor Cedo** — Cada fase entrega algo usavel.

---

## 6. Estrutura de Apps

```
apps/
├── users/          # User, Profile, RBAC, django-allauth
├── academic/       # Student, Teacher, Subject, ClassGroup
├── schedules/      # Grade horaria (CP-SAT em services/solver.py)
├── attendance/     # Chamada, justificativas
├── assessments/    # Simulados, notas, dashboards Plotly (services/)
└── audit/          # Logs imutaveis django-pghistory (READ-ONLY)
```

Logica de negocio complexa vai em `services/`, NAO em views ou models.
Services nunca importam de views. Views importam de services.

---

## 7. O Que NAO Usar (decisoes documentadas em ADRs)

| NAO usar | Usar em vez disso | Motivo |
|---|---|---|
| SQLAlchemy / Alembic | Django ORM / Django Migrations | Incompativel com pghistory, allauth, DRF, Admin |
| django-guardian | Django Groups + queryset filters | 4 perfis fixos, vinculos deterministicos |
| Supabase Storage (Fases 1-4) | Filesystem local (dev) / Supabase Storage S3 (prod, Fase 5) | Filesystem local acelera MVP; Supabase S3 em producao por orientacao do coordenador |
| Celery + Redis | django-crontab / Railway Cron Jobs | Escala nao justifica |
| Alpine.js | HTMX puro | Simplicidade |
| Chart.js / Metabase | Plotly (100% Python) | Stack unificada |
| Raw SQL | Django ORM (annotate, Subquery, F, Q, Window) | Principio #6 |
