---
adr: 004
title: "ADR-004 — django-crontab + Railway Cron Jobs em vez de Celery"
status: Mantida
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - agendamento
---

# ADR-004 — django-crontab + Railway Cron Jobs em vez de Celery

> ### 🔄 Status após o pivô v4.0
> ****Mantida em espírito; mecanismo substituído** (2026-09-02)**
>
> A rejeição a Celery + Redis continua válida e **reforçada**: a escala do SGA não justifica broker dedicado. O django-crontab dá lugar a APScheduler em desenvolvimento e Railway Cron em produção. Atenção: a natureza assíncrona do FastAPI aumenta a tentação de reintroduzir Celery — ela permanece proibida.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-17
**Status**: Aprovada

## Contexto

Versoes anteriores especificavam Celery + Redis para tasks assincronas. A v3.4 simplificou para django-crontab.

## Problema

Celery + Redis exige:
- Servidor Redis rodando continuamente (~$5/mes no Railway)
- Worker Celery rodando como processo separado
- Configuracao de broker, result backend, serializer
- Debugging de tasks distribuidas e muito mais complexo que codigo sincrono

Para a escala do SGA (~90 alunos), nenhuma task justifica essa complexidade.

## Decisao

- **Dev local**: django-crontab para agendamento
- **Producao (Railway)**: Railway Cron Jobs executando management commands Django
- **Se surgir necessidade de task async com feedback** (ex: barra de progresso no upload de simulado): avaliar Django-Q2 (usa PostgreSQL como broker, sem Redis)

## Consequencias

- Nao usar Redis em nenhuma fase
- Pipeline EvalBee roda como management command: `python manage.py process_evalbee <arquivo.xlsx>`
- Sync Classroom roda via cron: `python manage.py sync_classroom` (agendado diariamente)

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-003](./0003-storage-filesystem-local-e-supabase-s3.md) | [Índice de ADRs](./README.md) | [ADR-005](./0005-plotly-em-vez-de-chartjs.md) |
