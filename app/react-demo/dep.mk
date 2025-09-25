# Build rules for the React Demo component placeholder.
# Included by src/dep.mk so the top-level makefile knows how to generate
# bundled assets for the Press documentation site.

all: build/static/js/react-demo.js

build/static/js/react-demo.js: app/build/static/js/react-demo.js | build/static/js
	cp $< $@

app/build/static/js/react-demo.js: $(wildcard app/react-demo/src/*) app/react-demo/.init
	cd app/react-demo; npm run build

app/react-demo/.init:
	cd app/react-demo; npm install
	touch $@
