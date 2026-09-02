---
adr: 013
title: "ADR-013 — FastAPI como Único Authorization Server"
status: Aprovada
era: "v4.0 (API-First)"
tags:
  - adr
  - sga
  - auth
  - seguranca
  - oauth2
---

# ADR-013 — FastAPI como Único Authorization Server

**Data**: 2026-09-02
**Status**: Aprovada
**Substitui**: django-allauth + simplejwt
**Decisores**: Coordenador de IC + Dev

## Contexto

A v3.4 usava `django-allauth` para OAuth2 com Google, restrito ao domínio institucional, e
`djangorestframework-simplejwt` para os endpoints de API. Com o pivô, é preciso redefinir
onde a autenticação acontece.

## Problema

O erro clássico deste tipo de arquitetura é distribuir a autenticação entre dois sistemas: o
NextAuth (Auth.js) autenticando o usuário contra o Google no frontend, **e** uma solução como
`fastapi-users` autenticando no backend. O resultado são duas fontes de verdade sobre
identidade, dois armazenamentos de sessão e nenhuma resposta clara para "quem é o dono do
usuário".

Há um agravante decisivo neste projeto: **a justificativa declarada do pivô é viabilizar
aplicativos móveis** (ADR-008). Um aplicativo React Native não consegue usar NextAuth, que é
uma biblioteca do ecossistema Next.js. Se a autenticação morar no frontend web, o cliente
móvel — razão de ser do pivô — precisaria de um fluxo de autenticação completamente separado,
com regras de sessão próprias. O pivô perderia seu próprio propósito.

## Alternativas Consideradas

| Opção | Prós | Contras |
|---|---|---|
| NextAuth autenticando direto no Google; backend confia no token | Rapidez de implementação (~1 semana a menos) | **Mobile fica órfão**; backend passa a confiar em token emitido por terceiro para o frontend; sessão presa ao Next.js |
| NextAuth + fastapi-users, ambos completos | Cada camada "resolve o seu" | Duas fontes de verdade; sincronização manual de usuários; fonte garantida de bugs de sessão |
| **FastAPI como único Authorization Server** (adotada) | Uma fonte de verdade; qualquer cliente (web, mobile, integração) usa o mesmo fluxo; controle total sobre a restrição de domínio institucional | ~1 semana a mais de implementação; menos "mágica" pronta |

## Decisão

**O FastAPI é o único Authorization Server do SGA.**

Fluxo:

1. O usuário clica em "Entrar com Google" no Next.js, que redireciona para
   `GET /api/v1/auth/google/login` no FastAPI.
2. O FastAPI (Authlib) conduz o fluxo OAuth2 Authorization Code com o Google.
3. No callback, o FastAPI **valida o domínio institucional do e-mail**, cria ou recupera o
   usuário, e emite:
   - *access token* JWT, validade 15 minutos
   - *refresh token*, validade 7 dias, persistido e revogável
4. **Cliente web**: ambos os tokens são entregues em cookies `httpOnly`, `Secure`,
   `SameSite=Lax`. O JavaScript do Next.js nunca lê o token — proteção contra XSS.
5. **Cliente mobile (futuro)**: os mesmos tokens são retornados no corpo da resposta e
   armazenados no keychain do dispositivo, enviados em `Authorization: Bearer`.
6. `POST /api/v1/auth/refresh` rotaciona o par de tokens. `POST /api/v1/auth/logout` revoga
   o refresh token.

**Se NextAuth (Auth.js) for utilizado no Next.js, é exclusivamente como cliente OIDC
apontando para o próprio SGA** — nunca com o Google como provedor direto.

## Consequências

- Uma única fonte de verdade sobre identidade, para todos os clientes presentes e futuros
- A restrição de domínio institucional é aplicada no servidor, onde não pode ser burlada
- Cookies `httpOnly` exigem atenção a CORS e a `SameSite` na topologia de dois serviços
  (ver `blueprint.md`)
- Refresh tokens exigem tabela própria com revogação — trabalho que o allauth fazia pronto
- Testes de autenticação exigem mock do provedor Google

---

## Navegação

| Anterior | Índice | Próxima |
|---|---|---|
| [ADR-012](./0012-auditoria-hibrida-listeners-e-triggers.md) | [Índice de ADRs](./README.md) | [ADR-014](./0014-console-nextjs-com-sqladmin-como-ponte.md) |
