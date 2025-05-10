# Makefile for building and managing Press

# Define the Pandoc command using Docker Compose
# 	-T: Don't allocate pseudo-tty. Makes parallel builds work.
PANDOC_CMD := docker compose run \
			  --rm \
			  -T \
			  -u $(shell id -u) \
			  pandoc

PANDOC_TEMPLATE := src/pandoc-template.html

# Options for generating HTML output with Pandoc
PANDOC_OPTS := \
		--css '/style.css' \
		--css '/numbered-headings.css' \
		--standalone \
		-t html \
		--toc \
		--toc-depth=2 \
		--filter pandoc-crossref \
		--template=$(PANDOC_TEMPLATE) \

# Options for generating PDF output with Pandoc
PANDOC_OPTS_PDF := \
		--css "/style.css" \
		--css '/numbered-headings.css' \
		--standalone \
		-t pdf \
		--toc \
		--toc-depth=2 \
		--number-sections \
		--pdf-engine=xelatex \
		--resource-path=build \
		--filter pandoc-crossref \

# Command for minifying HTML files
MINIFY_CMD := minify

EMOJIFY_CMD := docker compose run --rm shell emojify

LINKCHECKER_CMD := docker compose run --rm -T linkchecker

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
all: | build $(BUILD_SUBDIRS)
all: $(HTMLS)
all: $(CSS)

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
docker: .minify
	docker compose build nginx
	#docker tag artistic-anatomy-nginx registry.digitalocean.com/artisticanatomy/book:latest
	#docker push registry.digitalocean.com/artisticanatomy/book:latest

.PHONY: test
test: $(HTMLS)
	$(LINKCHECKER_CMD) build

# Target to bring up the development Nginx container
.PHONY: up
up:
	docker compose up nginx-dev to-webp --build --remove-orphans

.PHONY: upd
upd:
	docker compose up nginx-dev to-webp -d

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

# Copy CSS files to the build directory
build/%.css: %.css
	cp $< $@

# Include and process Markdown files up to three levels deep
build/%.md: %.md | build
	includefilter build $< $@
	includefilter build $< $@
	includefilter build $< $@
	$(EMOJIFY_CMD) < $@ > $@.tmp && mv $@.tmp $@

# Generate HTML from processed Markdown using Pandoc
build/%.html: build/%.md $(PANDOC_TEMPLATE) | build
	$(PANDOC_CMD) $(PANDOC_OPTS) -o $@ $<

# Generate PDF from processed Markdown using Pandoc
build/%.pdf: %.md | build
	includefilter build $< build/$*.1.md
	includefilter build build/$*.1.md build/$*.2.md
	includefilter build build/$*.2.md build/$*.3.md
	$(PANDOC_CMD) \
		$(PANDOC_OPTS_PDF) \
		-o $@ \
		build/$*.3.md

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
