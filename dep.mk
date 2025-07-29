include app/quiz/dep.mk

DIST_YAMLS = $(shell find src/dist -name '*.yml')

all: build/static/index/dist.md

build/static/index:
	mkdir -p $@

build/static/index/dist.md: $(patsubst src/%,build/%,$(DIST_YAMLS)) | build/static/index
	gen-markdown-index-2 build/dist > $@
	emojify < $@ > $@.tmp
	mv $@.tmp $@
