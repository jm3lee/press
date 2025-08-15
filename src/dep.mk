## Aggregate dependency rules for Press. Included by build.mk so
## module-specific makefiles can provide asset targets.
## See docs/guides/dep-mk.md for details on dependency makefiles.
include app/quiz/dep.mk
include app/indextree/dep.mk
include app/magicbar/dep.mk
