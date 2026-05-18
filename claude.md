# DIRETRIZES DE DESENVOLVIMENTO DO SGA v3.4 (LEAN)

## 1. Regras de Comportamento (Cinto de Segurança)
- **NUNCA** apague arquivos ou rode `migrate` sem me pedir permissão antes.
- Se eu pedir algo que fira os princípios do Django, me avise e sugira a melhor prática.
- Antes de refatorar, faça perguntas de esclarecimento se tiver menos de 95% de certeza.

## 2. Stack e Arquitetura
- **Backend:** Django 5 + Django ORM (NÃO USE SQLALCHEMY).
- **Frontend:** Django Templates + HTMX + Bootstrap 5. Zero SPAs (React/Vue).
- **Banco de Dados:** PostgreSQL.
- **Gráficos:** Plotly (gerado no backend) ou Matplotlib.
- **Auditoria:** django-pghistory.

## 3. Padrões de Código (Harness)
- **Typing:** Use Type Hints em todas as funções (`def get_student(id: int) -> Student:`).
- **Performance:** É ESTRITAMENTE PROIBIDO gerar N+1 queries. Sempre use `select_related` e `prefetch_related` em listagens.
- **Linter:** O código deve passar no `ruff check .` e `ruff format .`.
- **Testes:** Use `pytest-django`. Para cada nova feature crítica, escreva o teste correspondente.

## 4. Permissões (RBAC)
- Acesso padrão é NEGAR.
- Use Django Groups para os 4 perfis: Coordenador, Professor, Monitor, Aluno.
- Filtre os QuerySets baseados no perfil (`if user.groups.filter(name='Professor').exists():`).