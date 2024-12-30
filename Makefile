# POSTGRESQL

postgres-up:
	docker compose --env-file .env -f docker-compose.postgresql.yml up -d

postgres-down:
	docker compose --env-file .env -f docker-compose.postgresql.yml down

postgres-logs:
	docker compose --env-file .env -f docker-compose.postgresql.yml logs
