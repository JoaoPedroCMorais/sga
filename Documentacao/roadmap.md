# Roadmap Estratégico — SGA v4.0 (API-First)

> Duração total estimada: 10 a 11 meses | Execução solo, com sprints intensivos em recessos
> Escopo: **integral** — nenhuma fase foi cortada em relação à v3.4
> Versão: 4.0 | Atualizado em: 2026-09-02
> Substitui: `_arquivo_v3_4/roadmap_v3_4_revisado.md`

---

## Premissa de cronograma

A v3.4 previa 9-11 meses para uma stack de linguagem única. A v4.0 tem escopo equivalente,
porém sobre duas linguagens, dois toolchains e duas suítes de teste, e ainda precisa
reconstruir o CRUD administrativo que o Django Admin oferecia pronto.

A estimativa técnica em ritmo constante seria de aproximadamente 13 meses. **Por decisão do
desenvolvedor, o escopo é mantido integralmente e o cronograma é condensado para 10-11
meses**, com o excedente absorvido por sprints intensivos durante recessos e férias
acadêmicas. O risco dessa compressão é assumido conscientemente e está registrado na seção
"Riscos do cronograma condensado", ao final deste documento.

```
Fase 0  ██░░░░░░░░░░░░░░░░░░  Mês 1        Fundação Dupla e Prova de Arquitetura
Fase 1  ░░██████░░░░░░░░░░░░  Meses 2-4    API Core, Auth e Console Administrativo
Fase 2  ░░░░░░░░████░░░░░░░░  Meses 5-6    Chamada Mobile-First e Portal do Aluno
Fase 3  ░░░░░░░░░░░░██░░░░░░  Mês 7        Grade Horária e Voluntários
Fase 4  ░░░░░░░░░░░░░░████░░  Meses 8-10   Simulados, Boletins e Dashboards
Fase 5  ░░░░░░░░░░░░░░░░░░██  Mês 11       Automação, Segurança e Deploy
```

| Período | Situação acadêmica | Regime de trabalho |
|---|---|---|
| Mês 1 | Letivo | Constante |
| Meses 2-4 | Letivo + **recesso** | Constante + **sprint intensivo no recesso** |
| Meses 5-6 | Letivo | Constante |
| Mês 7 | **Férias** | **Sprint intensivo** |
| Meses 8-10 | Letivo | Constante |
| Mês 11 | Letivo | Constante + fechamento |

As Fases 3 e 4 são as que mais dependem dos sprints intensivos, e estão posicionadas para
coincidir com os períodos de menor carga acadêmica.

---

## Fase 0 — Fundação Dupla e Prova de Arquitetura (Mês 1)

**Fase nova, sem equivalente na v3.4.** Existe para validar o pivô antes de qualquer
funcionalidade: se a stack não se sustentar de ponta a ponta, é melhor descobrir no mês 1 do
que no mês 5.

### Semana 1 — Estrutura do monorepo

- Estrutura `apps/api`, `apps/web`, `packages/api-types` (ver `diretorios.md`)
- `docker-compose.yml` com PostgreSQL 16 (ADR-018)
- Backend: `uv` + `pyproject.toml`; Ruff, mypy configurados
- Frontend: pnpm workspaces, Next.js 15, TypeScript `strict`, Tailwind, shadcn/ui
- Tag git `v3.4-django-final` marcando o código Django antes da remoção

### Semana 2 — Esqueleto da API

- FastAPI com `/health` e configuração via pydantic-settings
- SQLModel + Alembic configurados (`target_metadata = SQLModel.metadata`)
- Primeira migration: tabela `user` mínima
- Sessão assíncrona com psycopg 3

### Semana 3 — Prova do contrato ponta a ponta

- Endpoint `GET /api/v1/health/echo` com `response_model` declarado
- Geração de `packages/api-types` via `openapi-typescript`
- Página Next.js consumindo esse endpoint com TanStack Query e **tipo gerado**
- Teste que confirma: alterar o campo no SQLModel quebra o `tsc` do frontend

### Semana 4 — CI e observabilidade

- GitHub Actions com dois jobs paralelos: `api` (ruff + mypy + pytest) e `web` (eslint + tsc + vitest)
- Job de verificação do contrato: regenerar tipos e falhar se divergirem do commit
- Sentry nos dois serviços
- Deploy de validação no Railway: dois serviços conversando

**Entrega:** um endpoint tipado consumido pelo frontend, com CI verde e deploy funcionando.
Nenhuma regra de negócio ainda — e é intencional. O que está sendo entregue é a **prova de
que a arquitetura do pivô é executável por este desenvolvedor neste prazo**.

**Critério de continuidade:** se ao fim do mês 1 a integração ponta a ponta não estiver
funcionando, reabrir a conversa com o Coordenador de IC antes de prosseguir.

---

## Fase 1 — API Core, Autenticação e Console Administrativo (Meses 2 a 4)

A fase mais longa e a mais crítica. É onde o Django Admin é reconstruído.

### Semanas 1-2 — Modelagem de domínio

- Modelos SQLModel: `User` (com `role`), `Student`, `ClassGroup`, `Teacher`, `Subject`
- Migrations Alembic revisadas manualmente
- Repositórios com filtro por vínculo (ADR-011)
- Testes de modelo e de constraint com PostgreSQL real
- **Regras de negócio portadas do código Django v3.4**, preservando semântica

### Semanas 3-4 — Autenticação

- OAuth2 Google com Authlib no FastAPI (ADR-013)
- Validação do domínio institucional no servidor
- JWT (15 min) + refresh token (7 dias) revogável, em cookie `httpOnly`
- Endpoints `login`, `callback`, `refresh`, `logout`, `me`
- Telas de login e callback no Next.js
- Testes de autenticação com provedor mockado

### Semana 5 — Autorização e SQLAdmin

- `require_role()` e guarda de rota por perfil no Next.js
- Testes de permissão para os quatro perfis, incluindo **teste explícito de IDOR**
- **SQLAdmin montado em rota protegida, exclusivo do Coordenador** (ADR-014)
- *Marco: a coordenação já consegue cadastrar dados reais a partir daqui*

### Semanas 6-7 — Componentes genéricos do console

O investimento que viabiliza o cronograma condensado.

- `<DataTable />`: TanStack Table com paginação, ordenação e busca server-side
- `<CrudForm />`: React Hook Form + Zod derivado do OpenAPI
- Layout do console: sidebar por perfil, breadcrumbs, tratamento de erro e estados de carga
- Testes de componente com Vitest

### Semanas 8-9 — Telas administrativas essenciais

- CRUD de Usuários (criar, atribuir perfil, desativar)
- CRUD de Turmas com vínculo de professores e monitores
- CRUD de Alunos
- **Importação em lote de planilha de alunos** (upload → Pandera → preview → confirmação)

### Semanas 10-11 — Telas complementares e auditoria

- CRUD de Professores e Disciplinas
- Auditoria: listeners SQLAlchemy + triggers PL/pgSQL em migration (ADR-012)
- Tela de consulta de auditoria, read-only, exclusiva do Coordenador
- Teste que confirma que escrita fora da sessão da aplicação é capturada pelo trigger

### Semana 12 — Consolidação

- Cobertura de testes da API acima de 60%
- Revisão de segurança com o Coordenador de IC
- Documentação da API revisada em `/docs`

**Entrega:** a coordenação cadastra alunos, turmas, professores e disciplinas pelo console em
Next.js. Login com Google funciona. Toda alteração é auditada.

**Checkpoint Go/No-Go:** se a Fase 1 ultrapassar 3,5 meses, pausar e reavaliar com o
Coordenador antes de iniciar a Fase 2. Alternativas nesse cenário: estender o uso do
SQLAdmin (exige nova ADR, conforme ADR-014) ou reduzir o escopo da Fase 4.

---

## Fase 2 — Chamada Mobile-First e Portal do Aluno (Meses 5 a 6)

Reimplementação do módulo já entregue na v3.4, agora na nova arquitetura. As regras de
negócio estão validadas em produção conceitual e documentadas em
`Cerebro/_arquivoV3_django/Records/02_Modulo_Chamada_Fase2.md`.

### Semanas 1-2 — API de chamada

- Modelos `AttendanceRecord` e `AbsenceJustification`
- **`UNIQUE(student_id, date, period)`** com `period ∈ {BEFORE_BREAK, AFTER_BREAK}` — a regra
  de dupla chamada do CAAI, preservada integralmente
- Upsert via `INSERT ... ON CONFLICT DO UPDATE` (equivalente ao `update_or_create` da v3.4)
- Endpoints de lançamento, consulta por turma e por data, e correção
- Testes cobrindo: dois períodos no mesmo dia, correção sem duplicação, permissão por perfil

### Semanas 3-4 — Interface de chamada mobile-first

- Tela otimizada para celular: alvos de toque grandes, contraste alto
- Busca local de aluno com `useState` + `filter` (o caso que motivou a ADR-007 no Alpine.js)
- **Optimistic update** com TanStack Query: a interface responde antes da rede, com rollback
  automático em falha — melhoria real sobre o HTMX em conexão 3G instável
- Indicador de estado de sincronização

### Semanas 5-6 — Portal do aluno e coordenação

- Ficha individual do aluno (dados, frequência, notas)
- Painel de acompanhamento ao vivo da coordenação (`refetchInterval`; avaliar SSE)
- Fluxo de justificativa de falta com upload de arquivo
- Fila de aprovação de justificativas para o Coordenador
- Correção manual de chamada pelo Coordenador

### Semana 7 — Encerramento da ponte

- **Remoção do SQLAdmin do projeto** — item obrigatório do checklist (ADR-014)
- Verificação de que o console em Next.js cobre todas as entidades administrativas
- Se não cobrir: nova ADR é obrigatória para estender a ponte

**Entrega:** monitores fazem chamada pelo celular. A coordenação acompanha ao vivo. Alunos
consultam sua ficha e justificam faltas. O projeto passa a rodar sem andaimes.

---

## Fase 3 — Grade Horária e Voluntários (Mês 7 — sprint intensivo de férias)

### Semana 1 — Disponibilidade e modelagem

- Modelos `Schedule`, `TimeSlot`, `Availability`
- Formulário de disponibilidade do professor no Next.js
- Endpoints de coleta e consulta

### Semana 2 — Solver assíncrono

- `services/solver.py` com CP-SAT (portado de `gerar_grade.py`)
- Tabela `job` e execução via `BackgroundTasks` (ADR-015)
- `POST /schedules/generate` retorna **202 Accepted** com `job_id`
- `GET /jobs/{id}` para acompanhamento
- Testes do solver isolados da camada HTTP

### Semana 3 — Interface da grade

- Visualização da grade por sala, por professor e por turma
- Alocação manual com drag-and-drop (caso de uso que o HTMX tornava custoso e o React resolve)
- Indicador de progresso durante o processamento

### Semana 4 — Sugestão de trocas

- Algoritmo de detecção de conflitos e sugestão de permutações válidas
- Fluxo: professor solicita troca → coordenação aprova
- Registro em auditoria

**Entrega:** grade horária gerada automaticamente sem travar o sistema. Professores informam
disponibilidade online e solicitam trocas.

---

## Fase 4 — Simulados, Boletins e Dashboards (Meses 8 a 10)

### Semanas 1-3 — Pipeline EvalBee

- Upload de `.xlsx` com validação Pandera do schema EvalBee (Princípio #3)
- Processamento com Pandas (portado de `gerar_estatisticas.py`)
- Persistência via SQLModel em lote
- Execução em background com acompanhamento de status (ADR-015)
- Tela de upload com preview e relatório de rejeições

### Semanas 4-6 — Boletins em PDF

- Templates Jinja2 + WeasyPrint no backend
- Gráficos estáticos com Matplotlib embarcados no PDF
- Geração individual e em lote (ZIP)
- Endpoint de download com verificação de permissão por objeto

### Semanas 7-10 — Dashboards

- Endpoints de agregação retornando **JSON** (nunca HTML de gráfico) — Princípio #8
- Agregação feita no PostgreSQL, não no cliente
- Gráficos em Recharts (ADR-016): percentual de acerto, comparativo entre salas, evolução
  temporal, desempenho por disciplina
- Filtros cruzados (sala, simulado, período) com estado em URL
- Dashboards diferenciados por perfil: coordenação vê tudo; professor vê suas turmas; aluno
  vê a si mesmo

### Semanas 11-12 — Consolidação

- Cobertura de testes acima de 70% na API
- Testes de componente dos dashboards
- Revisão de desempenho das consultas de agregação

**Entrega:** upload de simulado com processamento automático, boletins em PDF e dashboards
interativos para os quatro perfis.

---

## Fase 5 — Automação, Segurança e Deploy Definitivo (Mês 11)

### Semana 1 — Sincronização e automação

- Integração com Google Classroom via script Typer
- Railway Cron para sincronização diária
- E-mails agendados (notificação de simulado, alerta de frequência) via SMTP

### Semana 2 — Storage em produção

- Migração dos uploads do filesystem local para Supabase Storage via boto3 (ADR-003)
- Configuração por variável de ambiente, sem alteração de código de aplicação

### Semana 3 — Qualidade e segurança

- **Playwright: 10 testes E2E críticos** (ADR-006) — login, chamada nos dois períodos, upload
  de simulado, dashboard, geração de boletim
- Checklist OWASP Top 10, com atenção específica a:
  - **IDOR** — teste por perfil em todo endpoint que expõe dados de aluno
  - CORS restrito à origem do frontend
  - Cookies `httpOnly`, `Secure`, `SameSite`
  - Rate limiting nos endpoints de autenticação
  - Verificação de que `audit_log` não aceita UPDATE nem DELETE
- Revisão de segurança com o Coordenador de IC

### Semana 4 — Produção e entrega

- Railway: PostgreSQL managed + dois serviços com deploy automático
- Ordem de deploy documentada e testada: migration → API → web
- Sentry ativo nos dois serviços, correlacionado por trace
- Treinamento da equipe do CAAI (coordenação, professores, monitores)
- Fechamento da documentação de IC

**Entrega:** sistema em produção, equipe treinada, monitoramento ativo.

---

## Métricas de Sucesso por Fase

| Fase | Métrica | Alvo |
|---|---|---|
| 0 | Integração ponta a ponta com tipo gerado | CI verde; alteração no modelo quebra o `tsc` |
| 1 | Console administrativo funcional | Coordenação cadastra 90 alunos sem SQLAdmin ao fim da fase; cobertura >60% |
| 2 | Chamada mobile funcional | Menos de 3 toques para registrar presença; funciona em 3G instável |
| 3 | Grade gerada pelo solver | Solução em menos de 60 s **sem bloquear outras requisições** |
| 4 | Dashboard com dados reais | Do upload ao dashboard em menos de 2 min; cobertura >70% |
| 5 | Sistema em produção | Zero downtime na primeira semana; 10 testes E2E verdes |

---

## Riscos do Cronograma Condensado

O escopo integral em 10-11 meses depende de compressão via sprints intensivos. Os riscos
abaixo são reconhecidos e monitorados, não ignorados.

| Risco | Probabilidade | Impacto | Mitigação |
|---|---|---|---|
| Curva de aprendizado dupla (React + FastAPI) maior que o previsto | Alta | Alto | Fase 0 valida a stack antes de qualquer feature; checkpoint Go/No-Go na Fase 1 |
| Sprints de recesso não renderem o previsto (imprevistos pessoais, acadêmicos) | Média | Alto | Fases 3 e 4 posicionadas nos recessos; se falharem, a Fase 4 é a candidata natural a redução |
| Console administrativo consumir mais que 4 semanas | Média | Alto | SQLAdmin já cobre o cadastro; a extensão da ponte é a válvula de escape, com ADR |
| Auditoria própria (sem pghistory) apresentar falha | Média | **Crítico** | Camada dupla; testes específicos; revisão de segurança na Fase 5 |
| Compressão gerar dívida técnica silenciosa | Alta | Médio | Cobertura mínima por fase é critério de encerramento, não item opcional |

**Gatilho de renegociação:** se ao fim da Fase 2 (mês 6) o projeto estiver com mais de 4
semanas de atraso acumulado, a redução de escopo da Fase 4 deve ser discutida com o
Coordenador de IC — antes que a compressão vire dívida técnica ou entrega incompleta.

---

## Referências

- `stack.md` — pilha tecnológica
- `principios.md` — princípios que orientam as prioridades de cada fase
- `decisoes_arquiteturais.md` — ADRs citadas ao longo deste roadmap
- `migracao_v3_para_v4.md` — o que foi aproveitado do trabalho das fases 1 e 2 da v3.4
