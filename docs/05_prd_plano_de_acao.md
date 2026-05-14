# PRD PLANO DE AÇÃO — ROADMAP

## PROJECT COFRE DIGITAL
### Sprint-based Execution Plan

**Cronograma de Desenvolvimento com Entregáveis e Definição de Pronto**  
*v1.0 — Maio 2026*

---

# 1. Visão Geral do Roadmap


# 2. Fase 1 — Foundations


## 2.1 Entregáveis
Estrutura de pastas Clean Architecture criada e documentada no README.
docker-compose.yml com PostgreSQL 16, Redis 7, RabbitMQ 3.12 — todos com healthchecks.
**Terraform manifests** para provisionamento de infraestrutura local (Kind/Minikube).
**Configuração Mozilla SOPS / Vault** para gestão das chaves mestras (KEK).
Configuração do PostgreSQL: usuário, banco e extensões (uuid-ossp, pgcrypto) via init script.
Migrations Alembic: Tabelas secrets, users, audit_logs com índices e constraints corretos.
Database Seeding: Script seed.py que cria 2 usuários de teste, 5 segredos com TTLs variados — dados reais no banco desde o primeiro up.
Variáveis de ambiente: .env.example documentado; dotenv carregado via pydantic-settings.
Makefile: Comandos up, down, migrate, seed, test para onboarding rápido.

## 2.2 Definição de Pronto
docker compose up --build executa sem erros.
alembic upgrade head aplica todas as migrations.
python scripts/seed/seed.py popula o banco com dados verificáveis.
psql confirma registros nas tabelas users e secrets.
Redis PING retorna PONG; TTLs dos segredos visíveis com TTL <key>.

# 3. Fase 2 — Core API

## 3.1 Entregáveis
Entidades de domínio: Secret, User, AuditLog — puras, sem imports de FastAPI.
Repositórios: Interfaces ABCs + implementações PostgresSecretRepo e PostgresUserRepo.
**Transactional Outbox Service**: Implementação para garantir atomicidade entre DB e RabbitMQ.
**Idempotency Middleware**: Controle de chaves via Redis para endpoints mutáveis.
Use Cases: CreateSecret (Command), ReadAndDestroySecret (Query/Command), ListUserSecrets (Query).
CryptoEngine: AES-256-GCM com geração de DEK por segredo; HMAC-SHA256 para URLs.
FastAPI Routers: POST /secrets, GET /secrets/{token}, DELETE /secrets/{id}.
Swagger UI: Documentação OpenAPI auto-gerada acessível em /docs.
Testes unitários: CryptoEngine 100% coberto; Use Cases com repositórios mockados.

## 3.2 Definição de Pronto
POST /secrets cria segredo no PostgreSQL; Redis registra TTL.
GET /secrets/{token} retorna segredo e o destrói atomicamente.
Segunda leitura do mesmo token retorna 404.
Pytest: 100% dos testes unitários passando no CI.

# 4. Fase 3 — Security & Infrastructure

## 4.1 Entregáveis
OAuth2 + JWT: Endpoints /auth/register, /auth/token, /auth/refresh, /auth/logout.
Argon2id: Hashing de senhas com parâmetros de custo configuráveis via env.
Rate Limiting: Middleware Redis por (IP + Endpoint); headers X-RateLimit-* na resposta.
Manifests Kubernetes: Deployment, Service, HPA, ConfigMap, Secret para backend + workers.
Testes de integração: Auth flow completo com banco real; rate limit com Redis real.

## 4.2 Definição de Pronto
Registro e login funcionais com tokens JWT válidos.
6ª requisição em 1 minuto retorna HTTP 429 com Retry-After header.
kubectl apply -f k8s/ deploya sem erros em cluster local (minikube/kind).
HPA visível com kubectl get hpa.

# 5. Fase 4 — Async & Observability

## 5.1 Entregáveis
RabbitMQ Producer: Publica evento após leitura de segredo na fila delete_queue.
Delete Worker: Consumer assíncrono processa deleção física; confirma ack após sucesso.
Notify Worker: Consumer da notify_queue; envia webhook (mock) ou log estruturado.
Dead Letter Queue: Configurada com binding; mensagens falhas redirecionadas após 3 tentativas.
Prometheus: Endpoint /metrics expondo todas as métricas customizadas definidas no PRD Backend.
Grafana: 3 dashboards provisionados via JSON (operacional, segurança, infraestrutura).
Sentry: Integrado no FastAPI e no Next.js; alertas de erro 5xx configurados.

## 5.2 Definição de Pronto
Criar e ler um segredo gera métricas visíveis no Grafana em < 30 segundos.
RabbitMQ Management UI mostra filas ativas e mensagens processadas.
DLQ recebe mensagem após simular falha no consumer (kill -9 do processo).
Sentry captura erro 500 artificialmente induzido.

# 6. Fase 5 — Frontend UI

## 6.1 Entregáveis
Projeto Next.js 14: App Router, TypeScript strict, Tailwind CSS com design system.
Secret Creator: Formulário completo com validação, seleção de TTL e exibição única da URL.
Access Portal: Tela de resgate com confirmação de uso único e destruição visual.
Auth Pages: Login e registro com validação em tempo real (react-hook-form + zod).
Audit Dashboard: Lista de segredos ativos com timeline de acessos e ação de revogação.
Axios + Interceptors: Refresh token transparente; tratamento global de erros.
Testes Playwright: Fluxo E2E completo + testes de segurança (duplo acesso, link expirado).

## 6.2 Definição de Pronto
Fluxo end-to-end (criar → compartilhar → resgatar → ver log) funciona via browser.
Segundo acesso ao mesmo link exibe mensagem de erro adequada.
Testes Playwright passando no CI com browser headless.
Lighthouse: Performance > 90, Acessibilidade > 90.

# 7. Fase 6 — The Polish

## 7.1 Entregáveis
README.md: Diagrama de arquitetura (Mermaid), quick start em 3 comandos, decisões documentadas.
ADRs: Architecture Decision Records para as 3 decisões principais (ver PRD Explicação).
CI/CD Pipeline final: Lint → Test → Build → Security Scan → Deploy em GitHub Actions.
ISO 27001 Mock Audit: Evidências coletadas (screenshots Grafana, logs PostgreSQL, scan Trivy).
Swagger documentado: Todos os endpoints com exemplos de request/response e códigos de erro.
CHANGELOG.md: Histórico de versões seguindo Conventional Commits.

## 7.2 Definição de Pronto — Projeto Completo
README permite que um engenheiro sem contexto rode o projeto em < 5 minutos.
CI/CD executa do início ao fim sem intervenção manual.
Nenhuma credencial hardcoded no código (verificado por git-secrets no CI).
Cobertura de testes >= 80% (Pytest coverage report no CI).
Imagem Docker sem CVEs críticos (Trivy report no CI).

# 8. Dependências e Riscos
