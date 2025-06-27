# Makefile for building and managing Press

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
override MAKEFLAGS += --warn-undefined-variables  \
	              --no-builtin-rules        \
	              -j16                      \

# Export it so sub-makes see the same flags
export MAKEFLAGS

# Default services to run
SERVICES := nginx-dev sync webp

VPATH := src

MAKE_CMD := docker compose run --rm --entrypoint make -u $(shell id -u) -T --build shell

# Default make target
.DEFAULT_GOAL := all

# Define the default target to build everything
.PHONY: all
all: ## Build the site by invoking /app/mk/build.mk inside the shell container
	$(MAKE_CMD) -f /app/mk/build.mk

build: ## Helper target used by other rules
	mkdir -p $@

# Docker-related targets
# Initialize Docker authentication and build the Nginx image
# Uncomment the lines below to tag and push the Docker image
# doctl auth init; remove extraneous context as necessary
# doctl registry login

CONTAINER_REGISTRY := registry.digitalocean.com/artisticanatomy

.PHONY: docker
docker: test ## Build and push the Nginx image after running test
	docker compose build nginx
	docker tag koreanbriancom-nginx $(CONTAINER_REGISTRY)/koreanbrian.com:latest
	docker push registry.digitalocean.com/artisticanatomy/koreanbrian.com:latest

.PHONY: test
test: ## Restart nginx-dev and run tests
	docker compose restart nginx-dev
	$(MAKE_CMD) -f /app/mk/build.mk test

# Target to bring up the development Nginx container
.PHONY: up
up: ## Start development containers defined in SERVICES
	docker compose up $(SERVICES) --build --remove-orphans

.PHONY: upd
upd: ## Start development containers in detached mode
	docker compose up $(SERVICES) --build --remove-orphans -d

.PHONY: down
down: ## Stop and remove the compose stack
	docker compose down

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean: ## Remove everything under build/
	-rm -rf build/*

.PHONY: prune
prune: ## Run docker system prune -f to clean unused resources
	docker system prune -f

.PHONY: setup
setup: ## Build the service framework image and prepare app/webp directories
	docker compose build service-framework
	mkdir -p app/webp/input
	mkdir -p app/webp/output
	docker compose build

.PHONY: seed
seed: ## Run the seed container to populate initial data
	docker compose run --build --rm -T seed

.PHONY: sync
sync: ## Upload site files to S3 using the sync container
	docker compose run --build --rm -T sync

.PHONY: webp
webp: ## Convert images to webp format
	docker compose run --build --rm -T webp

.PHONY: shell
shell: ## Open an interactive shell container
	docker compose run --build --rm shell

.PHONY: rmi
rmi: ## Remove Docker images matching press-*
	./bin/docker-rmi-pattern 'press-*'

.PHONY: help
help: ## List available tasks
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | \
	awk -F ':.*##' '{printf "%-10s %s\n", $$1, $$2}'
