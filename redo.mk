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

# Find all Markdown files excluding specified directories
MARKDOWNS := $(shell find src/ -name '*.md')

# Define the corresponding HTML and PDF output files
HTMLS := $(patsubst src/%.md, build/%.html, $(MARKDOWNS))
PDFS := $(patsubst src/%.md, build/%.pdf, $(MARKDOWNS))

# Sort and define build subdirectories based on HTML files
BUILD_SUBDIRS :=

CSS := $(wildcard src/*.css)
CSS := $(patsubst src/%.css,build/%.css, $(CSS))

MAKE_CMD := docker compose run --rm --entrypoint make -u $(shell id -u) -T --build shell

# Define the default target to build everything
.PHONY: all
all:
	$(MAKE_CMD) -f /app/mk/build.mk

# Docker-related targets
# Initialize Docker authentication and build the Nginx image
# Uncomment the lines below to tag and push the Docker image
# doctl auth init; remove extraneous context as necessary
# doctl registry login
.PHONY: docker
docker: test
	docker compose build nginx
	#docker tag artistic-anatomy-nginx registry.digitalocean.com/artisticanatomy/book:latest
	#docker push registry.digitalocean.com/artisticanatomy/book:latest

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
