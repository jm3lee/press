# Build rules for the Flashoffer component showcase.
# Included by src/dep.mk so the top-level makefile can bundle demo assets.

FLASHOFFER_DEMO_SRC := $(shell find app/flashoffer/flashoffer-demo/src -type f)

all: build/static/js/flashoffer-demo.js

build/static/js/flashoffer-demo.js: app/flashoffer/build/static/js/flashoffer-demo.js | build/static/js
        cp $< $@

app/flashoffer/build/static/js/flashoffer-demo.js: $(FLASHOFFER_DEMO_SRC) \
        app/flashoffer/flashoffer-demo/index.html \
        app/flashoffer/flashoffer-demo/vite.config.ts \
        app/flashoffer/flashoffer-demo/tsconfig.json \
        app/flashoffer/flashoffer-demo/tsconfig.node.json \
        app/flashoffer/flashoffer-demo/package.json \
        app/flashoffer/flashoffer-demo/.init
        cd app/flashoffer/flashoffer-demo; npm run build

app/flashoffer/flashoffer-demo/.init:
        cd app/flashoffer/flashoffer-demo; npm install
        touch $@
