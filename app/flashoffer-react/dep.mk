# Build rules for the Flashoffer React component library.
# Mirrors the Vite build workflow used by app/indextree.

ALL_FLASHOFFER_ASSETS := \
        build/static/js/flashoffer-react.es.js \
        build/static/js/flashoffer-react.cjs.js \
        build/types/flashoffer-react/index.d.ts

FLASHOFFER_TYPEDOC_STAMP := app/flashoffer-react/.typedoc

.PHONY: docs
docs: $(FLASHOFFER_TYPEDOC_STAMP)

all: $(ALL_FLASHOFFER_ASSETS)

build/static/js:
	mkdir -p $@

build/types/flashoffer-react:
	mkdir -p $@

build/static/js/flashoffer-react.es.js: app/flashoffer-react/dist/flashoffer-react.es.js | build/static/js
	cp $< $@

build/static/js/flashoffer-react.cjs.js: app/flashoffer-react/dist/flashoffer-react.cjs.js | build/static/js
	cp $< $@

build/types/flashoffer-react/index.d.ts: app/flashoffer-react/dist/types/index.d.ts | build/types/flashoffer-react
	cp $< $@

app/flashoffer-react/dist/flashoffer-react.es.js: app/flashoffer-react/.built

app/flashoffer-react/dist/flashoffer-react.cjs.js: app/flashoffer-react/.built

app/flashoffer-react/dist/types/index.d.ts: app/flashoffer-react/.built

app/flashoffer-react/.built: app/flashoffer-react/.init \
        $(wildcard app/flashoffer-react/src/**/*) \
        app/flashoffer-react/vite.config.ts \
        app/flashoffer-react/tsconfig.json \
        app/flashoffer-react/tsconfig.node.json \
        app/flashoffer-react/package.json
	cd app/flashoffer-react; npm run lint:ci
	cd app/flashoffer-react; npm run build
	touch $@

app/flashoffer-react/.init:
        cd app/flashoffer-react; npm install
        touch $@

$(FLASHOFFER_TYPEDOC_STAMP): app/flashoffer-react/.init \
        $(wildcard app/flashoffer-react/src/**/*) \
        app/flashoffer-react/package.json \
        app/flashoffer-react/typedoc.json \
        app/flashoffer-react/tsconfig.docs.json
        cd app/flashoffer-react; npm run docs
        touch $@
