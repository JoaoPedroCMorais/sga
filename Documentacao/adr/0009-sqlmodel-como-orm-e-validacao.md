---
adr: 009
title: "ADR-009 — SQLModel como ORM e Camada de Validação Unificada"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - orm
  - sqlmodel
---

# ADR-009 — SQLModel como ORM e Camada de Validação Unificada

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: ADR-001
**Decisores**: Coordenador de IC + Dev

## Contexto

O pivô (ADR-008) removeu o Django e, com ele, o Django ORM. É preciso escolher a camada de
persistência do FastAPI.

## Problema

A ADR-001 havia rejeitado o SQLAlchemy com quatro argumentos: incompatibilidade com
django-pghistory, django-allauth, DRF ModelSerializer e Django Admin. **Os quatro
desapareceram com o pivô** — nenhuma dessas bibliotecas existe mais no projeto. O quinto
argumento (dois sistemas de migração concorrentes) também deixa de valer, porque sem Django
Migrations o Alembic passa a ser sistema único (ADR-010).

Resta escolher entre SQLAlchemy puro e SQLModel.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| SQLAlchemy 2.0 puro + Pydantic separado | Máximo controle; ecossistema maduro; documentação extensa | Duplicação: cada entidade precisa de um modelo SQLAlchemy e de dois a três schemas Pydantic escritos à mão, mantidos em sincronia manualmente |
| **SQLModel** (adotada) | Um modelo serve como tabela e como base de validação; escrito pelo autor do FastAPI; integração direta com `response_model` | Camada de abstração mais nova, com menos material de referência; casos avançados exigem descer para SQLAlchemy |
| Tortoise ORM | Async nativo; sintaxe familiar a quem vem do Django | Ecossistema menor; Alembic não é o padrão; menos aderente ao FastAPI |
| Peewee / bancos de documentos | — | Descartados: não atendem ao Princípio #1 (SSOT relacional) |

## Decisão

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

## Consequências

- Uma definição de entidade em vez de duas ou três
- `response_model` alimenta o OpenAPI automaticamente, sustentando o Princípio #8
- Alembic gera migrations a partir do metadata do SQLModel (`target_metadata = SQLModel.metadata`)
- A equipe precisa conhecer SQLAlchemy 2.0 para os casos avançados — o SQLModel não isola completamente

## Nota de rastreabilidade

Registra-se explicitamente, para a banca: **a ADR-001 não foi um erro.** Ela foi tomada em
maio de 2026 com premissas corretas para o contexto Django, e é revertida em setembro de
2026 porque o contexto foi alterado por decisão de orientação. Essa é a diferença entre
revisar uma decisão e corrigir uma falha de análise.

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-008](./0008-pivo-para-arquitetura-api-first.md) | [Índice de ADRs](./README.md) | [ADR-010](./0010-alembic-como-sistema-unico-de-migrations.md) |
