---
adr: 003
title: "ADR-003 — Filesystem Local (dev) + Supabase Storage S3 (prod)"
status: Mantida
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - storage
---

# ADR-003 — Filesystem Local (dev) + Supabase Storage S3 (prod)

> ### 🔄 Status após o pivô v4.0
> ****Mantida, com adaptação de biblioteca** (2026-09-02)**
>
> A decisão de usar filesystem local nas fases iniciais e Supabase Storage (S3-compatible) em produção permanece vigente. Apenas a biblioteca de acesso muda: `django-storages` dá lugar a `boto3` direto. Ver `stack.md`.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-17
**Status**: Aprovada
**Decisores**: Dev + Coordenador de IC

## Contexto

O blueprint v3.4 original especificava Supabase Storage para todas as fases. A analise arquitetural identificou que nas fases iniciais o filesystem local basta, mas o coordenador de IC orientou manter Supabase Storage para producao.

## Decisao

**Fases 1-4**: Filesystem local (`media/`) servido por WhiteNoise ou Django em dev. Zero config extra. Acelera o MVP sem dependencia de servico externo.

**Fase 5 (producao)**: Supabase Storage via endpoint S3-compatible + `django-storages`. Motivos:
- Supabase agora oferece endpoint S3-compatible, entao `django-storages` funciona nativamente
- Migracao trivial: mudar `DEFAULT_FILE_STORAGE` no `production.py`
- Alinhamento com orientacao do coordenador de IC
- Gratuito ate 1GB (suficiente para o volume do SGA)

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-002](./0002-django-groups-em-vez-de-guardian.md) | [Índice de ADRs](./README.md) | [ADR-004](./0004-cron-em-vez-de-celery.md) |
