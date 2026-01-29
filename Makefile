.PHONY: up down build logs migrate test lint format clean seed setup-demo

# Docker Compose commands
up:
	docker compose up -d

up-build:
	docker compose up -d --build

down:
	docker compose down

logs:
	docker compose logs -f

logs-api:
	docker compose logs -f api

logs-worker:
	docker compose logs -f worker

logs-frontend:
	docker compose logs -f frontend

# Database commands
migrate:
	docker compose exec api alembic upgrade head

migrate-generate:
	docker compose exec api alembic revision --autogenerate -m "$(MSG)"

migrate-downgrade:
	docker compose exec api alembic downgrade -1

# Shell access
shell-api:
	docker compose exec api bash

shell-worker:
	docker compose exec worker bash

shell-db:
	docker compose exec db mysql -u screening_user -pscreening_pass screening

# Testing
test-api:
	docker compose exec api pytest --cov=app -v

test-worker:
	docker compose exec worker pytest --cov=worker -v

test-frontend:
	docker compose exec frontend npm test

test: test-api test-worker test-frontend

# Code quality
lint-api:
	docker compose exec api ruff check .

lint-worker:
	docker compose exec worker ruff check .

format-api:
	docker compose exec api ruff format .

format-worker:
	docker compose exec worker ruff format .

# Cleanup
clean:
	docker compose down -v
	rm -rf storage/raw/* storage/text/* storage/evidence/*

# Initialize storage directories
init-storage:
	mkdir -p storage/raw storage/text storage/evidence

# Seed sample data
seed:
	docker compose exec api python -m app.seed
	@echo "Sample data created successfully!"

# Full setup
setup: init-storage up-build migrate
	@echo "Setup complete! API: http://localhost:8000, Frontend: http://localhost:3000"

# Full setup with sample data
setup-demo: setup seed
	@echo "Demo setup complete with sample data!"
