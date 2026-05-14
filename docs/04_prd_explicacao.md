# PRD EXPLICAÇÃO — MANIFESTO TÉCNICO

## PROJECT COFRE DIGITAL
### The Why

**Para Recrutadores, Tech Leads e Engenheiros Seniores**  
*v1.0 — Maio 2026*

---

# 1. Propósito deste Documento
Este manifesto explica as decisões de arquitetura do Project Cofre Digital no contexto de demonstração de competências profissionais. Cada escolha técnica foi feita para evidenciar capacidades específicas relevantes para posições sênior de backend, DevOps e segurança.

# 2. Justificativa das Decisões Técnicas

## 2.1 Por que FastAPI?
Alternativas consideradas: Django REST Framework, Flask, Litestar.
Async nativo: FastAPI + asyncio permite que uma única thread gerencie centenas de conexões simultâneas (PostgreSQL, Redis, RabbitMQ) sem bloqueio de CPU — essencial em um sistema I/O-bound.
Pydantic v2: Validação de dados com geração automática de schema OpenAPI — documentação e validação são a mesma coisa.
Injeção de dependências: O sistema Depends do FastAPI viabiliza Clean Architecture sem frameworks de DI externos.

## 2.2 Por que PostgreSQL + Redis? (Dados Reais, Zero Mocks)
Esta é a decisão mais crítica do projeto do ponto de vista de demonstração profissional.
PostgreSQL demonstra: Capacidade de gerenciar integridade transacional (ACID) em logs de auditoria; uso de índices parciais para queries de segredos ativos; migrations versionadas com Alembic.
Redis demonstra: Controle de fluxo real com INCR/EXPIRE para rate limiting; TTL nativo para expiração de segredos; caching de sessão com invalidação granular.
Database Seeding real: Scripts que populam o banco com dados consistentes na inicialização provam que o candidato sabe inicializar um sistema end-to-end — não apenas escrever modelos.

## 2.3 Por que RabbitMQ & EDA?
Alternativas consideradas: Celery+Redis, AWS SQS, APScheduler.
**Deleção assíncrona**: O producer confirma a leitura imediatamente; o consumer processa a deleção física em background — latência do endpoint protegida.
**Transactional Outbox**: Demonstra conhecimento avançado em consistência eventual, garantindo que a mensagem de deleção nunca seja perdida se o banco confirmar a leitura.
**Idempotência**: Implementada via chaves no Redis, garante resiliência contra retentativas de mensagens ou requisições duplicadas.
**Acoplamento fraco**: Adicionar um novo consumidor (ex: SIEM integration) não toca no produtor.

## 2.4 Por que Prometheus + Grafana?
Estas ferramentas só geram valor visual se houver dados reais trafegando pelo sistema:
Métricas custom demonstram: Capacidade de instrumentar código com counters, histograms e gauges — habilidade valorizada em times de Platform Engineering.
Dashboards reais: Com dados de seeding e tráfego simulado, os dashboards mostram curvas reais — não telas vazias.
Alertas configurados: Demonstra conhecimento de SLO/SLA e cultura de observabilidade.

# 3. Diferenciais Profissionais (DevOps & IaC)
*   **Infraestrutura como Código (IaC)**: Provisionamento via Terraform garante reprodutibilidade total do ambiente.
*   **Secrets Management**: Implementação de SOPS/Vault demonstra maturidade em segurança de credenciais do sistema.
*   **Observabilidade Real**: Dashboards que refletem tráfego real e métricas de negócio.


# 4. Decisões de Arquitetura (ADRs)

## ADR-001: Criptografia de Envelope vs. Criptografia Simples
Decisão: Envelope Encryption com DEK por segredo e KEK centralizado.
Motivação: Permite rotação do KEK sem re-encriptar todos os dados; DEK comprometido expõe apenas um segredo.
Trade-off aceito: Complexidade maior no CryptoEngine. Mitigado com testes unitários extensivos.

## ADR-002: PostgreSQL como Single Source of Truth para Auditoria
Decisão: Logs de auditoria gravados diretamente no PostgreSQL, não no Redis.
Motivação: Garantia ACID — um log nunca é perdido por eviction de cache ou restart do Redis.
Trade-off aceito: Latência ligeiramente maior. Mitigado com índices e connection pool configurado.

## ADR-003: Refresh Token como Cookie HttpOnly
Decisão: Refresh Token em cookie HttpOnly + SameSite=Strict; Access Token em memória JS.
Motivação: Inacessível a XSS. Combinação é o padrão recomendado pelo OWASP para SPAs.
Trade-off aceito: Requisita CORS configurado corretamente entre frontend e backend.

# 5. CI/CD Pipeline (DevSecOps)
Trigger: Push em qualquer branch; merge em main requer PR aprovado.
Estágio 1 — Lint & SAST: Ruff (Python) + ESLint (TypeScript) + Bandit (Análise estática de segurança).
Estágio 2 — Secret Scan: Gitleaks para prevenir vazamento de segredos no git.
Estágio 3 — Testes: Pytest em container com PostgreSQL + Redis reais (testcontainers-python).
Estágio 4 — Build & Scan: Docker multi-stage. Scan de vulnerabilidades na imagem via Trivy.
Estágio 5 — IaC Validation: Validação de manifestos Terraform / K8s (tflint / kube-linter).
Estágio 6 — Deploy: Deploy automático em ambiente de staging para validação final.