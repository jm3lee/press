PANDOC_CMD := docker compose run \
			  --rm \
			  -u $(shell id -u) \
			  pandoc

PANDOC_OPTS := \
		--css '/style.css' \
		--css '/numbered-headings.css' \
		--standalone \
		-t html \
		--toc \
		--toc-depth=2 \
		--filter pandoc-crossref \
		--template=pandoc-template.html \

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

MINIFY_CMD := minify

MARKDOWNS := $(shell find . \
	\( -path ./build -o -path ./includes -o -path ./templates \) \
	-prune -o -name '*.md' -print)
HTMLS := $(MARKDOWNS:.md=.html)
HTMLS := $(addprefix build/,$(HTMLS))

CSS_FILES := $(shell find . \( -path ./build \) -prune -o -name '*.css' -print)
CSS := $(addprefix build/,$(CSS_FILES))

BUILD_ROOT := build
BUILD_SUBDIRS := $(shell dirname $(HTMLS) | sort | uniq)

.PHONY: all
all: | $(BUILD_ROOT) $(BUILD_SUBDIRS)
all: $(HTMLS)
all: $(CSS)

.minify: $(HTMLS) $(CSS)
	cd build; minify -a -v -r -o . .
	touch .minify

# doctl auth init; remove extraneous context as necessary
# doctl registry login
.PHONY: docker
docker: .minify
	docker compose build nginx
	#docker tag artistic-anatomy-nginx registry.digitalocean.com/artisticanatomy/book:latest
	#docker push registry.digitalocean.com/artisticanatomy/book:latest

.PHONY: up
up:
	docker compose up nginx-dev -d

.PHONY: docker
down:
	docker compose down

$(BUILD_SUBDIRS):
	echo $(BUILD_SUBDIRS) | xargs mkdir -p

build:
	docker compose restart nginx-dev

build/%.css: %.css
	cp $< $@

build/%.1.md: %.md | build
	includefilter build $< $@

build/%.2.md: build/%.1.md
	includefilter build $< $@

build/%.3.md: build/%.2.md
	includefilter build $< $@
	( cat $@ | ./bin/emojify > $$$$ ) && mv $$$$ $@

build/%.html: build/%.3.md pandoc-template.html
	$(PANDOC_CMD) \
		$(PANDOC_OPTS) \
		-o $@ \
		$<


build/%.pdf: %.md | build
	includefilter build $< build/$*.1.md
	includefilter build build/$*.1.md build/$*.2.md
	includefilter build build/$*.2.md build/$*.3.md
	$(PANDOC_CMD) \
		$(PANDOC_OPTS_PDF) \
		-o $@ \
		build/$*.3.md

.PHONY: clean
clean:
	-rm -rf build
