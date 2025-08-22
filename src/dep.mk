## Aggregate dependency rules for Press. Included by build.mk so
## module-specific makefiles can provide asset targets.
## See docs/guides/dep-mk.md for details on dependency makefiles.
 
# Directory for built JavaScript assets
build/static/js:
	mkdir -p $@

include app/quiz/dep.mk
include app/indextree/dep.mk
include app/magicbar/dep.mk

# Mermaid example diagram
all: build/examples/mermaid/diagram.mmd

build/examples/mermaid:
	mkdir -p $@

build/examples/mermaid/diagram.mmd: src/examples/mermaid/diagram.mmd | build/examples/mermaid
	cp $< $@
