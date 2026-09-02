# Princípios Invioláveis do SGA — v4.0 (API-First)

> Estes princípios guiam TODAS as decisões técnicas do projeto.
> Quando duas opções parecem equivalentes, o princípio relevante desempata.
> Versão: 4.0 | Atualizado em: 2026-09-02
> Substitui: `_arquivo_v3_4/principios_v3_4.md`

---

## Nota sobre a revisão

O pivô arquitetural de 02/09/2026 (Django monolítico → API-First) preservou a **intenção**
de todos os sete princípios originais. Dois deles (#5 Auditoria Total e #6 Código Agnóstico
de Banco) tiveram sua redação reescrita porque o *meio de implementação* mudou. Um oitavo
princípio foi acrescentado para governar a nova fronteira criada pela separação
frontend/backend.

| Princípio | Situação após o pivô |
|---|---|
| 1. SSOT | Inalterado |
| 2. Simplicidade Primeiro | Inalterado (exemplos atualizados) |
| 3. Validação na Entrada | Ampliado — agora há duas fronteiras de validação |
| 4. Permissão Padrão é Negar | Inalterado no conceito, reforçado no risco |
| 5. Auditoria Total | **Reescrito** — implementação híbrida |
| 6. Código Agnóstico de Banco | **Reescrito** — SQLModel no lugar do Django ORM |
| 7. Entregue Valor Cedo | Inalterado (com consequência direta no roadmap) |
| 8. O Contrato de API é a Fronteira | **Novo** |

---

## 1. SSOT (Single Source of Truth)

**Todo dado oficial vive no PostgreSQL.**

Fontes externas (EvalBee, Google Sheets, Classroom) são ingeridas, validadas e persistidas
no banco. Nenhuma decisão do sistema depende de dados que não estejam no PostgreSQL.

Implicação prática: se um dado existe numa planilha Google E no banco, a versão do banco é
a verdade. A planilha é apenas uma fonte de ingestão.

**Extensão v4.0 — o frontend não é fonte de verdade.** O Next.js mantém cache de dados
(TanStack Query) e estado de UI, mas nenhum desses é autoritativo. Cache é invalidado, não
consultado como verdade. Nenhuma regra de negócio é decidida no cliente.

---

## 2. Simplicidade Primeiro

**Sempre escolha a solução mais simples que funcione.**

Antes de adicionar uma biblioteca, pergunte: "o FastAPI ou o SQLModel resolvem isso
nativamente? Existe um componente shadcn/ui que resolve?" Se sim, não adicione a
biblioteca. Antes de criar uma abstração, pergunte: "vou usar isso em mais de dois
lugares?" Se não, não abstraia.

Implicação prática na v4.0: comece com SQLAdmin para o CRUD emergencial (ADR-014),
dependências do FastAPI para permissões, filesystem para storage. Adicione complexidade
apenas quando a simplicidade comprovadamente não resolver.

**Aviso específico da nova stack:** o ecossistema JavaScript oferece uma biblioteca para
cada problema. A tentação de instalar é maior aqui do que era no Django. Toda dependência
nova no `package.json` exige a mesma justificativa que uma dependência Python.

---

## 3. Validação na Entrada

**Dados são validados ANTES de qualquer processamento — em ambas as fronteiras.**

A v4.0 tem duas fronteiras de entrada distintas, com ferramentas distintas:

| Fronteira | Ferramenta | O que valida |
|---|---|---|
| **HTTP** (requisições da web e do mobile) | Pydantic v2 / SQLModel | Corpo, query params, path params de cada endpoint |
| **ETL** (planilhas, APIs externas) | Pandera | Schema e tipagem de DataFrames antes do processamento |

Nenhum DataFrame chega ao banco sem ter passado por um schema Pandera. Nenhum payload HTTP
chega a um service sem ter passado por um modelo Pydantic. Dados inválidos são rejeitados
com log no Sentry, nunca silenciados.

Implicação prática: cada pipeline ETL define um `pa.DataFrameSchema`. Cada endpoint declara
seu `response_model` e seus tipos de entrada. Se a validação falha, o processo para e
reporta — nunca insere dados parciais ou corrompidos.

---

## 4. Permissão Padrão é Negar

**Acesso deve ser EXPLÍCITO. Se não foi concedido, está negado.**

Os quatro perfis (Coordenador, Professor, Monitor, Aluno) têm acesso determinado por
dependências de autorização no FastAPI e por filtros aplicados na camada de repositório.
Se um usuário não se enquadra em nenhum perfil autorizado, a consulta retorna vazio e o
endpoint retorna 403.

Implicação prática: todo router declara `dependencies=[Depends(require_role(...))]`. Toda
consulta que retorna dados de alunos passa por um repositório que recebe o usuário
autenticado e filtra por vínculo.

**Risco novo e crítico da v4.0 — IDOR.** No Django, a maior parte do acesso passava por
views renderizadas no servidor; esconder um botão escondia a operação. Numa API REST
pública, **esconder no frontend não esconde nada**. Qualquer pessoa autenticada pode
chamar `GET /api/v1/students/42` diretamente. Portanto:

> Autorização é sempre verificada no endpoint, por objeto, nunca apenas por rota.
> Um professor autenticado que solicita um aluno que não é dele recebe 404 (não 403 —
> para não revelar a existência do recurso).

Nenhuma tela do Next.js é considerada mecanismo de segurança. Ela é conveniência de UX.

---

## 5. Auditoria Total

**Quem fez, quando fez, o que mudou — imutável.**

A v3.4 delegava esse princípio integralmente ao `django-pghistory`, que grava por triggers
no PostgreSQL. Não existe equivalente maduro para SQLModel. A v4.0 adota uma
**estratégia híbrida em duas camadas** (ADR-012):

| Camada | Mecanismo | O que garante |
|---|---|---|
| **Aplicação** | Listeners do SQLAlchemy (`before_flush`) gravando em `audit_log` | Registro rico: usuário autenticado, IP, endpoint, motivo da alteração |
| **Banco** | Triggers PL/pgSQL nas entidades críticas, versionados em migration Alembic | Rede de segurança: captura qualquer escrita que escape da aplicação |

As entidades críticas cobertas pelas duas camadas são: `User`, `Student`, `ClassGroup`,
`AttendanceRecord` e `AbsenceJustification`.

A tabela `audit_log` é **append-only**. Nenhum endpoint do sistema expõe operação de
UPDATE ou DELETE sobre ela. O router `audit` é estritamente read-only e acessível apenas
ao perfil Coordenador.

**Consequência de infraestrutura:** como os triggers são específicos do PostgreSQL, o
ambiente de desenvolvimento passa a usar PostgreSQL via Docker Compose. O SQLite foi
aposentado do projeto (ADR-018).

---

## 6. Código Agnóstico de Banco

**SQLModel e SQLAlchemy Core exclusivamente. Nunca raw SQL na camada de aplicação.**

Todo acesso ao banco a partir do código da aplicação é feito via SQLModel
(`select(Student).where(...)`) ou, quando a expressividade exigir, via SQLAlchemy Core.
Concatenação de strings SQL e `session.execute(text("SELECT ..."))` com interpolação de
variáveis são proibidos — são vetor de SQL injection e quebram a portabilidade.

Isso garante:

- Portabilidade entre versões e instâncias do PostgreSQL
- Consultas parametrizadas por construção (proteção contra injection)
- Reuso dos mesmos modelos como schema de validação Pydantic (ADR-009)
- Migrations gerenciadas por um único sistema (Alembic)

### Exceção documentada — triggers de auditoria

O Princípio #5 exige triggers PL/pgSQL. Isso é SQL específico do PostgreSQL, e portanto uma
exceção formal a este princípio. A exceção é delimitada assim:

**Permitido:** SQL bruto dentro de arquivos de migration Alembic, exclusivamente para
criar, alterar ou remover triggers, funções de trigger e a tabela `audit_log`.

**Proibido:** SQL bruto em routers, services, repositories ou qualquer código executado em
tempo de requisição.

**Justificativa:** a auditoria imutável é um requisito de integridade que só o banco pode
garantir. Um trigger versionado em migration é código revisável, testável e rastreável —
diferente de uma query solta no meio de um service. Ver ADR-012.

### Nota histórica

As versões v3.1 a v3.4 percorreram um caminho não trivial neste princípio: SQLAlchemy foi
especificado, depois rejeitado em favor do Django ORM (ADR-001), e agora retorna sob a
forma de SQLModel (ADR-008, ADR-009). A ADR-001 não estava equivocada: seus quatro
argumentos (incompatibilidade com pghistory, allauth, DRF e Django Admin) eram corretos
enquanto essas quatro dependências existiam. O pivô as eliminou. **O princípio nunca mudou;
mudou o contexto que determinava o melhor meio de realizá-lo.**

---

## 7. Entregue Valor Cedo

**Cada fase entrega algo usável. Não existe "fase de infraestrutura pura".**

Fase 0 entrega um endpoint tipado consumido de ponta a ponta pelo frontend, com CI verde —
prova de que o pivô é executável. Fase 1 entrega o console administrativo, com o qual a
coordenação cadastra alunos e turmas. Fase 2 entrega a chamada mobile. Nenhuma fase termina
sem um usuário real podendo usar algo novo.

**Tensão criada pelo pivô — e como ela foi resolvida.** A v3.4 cumpria este princípio de
graça: o Django Admin dava CRUD funcional na primeira semana. O FastAPI não oferece nada
equivalente, e construir o console em Next.js leva meses. Sem mitigação, a coordenação
ficaria sem sistema utilizável até o mês 5, o que violaria frontalmente este princípio.

A mitigação adotada é o SQLAdmin como ponte descartável na Fase 1 (ADR-014), com cláusula
de remoção explícita ao fim da Fase 2. Este princípio é a razão pela qual essa dependência
temporária foi aceita.

Implicação prática: se uma fase está demorando mais que o checkpoint previsto no roadmap,
pausar, reavaliar escopo e entregar o que estiver pronto. Não acumular dívida técnica para
"compensar depois".

---

## 8. O Contrato de API é a Fronteira

**O OpenAPI é gerado pelo backend e é a única fonte dos tipos do frontend.**

A separação entre `apps/api` e `apps/web` cria uma fronteira que não existia no monolito.
Numa arquitetura API-First, o modo clássico de falhar é a divergência silenciosa: o backend
renomeia um campo, o frontend continua lendo o nome antigo, e o erro só aparece em produção.

Regra: nenhum tipo de dado da API é escrito à mão em TypeScript. O fluxo é sempre

```
SQLModel (Python)  →  /openapi.json (FastAPI)  →  openapi-typescript  →  packages/api-types
```

Implicações práticas:

- Todo endpoint declara `response_model` explícito. Endpoint sem `response_model` não passa
  em code review, porque produz um contrato vazio.
- A geração de tipos roda no CI. Se o tipo gerado diverge do commitado, o build falha.
- Alterações incompatíveis no contrato são versionadas em `/api/v1/`, `/api/v2/`. O app
  mobile futuro não pode ser quebrado por um deploy do backend — é a razão declarada do
  pivô e precisa ser protegida por construção.
- O contrato é documentação viva: `/docs` (Swagger) substitui o que o drf-spectacular fazia,
  sem configuração.

Ver ADR-017.

---

## Referências

- `stack.md` — pilha tecnológica canônica
- `decisoes_arquiteturais.md` — ADRs que fundamentam cada princípio
- `migracao_v3_para_v4.md` — registro do pivô arquitetural
