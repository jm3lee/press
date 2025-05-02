# Makefile for building and managing Press

# Define the Pandoc command using Docker Compose
PANDOC_CMD := docker compose run \
			  --rm \
			  -u $(shell id -u) \
			  pandoc

# Options for generating HTML output with Pandoc
PANDOC_OPTS := \
		--css '/style.css' \
		--css '/numbered-headings.css' \
		--standalone \
		-t html \
		--toc \
		--toc-depth=2 \
		--filter pandoc-crossref \
		--template=pandoc-template.html \

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

# Find all Markdown files excluding specified directories
MARKDOWNS := $(shell find . \
	\( -path ./build -o -path ./includes -o -path ./templates \) \
	-prune -o -name '*.md' -print)

# Define the corresponding HTML and PDF output files
HTMLS := $(patsubst %.md, build/%.html, $(MARKDOWNS))
PDFS := $(patsubst %.md, build/%.pdf, $(MARKDOWNS))

# Sort and define build subdirectories based on HTML files
BUILD_SUBDIRS := $(sort $(dir $(HTMLS)))

CSS := $(wildcard *.css)
CSS := $(addprefix build/,$(CSS))

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

# Target to bring up the development Nginx container
.PHONY: up
up:
	docker compose up nginx-dev -d

.PHONY: down
down:
	docker compose down nginx-dev

# Create necessary build directories
build: $(BUILD_SUBDIRS)

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	mkdir -p $@

# Restart the development Nginx container
build:
	docker compose restart nginx-dev

# Copy CSS files to the build directory
build/%.css: %.css
	cp $< $@

# Include and process Markdown files up to three levels deep
build/%.1.md: %.md | build
	includefilter build $< $@

build/%.2.md: build/%.1.md
	includefilter build $< $@

build/%.3.md: build/%.2.md
	includefilter build $< $@
	./bin/emojify < $@ > $$@.tmp && mv $$@.tmp $@

# Generate HTML from processed Markdown using Pandoc
build/%.html: build/%.3.md pandoc-template.html | build
	$(PANDOC_CMD) $(PANDOC_OPTS) -o $@ $<

build/%.html: build/%.3.md pandoc-template.html
	$(PANDOC_CMD) \
		$(PANDOC_OPTS) \
		-o $@ \
		$<

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
	docker system prune

.PHONY: setup
setup:
	docker compose build
