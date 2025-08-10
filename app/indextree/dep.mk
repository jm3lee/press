# Build rules for the IndexTree React interface.
# Included by src/dep.mk so build.mk knows how to generate assets.
# See docs/guides/dep-mk.md for details on dependency makefiles.

# Ensure built JS is available under build/static/
all: build/static/js/indextree.js

# Copy the generated bundle from the app directory into the build tree
build/static/js/indextree.js: app/build/static/js/indextree.js | build/static/js
	cp $< $@

# Build the React application with Vite; output lives under app/build/static/js
app/build/static/js/indextree.js: $(wildcard app/indextree/src/*) app/indextree/.init
	cd app/indextree; npm run build

# Install node modules once
app/indextree/.init:
	cd app/indextree; npm install
	touch $@

# Example tree data used for the demo page
all: build/examples/indextree/demo.json

# Directory for example assets
build/examples/indextree:
	mkdir -p $@

build/examples/indextree/demo.json: | build/examples/indextree
	indextree-json src > $@

# Helper rule for copying example JSON into build tree
build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
