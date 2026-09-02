# Roadmap Estrategico — SGA v3.4 Revisado

> Duracao Total Estimada: 9 a 11 meses | Execucao Solo/Lean
> Atualizado em: 2026-05-17

---

## Visao Geral das Fases

```
Fase 1 ████████████░░░░░░░░  Meses 1-3    Fundacao, Auth, Qualidade
Fase 2 ░░░░████████░░░░░░░░  Meses 4-5    Portal do Aluno, Chamada
Fase 3 ░░░░░░░░████░░░░░░░░  Mes 6        Grade Horaria, Voluntarios
Fase 4 ░░░░░░░░░░░░████████  Meses 7-8    Simulados, Dashboards
Fase 5 ░░░░░░░░░░░░░░░░████  Meses 9-10   Automacao, Deploy Producao
```

---

## Fase 1 — Fundacao, Auth e Qualidade (Meses 1 a 3)

### Walking Skeleton (Semanas 1-2)

**Objetivo: Django rodando com models basicos e Admin funcional.**

- `django-admin startproject config .`
- Criar 6 apps: `users`, `academic`, `schedules`, `attendance`, `assessments`, `audit`
- Models fundacionais com Django ORM: `Student`, `Teacher`, `Subject`, `ClassGroup`
- Django Admin configurado com `list_display`, `search_fields`, `list_filter`
- pytest-django: 10 testes nos models (validacoes, relacoes, constraints)
- `.gitignore`, `requirements.txt`, `pyproject.toml` (ruff config)
- Settings split: `config/settings/base.py`, `local.py`, `production.py`

**Entrega**: Coordenacao pode cadastrar alunos, professores e turmas pelo Django Admin.

### Auth e RBAC (Semanas 3-4)

- django-allauth com Google OAuth2 restrito ao dominio institucional
- Django Groups criados: `coordenador`, `professor`, `monitor`, `aluno`
- Mixin `BaseFilteredView` para filtrar querysets por grupo
- Testes de permissao: "professor so ve suas turmas", "aluno so ve seus dados"

**Entrega**: Login funcional com Google, perfis atribuidos automaticamente.

### Auditoria e Qualidade (Semanas 5-8)

- django-pghistory nos models core (`Student`, `ClassGroup`, `Attendance`)
- App `audit/` com views read-only para consulta de historico
- CI basico: GitHub Actions rodando `ruff check` + `pytest`
- Coverage target: >50% nos models

**Entrega**: Toda alteracao de dados e rastreavel. CI verde no GitHub.

### Checkpoint Go/No-Go

**Se ultrapassar 3.5 meses**: pausar, reavaliar escopo, entregar o que estiver pronto. Nao acumular divida tecnica para "compensar depois".

---

## Fase 2 — Portal do Aluno e Chamada Mobile-First (Meses 4 a 5)

### Frontend Basico (Semanas 9-10)

- `templates/base.html` com Bootstrap 5 (navbar, sidebar, responsivo)
- `templates/partials/` para fragmentos HTMX
- Ficha individual do aluno (dados pessoais, frequencia, notas)
- View responsiva que funciona em desktop e mobile

### Sistema de Chamada (Semanas 11-14)

- Interface mobile-first para monitores: botoes grandes, touch-friendly
- HTMX `hx-post` para salvar presenca sem reload
- HTMX polling (`hx-trigger="every 5s"`) para coordenacao acompanhar em tempo real
- Fluxo de justificativa de faltas com upload de arquivo (filesystem local)

**Entrega**: Monitores fazem chamada no celular. Coordenacao acompanha ao vivo. Alunos consultam sua ficha.

---

## Fase 3 — Grade Horaria e Voluntarios (Mes 6)

### Interface de Disponibilidade

- Formulario online para professores informarem disponibilidade
- Armazenamento no banco via Django ORM (mesmo schema do solver existente)

### Gerador de Grade

- Modo manual: coordenacao aloca aulas via drag-and-drop (HTMX)
- Modo solver: CP-SAT (OR-Tools) isolado em `apps/schedules/services/solver.py`
- Solver roda sincrono para grades pequenas (3 salas, 5 dias, 4 periodos)
- Se solver demorar >30s: considerar management command + Railway Cron Job

### Sugestao de Trocas

- Algoritmo simples: detecta conflitos e sugere permutacoes validas
- Interface para professor solicitar troca, coordenacao aprovar

**Entrega**: Grade horaria gerada automaticamente. Professores informam disponibilidade online.

---

## Fase 4 — Simulados e Dashboards Nativos (Meses 7 a 8)

### Pipeline EvalBee

- Upload de .xlsx via formulario Django (django-crispy-forms)
- Validacao Pandera do schema EvalBee
- Processamento com Pandas (adaptar `gerar_estatisticas.py` existente)
- Persistencia de resultados via Django ORM (`bulk_create`)
- Se processamento >30s: executar como management command async (Django-Q2 ou Railway Cron)

### Boletins PDF

- WeasyPrint: HTML/CSS para PDF do boletim individual
- Matplotlib: graficos estatisticos embarcados no PDF
- Download individual ou em lote (ZIP)

### Dashboards BI

- Plotly: graficos de % acerto, comparativo entre salas, evolucao temporal
- Renderizados no backend e injetados via HTMX (`hx-get="/dashboard/chart/1/"`)
- Filtros interativos (por sala, por simulado, por periodo) via HTMX

**Entrega**: Upload de simulado com processamento automatico. Dashboards interativos. Boletins PDF.

---

## Fase 5 — Automacao Final e Deploy Producao (Meses 9 a 10)

### Sincronizacao e Automacao

- Sincronizacao com Google Classroom via django-crontab (diaria)
- E-mails agendados (notificacoes de simulado, alertas de frequencia)
- Para e-mail: SMTP nativo do Django (Fase 1-4) ou SendGrid (Fase 5 se volume justificar)

### Storage em Producao

- Migrar uploads de filesystem local para Supabase Storage (endpoint S3-compatible via django-storages)
- Configurar `DEFAULT_FILE_STORAGE` no `production.py` apontando para o bucket Supabase

### Qualidade e Seguranca

- pytest-django: coverage >70%
- Playwright: 10 testes E2E criticos (login, chamada, upload simulado, dashboard, boletim)
- Checklist OWASP Top 10 (CSRF, XSS, SQL injection, auth bypass)
- Review de seguranca com coordenador de IC

### Deploy Definitivo

- Railway: PostgreSQL managed + deploy automatico via GitHub push
- Sentry: monitoramento de erros em producao
- Treinamento da equipe CAAI (coordenacao, professores, monitores)

**Entrega**: Sistema em producao, equipe treinada, monitoramento ativo.

---

## Metricas de Sucesso por Fase

| Fase | Metrica | Target |
|---|---|---|
| 1 | Models testados + Admin funcional | >50% coverage, CI verde |
| 2 | Chamada mobile funcional | <3 cliques para registrar presenca |
| 3 | Grade gerada pelo solver | Solucao otima em <60s |
| 4 | Dashboard com dados reais | Upload→Dashboard em <2min |
| 5 | Sistema em producao | Zero downtime na primeira semana |
