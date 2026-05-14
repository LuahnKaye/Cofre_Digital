# PRD BACKEND — COFRE DIGITAL CORE

## PROJECT COFRE DIGITAL
### The Engine

**Especificação Técnica de Engenharia de Sistemas**  
*v1.0 — Maio 2026*

---

# 1. Arquitetura e Padrões

## 1.1 Clean Architecture & CQRS
Domain Layer: Entidades puras (Secret, User, AuditLog), sem dependência de frameworks.
Application Layer: Use Cases segregados em **Commands** (CreateSecret, RevokeSecret) e **Queries** (ReadAndDestroySecret, ListAuditLogs).
Infrastructure Layer: Repositórios concretos, adaptadores externos e implementação de **Transactional Outbox**.
Interface Layer: FastAPI Routers e Schemas Pydantic v2 — apenas I/O, sem lógica.

## 1.2 Princípios de Engenharia
SOLID: Single Responsibility em cada Use Case; Dependency Injection via FastAPI Depends.
DRY: Decoradores customizados para rate limiting e auditoria reutilizáveis em qualquer endpoint.
SoC: Criptografia encapsulada no CryptoEngine; Storage encapsulado nos Repositories.

# 2. Módulos Funcionais

## 2.1 Crypto-Engine
Implementa Criptografia de Envelope (Envelope Encryption) com duas camadas de chave:
Data Encryption Key (DEK): Chave AES-256-GCM gerada por segredo, efêmera, nunca persiste em texto puro.
Key Encryption Key (KEK): Chave mestra gerenciada via **Mozilla SOPS** ou **HashiCorp Vault** (integrado via Cloud KMS em produção). Nunca exposta no código.
Geração de URL: HMAC-SHA256 do segredo ID + salt; token de acesso de uso único.


## 2.2 Storage Logic — PostgreSQL + Redis
Esta seção demonstra o gerenciamento real de dados com banco de produção. Não há mocks.
PostgreSQL: Persistência dos segredos cifrados, logs de auditoria (imutáveis) e usuários.
Redis TTL: Cada segredo é registrado no Redis com TTL exato. Expiração nativa do Redis aciona evento.
Database Seeding: Scripts Alembic populam tabelas de referência e criam usuários de teste reais na inicialização do container.
Migrations: Alembic com versioning explícito; rollback documentado para cada migration.


## 2.3 Messaging & EDA (Event-Driven Architecture)
Implementação de arquitetura orientada a eventos para desacoplamento e resiliência:
**Transactional Outbox Pattern**: Garante que eventos de auditoria e deleção sejam publicados no RabbitMQ apenas após o commit bem-sucedido no PostgreSQL.
Fila delete_queue: Consumidor assíncrono processa deleção física após confirmação de leitura.
Fila notify_queue: Worker envia notificações (email/webhook) quando segredo é acessado ou expira.
**Idempotência**: Todos os consumidores de mensagens e endpoints de criação implementam chaves de idempotência para evitar duplicidade.

# 3. Especificação de Segurança

## 3.1 Autenticação e Autorização
OAuth2 com Password Flow (interno) e suporte a Provider Flow (Google OAuth).
JWT Access Token: Expiração de 15 minutos. Minimiza janela de exposição.
Refresh Token: Rotação obrigatória a cada uso. Invalidação imediata no logout.
Hashing de senhas: Argon2id com parâmetros de custo ajustáveis (memory=65536, iterations=3).

## 3.2 Rate Limiting
Implementado diretamente no Redis por par (IP + Endpoint), sem dependência de proxy:
POST /secrets: máximo 10 criações/minuto por IP.
GET /secrets/{id}: máximo 5 leituras/minuto por token (previne brute-force de URLs).
POST /auth/token: máximo 5 tentativas/15min por IP (proteção contra credential stuffing).

## 3.3 Proteções Adicionais
CORS: Whitelist explícita de origens; sem wildcard em produção.
Input Validation: Pydantic v2 com validators customizados; payload máximo de 64KB.
SQL Injection: SQLAlchemy com prepared statements; sem queries raw com interpolação.

# 4. Infraestrutura e DevOps

## 4.1 Docker
Multi-stage build: Estágio builder (dependências + compilação) → estágio runtime (apenas binários).
Imagem base: python:3.12-slim. Resultado final: imagem < 200MB.
Non-root user: Container executa como usuário app (UID 1000), sem privilégios root.
Health check: Endpoint /healthz com verificação de conectividade DB + Redis.

## 4.2 Kubernetes
Deployment: 2 réplicas mínimas com rolling update strategy.
HPA: Escala de 2 a 10 pods com base em CPU (70%) e métrica customizada (req/s via Prometheus).
ConfigMaps + Secrets: Separação rigorosa entre configuração e credenciais com gestão via Terraform e integração Vault/SOPS.
Liveness / Readiness Probes: Independentes; readiness verifica DB, liveness verifica processo.

# 5. Monitoramento e Observabilidade

## 5.1 Métricas Prometheus (4 Golden Signals)
Monitoramento baseado nos 4 Sinais Dourados do SRE:
**Latência**: Histogramas de tempo de resposta por endpoint (P50, P90, P99).
**Tráfego**: Counter de requisições por segundo (throughput).
**Erros**: Taxa de erros 4xx/5xx segmentada por endpoint e motivo.
**Saturação**: Uso de CPU/Memória dos pods e ocupação do connection pool do DB.

## 5.2 Métricas Customizadas de Negócio
aegis_secrets_created_total: Counter de segredos criados (label: user_tier).
aegis_secrets_accessed_total: Counter de acessos bem-sucedidos e falhos.
aegis_secret_ttl_seconds: Histogram de TTLs configurados pelos usuários.
Dashboard Operacional: Taxa de criação, leitura e expiração em tempo real.
Dashboard de Segurança: Tentativas de acesso inválido, rate limit atingido, erros 401/403.
Dashboard de Infraestrutura: CPU/Mem por pod, latência de queries PostgreSQL, hit rate Redis.

## 5.3 Alertas
Latência P95 > 500ms por mais de 2 minutos → alerta crítico.
Taxa de erro 5xx > 1% → alerta crítico.
Redis hit rate < 80% → alerta de aviso.

# 6. Estrutura de Pastas (Clean Architecture)
