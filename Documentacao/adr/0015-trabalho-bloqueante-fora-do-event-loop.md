---
adr: 015
title: "ADR-015 — Execução de Trabalho Bloqueante Fora do Event Loop"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - performance
  - async
---

# ADR-015 — Execução de Trabalho Bloqueante Fora do Event Loop

**Data**: 2026-09-02
**Status**: Aprovada
**Decisores**: Dev

## Contexto

O SGA executa duas operações pesadas e CPU-bound: o solver de grade horária (OR-Tools
CP-SAT, 10-60 segundos) e o pipeline de simulados (Pandas + WeasyPrint, 5-120 segundos). Na
v3.4, ambas rodavam de forma síncrona sob WSGI.

## Problema

O Uvicorn executa um event loop assíncrono de thread única por worker. Uma chamada
bloqueante dentro de um endpoint `async def` **não cede o controle do loop** — todas as
demais requisições daquele worker ficam enfileiradas até a operação terminar.

Concretamente: um coordenador gerando a grade horária deixaria todos os monitores sem
conseguir registrar chamada por até um minuto.

Este risco **não existia no Django/WSGI**, onde cada requisição ocupava um worker próprio e
síncrono. É um risco introduzido pelo pivô, e é o tipo de detalhe que uma banca avaliadora
questiona.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| `def` síncrono no lugar de `async def` | O FastAPI joga automaticamente para o threadpool | Funciona, mas consome thread do pool por até 60 s; escala mal; não dá feedback de progresso |
| `run_in_threadpool()` explícito | Simples; controle explícito | Sem feedback de progresso; requisição fica pendurada |
| **`BackgroundTasks` + endpoint de status** (adotada) | Resposta imediata (202); frontend acompanha progresso; loop livre | Exige tabela de status de job |
| Celery + Redis | Solução canônica | **Proibido** (ADR-004): a escala não justifica broker e worker dedicados |
| Processo worker separado no Railway | Isolamento real de CPU | Custo adicional; complexidade de deploy |

## Decisão

**Nenhuma operação bloqueante ou CPU-bound é executada no corpo de um endpoint `async def`.**

Padrão adotado para as duas operações pesadas:

1. `POST /api/v1/schedules/generate` cria um registro em `job` com status `PENDING`, agenda a
   execução com `BackgroundTasks` e retorna **202 Accepted** com o `job_id`
2. A tarefa executa o solver em threadpool e atualiza o `job` para `RUNNING` → `DONE` ou `FAILED`
3. O frontend consulta `GET /api/v1/jobs/{job_id}` via TanStack Query com `refetchInterval`
4. Ao concluir, o resultado fica disponível em `GET /api/v1/schedules/{id}`

Para operações agendadas sem usuário aguardando (sincronização com Classroom, processamento
noturno), usa-se script Typer disparado por Railway Cron — sem passar pela API.

## Cláusula de escalonamento

Se o tempo de solver ultrapassar 5 minutos ou a concorrência de jobs se tornar relevante,
avaliar processo worker dedicado no Railway consumindo a tabela `job` como fila. **Celery e
Redis permanecem proibidos**; a tabela `job` no PostgreSQL já é a fila.

## Consequências

- Tabela `job` e endpoint de status entram no escopo da Fase 3
- A interface precisa de estado de "processando" — é UX melhor que a espera bloqueada da v3.4
- Testes precisam cobrir o caminho assíncrono, não apenas o resultado do solver

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-014](./0014-console-nextjs-com-sqladmin-como-ponte.md) | [Índice de ADRs](./README.md) | [ADR-016](./0016-recharts-como-biblioteca-de-graficos.md) |
