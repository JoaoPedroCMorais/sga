# Decisões Arquiteturais (ADRs) — SGA

> Registro formal e cumulativo das decisões de arquitetura do projeto.
> Cada decisão é registrada com data, contexto, alternativas consideradas e justificativa.
> Formato inspirado nos ADRs de projetos como Zulip e Wagtail.
> Versão do documento: 4.0 | Atualizado em: 2026-09-02

---

## Como ler este documento

Este é um **log append-only**. Decisões nunca são apagadas — quando deixam de valer, recebem
um bloco de status no topo indicando o que as substituiu e por quê. O texto original é
preservado sem alteração.

Essa política existe por três razões: a rastreabilidade exigida pela banca de Iniciação
Científica, a possibilidade de auditar o raciocínio que levou a cada mudança, e o fato de
que uma decisão revogada frequentemente contém o argumento que impede que o erro oposto
seja cometido no futuro.

| Status | Significado |
|---|---|
| **Aprovada** | Vigente |
| **Substituída pela ADR-XXX** | O problema continua existindo; a solução mudou |
| **Revogada** | A premissa que motivava a decisão deixou de existir |
| **Obsoleta** | A decisão perdeu objeto (o caso de uso desapareceu) |

---

## Índice

### Decisões da v3.4 (era Django) — 2026-05

| ADR | Título | Status |
|---|---|---|
| 001 | Django ORM em vez de SQLAlchemy | 🔄 Substituída pela ADR-009 |
| 002 | Django Groups em vez de django-guardian | 🔄 Substituída pela ADR-011 |
| 003 | Filesystem Local (dev) + Supabase Storage S3 (prod) | ✅ Mantida (biblioteca adaptada) |
| 004 | django-crontab + Railway Cron em vez de Celery | ✅ Mantida em espírito |
| 005 | Plotly em vez de Chart.js | ❌ Revogada |
| 006 | Playwright apenas na Fase 5 | ✅ Mantida e reforçada |
| 007 | Exceção controlada — Alpine.js no módulo de Chamada | ⚪ Obsoleta |

### Decisões da v4.0 (pivô API-First) — 2026-09

| ADR | Título | Criticidade |
|---|---|---|
| 008 | Pivô para arquitetura API-First (decisão-mãe) | 🔴 Estrutural |
| 009 | SQLModel como ORM e camada de validação unificada | 🔴 Estrutural |
| 010 | Alembic como sistema único de migrations | 🔴 Estrutural |
| 011 | RBAC por dependências FastAPI + filtro no repositório | 🔴 Segurança |
| 012 | Auditoria híbrida: listeners SQLAlchemy + triggers PL/pgSQL | 🔴 Segurança |
| 013 | FastAPI como único Authorization Server | 🔴 Segurança |
| 014 | Console administrativo em Next.js + SQLAdmin como ponte temporária | 🔴 Produto |
| 015 | Execução de trabalho bloqueante fora do event loop | 🟡 Operação |
| 016 | Recharts como biblioteca de gráficos (substitui a ADR-005) | 🟡 Frontend |
| 017 | Contrato OpenAPI como fonte única dos tipos TypeScript | 🟡 Integração |
| 018 | PostgreSQL em desenvolvimento via Docker (aposentadoria do SQLite) | 🟡 Infraestrutura |

---

# Parte I — Decisões da era Django (v3.4)

## ADR-001: Django ORM em vez de SQLAlchemy

> ### 🔄 Status após o pivô v4.0
> ****Substituída pela ADR-009** (2026-09-02)**
>
> O pivô arquitetural eliminou as quatro dependências que fundamentavam esta decisão (django-pghistory, django-allauth, DRF e Django Admin). Sem elas, os argumentos de incompatibilidade deixam de se aplicar. O SQLAlchemy retorna ao projeto sob a forma de SQLModel. **Esta ADR não estava incorreta**: ela era válida no contexto em que foi tomada, e o contexto mudou por decisão do Coordenador de IC.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


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

> ### 🔄 Status após o pivô v4.0
> ****Substituída pela ADR-011** (2026-09-02)**
>
> O diagnóstico central desta ADR permanece integralmente válido: o acesso no SGA é determinado pelo vínculo no modelo, não por permissão atribuída objeto a objeto. O que muda é apenas o mecanismo — Django Groups dão lugar a dependências do FastAPI, e os queryset filters dão lugar a filtros na camada de repositório.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


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

> ### 🔄 Status após o pivô v4.0
> ****Mantida, com adaptação de biblioteca** (2026-09-02)**
>
> A decisão de usar filesystem local nas fases iniciais e Supabase Storage (S3-compatible) em produção permanece vigente. Apenas a biblioteca de acesso muda: `django-storages` dá lugar a `boto3` direto. Ver `stack.md`.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


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

> ### 🔄 Status após o pivô v4.0
> ****Mantida em espírito; mecanismo substituído** (2026-09-02)**
>
> A rejeição a Celery + Redis continua válida e **reforçada**: a escala do SGA não justifica broker dedicado. O django-crontab dá lugar a APScheduler em desenvolvimento e Railway Cron em produção. Atenção: a natureza assíncrona do FastAPI aumenta a tentação de reintroduzir Celery — ela permanece proibida.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


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

> ### 🔄 Status após o pivô v4.0
> ****Revogada** (2026-09-02)**
>
> Esta ADR foi revogada, não substituída. Seu argumento central era literalmente eliminar JavaScript de charting e manter os gráficos 100% em Python. Com a adoção do Next.js, escrever JavaScript deixou de ser evitável, e a premissa da decisão desapareceu. A escolha de biblioteca de gráficos foi refeita do zero na ADR-016.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


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

> ### 🔄 Status após o pivô v4.0
> ****Mantida e reforçada** (2026-09-02)**
>
> A decisão de adiar Playwright para a Fase 5 continua correta e ganha força: uma interface React em construção é ainda mais instável para testes E2E do que templates Django eram. A pirâmide de testes da v4.0 acrescenta Vitest na camada de componente.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


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

---

## ADR-007: Excecao Controlada — Alpine.js no Modulo de Chamada

> ### 🔄 Status após o pivô v4.0
> ****Obsoleta** (2026-09-02)**
>
> Esta exceção deixou de ter objeto. O React resolve nativamente o caso de uso que motivou a introdução do Alpine.js — filtro local de lista já carregada, sem requisição ao servidor — com `useState` e `Array.filter`. O Alpine.js foi removido do projeto. O raciocínio registrado aqui permanece relevante como precedente metodológico: exceções a uma regra de stack devem ser documentadas com escopo e limites explícitos, nunca adotadas em silêncio.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-20
**Status**: Aprovada
**Decisores**: Dev

### Contexto

A stack v3.4 Revisada proibe Alpine.js globalmente (ver ADR de stack). Toda interatividade de frontend deve ser resolvida com HTMX + Django Templates. Durante a implementacao do modulo de Chamada (Fase 2), surgiu a necessidade de um filtro de busca instantaneo na lista de alunos — o monitor precisa localizar rapidamente um aluno em ~30-40 nomes no celular, com conexao potencialmente instavel (3G/4G).

### Problema

O filtro de busca tem caracteristicas que tornam HTMX inadequado:

- Dados ja estao carregados na pagina (nao ha nada para buscar no servidor)
- Filtragem precisa ser instantanea (keystroke a keystroke)
- Ambiente mobile com 3G/4G instavel (requisicoes ao servidor podem falhar)
- Lista pequena (~30-40 alunos por turma, filtro no cliente e trivial)

HTMX e projetado para interacoes servidor-cliente (request → response → swap). Para filtro puramente local de dados ja carregados, ele exigiria `hx-get` a cada keystroke — latencia perceptivel, sobrecarga no servidor, falha em conexao instavel.

### Alternativas Consideradas

| Opcao | Pros | Contras |
|---|---|---|
| HTMX `hx-get` com debounce | Mantem stack pura | Latencia de rede; falha em 3G; sobrecarga a cada keystroke |
| JavaScript vanilla (`addEventListener`) | Zero dependencias extras | ~15-20 linhas de JS imperativo vs. 3 atributos declarativos; mais propenso a bugs |
| Alpine.js (excecao controlada) | 3 atributos declarativos; zero requisicoes; funciona offline; ~8KB gzipped | Adiciona dependencia; contradiz proibicao geral |
| Nao ter filtro de busca | Zero complexidade | UX inaceitavel — monitor rola manualmente ~40 nomes no celular |

### Decisao

**Usar Alpine.js exclusivamente para o filtro local de busca na tela de chamada** (`take_attendance.html`). O uso e restrito a:

- `x-data="{ query: '' }"` — estado reativo local
- `x-model="query"` — two-way binding no input de busca
- `x-show` — filtrar linhas de alunos no DOM (zero requisicoes)
- `x-transition` — animacao suave

### Justificativa

A proibicao original do Alpine.js foi motivada por evitar fragmentacao do frontend entre Alpine.js e HTMX para interacoes servidor-cliente. Esta excecao nao viola o espirito da proibicao porque:

1. **Escopo ortogonal:** Alpine.js faz filtro local (client-only). HTMX faz toggle de status (client-server). Nao ha sobreposicao.
2. **Principio #2 (Simplicidade Primeiro):** Alpine.js e a solucao mais simples que funciona. 3 atributos HTML vs. 15+ linhas de JS imperativo.
3. **Principio #7 (Entregue Valor Cedo):** Evitar Alpine.js aqui significaria reinventar reatividade declarativa sem ganho funcional.

### Escopo e Limites da Excecao

**Permitido:**
- `x-data`, `x-model`, `x-show`, `x-transition` para filtro local em `take_attendance.html`

**Proibido:**
- Qualquer uso de Alpine.js em outros modulos
- `x-bind`, `x-on` para substituir funcionalidade HTMX
- Chamadas ao servidor via Alpine.js (fetch, $watch com API)
- Gerenciamento de estado complexo (stores, componentes aninhados)

### Clausula de Extensao

Se surgir outra necessidade de filtro local no futuro:
1. Avaliar se HTMX com `hx-get` + debounce e viavel (quando latencia for aceitavel)
2. Se nao for, **estender esta ADR** documentando o novo caso — nao usar Alpine.js silenciosamente

### Consequencias

- Dependencia `alpinejs` adicionada ao template `take_attendance.html` (via CDN, ~8KB gzipped)
- Code review deve rejeitar qualquer uso de Alpine.js fora do escopo definido
- CLAUDE.md do projeto deve incluir nota sobre esta excecao

---

# Parte II — Decisões do pivô API-First (v4.0)

## ADR-008: Pivô para Arquitetura API-First

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Coordenador de IC (determinante) + Dev

### Contexto

A v3.4 Revisada consolidou uma arquitetura monolítica Django 5 + DRF + HTMX + Bootstrap 5,
com duas fases já entregues: fundação/autenticação (Fase 1) e módulo de chamada (Fase 2),
somando aproximadamente 1.920 linhas de Python distribuídas em três apps (`users`,
`academic`, `attendance`).

O Coordenador de IC determinou a mudança para uma arquitetura API-First desacoplada, com
dois objetivos declarados: escalabilidade e viabilização de aplicativos móveis (React Native
ou Flutter) consumindo a mesma API.

### Problema

O monolito Django atende bem ao caso de uso web, mas apresenta três limitações estruturais
para os objetivos declarados:

1. **Acoplamento de apresentação.** Em Django Templates + HTMX, a regra de renderização vive
   no servidor e é específica de HTML. Um cliente móvel nativo não consome fragmentos HTML;
   precisaria de uma segunda camada de API mantida em paralelo aos templates, com risco
   permanente de divergência entre os dois caminhos.
2. **Contrato implícito.** O DRF oferece API REST, mas no desenho da v3.4 ela era acessória
   — a maior parte da funcionalidade só existia em views renderizadas. Não havia contrato
   formal completo do sistema.
3. **Limite de evolução do frontend.** O HTMX cobre bem interações de baixa complexidade.
   Telas com estado local rico (grade horária com drag-and-drop, dashboards com filtros
   cruzados, edição em massa) exigiriam JavaScript customizado crescente, corroendo a
   simplicidade que justificava o HTMX.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Manter o monolito Django (status quo) | Duas fases entregues; uma linguagem; Django Admin de graça; menor prazo | Não atende ao objetivo de mobile; contrato de API parcial; frontend limitado |
| Django + DRF como API pura + Next.js | Aproveita ORM, Admin, allauth e pghistory já implementados; risco muito menor | Mantém peso do Django sem usar suas telas; DRF é mais verboso que FastAPI; não foi a orientação do Coordenador |
| **FastAPI + SQLModel + Next.js** (adotada) | Contrato OpenAPI nativo; tipagem end-to-end; async; mobile viável; maior valor acadêmico | Descarte de ~85-90% do código existente; duas linguagens; perda do Django Admin; perda do pghistory; prazo maior |
| FastAPI + frontend em templates Jinja2 | Menos JavaScript | Não resolve o objetivo de mobile; pior dos dois mundos |

### Decisão

**Adotar arquitetura API-First**, com a pilha definida em `stack.md`:

- **Backend**: FastAPI + Uvicorn
- **ORM e validação**: SQLModel (SQLAlchemy 2.0 + Pydantic v2)
- **Banco**: PostgreSQL 16 (dev via Docker, prod via Railway)
- **Frontend web**: Next.js 15 + Tailwind CSS
- **Contrato**: OpenAPI 3.1 gerado pelo FastAPI, com tipos TypeScript derivados dele

As regras de negócio do CAAI são preservadas integralmente: quatro perfis de acesso, dupla
chamada diária (antes e depois do intervalo), grade horária por CP-SAT, e exigência de
auditoria e rastreabilidade.

### Consequências

**Custo assumido:**

| Item | Impacto |
|---|---|
| Código descartado | ~85-90% das 1.920 linhas Python. Preservam-se o modelo conceitual de dados e as regras de negócio, não a implementação |
| Fases refeitas | Fases 1 e 2 do roadmap v3.4 são reimplementadas na nova stack |
| Django Admin | Perdido. Maior custo isolado do pivô — ver ADR-014 |
| django-pghistory | Perdido. Não há equivalente maduro — ver ADR-012 |
| Superfície de linguagens | De uma (Python) para duas (Python + TypeScript), com dois toolchains, dois linters e dois conjuntos de testes |
| Prazo | De 9-11 meses para 10-11 meses **com sprints intensivos em recessos acadêmicos**, mantido o escopo total por decisão do Dev |
| Riscos de segurança novos | IDOR (Princípio #4), CORS, gestão de token entre dois serviços |

**Ganho obtido:**

| Item | Impacto |
|---|---|
| Múltiplos clientes | Mobile viável sem duplicar regra de negócio — objetivo declarado do pivô |
| Contrato formal | OpenAPI completo e gerado automaticamente; documentação nunca desatualiza |
| Tipagem end-to-end | Mudança de campo no backend quebra a compilação do frontend (Princípio #8) |
| Separação de responsabilidades | Camadas router/service/repository explicitamente separadas |
| Valor acadêmico | Arquitetura desacoplada é objeto de estudo mais substantivo para o relatório de IC do que um CRUD monolítico |

**Preservação do histórico:** o código Django permanece no repositório até a Fase 0 entregar
o esqueleto novo, e é marcado com a tag git `v3.4-django-final` antes de ser removido. Ver
`migracao_v3_para_v4.md`.

### Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Prazo estourar por causa da curva de aprendizado dupla | Fase 0 (mês 1) valida a stack ponta a ponta antes de qualquer feature; checkpoint Go/No-Go ao fim da Fase 1 |
| Coordenação ficar sem sistema utilizável por meses | SQLAdmin como ponte na Fase 1 (ADR-014) |
| Auditoria mais fraca que a da v3.4 | Estratégia híbrida com triggers no banco (ADR-012) |
| Autenticação fragmentada entre dois sistemas | FastAPI como único Authorization Server (ADR-013) |

---

## ADR-009: SQLModel como ORM e Camada de Validação Unificada

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: ADR-001
**Decisores**: Coordenador de IC + Dev

### Contexto

O pivô (ADR-008) removeu o Django e, com ele, o Django ORM. É preciso escolher a camada de
persistência do FastAPI.

### Problema

A ADR-001 havia rejeitado o SQLAlchemy com quatro argumentos: incompatibilidade com
django-pghistory, django-allauth, DRF ModelSerializer e Django Admin. **Os quatro
desapareceram com o pivô** — nenhuma dessas bibliotecas existe mais no projeto. O quinto
argumento (dois sistemas de migração concorrentes) também deixa de valer, porque sem Django
Migrations o Alembic passa a ser sistema único (ADR-010).

Resta escolher entre SQLAlchemy puro e SQLModel.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| SQLAlchemy 2.0 puro + Pydantic separado | Máximo controle; ecossistema maduro; documentação extensa | Duplicação: cada entidade precisa de um modelo SQLAlchemy e de dois a três schemas Pydantic escritos à mão, mantidos em sincronia manualmente |
| **SQLModel** (adotada) | Um modelo serve como tabela e como base de validação; escrito pelo autor do FastAPI; integração direta com `response_model` | Camada de abstração mais nova, com menos material de referência; casos avançados exigem descer para SQLAlchemy |
| Tortoise ORM | Async nativo; sintaxe familiar a quem vem do Django | Ecossistema menor; Alembic não é o padrão; menos aderente ao FastAPI |
| Peewee / bancos de documentos | — | Descartados: não atendem ao Princípio #1 (SSOT relacional) |

### Decisão

**Adotar SQLModel** como camada única de modelagem e validação, com a seguinte convenção:

```python
# models/student.py — a tabela
class Student(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    enrollment_number: str = Field(unique=True, index=True)
    full_name: str
    class_group_id: int = Field(foreign_key="classgroup.id")

# schemas/student.py — os contratos de I/O
class StudentBase(SQLModel):
    enrollment_number: str
    full_name: str

class StudentCreate(StudentBase):
    class_group_id: int

class StudentRead(StudentBase):
    id: int
    class_group_id: int
```

**Regra:** modelos com `table=True` nunca são usados como `response_model`. Sempre existe um
schema `...Read` correspondente. Isso evita vazamento acidental de campos sensíveis (hash de
senha, campos internos) para a resposta HTTP.

Quando a expressividade do SQLModel for insuficiente (CTEs, window functions, upsert com
`ON CONFLICT`), é permitido descer para SQLAlchemy Core — que é a camada subjacente, não uma
dependência adicional. Raw SQL em tempo de requisição permanece proibido (Princípio #6).

### Consequências

- Uma definição de entidade em vez de duas ou três
- `response_model` alimenta o OpenAPI automaticamente, sustentando o Princípio #8
- Alembic gera migrations a partir do metadata do SQLModel (`target_metadata = SQLModel.metadata`)
- A equipe precisa conhecer SQLAlchemy 2.0 para os casos avançados — o SQLModel não isola completamente

### Nota de rastreabilidade

Registra-se explicitamente, para a banca: **a ADR-001 não foi um erro.** Ela foi tomada em
maio de 2026 com premissas corretas para o contexto Django, e é revertida em setembro de
2026 porque o contexto foi alterado por decisão de orientação. Essa é a diferença entre
revisar uma decisão e corrigir uma falha de análise.

---

## ADR-010: Alembic como Sistema Único de Migrations

**Data**: 2026-09-02
**Status**: Aprovada
**Relacionada**: ADR-001 (que proibia Alembic), ADR-009
**Decisores**: Dev

### Contexto

A v3.4 listava Alembic entre as tecnologias proibidas. O motivo, registrado na ADR-001, era
específico: *"Django Migrations e Alembic são dois sistemas de migração de schema
concorrentes. Mantê-los sincronizados é fonte garantida de bugs."*

### Problema

Com a remoção do Django, não há mais Django Migrations. O SQLModel não possui sistema de
migração próprio. Sem Alembic, a evolução de schema seria manual — inaceitável para um
sistema com auditoria e dados reais de alunos.

### Decisão

**Adotar Alembic como sistema único de migrations**, configurado com
`target_metadata = SQLModel.metadata`.

Convenções obrigatórias:

1. Toda migration é gerada com `alembic revision --autogenerate` e **revisada manualmente
   antes do commit**. O autogenerate não detecta renomeações nem alterações de tipo com
   segurança.
2. Toda migration tem `downgrade()` implementado. Migration sem downgrade não passa em
   review.
3. Triggers e funções PL/pgSQL da auditoria (ADR-012) vivem em migrations, com `op.execute()`.
4. Migrations rodam antes do deploy da API, nunca depois (ver topologia em `blueprint.md`).
5. As migrations do Django (7 arquivos em `academic/`, `attendance/`, `users/`) são
   descartadas. O banco de desenvolvimento é recriado do zero na Fase 0; não há dados de
   produção a preservar nesta etapa.

### Consequências

- A proibição da v3.4 é formalmente levantada, com o registro do motivo
- Um único histórico linear de schema, versionado em git
- Risco conhecido: `--autogenerate` com PostgreSQL e SQLModel ocasionalmente produz diffs
  espúrios em tipos `Enum` — daí a exigência de revisão manual

---

## ADR-011: RBAC por Dependências FastAPI e Filtro no Repositório

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: ADR-002
**Decisores**: Dev

### Contexto

A ADR-002 estabeleceu que, no SGA, o acesso é determinado pelo **vínculo no modelo**
(professor→turma, monitor→turma, aluno→si mesmo) e não por permissão atribuída objeto a
objeto, e que por isso Django Groups + queryset filters bastavam.

Esse diagnóstico continua correto. O que desapareceu foi a implementação: não há Django
Groups nem querysets.

### Problema

Numa API REST, o risco de autorização muda de natureza. No monolito, esconder um botão no
template escondia efetivamente a operação, porque não havia outro caminho até ela. Numa API
pública, toda operação é alcançável por requisição direta. Uma verificação apenas na rota
não impede que um professor autenticado leia `GET /api/v1/students/42` de um aluno que não é
dele — a vulnerabilidade conhecida como **IDOR** (Insecure Direct Object Reference).

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Verificação apenas por dependência de rota | Simples | **Não impede IDOR** — inaceitável |
| Biblioteca de ACL por objeto (Casbin, oso) | Flexível; políticas declarativas | Overhead para 4 perfis determinísticos; repete o erro que a ADR-002 evitou com o guardian |
| **Dependência de rota + filtro no repositório** (adotada) | Duas camadas; sem dependência extra; o filtro fica onde a consulta é montada | Exige disciplina: todo repositório deve receber o usuário autenticado |
| Row-Level Security do PostgreSQL | Garantia no banco | Complexo de testar; exige conexão por usuário; desproporcional para a escala |

### Decisão

**Duas camadas obrigatórias e complementares:**

```python
# Camada 1 — a rota. Protege o endpoint por perfil.
@router.get("/students", response_model=list[StudentRead])
async def list_students(
    user: User = Depends(require_role(Role.COORDENADOR, Role.PROFESSOR, Role.MONITOR)),
    session: AsyncSession = Depends(get_session),
):
    return await student_repo.list_for(session, user)


# Camada 2 — o repositório. Protege o objeto por vínculo.
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
        return []                      # Permissão padrão: NEGAR
    return (await session.exec(stmt)).all()
```

Regras adicionais:

- **Consulta de objeto individual retorna 404, não 403**, quando o objeto existe mas não
  pertence ao usuário. Um 403 confirmaria a existência do recurso e vazaria informação.
- Nenhum endpoint acessa `session.exec(select(Model))` diretamente. Todo acesso passa por um
  repositório que recebe o usuário autenticado.
- Toda entidade que expõe dados de alunos tem teste de permissão para os quatro perfis.

### Cláusula de Revisão

Se durante as Fases 2-3 surgir caso concreto de permissão ad-hoc por objeto individual
(por exemplo, "o professor X pode ver esta turma mas não aquela, mesmo lecionando em ambas"),
reavaliar a adoção de uma biblioteca de políticas. Até lá, a solução mais simples que
funciona é a adotada (Princípio #2).

---

## ADR-012: Auditoria Híbrida — Listeners SQLAlchemy e Triggers PL/pgSQL

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: a implementação do Princípio #5 baseada em django-pghistory
**Decisores**: Coordenador de IC + Dev

### Contexto

O Princípio #5 (Auditoria Total) exige registro imutável de quem alterou o quê e quando. Na
v3.4 esse princípio era realizado inteiramente pelo `django-pghistory`, que instala triggers
no PostgreSQL e grava eventos em tabelas dedicadas. Os modelos `ClassGroup`, `Student`,
`AttendanceRecord` e `AbsenceJustification` já estavam rastreados.

### Problema

**Não existe equivalente maduro do django-pghistory para SQLModel.** As opções do ecossistema
SQLAlchemy foram avaliadas e nenhuma é substituto direto:

| Biblioteca | Avaliação |
|---|---|
| `sqlalchemy-continuum` | Histórico de manutenção irregular; suporte a async problemático; acoplada a padrões de sessão que o FastAPI não usa |
| `sqlalchemy-history` | Fork mais recente do continuum; menos maduro; base de usuários pequena |
| Implementação própria | Exige decidir explicitamente o nível da garantia |

Registra-se com honestidade: **esta é a maior perda técnica do pivô.** O pghistory oferecia
imutabilidade garantida pelo banco, com configuração de uma linha por modelo.

### Alternativas Consideradas

| Opção | Garantia | Prós | Contras |
|---|---|---|---|
| A. Apenas listeners SQLAlchemy | Nível de aplicação | 100% Python; testável; registro rico (usuário, IP, endpoint) | Qualquer escrita que não passe pela sessão da aplicação escapa: `bulk_insert`, script de manutenção, acesso direto ao banco |
| B. Apenas triggers PL/pgSQL | Nível de banco | Imutabilidade real; equivalente ao pghistory | Não captura contexto de aplicação (qual usuário HTTP, qual endpoint); exige SQL bruto |
| **C. Híbrida** (adotada) | Ambos | Cobre os dois flancos; o contexto rico vem da aplicação e a garantia vem do banco | Duas implementações a manter; possibilidade de registro duplicado a ser tratada |

### Decisão

**Adotar a estratégia híbrida (opção C)**, em duas camadas:

**Camada de aplicação** — listener `before_flush` do SQLAlchemy grava em `audit_log` o
registro rico: `actor_id`, `actor_role`, `ip`, `endpoint`, `entity`, `entity_id`, `action`,
`changes` (JSONB com o diff), `occurred_at`, `source='app'`.

**Camada de banco** — triggers `AFTER INSERT/UPDATE/DELETE` nas entidades críticas gravam em
`audit_log` com `source='db'`, capturando `row_to_json(OLD)` e `row_to_json(NEW)`. Os
triggers são criados em migration Alembic e versionados em git.

Entidades cobertas pelas duas camadas: `User`, `Student`, `ClassGroup`, `AttendanceRecord`,
`AbsenceJustification`.

**Imutabilidade da tabela:** `audit_log` é append-only. Nenhum endpoint expõe UPDATE ou
DELETE sobre ela. Em produção, o usuário de aplicação recebe apenas `INSERT` e `SELECT` na
tabela; `UPDATE`/`DELETE` são revogados via `REVOKE`.

**Consulta:** router `audit` estritamente read-only, acessível apenas ao perfil Coordenador.

### Consequências

- **Exceção formal ao Princípio #6** (SQL bruto), delimitada a migrations Alembic. Registrada
  na redação do próprio princípio.
- **O SQLite deixa de ser viável em desenvolvimento** (ADR-018): sem triggers PL/pgSQL, a
  camada de garantia simplesmente não roda em dev, e bugs de auditoria só apareceriam em
  produção.
- Registro duplicado é esperado e desejado — as duas fontes são distinguidas por `source` e
  correlacionadas na consulta. Divergência entre elas é sinal de escrita que escapou da
  aplicação, e é exatamente o que se quer detectar.
- Testes de auditoria exigem PostgreSQL real, não banco em memória.

### Comparação honesta com a v3.4

| Aspecto | v3.4 (pghistory) | v4.0 (híbrida) |
|---|---|---|
| Imutabilidade | Garantida pelo banco | Garantida pelo banco (triggers) |
| Contexto de aplicação | Limitado (via middleware do pghistory) | Rico (usuário, IP, endpoint, motivo) |
| Esforço de implementação | Uma linha por modelo | Listener + trigger + migration + testes |
| Risco de erro de implementação | Baixo (biblioteca madura) | **Médio — código próprio** |

O risco residual é reconhecido: código de auditoria escrito no projeto é menos testado em
campo que uma biblioteca consolidada. A mitigação é cobertura de testes específica para os
cinco modelos críticos, incluindo teste que confirma que uma escrita fora da sessão da
aplicação ainda é capturada pelo trigger.

---

## ADR-013: FastAPI como Único Authorization Server

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: django-allauth + simplejwt
**Decisores**: Coordenador de IC + Dev

### Contexto

A v3.4 usava `django-allauth` para OAuth2 com Google, restrito ao domínio institucional, e
`djangorestframework-simplejwt` para os endpoints de API. Com o pivô, é preciso redefinir
onde a autenticação acontece.

### Problema

O erro clássico deste tipo de arquitetura é distribuir a autenticação entre dois sistemas: o
NextAuth (Auth.js) autenticando o usuário contra o Google no frontend, **e** uma solução como
`fastapi-users` autenticando no backend. O resultado são duas fontes de verdade sobre
identidade, dois armazenamentos de sessão e nenhuma resposta clara para "quem é o dono do
usuário".

Há um agravante decisivo neste projeto: **a justificativa declarada do pivô é viabilizar
aplicativos móveis** (ADR-008). Um aplicativo React Native não consegue usar NextAuth, que é
uma biblioteca do ecossistema Next.js. Se a autenticação morar no frontend web, o cliente
móvel — razão de ser do pivô — precisaria de um fluxo de autenticação completamente separado,
com regras de sessão próprias. O pivô perderia seu próprio propósito.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| NextAuth autenticando direto no Google; backend confia no token | Rapidez de implementação (~1 semana a menos) | **Mobile fica órfão**; backend passa a confiar em token emitido por terceiro para o frontend; sessão presa ao Next.js |
| NextAuth + fastapi-users, ambos completos | Cada camada "resolve o seu" | Duas fontes de verdade; sincronização manual de usuários; fonte garantida de bugs de sessão |
| **FastAPI como único Authorization Server** (adotada) | Uma fonte de verdade; qualquer cliente (web, mobile, integração) usa o mesmo fluxo; controle total sobre a restrição de domínio institucional | ~1 semana a mais de implementação; menos "mágica" pronta |

### Decisão

**O FastAPI é o único Authorization Server do SGA.**

Fluxo:

1. O usuário clica em "Entrar com Google" no Next.js, que redireciona para
   `GET /api/v1/auth/google/login` no FastAPI.
2. O FastAPI (Authlib) conduz o fluxo OAuth2 Authorization Code com o Google.
3. No callback, o FastAPI **valida o domínio institucional do e-mail**, cria ou recupera o
   usuário, e emite:
   - *access token* JWT, validade 15 minutos
   - *refresh token*, validade 7 dias, persistido e revogável
4. **Cliente web**: ambos os tokens são entregues em cookies `httpOnly`, `Secure`,
   `SameSite=Lax`. O JavaScript do Next.js nunca lê o token — proteção contra XSS.
5. **Cliente mobile (futuro)**: os mesmos tokens são retornados no corpo da resposta e
   armazenados no keychain do dispositivo, enviados em `Authorization: Bearer`.
6. `POST /api/v1/auth/refresh` rotaciona o par de tokens. `POST /api/v1/auth/logout` revoga
   o refresh token.

**Se NextAuth (Auth.js) for utilizado no Next.js, é exclusivamente como cliente OIDC
apontando para o próprio SGA** — nunca com o Google como provedor direto.

### Consequências

- Uma única fonte de verdade sobre identidade, para todos os clientes presentes e futuros
- A restrição de domínio institucional é aplicada no servidor, onde não pode ser burlada
- Cookies `httpOnly` exigem atenção a CORS e a `SameSite` na topologia de dois serviços
  (ver `blueprint.md`)
- Refresh tokens exigem tabela própria com revogação — trabalho que o allauth fazia pronto
- Testes de autenticação exigem mock do provedor Google

---

## ADR-014: Console Administrativo em Next.js com SQLAdmin como Ponte Temporária

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Coordenador de IC + Dev

### Contexto

O Django Admin cobria, sem nenhuma linha de código de interface, o CRUD completo de todas as
entidades: usuários, alunos, turmas, professores, disciplinas, registros de chamada e
justificativas. O roadmap v3.4 dependia disso: *"Fase 1 entrega Django Admin funcional para
cadastro"*.

O FastAPI não oferece nada equivalente. Cada tela administrativa passa a exigir endpoint,
schema, tabela, formulário, validação, tratamento de erro e verificação de permissão.

### Problema

Sem mitigação, a coordenação do CAAI ficaria sem qualquer sistema utilizável até
aproximadamente o mês 5 — quando o console em Next.js estivesse pronto. Isso viola
frontalmente o Princípio #7 (Entregue Valor Cedo), que existe precisamente para impedir
longos períodos sem entrega verificável.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Construir as 8 telas independentemente | Nenhuma dependência extra | ~8 semanas de trabalho repetitivo; nenhum usuário real por 5 meses |
| Manter o Django rodando em paralelo só pelo Admin | Admin pronto | Dois backends, dois ORMs, dois esquemas de migração sobre o mesmo banco. Reintroduz exatamente o problema que a ADR-001 evitava |
| **SQLAdmin como ponte + componentes genéricos no Next.js** (adotada) | Cadastro funcional no mês 2; console definitivo construído com reuso | Uma dependência temporária; risco de a "ponte" se tornar permanente |

### Decisão

**Duas medidas combinadas.**

**1. SQLAdmin como andaime temporário (Fase 1).**

`SQLAdmin` é uma interface administrativa para FastAPI construída sobre SQLAlchemy, e
portanto compatível com os modelos SQLModel do projeto. É adotada com restrições estritas:

- Montada em rota protegida, acessível **exclusivamente ao perfil Coordenador**
- Nunca exposta publicamente sem autenticação
- Não recebe customização além do mínimo (`column_list`, `column_searchable_list`)
- Nenhuma regra de negócio é implementada nela

**Cláusula de remoção (vinculante):** o SQLAdmin é removido do projeto ao término da Fase 2.
A remoção é item explícito do checklist de encerramento daquela fase. Se ao fim da Fase 2 o
console em Next.js não cobrir todas as entidades, a decisão de estender a ponte exige nova
ADR — não pode ocorrer por omissão.

**2. Dois componentes genéricos como base do console definitivo.**

Em vez de oito telas independentes, constrói-se uma vez:

| Componente | Base | Equivalente no Django Admin |
|---|---|---|
| `<DataTable />` | TanStack Table + paginação/ordenação/busca server-side | `list_display`, `search_fields`, `list_filter` |
| `<CrudForm />` | React Hook Form + Zod derivado do OpenAPI | `ModelForm` |

Cada nova entidade administrativa passa a custar aproximadamente um dia (um arquivo de
definição de colunas e uma rota), em vez de uma semana.

### Telas administrativas essenciais para o MVP

| Prioridade | Tela | Perfil | Fase |
|---|---|---|---|
| 🔴 | Login e callback OAuth | Todos | 1 |
| 🔴 | Layout do console com guarda de rota por perfil | Todos | 1 |
| 🔴 | CRUD de Usuários (criar, atribuir perfil, desativar) | Coordenador | 1 |
| 🔴 | CRUD de Turmas + vínculo de professores e monitores | Coordenador | 1 |
| 🔴 | CRUD de Alunos + **importação em lote de planilha** | Coordenador | 1 |
| 🟡 | CRUD de Professores e Disciplinas | Coordenador | 1 |
| 🟡 | Visualizador de auditoria (read-only, com filtros) | Coordenador | 1 |
| 🟡 | Correção manual de registro de chamada | Coordenador | 2 |
| 🟡 | Fila de justificativas (aprovar/rejeitar) | Coordenador | 2 |

A importação em lote é marcada como bloqueante: são aproximadamente 90 alunos, e cadastrá-los
individualmente em formulário é inviável na prática.

### Consequências

- O Princípio #7 é preservado: há sistema utilizável a partir do mês 2
- O investimento nos dois componentes genéricos (2 semanas na Fase 1) é o que torna o
  cronograma de escopo total viável
- Risco reconhecido: andaimes temporários tendem a se tornar permanentes. A cláusula de
  remoção com nova ADR obrigatória é a mitigação

---

## ADR-015: Execução de Trabalho Bloqueante Fora do Event Loop

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Dev

### Contexto

O SGA executa duas operações pesadas e CPU-bound: o solver de grade horária (OR-Tools
CP-SAT, 10-60 segundos) e o pipeline de simulados (Pandas + WeasyPrint, 5-120 segundos). Na
v3.4, ambas rodavam de forma síncrona sob WSGI.

### Problema

O Uvicorn executa um event loop assíncrono de thread única por worker. Uma chamada
bloqueante dentro de um endpoint `async def` **não cede o controle do loop** — todas as
demais requisições daquele worker ficam enfileiradas até a operação terminar.

Concretamente: um coordenador gerando a grade horária deixaria todos os monitores sem
conseguir registrar chamada por até um minuto.

Este risco **não existia no Django/WSGI**, onde cada requisição ocupava um worker próprio e
síncrono. É um risco introduzido pelo pivô, e é o tipo de detalhe que uma banca avaliadora
questiona.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| `def` síncrono no lugar de `async def` | O FastAPI joga automaticamente para o threadpool | Funciona, mas consome thread do pool por até 60 s; escala mal; não dá feedback de progresso |
| `run_in_threadpool()` explícito | Simples; controle explícito | Sem feedback de progresso; requisição fica pendurada |
| **`BackgroundTasks` + endpoint de status** (adotada) | Resposta imediata (202); frontend acompanha progresso; loop livre | Exige tabela de status de job |
| Celery + Redis | Solução canônica | **Proibido** (ADR-004): a escala não justifica broker e worker dedicados |
| Processo worker separado no Railway | Isolamento real de CPU | Custo adicional; complexidade de deploy |

### Decisão

**Nenhuma operação bloqueante ou CPU-bound é executada no corpo de um endpoint `async def`.**

Padrão adotado para as duas operações pesadas:

1. `POST /api/v1/schedules/generate` cria um registro em `job` com status `PENDING`, agenda a
   execução com `BackgroundTasks` e retorna **202 Accepted** com o `job_id`
2. A tarefa executa o solver em threadpool e atualiza o `job` para `RUNNING` → `DONE` ou `FAILED`
3. O frontend consulta `GET /api/v1/jobs/{job_id}` via TanStack Query com `refetchInterval`
4. Ao concluir, o resultado fica disponível em `GET /api/v1/schedules/{id}`

Para operações agendadas sem usuário aguardando (sincronização com Classroom, processamento
noturno), usa-se script Typer disparado por Railway Cron — sem passar pela API.

### Cláusula de escalonamento

Se o tempo de solver ultrapassar 5 minutos ou a concorrência de jobs se tornar relevante,
avaliar processo worker dedicado no Railway consumindo a tabela `job` como fila. **Celery e
Redis permanecem proibidos**; a tabela `job` no PostgreSQL já é a fila.

### Consequências

- Tabela `job` e endpoint de status entram no escopo da Fase 3
- A interface precisa de estado de "processando" — é UX melhor que a espera bloqueada da v3.4
- Testes precisam cobrir o caminho assíncrono, não apenas o resultado do solver

---

## ADR-016: Recharts como Biblioteca de Gráficos

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: ADR-005 (revogada)
**Decisores**: Coordenador de IC + Dev

### Contexto

A ADR-005 escolhera Plotly com um argumento explícito: gráficos gerados 100% no backend em
Python, sem JavaScript de charting, renderizados como HTML e injetados via HTMX.

### Problema

**A premissa da ADR-005 deixou de existir.** Com o Next.js, escrever JavaScript não é mais
evitável — é a linguagem da camada de apresentação. O argumento "o dev não precisa escrever
JavaScript para gráficos" perdeu sentido, e com ele toda a base da decisão anterior. A
escolha precisa ser refeita do zero, não adaptada.

Muda também a natureza do dado trafegado: em vez de o backend devolver HTML de um gráfico
pronto, ele passa a devolver **JSON agregado**, e o cliente decide como desenhar. Isso é
consequência direta do Princípio #8 — o contrato expõe dados, não apresentação.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| `react-plotly.js` | Continuidade conceitual; muito poderoso; zoom e pan científicos | ~1 MB no bundle; API imperativa que destoa do React; estilização difícil de casar com Tailwind |
| **Recharts** (adotada) | Componentes React declarativos; leve; combina bem com Tailwind e shadcn/ui; curva de aprendizado curta | Menos recursos para gráficos científicos complexos |
| Chart.js + react-chartjs-2 | Popular; leve | API imperativa via canvas; acessibilidade pior; **proibido desde a v3.4** |
| Visx / D3 | Controle total | Curva de aprendizado alta; excesso de código para gráficos simples |
| Manter Plotly server-side gerando imagens | Sem JS de charting | Perde interatividade; contraria o Princípio #8 |

### Decisão

**Adotar Recharts** como biblioteca única de gráficos do cliente web.

Regra de contrato: os endpoints de dashboard retornam **JSON agregado** — séries de dados
prontas para plotagem, agregadas no PostgreSQL — e nunca HTML, imagem ou configuração de
gráfico. Exemplo: `GET /api/v1/dashboards/exam/{id}/accuracy-by-room` devolve
`[{room: "Sala 1", accuracy: 0.72}, ...]`.

**Matplotlib permanece no backend**, exclusivamente para gráficos estáticos embarcados nos
boletins em PDF gerados por WeasyPrint. São contextos distintos: PDF é imagem, dashboard é
interação.

### Consequências

- A agregação passa a ser responsabilidade explícita do backend (SQL/SQLModel), o que é
  desejável: agregar 90 alunos no cliente seria desperdício de banda e bateria
- Gráficos ficam consistentes com o design system (Tailwind + shadcn/ui)
- Se surgir necessidade de visualização científica complexa (heatmaps densos, 3D), avaliar
  `react-plotly.js` pontualmente naquela tela, com extensão desta ADR — nunca em silêncio

---

## ADR-017: Contrato OpenAPI como Fonte Única dos Tipos TypeScript

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: drf-spectacular
**Relacionada**: Princípio #8
**Decisores**: Dev

### Contexto

A separação em dois aplicativos cria uma fronteira que não existia no monolito. O modo
clássico de falhar numa arquitetura API-First é a divergência silenciosa: o backend renomeia
`full_name` para `name`, o frontend continua lendo `full_name`, tudo compila, e o erro só
aparece em produção como campo vazio na tela.

### Problema

Escrever tipos TypeScript à mão para espelhar os schemas Pydantic significa manter a mesma
informação em dois lugares, em duas linguagens, sem qualquer verificação automática de que
continuam iguais.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Tipos TS escritos à mão | Nenhuma ferramenta extra | Divergência silenciosa garantida com o tempo |
| tRPC | Tipagem end-to-end excelente | Exige backend em TypeScript — incompatível com FastAPI |
| GraphQL | Contrato forte; tipos gerados | Complexidade desproporcional; abandona o REST já modelado |
| **openapi-typescript** (adotada) | Gera tipos do contrato real; verificável no CI; sem mudança de paradigma | Depende de `response_model` bem declarado em todo endpoint |

### Decisão

**O `openapi.json` gerado pelo FastAPI é a fonte única de verdade dos tipos do frontend.**

```
SQLModel (Python) → FastAPI → /openapi.json → openapi-typescript → packages/api-types
                                                                          │
                                                    apps/web importa ─────┘
```

Regras vinculantes:

1. **Todo endpoint declara `response_model` explícito.** Endpoint sem `response_model`
   produz contrato vazio e não passa em code review.
2. Nenhum tipo de dado da API é escrito à mão em TypeScript.
3. A geração roda no CI: se o tipo gerado divergir do commitado, o build falha.
4. Alterações incompatíveis são versionadas em `/api/v2/`. O cliente móvel futuro não pode
   ser quebrado por um deploy do backend — essa proteção é a razão declarada do pivô.
5. O Swagger em `/docs` é a documentação oficial da API, substituindo o drf-spectacular sem
   configuração adicional.

### Consequências

- Renomear um campo no SQLModel quebra o `tsc` do frontend imediatamente, em tempo de build
- A documentação da API nunca desatualiza, porque é derivada do código
- Ganho não trivial para a IC: o contrato OpenAPI é artefato apresentável à banca, e
  evidência objetiva do desacoplamento afirmado

---

## ADR-018: PostgreSQL em Desenvolvimento via Docker (Aposentadoria do SQLite)

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Coordenador de IC + Dev

### Contexto

Desde a v3.1, o SGA usava SQLite em desenvolvimento e PostgreSQL em produção, com a
justificativa de "zero configuração" para o ambiente local.

### Problema

A ADR-012 estabeleceu que a garantia de imutabilidade da auditoria depende de **triggers
PL/pgSQL**. O SQLite não os suporta na mesma forma, e não possui `JSONB`, `row_to_json()`
nem os tipos usados pelo `audit_log`.

Manter SQLite em desenvolvimento significaria que a camada mais crítica do Princípio #5
**não roda no ambiente onde o código é escrito e testado**. Bugs de auditoria só apareceriam
em produção, exatamente onde são mais caros e onde há dados reais de alunos.

Há ainda diferenças conhecidas que já mordem antes disso: SQLite não tem tipos `Enum`
nativos, é permissivo com tipagem, trata constraints e transações de forma distinta, e não
suporta `ON CONFLICT` com a mesma semântica usada no upsert da chamada.

### Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Manter SQLite em dev | Zero configuração | Auditoria não testável localmente; divergência de tipos e constraints; contraria a paridade dev/prod |
| SQLite em dev + Postgres só no CI | Setup local leve | O desenvolvedor descobre a quebra no CI, não ao escrever; pior ciclo de feedback |
| **PostgreSQL 16 via Docker Compose** (adotada) | Paridade total; auditoria testável; um comando para subir | Exige Docker instalado; consumo de memória no ambiente local |

### Decisão

**Aposentar o SQLite do projeto.** O desenvolvimento local usa PostgreSQL 16 em contêiner,
subido por `docker compose up -d`, com a mesma versão maior utilizada em produção no Railway.

Os testes automatizados usam PostgreSQL real (schema dedicado ou testcontainers), não banco
em memória, porque precisam exercitar triggers e constraints reais.

### Consequências

- Uma dependência nova no ambiente de desenvolvimento: Docker
- Paridade dev/produção: constraints, tipos, transações e triggers se comportam igual
- Os testes ficam mais lentos que com banco em memória — trade-off aceito em favor de
  fidelidade, dado que a suíte é pequena na escala do projeto
- A menção a "SQLite (dev)" nos documentos anteriores fica formalmente revogada
