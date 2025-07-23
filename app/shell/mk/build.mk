# Makefile for building and managing Press
# This file executes inside the shell container. See docs/redo-mk.md
# for how to run these targets from the host.

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
# docker-make passes these flags to the container; see docs/docker-make.md
override MAKEFLAGS += --warn-undefined-variables  \
                      --no-builtin-rules        \
                      -j16                      \

# Export it so sub-makes see the same flags
# docker-make handles running this file inside Docker; see docs/docker-make.md
export MAKEFLAGS

# Define the Pandoc command used inside the container
#       -T: Don't allocate pseudo-tty. Makes parallel builds work.
# For container setup details, see docs/docker-make.md.
PANDOC_CMD := pandoc
PANDOC_TEMPLATE := src/pandoc-template.html

# Options for generating HTML output with Pandoc
PANDOC_OPTS := \
		--css '/style.css' \
		--standalone \
		-t html \
		--toc \
		--toc-depth=2 \
		--filter pandoc-crossref \
		--template=$(PANDOC_TEMPLATE) \

# Options for generating PDF output with Pandoc
PANDOC_OPTS_PDF := \
		--css "/style.css" \
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

CHECKLINKS_CMD := checklinks

VPATH := src

# Find all Markdown files excluding specified directories
MARKDOWNS := $(shell find src/ -name '*.md')

# Define the corresponding HTML and PDF output files
HTMLS := $(patsubst src/%.md, build/%.html, $(MARKDOWNS))
PDFS := $(patsubst src/%.md, build/%.pdf, $(MARKDOWNS))

# Sort and define build subdirectories based on HTML files
BUILD_SUBDIRS := $(sort $(dir $(HTMLS))) log build/static

CSS := $(wildcard src/*.css)
CSS := $(patsubst src/%.css,build/%.css, $(CSS))

# Define the default target to build everything
.PHONY: all
all: | build $(BUILD_SUBDIRS)
all: $(HTMLS)
all: $(CSS)
all: build/.minify
all: build/static/index.json

.PRECIOUS: build/static/index.json
# See docs/build-index.md for how the index is generated.
build/static/index.json: $(MARKDOWNS) $(YAMLS) | build/static
	build-index src -o $@ 2> log/build-index

# Target to minify HTML and CSS files
build/.minify: $(HTMLS) $(CSS)
	cd build; minify -a -v -r -o . .
	@touch $@

.PHONY: test
# Triggered by the test target in redo.mk; see docs/redo-mk.md.
test: $(HTMLS) $(CSS) | log
	$(CHECKLINKS_CMD) http://nginx-dev 2>&1 | tee log/checklinks.txt

# Create necessary build directories
build: | $(BUILD_SUBDIRS)

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	mkdir -p $@

# Copy CSS files to the build directory
build/%.css: %.css | build
	cp $< $@

# Include and preprocess Markdown files up to three levels deep
# See docs/preprocess.md for preprocessing details
build/%.md: %.md build/static/index.json | build
	preprocess $<

# Generate HTML from processed Markdown using Pandoc
build/%.html: build/%.md $(PANDOC_TEMPLATE) | build
	$(PANDOC_CMD) $(PANDOC_OPTS) -o $@ $<

# Generate PDF from processed Markdown using Pandoc
# include-filter usage is documented in docs/include-filter.md
build/%.pdf: %.md | build
	include-filter build $< build/$*.1.md
	include-filter build build/$*.1.md build/$*.2.md
	include-filter build build/$*.2.md build/$*.3.md
	$(PANDOC_CMD) \
		$(PANDOC_OPTS_PDF) \
		-o $@ \
		build/$*.3.md

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean:
	-rm -rf build

# Optionally include user dependencies; see docs/redo-mk.md.
-include /app/mk/dep.mk

YAMLS := $(shell find src -name "*.yml")

build/picasso.mk: $(YAMLS) | build
	picasso > $@

include build/picasso.mk
