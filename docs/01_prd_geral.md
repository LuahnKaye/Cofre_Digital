# PRD GERAL — VISÃO DO PRODUTO

## PROJECT COFRE DIGITAL
### Plataforma de Custódia de Segredos Efêmeros

**Documento de Visão de Produto e Estratégia Técnica**  
*v1.0 — Maio 2026*

---

# 1. Resumo Executivo
O Project Cofre Digital é uma plataforma enterprise-grade de custódia de segredos efêmeros. Permite que indivíduos e sistemas troquem informações altamente sensíveis — senhas, chaves privadas, segredos industriais e tokens de acesso — de forma segura, com destruição garantida após consumo e rastreabilidade total de cada acesso via logs de auditoria imutáveis.


# 2. Problema de Negócio
O compartilhamento de credenciais via canais inseguros (Slack, WhatsApp, E-mail) é o principal vetor de vazamento de dados corporativos. Estudos do setor apontam que mais de 60% dos incidentes de segurança envolvem credenciais expostas em canais de comunicação não criptografados.

## 2.1 Dores Mapeadas
Credenciais enviadas em texto puro por e-mail ou mensageiros sem controle de expiração.
Ausência de rastreabilidade: impossível saber quem acessou qual segredo e quando.
Segredos que 'vivem para sempre' em históricos de chat, aumentando a superfície de ataque.
Processos de onboarding inseguros: senhas iniciais enviadas por canais corporativos não protegidos.

# 3. Usuários-Alvo e Casos de Uso


# 4. Tech Stack Completa

## 4.1 Backend
Linguagem: Python 3.12 com type hints completos em todo o codebase.
Framework: FastAPI — suporte nativo a async/await, ideal para I/O-bound workloads.
Banco de Dados: PostgreSQL 16 — garantia ACID para logs de auditoria imutáveis.
Cache / Rate-Limit: Redis 7 — controle de fluxo em memória e TTL de segredos.
Mensageria: RabbitMQ — filas para deleção assíncrona e notificações de expiração.
ORM / Migrations: SQLAlchemy + Alembic — controle versionado do schema.

## 4.2 Frontend
Framework: Next.js 14 (App Router) + TypeScript — SSR e segurança aprimorada.
Estilização: Tailwind CSS com dark mode nativo e acessibilidade WCAG 2.1.
State Management: React Context + Custom Hooks — sem dependências externas desnecessárias.

## 4.3 Infraestrutura e Observabilidade
Containerização: Docker com multi-stage builds — imagens < 200MB.
Orquestração: Kubernetes com HPA (Horizontal Pod Autoscaler).
Monitoramento: Prometheus (métricas) + Grafana (dashboards) + Sentry (erros).
CI/CD: GitHub Actions com testes automatizados em containers isolados.

# 5. Success Metrics (KPIs / SLOs)


# 6. Conformidade e Segurança
O projeto foi desenhado com controles alinhados à ISO 27001:2022:
Controle A.8.24 — Uso de criptografia: AES-256-GCM para dados em repouso, TLS 1.3 em trânsito.
Controle A.8.15 — Log de eventos: Registro imutável de criação, acesso e deleção de segredos.
Controle A.5.17 — Autenticação: OAuth2 + JWT com Refresh Tokens e expiração curta.
Controle A.8.6 — Gestão de capacidade: HPA com métricas customizadas no Prometheus.