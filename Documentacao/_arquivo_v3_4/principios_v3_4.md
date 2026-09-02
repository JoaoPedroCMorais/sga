# 7 Principios Inviolaveis do SGA

> Estes principios guiam TODAS as decisoes tecnicas do projeto.
> Quando duas opcoes parecem equivalentes, o principio relevante desempata.
> Atualizado em: 2026-05-17

---

## 1. SSOT (Single Source of Truth)

**Todo dado oficial vive no PostgreSQL.**

Fontes externas (EvalBee, Google Sheets, Classroom) sao ingeridas, validadas e persistidas no banco. Nenhuma decisao do sistema depende de dados que nao estejam no PostgreSQL.

Implicacao pratica: se um dado existe numa planilha Google E no banco, a versao do banco e a verdade. A planilha e apenas uma fonte de ingestao.

---

## 2. Simplicidade Primeiro

**Sempre escolha a solucao mais simples que funcione.**

Antes de adicionar uma biblioteca, pergunte: "Django nativo resolve?" Se sim, nao adicione a biblioteca. Antes de criar uma abstracacao, pergunte: "Vou usar isso em mais de 2 lugares?" Se nao, nao abstraia.

Implicacao pratica: comece com Django Admin para CRUD, Django Groups para permissoes, filesystem para storage. Adicione complexidade apenas quando a simplicidade comprovadamente nao resolver.

---

## 3. Validacao na Entrada

**Dados sao validados (Pandera) ANTES de qualquer processamento.**

Nenhum DataFrame chega ao Django sem ter passado por um schema Pandera. Dados invalidos sao rejeitados com log no Sentry, nunca silenciados.

Implicacao pratica: cada pipeline ETL define um `pa.DataFrameSchema` antes de processar. Se a validacao falha, o pipeline para e reporta — nunca insere dados parciais ou corrompidos.

---

## 4. Permissao Padrao e Negar

**Acesso deve ser EXPLICITO. Se nao foi concedido, esta negado.**

Os 4 perfis (Coordenador, Professor, Monitor, Aluno) tem acesso determinado por Django Groups e filtros no queryset. Se um usuario nao pertence a nenhum grupo, `queryset.none()` e retornado.

Implicacao pratica: toda View herda de `LoginRequiredMixin` e filtra o queryset pelo grupo. Nao existe "acesso padrao" — o padrao e ver nada.

---

## 5. Auditoria Total

**Quem fez, quando fez, o que mudou — imutavel.**

django-pghistory registra toda alteracao nos models core via triggers do PostgreSQL. Os logs de auditoria sao imutaveis — nenhum endpoint do sistema permite apagar ou editar logs.

Implicacao pratica: o app `audit/` e read-only. Coordenadores podem consultar o historico, mas ninguem pode alterar.

---

## 6. Codigo Agnostico de Banco

**Django ORM exclusivamente. Nunca raw SQL.**

Todo acesso ao banco e feito via Django ORM (`Model.objects.filter()`, `select_related()`, `prefetch_related()`). Raw SQL (`connection.cursor()`, `Model.objects.raw()`) e proibido.

Isso garante:
- Portabilidade entre SQLite (dev) e PostgreSQL (producao)
- Compatibilidade com django-pghistory (que depende de Django Migrations)
- Compatibilidade com DRF serializers (que esperam Django Models)
- Queries otimizaveis e auditaveis

**Nota historica**: versoes anteriores (v3.1-v3.4) mencionavam SQLAlchemy para este principio. A decisao foi corrigida: o Django ORM ja e database-agnostic, e SQLAlchemy e incompativel com o ecossistema de bibliotecas Django escolhido (pghistory, allauth, guardian, DRF).

---

## 7. Entregue Valor Cedo

**Cada fase entrega algo usavel. Nao existe "fase de infraestrutura pura".**

Fase 1 entrega Django Admin funcional para cadastro. Fase 2 entrega chamada mobile. Fase 3 entrega grade horaria. Nenhuma fase termina sem um usuario real podendo usar algo novo.

Implicacao pratica: se uma fase esta demorando mais que o checkpoint (ex: 3.5 meses para Fase 1), pausar, reavaliar escopo, e entregar o que estiver pronto.
