---
adr: 007
title: "ADR-007 — Excecao Controlada — Alpine.js no Modulo de Chamada"
status: Obsoleta
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - frontend
---

# ADR-007 — Excecao Controlada — Alpine.js no Modulo de Chamada

> ### 🔄 Status após o pivô v4.0
> ****Obsoleta** (2026-09-02)**
>
> Esta exceção deixou de ter objeto. O React resolve nativamente o caso de uso que motivou a introdução do Alpine.js — filtro local de lista já carregada, sem requisição ao servidor — com `useState` e `Array.filter`. O Alpine.js foi removido do projeto. O raciocínio registrado aqui permanece relevante como precedente metodológico: exceções a uma regra de stack devem ser documentadas com escopo e limites explícitos, nunca adotadas em silêncio.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-20
**Status**: Aprovada
**Decisores**: Dev

## Contexto

A stack v3.4 Revisada proibe Alpine.js globalmente (ver ADR de stack). Toda interatividade de frontend deve ser resolvida com HTMX + Django Templates. Durante a implementacao do modulo de Chamada (Fase 2), surgiu a necessidade de um filtro de busca instantaneo na lista de alunos — o monitor precisa localizar rapidamente um aluno em ~30-40 nomes no celular, com conexao potencialmente instavel (3G/4G).

## Problema

O filtro de busca tem caracteristicas que tornam HTMX inadequado:

- Dados ja estao carregados na pagina (nao ha nada para buscar no servidor)
- Filtragem precisa ser instantanea (keystroke a keystroke)
- Ambiente mobile com 3G/4G instavel (requisicoes ao servidor podem falhar)
- Lista pequena (~30-40 alunos por turma, filtro no cliente e trivial)

HTMX e projetado para interacoes servidor-cliente (request → response → swap). Para filtro puramente local de dados ja carregados, ele exigiria `hx-get` a cada keystroke — latencia perceptivel, sobrecarga no servidor, falha em conexao instavel.

## Alternativas Consideradas

| Opcao | Pros | Contras |
|---|---|---|
| HTMX `hx-get` com debounce | Mantem stack pura | Latencia de rede; falha em 3G; sobrecarga a cada keystroke |
| JavaScript vanilla (`addEventListener`) | Zero dependencias extras | ~15-20 linhas de JS imperativo vs. 3 atributos declarativos; mais propenso a bugs |
| Alpine.js (excecao controlada) | 3 atributos declarativos; zero requisicoes; funciona offline; ~8KB gzipped | Adiciona dependencia; contradiz proibicao geral |
| Nao ter filtro de busca | Zero complexidade | UX inaceitavel — monitor rola manualmente ~40 nomes no celular |

## Decisao

**Usar Alpine.js exclusivamente para o filtro local de busca na tela de chamada** (`take_attendance.html`). O uso e restrito a:

- `x-data="{ query: '' }"` — estado reativo local
- `x-model="query"` — two-way binding no input de busca
- `x-show` — filtrar linhas de alunos no DOM (zero requisicoes)
- `x-transition` — animacao suave

## Justificativa

A proibicao original do Alpine.js foi motivada por evitar fragmentacao do frontend entre Alpine.js e HTMX para interacoes servidor-cliente. Esta excecao nao viola o espirito da proibicao porque:

1. **Escopo ortogonal:** Alpine.js faz filtro local (client-only). HTMX faz toggle de status (client-server). Nao ha sobreposicao.
2. **Principio #2 (Simplicidade Primeiro):** Alpine.js e a solucao mais simples que funciona. 3 atributos HTML vs. 15+ linhas de JS imperativo.
3. **Principio #7 (Entregue Valor Cedo):** Evitar Alpine.js aqui significaria reinventar reatividade declarativa sem ganho funcional.

## Escopo e Limites da Excecao

**Permitido:**
- `x-data`, `x-model`, `x-show`, `x-transition` para filtro local em `take_attendance.html`

**Proibido:**
- Qualquer uso de Alpine.js em outros modulos
- `x-bind`, `x-on` para substituir funcionalidade HTMX
- Chamadas ao servidor via Alpine.js (fetch, $watch com API)
- Gerenciamento de estado complexo (stores, componentes aninhados)

## Clausula de Extensao

Se surgir outra necessidade de filtro local no futuro:
1. Avaliar se HTMX com `hx-get` + debounce e viavel (quando latencia for aceitavel)
2. Se nao for, **estender esta ADR** documentando o novo caso — nao usar Alpine.js silenciosamente

## Consequencias

- Dependencia `alpinejs` adicionada ao template `take_attendance.html` (via CDN, ~8KB gzipped)
- Code review deve rejeitar qualquer uso de Alpine.js fora do escopo definido
- CLAUDE.md do projeto deve incluir nota sobre esta excecao

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-006](./0006-playwright-apenas-na-fase-5.md) | [Índice de ADRs](./README.md) | [ADR-008](./0008-pivo-para-arquitetura-api-first.md) |
