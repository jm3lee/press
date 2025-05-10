# Makefile for building and managing Press

.PHONY: all build dirs docker test up upd down clean prune setup seed sync to-webp .minify

# -------------------------------------------------------------------
# Commands & flags
# -------------------------------------------------------------------

PANDOC_CMD       := docker compose run --rm -T -u $(shell id -u) pandoc
PANDOC_TEMPLATE  := src/pandoc-template.html

PANDOC_OPTS_HTML := \
  --css '/style.css' \
  --standalone \
  -t html \
  --toc \
  --toc-depth=2 \
  --filter pandoc-crossref \
  --template=$(PANDOC_TEMPLATE)

PANDOC_OPTS_PDF  := \
  --css '/press/style.css' \
  --standalone \
  -t pdf \
  --toc \
  --toc-depth=2 \
  --number-sections \
  --pdf-engine=xelatex \
  --resource-path=build \
  --filter pandoc-crossref

MINIFY_CMD       := minify
EMOJIFY_CMD      := docker compose run --rm shell emojify
LINKCHECKER_CMD  := docker compose run --rm -T linkchecker

SERVICES         := nginx-dev to-webp sync
VPATH            := src

# -------------------------------------------------------------------
# Sources and generated files
# -------------------------------------------------------------------

MARKDOWNS    := $(shell find src/ -name '*.md')
HTMLS        := $(patsubst src/%.md,build/%.html,$(MARKDOWNS))
PDFS         := $(patsubst src/%.md,build/%.pdf,$(MARKDOWNS))

CSS_SRC      := $(wildcard src/*.css)
CSS          := $(patsubst src/%.css,build/%.css,$(CSS_SRC))

BUILD_SUBDIRS := $(sort $(dir $(HTMLS)))

# -------------------------------------------------------------------
# Default: build HTML, CSS
# -------------------------------------------------------------------

all: build dirs $(HTMLS) $(CSS)

# Ensure build dirs exist, then restart nginx-dev so it sees them
build:
	docker compose restart nginx-dev

dirs: $(BUILD_SUBDIRS)

$(BUILD_SUBDIRS):
	mkdir -p $@

# -------------------------------------------------------------------
# CSS
# -------------------------------------------------------------------

build/%.css: src/%.css | build
	cp $< $@

# -------------------------------------------------------------------
# Markdown → intermediate MD (with includes + emojis)
# -------------------------------------------------------------------

build/%.md: src/%.md | build
	$(EMOJIFY_CMD) < $< > $@
	@# Apply includefilter 3 levels deep
	@infile=$@; \
	for lvl in 1 2 3; do \
	  outfile=build/$*.$$lvl.md; \
	  includefilter build $$infile $$outfile; \
	  infile=$$outfile; \
	done

# -------------------------------------------------------------------
# Intermediate MD → HTML
# -------------------------------------------------------------------

build/%.html: build/%.md $(PANDOC_TEMPLATE) | build
	$(PANDOC_CMD) $(PANDOC_OPTS_HTML) -o $@ $<

# -------------------------------------------------------------------
# Source MD → PDF (3‐level include preprocessing)
# -------------------------------------------------------------------

build/%.pdf: src/%.md | build
	@infile=$<; \
	for lvl in 1 2 3; do \
	  outfile=build/$*.$$lvl.md; \
	  includefilter build $$infile $$outfile; \
	  infile=$$outfile; \
	done; \
	$(PANDOC_CMD) $(PANDOC_OPTS_PDF) -o $@ $$infile

# -------------------------------------------------------------------
# Minify HTML & CSS
# -------------------------------------------------------------------

.minify: $(HTMLS) $(CSS)
	cd build && $(MINIFY_CMD) -a -v -r -o .
	touch .minify

# -------------------------------------------------------------------
# Docker image build & push
# -------------------------------------------------------------------

docker: .minify
	docker compose build nginx
	#docker tag brianleeart-nginx registry.digitalocean.com/artisticanatomy/brianlee.art:latest
	#docker push registry.digitalocean.com/artisticanatomy/brianlee.art:latest

# -------------------------------------------------------------------
# Linkchecker
# -------------------------------------------------------------------

test: $(HTMLS)
	$(LINKCHECKER_CMD) build

# -------------------------------------------------------------------
# Dev server controls
# -------------------------------------------------------------------

up:
	docker compose up $(SERVICES)

upd:
	docker compose up -d $(SERVICES)

down:
	docker compose down

# -------------------------------------------------------------------
# Cleanup & maintenance
# -------------------------------------------------------------------

clean:
	rm -rf build

prune:
	docker system prune -f

setup:
	mkdir -p app/to-webp/input app/to-webp/output
	docker compose build
	make -f redo.mk seed

seed:
	docker compose run --build --rm -T seed

sync:
	docker compose run --build --rm -T sync

to-webp:
	docker compose run --build --rm -T to-webp
