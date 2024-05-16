include .env

start:
	docker compose up --build -d

down:
	docker compose down

psql:
	docker exec -it recipes-postgres psql -U $(POSTGRES_USER)