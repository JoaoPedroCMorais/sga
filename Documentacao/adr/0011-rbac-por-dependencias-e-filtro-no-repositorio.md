---
adr: 011
title: "ADR-011 — RBAC por Dependências FastAPI e Filtro no Repositório"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - rbac
  - seguranca
  - idor
---

# ADR-011 — RBAC por Dependências FastAPI e Filtro no Repositório

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: ADR-002
**Decisores**: Dev

## Contexto

A ADR-002 estabeleceu que, no SGA, o acesso é determinado pelo **vínculo no modelo**
(professor→turma, monitor→turma, aluno→si mesmo) e não por permissão atribuída objeto a
objeto, e que por isso Django Groups + queryset filters bastavam.

Esse diagnóstico continua correto. O que desapareceu foi a implementação: não há Django
Groups nem querysets.

## Problema

Numa API REST, o risco de autorização muda de natureza. No monolito, esconder um botão no
template escondia efetivamente a operação, porque não havia outro caminho até ela. Numa API
pública, toda operação é alcançável por requisição direta. Uma verificação apenas na rota
não impede que um professor autenticado leia `GET /api/v1/students/42` de um aluno que não é
dele — a vulnerabilidade conhecida como **IDOR** (Insecure Direct Object Reference).

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| Verificação apenas por dependência de rota | Simples | **Não impede IDOR** — inaceitável |
| Biblioteca de ACL por objeto (Casbin, oso) | Flexível; políticas declarativas | Overhead para 4 perfis determinísticos; repete o erro que a ADR-002 evitou com o guardian |
| **Dependência de rota + filtro no repositório** (adotada) | Duas camadas; sem dependência extra; o filtro fica onde a consulta é montada | Exige disciplina: todo repositório deve receber o usuário autenticado |
| Row-Level Security do PostgreSQL | Garantia no banco | Complexo de testar; exige conexão por usuário; desproporcional para a escala |

## Decisão

**Duas camadas obrigatórias e complementares:**

```python
# Camada 1 — a rota. Protege o endpoint por perfil.
@router.get("/students", response_model=list[StudentRead])
async def list_students(
    user: User = Depends(require_role(Role.COORDENADOR, Role.PROFESSOR, Role.MONITOR)),
    session: AsyncSession = Depends(get_session),
):
    return await student_repo.list_for(session, user)


# Camada 2 — o repositório. Protege o objeto por vínculo.
async def list_for(session: AsyncSession, user: User) -> Sequence[Student]:
    stmt = select(Student)
    if user.role == Role.COORDENADOR:
        pass
    elif user.role == Role.PROFESSOR:
        stmt = stmt.join(ClassGroup).where(ClassGroup.teachers.any(id=user.id))
    elif user.role == Role.MONITOR:
        stmt = stmt.join(ClassGroup).where(ClassGroup.monitors.any(id=user.id))
    elif user.role == Role.ALUNO:
        stmt = stmt.where(Student.user_id == user.id)
    else:
        return []                      # Permissão padrão: NEGAR
    return (await session.exec(stmt)).all()
```

Regras adicionais:

- **Consulta de objeto individual retorna 404, não 403**, quando o objeto existe mas não
  pertence ao usuário. Um 403 confirmaria a existência do recurso e vazaria informação.
- Nenhum endpoint acessa `session.exec(select(Model))` diretamente. Todo acesso passa por um
  repositório que recebe o usuário autenticado.
- Toda entidade que expõe dados de alunos tem teste de permissão para os quatro perfis.

## Cláusula de Revisão

Se durante as Fases 2-3 surgir caso concreto de permissão ad-hoc por objeto individual
(por exemplo, "o professor X pode ver esta turma mas não aquela, mesmo lecionando em ambas"),
reavaliar a adoção de uma biblioteca de políticas. Até lá, a solução mais simples que
funciona é a adotada (Princípio #2).

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-010](./0010-alembic-como-sistema-unico-de-migrations.md) | [Índice de ADRs](./README.md) | [ADR-012](./0012-auditoria-hibrida-listeners-e-triggers.md) |
