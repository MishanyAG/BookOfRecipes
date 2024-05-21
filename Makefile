include .env

down:
	docker compose down

start: down
	docker compose up --build -d

psql:
	docker exec -it recipes-postgres psql -U $(POSTGRES_USER)

format:
	ruff format .
	ruff check --fix --select I
