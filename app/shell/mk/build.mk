# Makefile for building and managing Press

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
override MAKEFLAGS += --warn-undefined-variables  \
                      --no-builtin-rules        \
                      -j16                      \

# Export it so sub-makes see the same flags
export MAKEFLAGS

# Define the Pandoc command using Docker Compose
# 	-T: Don't allocate pseudo-tty. Makes parallel builds work.
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
BUILD_SUBDIRS := $(sort $(dir $(HTMLS))) /app/log

CSS := $(wildcard src/*.css)
CSS := $(patsubst src/%.css,build/%.css, $(CSS))

# Define the default target to build everything
.PHONY: all
all: | build $(BUILD_SUBDIRS)
all: $(HTMLS)
all: $(CSS)
all: test

# Target to minify HTML and CSS files
.minify: $(HTMLS) $(CSS)
	cd build; minify -a -v -r -o . .
	touch .minify

.PHONY: test
test: $(HTMLS) | /app/log
	$(CHECKLINKS_CMD) http://nginx-dev | tee /app/log/checklinks.txt

# Create necessary build directories
build: | $(BUILD_SUBDIRS)

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	mkdir -p $@

# Copy CSS files to the build directory
build/%.css: %.css | build
	cp $< $@

# Include and preprocess Markdown files up to three levels deep
build/%.md: %.md | build
	preprocess $<

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

# Optinally include user dependencies.
-include /app/mk/dep.mk
