## Aggregate dependency rules for Press. Included by the top-level makefile so
## module-specific makefiles can provide asset targets.
## See docs/guides/dep-mk.md for details on dependency makefiles.
 
# Directory for built JavaScript assets
build/static/js:
	mkdir -p $@

build/static/index:
	mkdir -p $@

include app/quiz/dep.mk
include app/indextree/dep.mk
include app/magicbar/dep.mk
include app/analytics/dep.mk

all: build/static/index/examples.json

build/static/index/examples.json: $(shell find src/examples -name '*.yml') | build/static/index
	$(call status,Indexing src/examples)
	$(Q)indextree-json src/examples > $@
