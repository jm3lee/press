# Build rules for the Flashoffer component showcase.
# Included by src/dep.mk so the top-level makefile can bundle demo assets.

FLASHOFFER_DEMO_SRC := $(shell find app/flashoffer-demo/src -type f)

all: build/static/js/flashoffer-demo.js

build/static/js/flashoffer-demo.js: app/build/static/js/flashoffer-demo.js | build/static/js
cp $< $@

app/build/static/js/flashoffer-demo.js: $(FLASHOFFER_DEMO_SRC) \
app/flashoffer-demo/index.html \
app/flashoffer-demo/vite.config.ts \
app/flashoffer-demo/tsconfig.json \
app/flashoffer-demo/tsconfig.node.json \
app/flashoffer-demo/package.json \
app/flashoffer-demo/.init
cd app/flashoffer-demo; npm run build

app/flashoffer-demo/.init:
cd app/flashoffer-demo; npm install
touch $@
