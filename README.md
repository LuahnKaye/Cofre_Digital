# 🛡️ Cofre Digital — Zero-Knowledge Secret Sharing

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)](https://reactjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![RabbitMQ](https://img.shields.io/badge/RabbitMQ-FF6600?style=for-the-badge&logo=rabbitmq&logoColor=white)](https://www.rabbitmq.com/)
[![Prometheus](https://img.shields.io/badge/Prometheus-000000?style=for-the-badge&logo=prometheus&logoColor=white)](https://prometheus.io/)

**Cofre Digital** é uma plataforma de alta segurança para compartilhamento de segredos que se auto-destroem. Projetada com uma arquitetura **Zero-Knowledge**, onde nem mesmo o administrador do servidor tem acesso aos dados descriptografados.

---

## 🏗️ Arquitetura do Sistema

```mermaid
graph TD
    subgraph "Client Side (Navegador)"
        A[User Input] --> B[Criptografia AES-256]
        B --> C{Link Gerado}
        C -->|Fragmento #| D[Chave de Decifração]
        C -->|Payload Cifrado| E[API Backend]
    end

    subgraph "Backend (FastAPI)"
        E --> F[Middleware: Rate Limit & Idempotência]
        F --> G[Envelope Encryption: AES-GCM]
        G --> H[(PostgreSQL 16)]
        G --> I[Transactional Outbox]
        I --> J[(RabbitMQ)]
    end

    subgraph "Asynchronous Workers"
        J --> K[Worker: Deleção Física]
        J --> L[Worker: Auditoria de Acesso]
        K --> H
    end

    subgraph "Observabilidade"
        E --> M[Prometheus Metrics]
        M --> N[(Grafana Dashboards)]
    end
```

---

## 🔒 Segurança de Nível Enterprise

1.  **Zero-Knowledge Architecture**: O segredo é cifrado no cliente antes do envio. A chave viaja na URL como um fragmento (`#`), que nunca é enviado ao servidor pelo navegador.
2.  **Criptografia de Envelope**: No servidor, os dados já cifrados recebem uma segunda camada de proteção (AES-256-GCM) com chaves mestras geradas por segredo.
3.  **Destruição Atômica**: O sistema garante que, após o limite de acessos ou expiração, os dados sejam fisicamente removidos do banco e do cache via workers assíncronos.
4.  **Transactional Outbox Pattern**: Garante a consistência eventual perfeita; um evento de deleção nunca é perdido, mesmo se o broker (RabbitMQ) estiver temporariamente fora do ar.

---

## 🚀 Como Iniciar

### Pré-requisitos
*   Docker & Docker Compose
*   Python 3.12+ (opcional para rodar local)

### Quick Start (3 Comandos)

```bash
# 1. Subir toda a infraestrutura (DB, Cache, Broker, Metrics)
make up

# 2. Popular banco com dados de teste
make seed

# 3. Iniciar o Frontend
make frontend-dev
```

Acesse:
*   **App**: [http://localhost:5174](http://localhost:5174)
*   **API Docs**: [http://localhost:54321/docs](http://localhost:54321/docs)
*   **Monitoramento**: [http://localhost:3000](http://localhost:3000) (admin/admin)

---

## 📊 Observabilidade (Golden Signals)

O sistema expõe métricas nativas para o Prometheus focadas nos 4 Golden Signals:
*   **Latência**: Tempo de resposta por endpoint.
*   **Tráfego**: Volume de requisições.
*   **Erros**: Taxa de falhas 4xx/5xx.
*   **Saturação**: Uso de recursos do sistema.

---

## 🛠️ Tecnologias Utilizadas

*   **Backend**: Python, FastAPI, SQLAlchemy, Alembic.
*   **Frontend**: React, Vite, Framer Motion, Lucide.
*   **Infra**: PostgreSQL, Redis, RabbitMQ.
*   **Observability**: Prometheus, Grafana.

---

Desenvolvido com ❤️ para portfólios de alta performance.
