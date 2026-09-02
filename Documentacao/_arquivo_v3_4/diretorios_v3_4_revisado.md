# Especificacao de Diretorios — SGA v3.4 Revisado

> Documento de Uso Interno: Controle de Implementacao de Arquitetura
> Atualizado em: 2026-05-17

---

## Estrutura Completa

```
sga/                                    # Raiz do projeto Django
│
├── config/                             # Configuracoes do projeto
│   ├── __init__.py
│   ├── urls.py                         # URL root (inclui apps via include())
│   ├── wsgi.py
│   ├── asgi.py
│   ├── cron.py                         # Funcoes agendadas via django-crontab
│   └── settings/
│       ├── __init__.py
│       ├── base.py                     # Settings compartilhados (INSTALLED_APPS, etc.)
│       ├── local.py                    # Dev: DEBUG=True, SQLite, etc.
│       └── production.py              # Prod: PostgreSQL, Sentry, R2, etc.
│
├── apps/                               # Aplicacoes Django (regras de negocio)
│   │
│   ├── users/                          # Gestao de usuarios e RBAC
│   │   ├── models.py                   # Profile (extends User), Group setup
│   │   ├── views.py                    # Login redirect, perfil
│   │   ├── admin.py                    # UserAdmin customizado
│   │   ├── permissions.py              # Mixins e decorators de permissao
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   └── test_permissions.py
│   │   └── urls.py
│   │
│   ├── academic/                       # Models fundacionais
│   │   ├── models.py                   # Student, Teacher, Subject, ClassGroup
│   │   ├── views.py                    # Ficha do aluno, listagens
│   │   ├── admin.py                    # Admin com list_display, search, filters
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   └── test_views.py
│   │   └── urls.py
│   │
│   ├── schedules/                      # Grade horaria
│   │   ├── models.py                   # Schedule, TimeSlot, Availability
│   │   ├── views.py                    # Interface de disponibilidade, visualizacao
│   │   ├── admin.py
│   │   ├── services/                   # Logica isolada (nao depende de views)
│   │   │   ├── __init__.py
│   │   │   ├── solver.py              # CP-SAT solver (adaptado de gerar_grade.py)
│   │   │   └── swap_suggester.py      # Algoritmo de sugestao de trocas
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   └── test_solver.py
│   │   └── urls.py
│   │
│   ├── attendance/                     # Chamada e justificativas
│   │   ├── models.py                   # Attendance, AttendanceRecord, Justification
│   │   ├── views.py                    # Interface de chamada (HTMX), justificativas
│   │   ├── admin.py
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   └── test_views.py
│   │   └── urls.py
│   │
│   ├── assessments/                    # Simulados e resultados
│   │   ├── models.py                   # Exam, ExamResult, Question
│   │   ├── views.py                    # Upload, dashboard, boletim
│   │   ├── admin.py
│   │   ├── services/                   # Logica isolada
│   │   │   ├── __init__.py
│   │   │   ├── evalbee_pipeline.py    # Pipeline ETL (adaptado de gerar_estatisticas.py)
│   │   │   ├── charts.py             # Geracao de graficos Plotly
│   │   │   └── pdf_generator.py       # Boletins PDF via WeasyPrint
│   │   ├── schemas/                    # Schemas Pandera para validacao
│   │   │   ├── __init__.py
│   │   │   └── evalbee_schema.py
│   │   ├── tests/
│   │   │   ├── test_models.py
│   │   │   ├── test_pipeline.py
│   │   │   └── test_charts.py
│   │   └── urls.py
│   │
│   └── audit/                          # Logs imutaveis (READ-ONLY)
│       ├── models.py                   # Proxy models para django-pghistory events
│       ├── views.py                    # Consulta de historico (somente coordenador)
│       ├── admin.py                    # Admin read-only
│       ├── tests/
│       │   └── test_views.py
│       └── urls.py
│
├── templates/                          # Templates Django (frontend)
│   ├── base.html                       # Esqueleto: Bootstrap 5, navbar, sidebar
│   ├── partials/                       # Fragmentos HTMX (swap parcial)
│   │   ├── _attendance_row.html       # Uma linha da chamada
│   │   ├── _student_card.html         # Card resumo do aluno
│   │   ├── _chart_container.html      # Container para graficos Plotly
│   │   └── _alert.html               # Componente de alerta reutilizavel
│   ├── mobile/                         # Views otimizadas para telas pequenas
│   │   └── attendance_form.html       # Chamada mobile-first
│   ├── users/                          # Templates de auth
│   ├── academic/                       # Templates de ficha, listagens
│   ├── schedules/                      # Templates de grade
│   ├── attendance/                     # Templates de chamada
│   ├── assessments/                    # Templates de simulados, dashboards
│   └── audit/                          # Templates de historico
│
├── static/                             # Arquivos estaticos
│   ├── css/
│   │   └── custom.css                 # Customizacoes sobre Bootstrap 5
│   ├── js/
│   │   └── htmx.min.js               # HTMX (Plotly carregado via CDN)
│   └── img/
│       └── logo.png
│
├── media/                              # Uploads de usuarios (dev)
│   └── justificativas/               # Atestados, justificativas de faltas
│
├── manage.py
├── requirements.txt                    # Dependencias pip
├── pyproject.toml                      # Config do Ruff, pytest, etc.
├── pytest.ini                          # Ou dentro do pyproject.toml
├── .gitignore
├── .env.example                        # Variaveis de ambiente (template)
├── CLAUDE.md                           # Stack e diretrizes para o Claude Code
└── README.md
```

---

## Regras de Organizacao

### Apps (`apps/`)

| App | Dominio | Models Principais |
|---|---|---|
| `users` | Autenticacao, perfis, RBAC | Profile (extends User) |
| `academic` | Dados academicos fundacionais | Student, Teacher, Subject, ClassGroup |
| `schedules` | Grade horaria e trocas | Schedule, TimeSlot, Availability |
| `attendance` | Chamada e justificativas | Attendance, AttendanceRecord, Justification |
| `assessments` | Simulados, notas, dashboards | Exam, ExamResult, Question |
| `audit` | Logs imutaveis (read-only) | Proxy models do pghistory |

### Services (`services/`)

Logica de negocio complexa fica em `services/`, NAO em `views.py` ou `models.py`:
- `solver.py` — Solver CP-SAT (nao depende de request/response)
- `evalbee_pipeline.py` — Pipeline ETL (processa DataFrames, persiste via ORM)
- `charts.py` — Gera graficos Plotly (retorna HTML/JSON, nao depende de view)
- `pdf_generator.py` — Gera PDFs com WeasyPrint

**Regra**: services/ nunca importa de views.py. Views importam de services/.

### Schemas Pandera (`schemas/`)

Validacao de dados externos antes de processamento:
- `evalbee_schema.py` — Schema para planilhas EvalBee (.xlsx)
- Futuros: `classroom_schema.py`, `sheets_schema.py`

### Templates (`templates/`)

| Pasta | Conteudo |
|---|---|
| `templates/` (raiz) | `base.html` — esqueleto compartilhado |
| `templates/partials/` | Fragmentos HTMX reutilizaveis (prefixo `_`) |
| `templates/mobile/` | Views otimizadas para celular |
| `templates/{app}/` | Templates especificos de cada app |

### Static (`static/`)

- `htmx.min.js` — unica dependencia JS local
- Plotly carregado via CDN (nao local)
- Bootstrap 5 via CDN ou pip (`django-bootstrap5`)
- `custom.css` — apenas overrides sobre Bootstrap

### Media (`media/`)

- Uploads de usuarios (justificativas, atestados)
- Dev: filesystem local
- Producao (Fase 5): Supabase Storage (S3-compatible) via django-storages
