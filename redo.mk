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

# Define the default target to build everything
.PHONY: all
all:
	$(MAKE_CMD) -f /app/mk/build.mk

build:
	mkdir -p $@

# Docker-related targets
# Initialize Docker authentication and build the Nginx image
# Uncomment the lines below to tag and push the Docker image
# doctl auth init; remove extraneous context as necessary
# doctl registry login

ECR := registry.digitalocean.com/artisticanatomy

.PHONY: docker
docker: test
	docker compose build nginx
	docker tag koreanbriancom-nginx $(ECR)/koreanbrian.com:latest
	docker push registry.digitalocean.com/artisticanatomy/koreanbrian.com:latest

.PHONY: test
test:
	docker compose restart nginx-dev
	$(MAKE_CMD) -f /app/mk/build.mk test

# Target to bring up the development Nginx container
.PHONY: up
up:
	docker compose up $(SERVICES) --build --remove-orphans

.PHONY: upd
upd:
	docker compose up $(SERVICES) --build --remove-orphans -d

.PHONY: down
down:
	docker compose down

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean:
	-rm -rf build

.PHONY: prune
prune:
	docker system prune -f

.PHONY: setup
setup:
	docker compose build service-framework
	mkdir -p app/webp/input
	mkdir -p app/webp/output
	docker compose build

.PHONY: seed
seed:
	docker compose run --build --rm -T seed

.PHONY: sync
sync:
	docker compose run --build --rm -T sync

.PHONY: webp
webp:
	docker compose run --build --rm -T webp

.PHONY: shell
shell:
	docker compose run --build --rm shell

.PHONY: rmi

rmi:
	./bin/docker-rmi-pattern 'press-*'
