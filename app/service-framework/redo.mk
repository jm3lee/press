.PHONY: up
up:
	docker compose up --build

.PHONY: upd
upd:
	docker compose up --build -d

.PHONY: down
down:
	docker compose down

.PHONY: prune
prune:
	docker system prune

.PHONY: setup
setup:
	docker compose build
