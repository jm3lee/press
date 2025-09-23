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

INDEXTREE_MAP := $(strip $(shell python - <<'PY'
from pathlib import Path

root = Path('src')
entries = []
for index in sorted(root.rglob('index.yml')):
    try:
        rel_dir = index.parent.relative_to(root)
    except ValueError:
        continue
    if 'indextree:' not in index.read_text(encoding='utf-8'):
        continue
    target = (Path('build/static/index') / rel_dir).with_suffix('.json')
    entries.append(f"{target.as_posix()}|{index.parent.as_posix()}")
for item in entries:
    print(item)
PY))

define indextree_target
$(word 1,$(subst |, ,$(1)))
endef

define indextree_source
$(word 2,$(subst |, ,$(1)))
endef

define indextree_deps
$(shell find $(1) -type f \( -name '*.md' -o -name '*.mdi' -o -name '*.yml' -o -name '*.yaml' \))
endef

INDEXTREE_TARGETS := $(foreach entry,$(INDEXTREE_MAP),$(call indextree_target,$(entry)))

all: $(INDEXTREE_TARGETS)

define indextree_rule
$(call indextree_target,$(1)): $(call indextree_deps,$(call indextree_source,$(1))) | build/static/index
        $(call status,Indexing $(call indextree_source,$(1)))
        $(Q)mkdir -p $$(dir $$@)
        $(Q)indextree-json $(call indextree_source,$(1)) > $$@
endef

ifneq ($(strip $(INDEXTREE_MAP)),)
$(foreach entry,$(INDEXTREE_MAP),$(eval $(call indextree_rule,$(entry))))
endif
