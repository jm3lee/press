# Makefile for building and managing Press
# This file executes inside the shell container. See dist/docs/redo-mk.md
# for how to run these targets from the host.

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
# docker-make passes these flags to the container; see dist/docs/docker-make.md
override MAKEFLAGS += --warn-undefined-variables  \
                      --no-builtin-rules        \
                      -j16                      \

# Export it so sub-makes see the same flags
# docker-make handles running this file inside Docker; see dist/docs/docker-make.md
export MAKEFLAGS

# Verbosity control
VERBOSE ?= 0
ifeq ($(VERBOSE),1)
Q :=
else
Q := @
endif

# Helper to print status messages
status = @echo "==> $(1)"

# Redis connection settings
REDIS_HOST ?= dragonfly
REDIS_PORT ?= 6379
export REDIS_HOST
export REDIS_PORT

# Define the Pandoc command used inside the container
#       -T: Don't allocate pseudo-tty. Makes parallel builds work.
# For container setup details, see dist/docs/docker-make.md.
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
		--mathjax \
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
all: build/static/index.json
	update-index --host $(REDIS_HOST) --port $(REDIS_PORT) --log=log/update-index src

.PRECIOUS: build/static/index.json
# See dist/docs/build-index.md for how the index is generated.
build/static/index.json: $(MARKDOWNS) $(YAMLS) | build/static
	$(call status,Build index $@)
	$(Q)build-index src -o $@ --log log/build-index

# Target to minify HTML and CSS files
# Modifies file timestamps. The preserve option doesn't seem to work.
build/.minify:
	$(call status,Minify HTML and CSS)
	$(Q)cd build; $(MINIFY_CMD) -a -v -r -o . .
	$(Q)touch $@

.PHONY: test
# Triggered by the test target in redo.mk; see dist/docs/redo-mk.md.
test: build/.minify | log
	$(call status,Run link check)
	$(Q)$(CHECKLINKS_CMD) http://nginx-dev 2>&1 | tee log/checklinks.txt
	$(call status,Check page titles)
	$(Q)check-page-title -x cfg/check-page-title-exclude.yml build

# Create necessary build directories
build: | $(BUILD_SUBDIRS)

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	$(call status,Create directory $@)
	$(Q)mkdir -p $@

# Copy CSS files to the build directory
build/%.css: %.css | build
	$(call status,Copy CSS $<)
	$(Q)cp $< $@

# Include and preprocess Markdown files up to three levels deep
# See dist/docs/preprocess.md for preprocessing details
build/%.md: %.md build/static/index.json | build
	$(call status,Preprocess $<)
	$(Q)preprocess $<

# Generate HTML from processed Markdown using Pandoc
build/%.html: build/%.md $(PANDOC_TEMPLATE) | build
	$(call status,Generate HTML $@)
	$(Q)$(PANDOC_CMD) $(PANDOC_OPTS) -o $@ $<

# Generate PDF from processed Markdown using Pandoc
# include-filter usage is documented in dist/docs/include-filter.md
build/%.pdf: %.md | build
	$(call status,Generate PDF $@)
	$(Q)include-filter build $< build/$*.1.md
	$(Q)include-filter build build/$*.1.md build/$*.2.md
	$(Q)include-filter build build/$*.2.md build/$*.3.md
	$(Q)$(PANDOC_CMD) \
	$(PANDOC_OPTS_PDF) \
		-o $@ \
		build/$*.3.md

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean:
	$(call status,Remove build artifacts)
	$(Q)-rm -rf build

# Optionally include user dependencies; see dist/docs/redo-mk.md.
-include /app/mk/dep.mk

YAMLS := $(shell find src -name "*.yml")

build/picasso.mk: $(YAMLS) | build
	$(call status,Generate picasso rules)
	$(Q)picasso --src src --build build > $@

include build/picasso.mk
