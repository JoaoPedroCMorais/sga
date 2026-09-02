---
adr: 002
title: "ADR-002 — Django Groups em vez de django-guardian"
status: Substituída
substituida_por: ADR-011
era: "v3.4 (Django)"
tags:
  - adr
  - sga
  - rbac
  - permissoes
---

# ADR-002 — Django Groups em vez de django-guardian

> ### 🔄 Status após o pivô v4.0
> ****Substituída pela ADR-011** (2026-09-02)**
>
> O diagnóstico central desta ADR permanece integralmente válido: o acesso no SGA é determinado pelo vínculo no modelo, não por permissão atribuída objeto a objeto. O que muda é apenas o mecanismo — Django Groups dão lugar a dependências do FastAPI, e os queryset filters dão lugar a filtros na camada de repositório.
>
> *O texto original abaixo é preservado sem alteração, para rastreabilidade.*


**Data**: 2026-05-17
**Status**: Aprovada (revisavel na Fase 2)
**Decisores**: Dev + Coordenador de IC

## Contexto

O SGA tem 4 perfis fixos de acesso (Coordenador, Professor, Monitor, Aluno). A versao original especificava django-guardian para permissoes object-level.

## Problema

django-guardian brilha quando permissoes sao atribuidas por objeto individual (ex: "Prof. X pode ver a Turma Y especifica"). No SGA:

- **Coordenador** ve tudo — nao precisa de permissao por objeto
- **Professor** ve todas as turmas onde leciona — determinado pelo vinculo `ClassGroup.teachers`, nao por permissao atribuida
- **Monitor** ve a turma onde faz chamada — determinado pelo vinculo `ClassGroup.monitors`
- **Aluno** ve apenas seus proprios dados — filtro `student__user=request.user`

Em todos os casos, o acesso e determinado pelo **vinculo no model**, nao por uma permissao atribuida separadamente. django-guardian adicionaria uma camada de indireção desnecessaria.

## Alternativas Consideradas

| Opcao | Pros | Contras |
|---|---|---|
| django-guardian (status quo) | Flexivel, granular | Overhead para 4 perfis fixos; mais uma tabela de permissoes; curva de aprendizado |
| Django Groups + queryset filters | Simples, nativo, zero dependencia extra | Menos flexivel se surgir caso de permissao ad-hoc |
| Custom permission backend | Maximo controle | Mais codigo para manter |

## Decisao

**Usar Django Groups + filtros no queryset.** Padrao:

```python
def get_queryset(self):
    user = self.request.user
    if user.groups.filter(name='coordenador').exists():
        return self.model.objects.all()
    if user.groups.filter(name='professor').exists():
        return self.model.objects.filter(class_group__teachers=user)
    # ... etc
    return self.model.objects.none()
```

## Clausula de Revisao

Se durante a Fase 2-3 surgir um caso concreto onde permissao por objeto individual e necessaria (ex: "Prof. X pode ver ESTA turma mas nao AQUELA, mesmo lecionando em ambas"), reavaliar a inclusao de django-guardian pontualmente no app afetado.

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-001](./0001-django-orm-em-vez-de-sqlalchemy.md) | [Índice de ADRs](./README.md) | [ADR-003](./0003-storage-filesystem-local-e-supabase-s3.md) |
