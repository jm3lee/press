## Aggregate dependency rules for Press. Included by the top-level makefile so
## module-specific makefiles can provide asset targets.
## See docs/guides/dep-mk.md for details on dependency makefiles.
 
# Directory for built JavaScript assets
build/static/js:
	mkdir -p $@

include app/quiz/dep.mk
include app/indextree/dep.mk
include app/magicbar/dep.mk
