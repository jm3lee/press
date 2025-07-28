# Makefile for building and managing Press

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
override MAKEFLAGS += --warn-undefined-variables  \
	              --no-builtin-rules        \
	              -j16                      \

# Export it so sub-makes see the same flags
export MAKEFLAGS

# Containers started when running `up`/`upd`.
# See docs/redo-mk.md for details on targets and variables.
SERVICES := nginx-dev sync webp

VPATH := src

MAKE_CMD := docker compose run --rm --entrypoint make -u $(shell id -u) -T shell

# Verbosity control
VERBOSE ?= 0
ifeq ($(VERBOSE),1)
Q :=
else
Q := @
endif

# Helper to print status messages
status = @echo "==> $(1)"

# Default make target
.DEFAULT_GOAL := all

# Define the default target to build everything
.PHONY: all
all: ## Build the site by invoking /app/mk/build.mk inside the shell container
        $(call status,Build site)
        $(Q)$(MAKE_CMD) -f /app/mk/build.mk VERBOSE=$(VERBOSE)

build: ## Helper target used by other rules
	$(call status,Prepare build directory $@)
	$(Q)mkdir -p $@

# Docker-related targets
# Initialize Docker authentication and build the Nginx image
# Uncomment the lines below to tag and push the Docker image
# doctl auth init; remove extraneous context as necessary
# doctl registry login

CONTAINER_REGISTRY := registry.digitalocean.com/artisticanatomy

.PHONY: docker
docker: test ## Build and push the Nginx image after running test
	$(call status,Build nginx image)
	$(Q)docker compose build nginx
	$(call status,Tag image)
	$(Q)docker tag koreanbriancom-nginx $(CONTAINER_REGISTRY)/koreanbrian.com:latest
	$(call status,Push image)
	$(Q)docker push registry.digitalocean.com/artisticanatomy/koreanbrian.com:latest

.PHONY: test
test: ## Restart nginx-dev and run tests
        $(call status,Run tests)
        $(Q)$(MAKE_CMD) -f /app/mk/build.mk VERBOSE=$(VERBOSE) test

# Target to bring up the development Nginx container
.PHONY: up
up: ## Start development containers defined in SERVICES
	$(call status,Start services $(SERVICES))
	$(Q)docker compose up $(SERVICES) --build --remove-orphans

.PHONY: upd
upd: ## Start development containers in detached mode
	$(call status,Start services $(SERVICES) detached)
	$(Q)docker compose up $(SERVICES) --build --remove-orphans -d

.PHONY: down
down: ## Stop and remove the compose stack
	$(call status,Stop compose stack)
	$(Q)docker compose down

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean: ## Remove everything under build/
	$(call status,Remove build artifacts)
	$(Q)-rm -rf build/*

.PHONY: prune
prune: ## Run docker system prune -f to clean unused resources
	$(call status,Docker prune)
	$(Q)docker system prune -f

.PHONY: setup
setup: ## Build the service framework image and prepare app/webp directories
	$(call status,Build service-framework)
	$(Q)docker compose build service-framework
	$(call status,Prepare webp directories)
	$(Q)mkdir -p app/webp/input
	$(Q)mkdir -p app/webp/output
	$(call status,Build all services)
	$(Q)docker compose build

.PHONY: seed
seed: ## Run the seed container to populate initial data
	$(call status,Seed database)
	$(Q)docker compose run --build --rm -T seed

.PHONY: sync
sync: ## Upload site files to S3 using the sync container
	$(call status,Run sync container)
	$(Q)docker compose run --build --rm -T sync

.PHONY: webp
webp: ## Convert images to webp format
	$(call status,Convert images to webp)
	$(Q)docker compose run --build --rm -T webp

.PHONY: shell
shell: ## Open an interactive shell container
	$(call status,Open shell)
	$(Q)docker compose run --rm --build shell

.PHONY: rmi
rmi: ## Remove Docker images matching press-*
	$(call status,Remove images matching press-*)
	$(Q)./bin/docker-rmi-pattern 'press-*'

.PHONY: help
help: ## List available tasks
	@grep -E '^[a-zA-Z0-9_-]+:.*##' $(MAKEFILE_LIST) | \
	awk -F ':.*##' '{printf "%-10s %s\n", $$1, $$2}'

.PHONY: buildx
buildx: ## Run Docker buildx
	$(call status,Run buildx)
	$(Q)docker buildx build app/shell/


.PHONY: pytest
pytest:
	# Add option -s to see stdout.
	$(call status,Run pytest)
	$(Q)docker compose run --entrypoint pytest --rm shell /press/py/pie/tests

.PHONY: t
t: ## Restart nginx-dev and run tests, ansi colors
        $(call status,Run tests with colors)
        $(Q)docker compose run --entrypoint make --rm shell -f /app/mk/build.mk VERBOSE=$(VERBOSE) test
	$(Q)docker compose run --entrypoint pytest --rm shell /press/py/pie/tests
