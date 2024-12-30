update:
	uv sync --upgrade
start:
	uv run uvicorn src.main:app --host 127.0.0.1 --port 8000 --reload



# POSTGRESQL

postgres-up:
	docker compose --env-file .env -f docker-compose.postgresql.yml up -d

postgres-down:
	docker compose --env-file .env -f docker-compose.postgresql.yml down

postgres-logs:
	docker compose --env-file .env -f docker-compose.postgresql.yml logs
