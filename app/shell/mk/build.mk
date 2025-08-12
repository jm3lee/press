# Makefile for building and managing Press
# This file executes inside the shell container. See docs/guides/redo-mk.md
# for how to run these targets from the host.

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
# docker-make passes these flags to the container; see docs/guides/docker-make.md
override MAKEFLAGS += --warn-undefined-variables  \
                      --no-builtin-rules        \
                      -j16                      \
                      --no-print-directory      \

# Export it so sub-makes see the same flags
# docker-make handles running this file inside Docker; see docs/guides/docker-make.md
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

# Directories
SRC_DIR   := src
BUILD_DIR := build
LOG_DIR   := log
CFG_DIR   := cfg

# Define the Pandoc command used inside the container
#       -T: Don't allocate pseudo-tty. Makes parallel builds work.
# For container setup details, see docs/guides/docker-make.md.
PANDOC_CMD := pandoc
PANDOC_TEMPLATE := $(SRC_DIR)/pandoc-template.html

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
                --resource-path=$(BUILD_DIR) \
                --filter pandoc-crossref \

# Command for minifying HTML files
MINIFY_CMD := minify

CHECKLINKS_CMD := checklinks

VPATH := $(SRC_DIR)

# Find all Markdown files excluding specified directories
MARKDOWNS := $(shell find $(SRC_DIR)/ -name '*.md')
YAMLS := $(shell find $(SRC_DIR) -name "*.yml")

# Define the corresponding HTML and PDF output files
HTMLS := $(patsubst $(SRC_DIR)/%.md, $(BUILD_DIR)/%.html, $(MARKDOWNS))
PDFS := $(patsubst $(SRC_DIR)/%.md, $(BUILD_DIR)/%.pdf, $(MARKDOWNS))

# Sort and define build subdirectories based on HTML files
BUILD_SUBDIRS := $(sort $(dir $(HTMLS))) $(LOG_DIR) $(BUILD_DIR)/static

CSS := $(wildcard $(SRC_DIR)/*.css)
CSS := $(patsubst $(SRC_DIR)/%.css,$(BUILD_DIR)/%.css, $(CSS))

# Define the default target to build everything
.PHONY: everything
everything: | $(BUILD_DIR) $(BUILD_SUBDIRS)
	$(call status,Updating author)
	$(Q)update-author
	$(call status,Updating pubdate)
	$(Q)update-pubdate
	$(Q)make -s -f /app/mk/build.mk $(BUILD_DIR)/.update-index VERBOSE=$(VERBOSE)
	$(Q)make -s -f /app/mk/build.mk all VERBOSE=$(VERBOSE)

all: $(HTMLS)
all: $(CSS)
all: $(BUILD_DIR)/robots.txt

$(BUILD_DIR)/robots.txt: $(SRC_DIR)/robots.txt
	cp $< $@

$(BUILD_DIR)/.update-index: $(MARKDOWNS) $(YAMLS)
	$(call status,Updating Redis Index)
	$(Q)update-index --host $(REDIS_HOST) --port $(REDIS_PORT) src
	$(Q)touch $@

# Target to minify HTML and CSS files
# Modifies file timestamps. The preserve option doesn't seem to work.
$(BUILD_DIR)/.minify:
	$(call status,Minify HTML and CSS)
	$(Q)cd $(BUILD_DIR); $(MINIFY_CMD) -a -v -r -o . .
	$(Q)touch $@

.PHONY: test
# Triggered by the test target in redo.mk; see docs/guides/redo-mk.md.
test: $(BUILD_DIR)/.minify | $(LOG_DIR)
	$(call status,Run link check)
	$(Q)$(CHECKLINKS_CMD) http://nginx-dev
	$(call status,Check metadata authors)
	$(Q)check-author $(SRC_DIR)
	$(call status,Check page titles)
	$(Q)check-page-title -x $(CFG_DIR)/check-page-title-exclude.yml $(BUILD_DIR)
	$(call status,Check post-build artifacts)
	$(Q)check-post-build -c $(CFG_DIR)/check-post-build.yml
	$(call status,Check for unexpanded Jinja)
	$(Q)check-unexpanded-jinja $(BUILD_DIR)

# Create necessary build directories
$(BUILD_DIR): | $(BUILD_SUBDIRS)

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	$(call status,Create directory $@)
	$(Q)mkdir -p $@

# Copy CSS files to the build directory
$(BUILD_DIR)/%.css: %.css | $(BUILD_DIR)
	$(call status,Copy CSS $<)
	$(Q)cp $< $@

# Include and preprocess Markdown files up to three levels deep
# See docs/guides/preprocess.md for preprocessing details
$(BUILD_DIR)/%.md: %.md | $(BUILD_DIR)
	$(call status,Preprocess $<)
	$(Q)preprocess $<

# Generate HTML from processed Markdown using Pandoc
$(BUILD_DIR)/%.html: $(BUILD_DIR)/%.md $(PANDOC_TEMPLATE) | $(BUILD_DIR)
	$(call status,Generate HTML $@)
	$(Q)$(PANDOC_CMD) $(PANDOC_OPTS) -o $@ $<

# Generate PDF from processed Markdown using Pandoc
# include-filter usage is documented in docs/guides/include-filter.md
$(BUILD_DIR)/%.pdf: %.md | $(BUILD_DIR)
	$(call status,Generate PDF $@)
	$(Q)include-filter $(BUILD_DIR) $< $(BUILD_DIR)/$*.1.md
	$(Q)include-filter $(BUILD_DIR) $(BUILD_DIR)/$*.1.md $(BUILD_DIR)/$*.2.md
	$(Q)include-filter $(BUILD_DIR) $(BUILD_DIR)/$*.2.md $(BUILD_DIR)/$*.3.md
	$(Q)$(PANDOC_CMD) \
$(PANDOC_OPTS_PDF) \
        -o $@ \
        $(BUILD_DIR)/$*.3.md

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean:
	$(call status,Remove build artifacts)
	$(Q)-rm -rf $(BUILD_DIR)

# Optionally include user dependencies; see docs/guides/redo-mk.md and
# docs/guides/dep-mk.md.
-include /app/mk/dep.mk

$(BUILD_DIR)/picasso.mk: $(YAMLS) | $(BUILD_DIR)
	$(call status,Generate picasso rules)
	$(Q)picasso --src $(SRC_DIR) --build $(BUILD_DIR) > $@

include $(BUILD_DIR)/picasso.mk
