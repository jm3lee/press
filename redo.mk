PANDOC_CMD := docker run --rm \
		  --volume "$(PWD):/data" \
		  --user $(shell id -u):$(shell id -g) \
		  pandoc/extra

PANDOC_OPTS := \
		--css '/press/style.css' \
		--standalone \
		-t html \
		--toc \
		--toc-depth=2 \
		--filter pandoc-crossref \
		--template=pandoc-template.html \

PANDOC_OPTS_PDF := \
		--css "/press/style.css" \
		--standalone \
		-t pdf \
		--toc \
		--toc-depth=2 \
		--number-sections \
		--pdf-engine=xelatex \
		--resource-path=build \
		--filter pandoc-crossref \

MARKDOWNS := $(shell find . \
	\( -path ./build -o -path ./includes -o -path ./templates \) \
	-prune -o -name '*.md' -print)
HTMLS := $(MARKDOWNS:.md=.html)
HTMLS := $(addprefix build/,$(HTMLS))

.PHONY: all
all: | build
all: $(HTMLS)
all: build/style.css

# doctl auth init; remove extraneous context as necessary
# doctl registry login
.PHONY: docker
docker:
	docker compose build nginx
	#docker tag artistic-anatomy-nginx registry.digitalocean.com/artisticanatomy/book:latest
	#docker push registry.digitalocean.com/artisticanatomy/book:latest

.PHONY: up
up:
	docker compose up nginx-dev -d

.PHONY: docker
down:
	docker compose down

build:
	echo $@ $(dir $(HTMLS)) | sort | uniq | xargs mkdir -p
	docker compose restart nginx-dev

build/style.css: style.css
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
