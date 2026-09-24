.PHONY: setup infra db worker tui run down

setup:
	@if [ ! -f .env ]; then cp .env.template .env; echo "[INFO] .env file created. Please update COLAB_TUNNEL_URL."; fi

infra:
	@echo "[INFO] Starting Docker infrastructure..."
	docker-compose up -d postgres redis
	@echo "[INFO] Waiting for PostgreSQL and Redis to accept connections..."
	sleep 4

db:
	@echo "[INFO] Initializing database state..."
	PYTHONPATH=. python scripts/init_db.py

worker:
	@echo "[INFO] Starting ARQ orchestrator worker..."
	PYTHONPATH=. arq orchestrator.worker.WorkerSettings

tui:
	@echo "[INFO] Starting Textual Front..."
	PYTHONPATH=. python -m front.app

run: setup infra db
	@echo "[INFO] Launching unified environment..."
	@make worker & echo $$! > .worker.pid
	@make tui
	@echo "[INFO] TUI exited. Cleaning up worker process..."
	@if [ -f .worker.pid ]; then kill -15 `cat .worker.pid` 2>/dev/null || true; rm .worker.pid; fi

down:
	@echo "[INFO] Stopping infrastructure..."
	docker-compose down
	@if [ -f .worker.pid ]; then kill -15 `cat .worker.pid` 2>/dev/null || true; rm .worker.pid; fi
