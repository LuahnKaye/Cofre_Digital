# Makefile para o Projeto Cofre Digital

.PHONY: up down restart migrate seed test logs shell metrics frontend-dev

# Gerenciamento de Infra (Docker)
up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

# Banco de Dados e Migrations
migrate:
	cd apps/backend && alembic upgrade head

seed:
	python apps/backend/scripts/seed.py

# Testes
test:
	pytest apps/backend/tests

# Observabilidade
logs:
	docker compose logs -f

metrics:
	@echo "Acessando métricas do Prometheus..."
	curl http://localhost:54321/metrics

# Desenvolvimento
frontend-dev:
	cd apps/frontend && npm run dev

backend-dev:
	cd apps/backend/src && python main.py

# Utilitários
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
