# Registro de Migração — SGA v3.4 (Django) → v4.0 (API-First)

> Documento de rastreabilidade do pivô arquitetural.
> Destinado ao relatório de Iniciação Científica e à defesa perante a banca avaliadora.
> Data do pivô: 2026-09-02 | Determinação: Coordenador de IC

---

## 1. Resumo executivo

Em 02 de setembro de 2026, por determinação do Coordenador de Iniciação Científica, o
Sistema de Gerenciamento Acadêmico (SGA) do CAAI abandonou a arquitetura monolítica baseada
em Django 5 + Django REST Framework + HTMX + Bootstrap 5 e adotou uma arquitetura
**API-First desacoplada**, composta por uma API em FastAPI e um cliente web em Next.js.

Os objetivos declarados da mudança são escalabilidade e viabilização de aplicativos móveis
consumindo a mesma interface de programação.

O pivô ocorreu com duas das cinco fases do roadmap anterior já entregues, o que implicou
descarte de aproximadamente 85% a 90% do código produzido. As **regras de negócio do CAAI
foram integralmente preservadas**.

---

## 2. Estado do projeto no momento do pivô

### 2.1 Métricas do código descartado

| Métrica | Valor |
|---|---|
| Linhas de Python | ~1.920 |
| Commits | 3 |
| Aplicações Django implementadas | 3 (`users`, `academic`, `attendance`) |
| Migrations | 7 |
| Fases do roadmap v3.4 concluídas | 2 de 5 |
| Tempo de desenvolvimento investido | ~4 meses (maio a setembro de 2026) |

### 2.2 Funcionalidades operantes antes do pivô

| Módulo | Situação |
|---|---|
| Modelo de usuário customizado (e-mail como identificador, campo de perfil) | Implementado e testado |
| Modelos acadêmicos (`ClassGroup`, `Student`) com rastreamento de histórico | Implementados |
| Módulo de chamada com dupla chamada diária | Implementado, com testes de modelo e de view |
| Auditoria via `django-pghistory` | Ativa em 4 modelos |
| Interface de chamada com HTMX e busca local com Alpine.js | Implementada |

### 2.3 Preservação do código anterior

O código Django é marcado com a tag git `v3.4-django-final` antes de sua remoção, e
permanece recuperável no histórico do repositório. A documentação da era Django está
congelada em `Documentacao/_arquivo_v3_4/` e em
`Cerebro/_arquivoV3_django/`.

---

## 3. O que foi preservado

### 3.1 Regras de negócio do CAAI — preservadas integralmente

O pivô é arquitetural, não funcional. Nenhuma regra operacional do curso preparatório foi
alterada.

| Regra | Implementação v3.4 | Implementação v4.0 |
|---|---|---|
| **Quatro perfis de acesso** (Coordenador, Professor, Monitor, Aluno) | Django Groups + filtros de queryset | Dependências FastAPI + filtros no repositório (ADR-011) |
| **Dupla chamada diária** (antes e depois do intervalo, para detectar evasão) | `UniqueConstraint(student, date, period)` | `UNIQUE(student_id, date, period)` — semântica idêntica |
| **Correção de chamada sem duplicação** | `update_or_create()` do Django ORM | `INSERT ... ON CONFLICT DO UPDATE` |
| **Grade horária por otimização** | OR-Tools CP-SAT em `services/solver.py` | OR-Tools CP-SAT, agora executado fora do event loop (ADR-015) |
| **Auditoria e rastreabilidade** | `django-pghistory` | Listeners SQLAlchemy + triggers PL/pgSQL (ADR-012) |
| **Validação de dados na ingestão** | Pandera | Pandera (inalterado) |
| **Permissão padrão é negar** | `queryset.none()` | Repositório retorna vazio + 403/404 no endpoint |

### 3.2 Modelo conceitual de dados

As entidades, seus atributos e seus relacionamentos foram transportados sem alteração
semântica. O que mudou foi a sintaxe de declaração (Django ORM → SQLModel), não a modelagem.

### 3.3 Princípios arquiteturais

Dos sete princípios originais, cinco permaneceram com redação praticamente inalterada. Dois
(#5 Auditoria Total e #6 Código Agnóstico de Banco) tiveram a redação revista porque o meio
de implementação mudou — a **intenção de ambos foi preservada**. Um oitavo princípio foi
acrescentado (O Contrato de API é a Fronteira) para governar a fronteira criada pela
separação. Ver `principios.md`.

### 3.4 Conhecimento acumulado

O registro de implementação do módulo de chamada
(`Cerebro/_arquivoV3_django/Records/02_Modulo_Chamada_Fase2.md`) documenta lições que
permanecem válidas independentemente da stack — notadamente a necessidade de incluir o
período na restrição de unicidade e o padrão de idempotência para correção de lançamentos.
Essas lições foram incorporadas ao planejamento da Fase 2 da v4.0, evitando que os mesmos
erros sejam cometidos duas vezes.

---

## 4. O que foi descartado

| Categoria | Item | Motivo |
|---|---|---|
| Framework | Django 5, DRF | Substituídos por FastAPI (ADR-008) |
| Persistência | Django ORM, Django Migrations | Substituídos por SQLModel + Alembic (ADR-009, ADR-010) |
| Interface administrativa | Django Admin | Sem equivalente — reconstruído (ADR-014) |
| Autenticação | django-allauth, simplejwt | Substituídos por Authlib + PyJWT (ADR-013) |
| Auditoria | django-pghistory | Sem equivalente maduro — reimplementado (ADR-012) |
| Apresentação | Django Templates, Bootstrap 5, HTMX, Alpine.js | Substituídos por Next.js + Tailwind + React |
| Gráficos | Plotly server-side | Substituído por Recharts (ADR-016) |
| Formulários e tabelas | crispy-forms, django-tables2 | Substituídos por React Hook Form + TanStack Table |
| Documentação de API | drf-spectacular | Substituído pelo OpenAPI nativo (ADR-017) |
| Testes | pytest-django | Substituído por pytest + httpx |
| Banco em desenvolvimento | SQLite | Substituído por PostgreSQL em contêiner (ADR-018) |
| Código | ~1.920 linhas de Python, 7 migrations, templates HTML | Reimplementados na nova stack |

---

## 5. As três perdas técnicas mais relevantes

A honestidade sobre o custo é parte do valor acadêmico deste registro. Três perdas são
significativas e foram mitigadas de forma explícita.

### 5.1 Django Admin

**O que se perdeu:** interface administrativa completa, com CRUD, busca, filtros e
paginação para todas as entidades, obtida sem escrever código de interface.

**Impacto:** o Princípio #7 (Entregue Valor Cedo) dependia diretamente disso — o roadmap
v3.4 entregava cadastro funcional na primeira semana. Sem mitigação, a coordenação do CAAI
ficaria sem sistema utilizável até aproximadamente o mês 5.

**Mitigação (ADR-014):** adoção do SQLAdmin como ponte descartável na Fase 1, com cláusula
de remoção vinculante ao fim da Fase 2, combinada à construção de dois componentes genéricos
(`<DataTable />` e `<CrudForm />`) que reduzem o custo de cada tela administrativa
subsequente de uma semana para aproximadamente um dia.

### 5.2 django-pghistory

**O que se perdeu:** auditoria imutável garantida por triggers do PostgreSQL, com
configuração de uma linha por modelo, fornecida por biblioteca madura e testada em campo.

**Impacto:** o Princípio #5 (Auditoria Total) é requisito não negociável do projeto — o
sistema manipula dados de frequência e desempenho de aproximadamente 90 alunos. Não existe
equivalente maduro do pghistory no ecossistema SQLAlchemy/SQLModel; as opções avaliadas
(`sqlalchemy-continuum`, `sqlalchemy-history`) apresentam manutenção irregular e suporte
problemático a operação assíncrona.

**Mitigação (ADR-012):** estratégia híbrida em duas camadas — listeners do SQLAlchemy para o
registro rico de contexto de aplicação, e triggers PL/pgSQL versionados em migration como
rede de segurança no nível do banco. **Risco residual reconhecido:** código de auditoria
próprio é menos testado em campo que biblioteca consolidada; a mitigação é cobertura de
testes específica, incluindo verificação de que escritas fora da sessão da aplicação ainda
são capturadas.

### 5.3 Superfície de linguagens e ferramental

**O que se perdeu:** a simplicidade operacional de um projeto de linguagem única.

**Impacto:** o desenvolvimento passa a exigir Python e TypeScript, dois gerenciadores de
pacotes, dois linters, dois verificadores de tipo e três níveis de teste (API, componente,
E2E). Para um desenvolvedor solo de graduação, o custo em tempo de calendário é substancial —
a estimativa técnica em ritmo constante seria de aproximadamente 13 meses, contra os 9-11
previstos na v3.4.

**Mitigação:** manutenção do escopo integral com cronograma condensado para 10-11 meses via
sprints intensivos em recessos acadêmicos, decisão registrada e com riscos monitorados em
`roadmap.md`. A Fase 0 (mês 1) existe especificamente para validar a viabilidade da stack
dupla antes de qualquer investimento em funcionalidade.

---

## 6. Ganhos obtidos

| Ganho | Descrição | Evidência verificável |
|---|---|---|
| **Múltiplos clientes** | Aplicativos móveis passam a ser viáveis sem duplicação de regra de negócio | Objetivo declarado do pivô; ADR-013 garante que a autenticação também serve o mobile |
| **Contrato formal e completo** | OpenAPI 3.1 gerado automaticamente, cobrindo todo o sistema | `/openapi.json` e `/docs` são artefatos apresentáveis à banca |
| **Tipagem ponta a ponta** | Alteração de campo no backend quebra a compilação do frontend | Verificação automatizada no CI (ADR-017) |
| **Separação de responsabilidades explícita** | Camadas router/service/repository formalmente separadas e verificáveis | `diretorios.md`, seção "Direção das dependências" |
| **Segurança por camadas** | Autorização verificada na rota e por objeto, com testes de IDOR | ADR-011; suíte `test_permissions/` |
| **Documentação sempre atualizada** | Derivada do código, não escrita à mão | Swagger em `/docs` |
| **Valor acadêmico** | Arquitetura desacoplada com contrato formal é objeto de estudo mais substantivo do que um CRUD monolítico | Este documento e o conjunto de 18 ADRs |

---

## 7. Nota metodológica sobre revisão de decisões

Duas decisões formalmente registradas na v3.4 foram revertidas no pivô: a proibição do
SQLAlchemy (ADR-001) e a proibição do Alembic (constante da mesma ADR).

Registra-se explicitamente que **essas decisões não foram erros de análise**. A ADR-001
rejeitou o SQLAlchemy com quatro argumentos concretos: incompatibilidade com
`django-pghistory`, `django-allauth`, `DRF ModelSerializer` e Django Admin. Enquanto essas
quatro dependências existiram no projeto, os argumentos eram corretos e verificáveis. O pivô
eliminou as quatro. O Alembic, por sua vez, era rejeitado por representar um segundo sistema
de migração concorrente ao do Django — sem Django, ele se torna o sistema único.

A distinção é relevante para a defesa perante a banca:

> Uma decisão arquitetural é avaliada pela qualidade do raciocínio no contexto em que foi
> tomada, não pela sua permanência. Reverter uma decisão porque o contexto mudou é prática
> de engenharia; reverter porque o raciocínio era falho é correção de erro. Este projeto
> registra ambas as situações de forma distinta e rastreável.

Essa política é a razão pela qual as ADRs revogadas são preservadas com seu texto original
intacto, recebendo apenas um bloco de status que aponta para a decisão substituta. Ver
`decisoes_arquiteturais.md`.

---

## 8. Correspondência entre roadmaps

| Fase v3.4 | Situação | Fase v4.0 correspondente |
|---|---|---|
| — | — | **Fase 0** — Fundação dupla (nova; valida o pivô) |
| Fase 1 — Fundação, Auth e Qualidade | Entregue em Django; **refeita** | Fase 1 — API Core, Auth e Console Administrativo |
| Fase 2 — Portal do Aluno e Chamada | Entregue em Django; **refeita** | Fase 2 — Chamada Mobile-First e Portal do Aluno |
| Fase 3 — Grade Horária e Voluntários | Não iniciada | Fase 3 — Grade Horária e Voluntários |
| Fase 4 — Simulados e Dashboards | Não iniciada | Fase 4 — Simulados, Boletins e Dashboards |
| Fase 5 — Automação e Deploy | Não iniciada | Fase 5 — Automação, Segurança e Deploy |

O retrabalho concentra-se nas Fases 1 e 2. As Fases 3 a 5 não haviam sido iniciadas e,
portanto, não sofreram descarte — apenas replanejamento de tecnologia.

---

## 9. Documentos afetados pelo pivô

| Documento | Ação | Local |
|---|---|---|
| Stack tecnológica | Reescrita integral | `stack.md` |
| Princípios | Reescrita de 2 de 7; adição de 1 | `principios.md` |
| Blueprint de arquitetura | Reescrita integral; promovido a documento canônico | `blueprint.md` |
| ADRs | 7 marcadas com status; 11 novas | `decisoes_arquiteturais.md` |
| Roadmap | Reescrita integral | `roadmap.md` |
| Estrutura de diretórios | Reescrita integral (monorepo) | `diretorios.md` |
| Diretrizes de desenvolvimento | Reescrita integral | `../CLAUDE.md` |
| Mapa de conteúdo do projeto | Atualização | `../Cerebro/MOCs/SGA — IC.md` |
| Registro do módulo de chamada | Marcado como histórico | `../Cerebro/_arquivoV3_django/Records/` |
| Documentação da era Django | Congelada | `_arquivo_v3_4/` |

---

## 10. Referências

- `stack.md` — pilha tecnológica da v4.0
- `principios.md` — os 8 princípios vigentes
- `blueprint.md` — arquitetura em camadas
- `decisoes_arquiteturais.md` — ADR-001 a ADR-018, com histórico completo
- `roadmap.md` — cronograma e riscos assumidos
- `_arquivo_v3_4/` — documentação congelada da arquitetura anterior
