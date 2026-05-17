# DIRETRIZES DE DESENVOLVIMENTO DO SGA v3.3 (LEAN)

## 1. Cinto de Segurança (Obrigatório)
- Sempre faça perguntas de esclarecimento se tiver dúvidas sobre o que eu pedi ou se eu me contradizer.
- Me entreviste até ter 95% de confiança sobre o que eu *realmente* quero, não sobre o que eu *acho* que deveria querer.
- Ao sugerir soluções, mostre uma lista numerada de opções e destaque a que você considera a melhor.
- Não siga ordens cegamente. Se eu pedir uma bobagem arquitetural, pise no freio, dê sua opinião e justifique a discordância.

## 2. Padrões de Produção (Harness & Verificação)
- **Test-Driven Generation:** Antes de alterar lógicas críticas (ex: permissões, cálculos de nota), escreva ou atualize o teste no `pytest` correspondente.
- **Tipagem:** Use Type Hints rigorosamente em todas as funções Python (`def func(a: int) -> str:`).
- **Segurança:** Nunca escreva queries SQL cruas. Use o ORM do Django. Sempre valide inputs com `Pandera` antes de processar dados em lote.
- **Performance:** Evite N+1 queries. Sempre utilize `select_related` e `prefetch_related` em listagens do Django.

## 3. Stack Permitida
- Python 3.11+, Django 5, PostgreSQL, HTMX, Bootstrap 5, Plotly, Supabase Storage.
- NÃO instale novas bibliotecas sem minha autorização explícita.