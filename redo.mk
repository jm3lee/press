# Makefile for building and managing Press

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
override MAKEFLAGS += --warn-undefined-variables  \
                      --no-builtin-rules        \
                      -j16                      \

# Export it so sub-makes see the same flags
export MAKEFLAGS

# Default services to run
SERVICES := nginx-dev sync to-webp

# Command for minifying HTML files
MINIFY_CMD := minify

CHECKLINKS_CMD := docker compose run --rm -T checklinks

VPATH := src

# Find all Markdown files excluding specified directories
MARKDOWNS := $(shell find src/ -name '*.md')

# Define the corresponding HTML and PDF output files
HTMLS := $(patsubst src/%.md, build/%.html, $(MARKDOWNS))
PDFS := $(patsubst src/%.md, build/%.pdf, $(MARKDOWNS))

# Sort and define build subdirectories based on HTML files
BUILD_SUBDIRS := $(sort $(dir $(HTMLS)))

CSS := $(wildcard src/*.css)
CSS := $(patsubst src/%.css,build/%.css, $(CSS))

# Define the default target to build everything
.PHONY: all
all:
	docker compose run --rm --entrypoint make -u $(shell id -u) -T shell -f /app/mk/build.mk

# Target to minify HTML and CSS files
.minify: $(HTMLS) $(CSS)
	cd build; minify -a -v -r -o . .
	touch .minify

# Docker-related targets
# Initialize Docker authentication and build the Nginx image
# Uncomment the lines below to tag and push the Docker image
# doctl auth init; remove extraneous context as necessary
# doctl registry login
.PHONY: docker
docker: .minify test
	docker compose build nginx
	#docker tag artistic-anatomy-nginx registry.digitalocean.com/artisticanatomy/book:latest
	#docker push registry.digitalocean.com/artisticanatomy/book:latest

.PHONY: test
test: $(HTMLS)
	$(CHECKLINKS_CMD) http://localhost | tee log.test

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

# Create necessary build directories
build: | $(BUILD_SUBDIRS)
	# Restart the development Nginx container since it needs to remount the
	# docker volume to see the newly created build dirs.
	docker compose restart nginx-dev

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	mkdir -p $@

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean:
	-rm -rf build

.PHONY: prune
prune:
	docker system prune -f

.PHONY: setup
setup:
	mkdir -p app/to-webp/input
	mkdir -p app/to-webp/output
	docker compose build

.PHONY: seed
seed:
	docker compose run --build --rm -T seed

.PHONY: sync
sync:
	docker compose run --build --rm -T sync

.PHONY: to-webp
to-webp:
	docker compose run --build --rm -T to-webp

.PHONY: shell
shell:
	docker compose run --build --rm shell
