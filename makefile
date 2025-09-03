# Makefile for building and managing Press
# Targets run from the repository root.

export PATH := /app/bin:$(PATH)

# Allow the environment to override BASE_URL instead of forcing localhost.
# This ensures tooling such as the sitemap generator picks up the value
# provided via docker-compose or the user's shell.
BASE_URL ?= http://press.io
export BASE_URL

# Override MAKEFLAGS (so your settings can’t be clobbered by the environment)
# docker-make previously passed these flags inside the container; still useful.
override MAKEFLAGS += --warn-undefined-variables  \
              --no-builtin-rules        \
              -j16                      \
              --no-print-directory      \

# Export it so sub-makes see the same flags
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

# Default template used by render-html
HTML_TEMPLATE := $(SRC_DIR)/template.html.jinja

# Command for minifying HTML files
MINIFY_CMD := minify

CHECKLINKS_CMD := checklinks
TEST_HOST_URL ?= http://nginx-test

VPATH := $(SRC_DIR)

# Find all Markdown files excluding specified directories
MARKDOWNS := $(shell find $(SRC_DIR)/ -name '*.md')
YAMLS := $(shell find $(SRC_DIR) -name "*.yml")
BUILD_YAMLS := $(patsubst $(SRC_DIR)/%,$(BUILD_DIR)/%,$(YAMLS))

# Define the corresponding HTML output files
HTMLS := $(patsubst $(SRC_DIR)/%.md, $(BUILD_DIR)/%.html, $(MARKDOWNS))

# Sort and define build subdirectories based on HTML files
BUILD_SUBDIRS := $(sort $(dir $(HTMLS))) $(LOG_DIR) $(BUILD_DIR)/static $(BUILD_DIR)/css

CSS_SRC := $(wildcard $(SRC_DIR)/css/*.css)
CSS := $(patsubst $(SRC_DIR)/css/%.css,$(BUILD_DIR)/css/%.css, $(CSS_SRC))

# Nginx permalink redirect configuration
PERMALINKS_CONF := $(BUILD_DIR)/permalinks.conf

# Define the default target to build everything
.PHONY: everything
everything: | $(BUILD_DIR) $(BUILD_SUBDIRS)
	$(call status,Updating author)
	$(Q)update-author --sort-keys
	$(call status,Updating pubdate)
	$(Q)update-pubdate --sort-keys
	$(Q)$(MAKE) -s $(BUILD_DIR)/.update-index VERBOSE=$(VERBOSE)
	$(Q)$(MAKE) -s all VERBOSE=$(VERBOSE)

all: $(HTMLS)
all: $(CSS)
all: $(BUILD_DIR)/robots.txt
all: $(BUILD_DIR)/sitemap.xml
all: $(PERMALINKS_CONF)

$(BUILD_DIR)/robots.txt: $(SRC_DIR)/robots.txt
	cp $< $@

$(BUILD_DIR)/sitemap.xml: $(HTMLS)
	$(call status,Generate sitemap)
	$(Q)sitemap $(BUILD_DIR)

$(PERMALINKS_CONF): $(MARKDOWNS) $(YAMLS) | $(BUILD_DIR) $(LOG_DIR)
	$(call status,Generate permalink redirects)
	$(Q)nginx-permalinks $(SRC_DIR) -o $@ --log $(LOG_DIR)/nginx-permalinks.txt

$(BUILD_DIR)/.update-index: $(MARKDOWNS) $(YAMLS)
	$(call status,Updating Redis Index)
	$(Q)update-index --host $(REDIS_HOST) --port $(REDIS_PORT) src
	$(Q)touch $@

$(BUILD_DIR)/.process-yamls: $(BUILD_YAMLS) | $(BUILD_DIR)
	$(call status,Process YAML metadata)
	$(Q)find $(BUILD_DIR) -name '*.yml' -print0 | xargs -0 process-yaml
	$(call status,Updating Redis Index)
	$(Q)update-index --host $(REDIS_HOST) --port $(REDIS_PORT) build
	$(Q)touch $@

# Target to minify HTML and CSS files
# Modifies file timestamps. The preserve option doesn't seem to work.
# No touch at the end. Minify should always execute.
$(BUILD_DIR)/.minify:
	$(call status,Minify HTML and CSS)
	$(Q)cd $(BUILD_DIR); $(MINIFY_CMD) -a -v -r -o . .

.PHONY: test
# Triggered by the test target; see docs/guides/redo-mk.md.
test: $(BUILD_DIR)/.minify check | $(LOG_DIR)
	$(call status,Run link check)
	$(Q)$(CHECKLINKS_CMD) $(TEST_HOST_URL)

.PHONY: check
check:
	$(call status,Run checks)
	$(Q)check-all

# Create necessary build directories
$(BUILD_DIR): | $(BUILD_SUBDIRS)

# Create each build subdirectory if it doesn't exist
$(BUILD_SUBDIRS):
	$(call status,Create directory $@)
	$(Q)mkdir -p $@

# Compile SCSS files to the build directory
$(BUILD_DIR)/css/%.css: $(SRC_DIR)/css/%.css | $(BUILD_DIR)/css
	$(call status,Compile SCSS $<)
	$(Q)pysassc $< $@

# Include and preprocess Markdown files up to three levels deep
# See docs/guides/preprocess.md for preprocessing details
$(BUILD_DIR)/%.md: %.md | $(BUILD_DIR)
	$(call status,Preprocess $<)
	$(Q)cp $< $@

# Generate HTML from processed Markdown using render-html
$(BUILD_DIR)/%.html: $(BUILD_DIR)/%.md $(BUILD_DIR)/%.yml $(HTML_TEMPLATE) $(BUILD_DIR)/.process-yamls | $(BUILD_DIR)
	$(call status,Generate HTML $@)
	$(Q)render-html --template $(HTML_TEMPLATE) $< $@ -c $(BUILD_DIR)/$*.yml

# Clean the build directory by removing all build artifacts
.PHONY: clean
clean:
	$(call status,Remove build artifacts)
	$(Q)-rm -rf $(BUILD_DIR)/*
	$(Q)-rm -f $(BUILD_DIR)/.update-index

# Optionally include user dependencies
-include src/dep.mk

$(BUILD_DIR)/picasso.mk: $(YAMLS) | $(BUILD_DIR)
	$(call status,Generate picasso rules)
	$(Q)picasso --src $(SRC_DIR) --build $(BUILD_DIR) > $@

include $(BUILD_DIR)/picasso.mk
