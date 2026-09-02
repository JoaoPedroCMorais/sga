---
adr: 017
title: "ADR-017 — Contrato OpenAPI como Fonte Única dos Tipos TypeScript"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - contrato
  - openapi
---

# ADR-017 — Contrato OpenAPI como Fonte Única dos Tipos TypeScript

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: drf-spectacular
**Relacionada**: Princípio #8
**Decisores**: Dev

## Contexto

A separação em dois aplicativos cria uma fronteira que não existia no monolito. O modo
clássico de falhar numa arquitetura API-First é a divergência silenciosa: o backend renomeia
`full_name` para `name`, o frontend continua lendo `full_name`, tudo compila, e o erro só
aparece em produção como campo vazio na tela.

## Problema

Escrever tipos TypeScript à mão para espelhar os schemas Pydantic significa manter a mesma
informação em dois lugares, em duas linguagens, sem qualquer verificação automática de que
continuam iguais.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Tipos TS escritos à mão | Nenhuma ferramenta extra | Divergência silenciosa garantida com o tempo |
| tRPC | Tipagem end-to-end excelente | Exige backend em TypeScript — incompatível com FastAPI |
| GraphQL | Contrato forte; tipos gerados | Complexidade desproporcional; abandona o REST já modelado |
| **openapi-typescript** (adotada) | Gera tipos do contrato real; verificável no CI; sem mudança de paradigma | Depende de `response_model` bem declarado em todo endpoint |

## Decisão

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

## Consequências

- Renomear um campo no SQLModel quebra o `tsc` do frontend imediatamente, em tempo de build
- A documentação da API nunca desatualiza, porque é derivada do código
- Ganho não trivial para a IC: o contrato OpenAPI é artefato apresentável à banca, e
  evidência objetiva do desacoplamento afirmado

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-016](./0016-recharts-como-biblioteca-de-graficos.md) | [Índice de ADRs](./README.md) | [ADR-018](./0018-postgresql-em-dev-via-docker.md) |
