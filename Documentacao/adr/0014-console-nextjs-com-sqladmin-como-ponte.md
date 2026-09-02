---
adr: 014
title: "ADR-014 — Console Administrativo em Next.js com SQLAdmin como Ponte Temporária"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - produto
  - admin
  - frontend
---

# ADR-014 — Console Administrativo em Next.js com SQLAdmin como Ponte Temporária

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Coordenador de IC + Dev

## Contexto

O Django Admin cobria, sem nenhuma linha de código de interface, o CRUD completo de todas as
entidades: usuários, alunos, turmas, professores, disciplinas, registros de chamada e
justificativas. O roadmap v3.4 dependia disso: *"Fase 1 entrega Django Admin funcional para
cadastro"*.

O FastAPI não oferece nada equivalente. Cada tela administrativa passa a exigir endpoint,
schema, tabela, formulário, validação, tratamento de erro e verificação de permissão.

## Problema

Sem mitigação, a coordenação do CAAI ficaria sem qualquer sistema utilizável até
aproximadamente o mês 5 — quando o console em Next.js estivesse pronto. Isso viola
frontalmente o Princípio #7 (Entregue Valor Cedo), que existe precisamente para impedir
longos períodos sem entrega verificável.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Construir as 8 telas independentemente | Nenhuma dependência extra | ~8 semanas de trabalho repetitivo; nenhum usuário real por 5 meses |
| Manter o Django rodando em paralelo só pelo Admin | Admin pronto | Dois backends, dois ORMs, dois esquemas de migração sobre o mesmo banco. Reintroduz exatamente o problema que a ADR-001 evitava |
| **SQLAdmin como ponte + componentes genéricos no Next.js** (adotada) | Cadastro funcional no mês 2; console definitivo construído com reuso | Uma dependência temporária; risco de a "ponte" se tornar permanente |

## Decisão

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

## Telas administrativas essenciais para o MVP

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

## Consequências

- O Princípio #7 é preservado: há sistema utilizável a partir do mês 2
- O investimento nos dois componentes genéricos (2 semanas na Fase 1) é o que torna o
  cronograma de escopo total viável
- Risco reconhecido: andaimes temporários tendem a se tornar permanentes. A cláusula de
  remoção com nova ADR obrigatória é a mitigação

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-013](./0013-fastapi-como-unico-authorization-server.md) | [Índice de ADRs](./README.md) | [ADR-015](./0015-trabalho-bloqueante-fora-do-event-loop.md) |
