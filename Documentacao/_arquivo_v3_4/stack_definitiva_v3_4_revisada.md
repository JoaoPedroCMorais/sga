# Stack Definitiva — SGA v3.4 Revisada

> Documento canônico da pilha tecnológica do SGA.
> Qualquer divergência em outros documentos deve ser resolvida em favor DESTE arquivo.
> Atualizado em: 2026-05-17

---

## Visao Geral

Sistema de Gerenciamento Academico (SGA) para curso preparatorio CAAI.
Escala: ~90 alunos, ~20 professores, 3 salas, 4 perfis de acesso.
Execucao: dev solo com auxilio de IAs + coordenador de IC.
Timeline: 9-11 meses, 5 fases.

---

## Pilha Tecnologica Definitiva

### Backend e Framework

| Componente | Tecnologia | Versao |
|---|---|---|
| Framework Web | Django | 5.x |
| API REST | Django REST Framework (DRF) | 3.15+ |
| ORM e Migrations | **Django ORM + Django Migrations** | (built-in) |
| Banco de Dados (dev) | SQLite | (built-in) |
| Banco de Dados (prod) | PostgreSQL | 15+ |
| Agendamento de tarefas | django-crontab | latest |

### Autenticacao e Permissoes

| Componente | Tecnologia | Notas |
|---|---|---|
| Auth/Login | django-allauth | Google OAuth2, restrito ao dominio institucional |
| Token API | djangorestframework-simplejwt | Para endpoints da API REST |
| Permissoes (RBAC) | **Django Groups + queryset filters** | 4 perfis fixos, sem django-guardian |
| Auditoria | django-pghistory | Triggers PostgreSQL, logs imutaveis |

### ETL, Validacao e Dados

| Componente | Tecnologia | Notas |
|---|---|---|
| Processamento de dados | Pandas + openpyxl | ETL de planilhas EvalBee, Google Sheets |
| Validacao de schema | Pandera | Validacao de DataFrames antes de processar |
| Otimizacao (grade) | Google OR-Tools (CP-SAT) | Solver de grade horaria existente |

### Frontend

| Componente | Tecnologia | Notas |
|---|---|---|
| Templates | Django Templates | Server-side rendering |
| CSS Framework | Bootstrap 5 | Mobile-first, responsivo |
| Interatividade | HTMX | Atualizacoes parciais sem JavaScript customizado |
| Graficos/BI | Plotly | 100% Python, renderizado no backend, injetado via HTMX |
| Formularios | django-crispy-forms + crispy-bootstrap5 | Formularios Bootstrap automaticos |
| Tabelas | django-tables2 | Tabelas com ordenacao e paginacao |

### Infraestrutura e Deploy

| Componente | Tecnologia | Notas |
|---|---|---|
| Deploy | Railway | PostgreSQL managed |
| Storage (Fases 1-4) | Filesystem local / WhiteNoise | Volume baixo, sem dependencia extra |
| Storage (Fase 5) | Supabase Storage (S3-compatible) + django-storages | Endpoint S3, gratuito ate 1GB, alinhado com coordenacao de IC |
| Monitoramento | Sentry | Error tracking e performance |

### Documentos e Relatorios

| Componente | Tecnologia | Notas |
|---|---|---|
| PDF (boletins, relatorios) | WeasyPrint | HTML/CSS para PDF |
| Graficos em PDF | Matplotlib | Graficos estaticos para relatorios |

### Testes e Qualidade

| Componente | Tecnologia | Quando |
|---|---|---|
| Testes (unit + integration) | pytest-django | Fases 1-5 (desde o inicio) |
| Testes E2E | Playwright | Apenas Fase 5 (10 testes criticos) |
| Linter/Formatter | Ruff | `ruff check .` e `ruff format .` |
| Docs API | drf-spectacular | Swagger/OpenAPI automatico |

---

## O Que FOI REMOVIDO (e por que)

| Removido | Motivo |
|---|---|
| **SQLAlchemy + Alembic** | Incompativel com django-pghistory, django-allauth, DRF. Django ORM ja e database-agnostic. Nenhum projeto Django de sucesso usa SQLAlchemy em paralelo. |
| **django-guardian** | Para 4 perfis fixos com vinculos deterministicos (professor→turma), Django Groups + filtros no queryset bastam. Adicionar guardian apenas se surgir caso concreto de permissao por objeto individual. |
| **Supabase Storage (Fases 1-4)** | Desnecessario nas fases iniciais — filesystem local basta. Supabase Storage (S3-compatible) entra na Fase 5 para producao, via django-storages. |
| **Alpine.js** | HTMX cobre as necessidades de interatividade. Alpine.js adicionaria complexidade de frontend sem beneficio claro. |
| **Celery + Redis** | django-crontab e suficiente para a escala. Se tasks async com feedback forem necessarias, considerar Django-Q2 (usa PostgreSQL como broker, sem Redis). |
| **Prefect 2** | Orquestrador de ETL enterprise. Para um pipeline de ~90 alunos, management commands Django bastam. |
| **Chart.js** | Substituido por Plotly na v3.4 (100% Python, sem JavaScript de charting). |
| **Metabase** | Substituido por dashboards nativos Django + Plotly na v3.4. |
| **Next.js / Flutter** | Removidos do escopo. PWA via Django Templates + HTMX e suficiente. |
| **django-admin-interface** | Customizacao visual do Admin nao e prioridade. Django Admin padrao funciona. |

---

## 4 Perfis de Acesso (RBAC)

| Perfil | Acesso | Implementacao |
|---|---|---|
| **Coordenador** | Tudo (dados, relatorios, config, gestao de usuarios, auditoria) | `Group: coordenador` — sem filtro no queryset |
| **Professor** | Suas turmas (notas, frequencia, ocorrencias, solicitacao de troca) | `Group: professor` — filtro: `class_group__teachers=user` |
| **Monitor** | Realizar chamada, historico de chamadas da sua turma | `Group: monitor` — filtro: `class_group__monitors=user` |
| **Aluno** | Consulta propria (notas, boletim, frequencia, materiais, justificar faltas) | `Group: aluno` — filtro: `student__user=user` |

Permissao padrao: **NEGAR**. Acesso deve ser explicito via Group membership + queryset filter.

---

## Fontes de Dados Externas

| Fonte | Formato | Uso |
|---|---|---|
| EvalBee | .xlsx | Simulados e gabaritos |
| Google Sheets | API v4 | Frequencia e redacoes |
| Google Classroom | API REST | Notas e prazos |
