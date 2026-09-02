# Arquivo Histórico — SGA v3.4 Revisada (Django)

> **Status: CONGELADO.** Nenhum documento desta pasta deve ser editado.
> Arquivado em: 2026-09-02, por ocasião do pivô arquitetural para a v4.0 (API-First).

---

## Por que esta pasta existe

Em 02/09/2026 o SGA sofreu um pivô arquitetural determinado pelo Coordenador de IC:
a stack monolítica Django 5 + DRF + HTMX + Bootstrap 5 foi substituída por uma
arquitetura API-First desacoplada (Next.js + FastAPI + SQLModel).

Os documentos aqui preservados descrevem a arquitetura **anterior** ao pivô. Eles são
mantidos por três motivos:

1. **Rastreabilidade acadêmica.** O relatório de IC e a defesa perante a banca precisam
   demonstrar que as decisões da v3.4 foram tomadas com fundamento, e que a mudança
   decorreu de alteração de contexto — não de erro de análise.
2. **Auditoria de decisões.** As ADRs da v3.4 continuam sendo o registro formal do
   raciocínio original. As ADRs da v4.0 as referenciam explicitamente.
3. **Recuperação de contexto.** As regras de negócio do CAAI documentadas na v3.4
   (4 perfis de acesso, dupla chamada diária, grade horária) permanecem válidas e
   foram integralmente transportadas para a v4.0.

## Conteúdo

| Arquivo | Descrição |
|---|---|
| `stack_definitiva_v3_4_revisada.md` | Pilha tecnológica Django (substituída por `../stack.md`) |
| `principios_v3_4.md` | 7 princípios na redação Django (substituídos por `../principios.md`) |
| `decisoes_arquiteturais_v3_4.md` | ADR-001 a ADR-006 na redação original (ver `../decisoes_arquiteturais.md`) |
| `roadmap_v3_4_revisado.md` | Roadmap de 5 fases em 9-11 meses (substituído por `../roadmap.md`) |
| `diretorios_v3_4_revisado.md` | Estrutura de apps Django (substituída por `../diretorios.md`) |
| `CLAUDE_v3_4.md` | Diretrizes de desenvolvimento Django |
| `postgres.txt` | **⚠️ Contém credencial em texto plano. Deve ser excluído manualmente.** |

## Documentação vigente

A documentação canônica do projeto está em `Documentacao/` (pasta-mãe desta).
Ver `../migracao_v3_para_v4.md` para o registro completo do pivô.
