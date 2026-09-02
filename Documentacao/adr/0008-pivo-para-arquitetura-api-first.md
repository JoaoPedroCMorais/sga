---
adr: 008
title: "ADR-008 — Pivô para Arquitetura API-First"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - arquitetura
  - pivo
---

# ADR-008 — Pivô para Arquitetura API-First

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Coordenador de IC (determinante) + Dev

## Contexto

A v3.4 Revisada consolidou uma arquitetura monolítica Django 5 + DRF + HTMX + Bootstrap 5,
com duas fases já entregues: fundação/autenticação (Fase 1) e módulo de chamada (Fase 2),
somando aproximadamente 1.920 linhas de Python distribuídas em três apps (`users`,
`academic`, `attendance`).

O Coordenador de IC determinou a mudança para uma arquitetura API-First desacoplada, com
dois objetivos declarados: escalabilidade e viabilização de aplicativos móveis (React Native
ou Flutter) consumindo a mesma API.

## Problema

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

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Manter o monolito Django (status quo) | Duas fases entregues; uma linguagem; Django Admin de graça; menor prazo | Não atende ao objetivo de mobile; contrato de API parcial; frontend limitado |
| Django + DRF como API pura + Next.js | Aproveita ORM, Admin, allauth e pghistory já implementados; risco muito menor | Mantém peso do Django sem usar suas telas; DRF é mais verboso que FastAPI; não foi a orientação do Coordenador |
| **FastAPI + SQLModel + Next.js** (adotada) | Contrato OpenAPI nativo; tipagem end-to-end; async; mobile viável; maior valor acadêmico | Descarte de ~85-90% do código existente; duas linguagens; perda do Django Admin; perda do pghistory; prazo maior |
| FastAPI + frontend em templates Jinja2 | Menos JavaScript | Não resolve o objetivo de mobile; pior dos dois mundos |

## Decisão

**Adotar arquitetura API-First**, com a pilha definida em `stack.md`:

- **Backend**: FastAPI + Uvicorn
- **ORM e validação**: SQLModel (SQLAlchemy 2.0 + Pydantic v2)
- **Banco**: PostgreSQL 16 (dev via Docker, prod via Railway)
- **Frontend web**: Next.js 15 + Tailwind CSS
- **Contrato**: OpenAPI 3.1 gerado pelo FastAPI, com tipos TypeScript derivados dele

As regras de negócio do CAAI são preservadas integralmente: quatro perfis de acesso, dupla
chamada diária (antes e depois do intervalo), grade horária por CP-SAT, e exigência de
auditoria e rastreabilidade.

## Consequências

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

## Riscos e mitigações

| Risco | Mitigação |
|---|---|
| Prazo estourar por causa da curva de aprendizado dupla | Fase 0 (mês 1) valida a stack ponta a ponta antes de qualquer feature; checkpoint Go/No-Go ao fim da Fase 1 |
| Coordenação ficar sem sistema utilizável por meses | SQLAdmin como ponte na Fase 1 (ADR-014) |
| Auditoria mais fraca que a da v3.4 | Estratégia híbrida com triggers no banco (ADR-012) |
| Autenticação fragmentada entre dois sistemas | FastAPI como único Authorization Server (ADR-013) |

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-007](./0007-excecao-alpinejs-no-modulo-de-chamada.md) | [Índice de ADRs](./README.md) | [ADR-009](./0009-sqlmodel-como-orm-e-validacao.md) |
