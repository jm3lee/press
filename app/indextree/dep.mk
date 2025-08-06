# Build rules for the IndexTree React interface.
# Included by src/dep.mk so build.mk knows how to generate assets.

# Ensure built JS is available under build/examples/indextree/
all: build/examples/indextree/indextree.js

# Directory for built assets
build/examples/indextree:
	mkdir -p $@

# Copy the generated bundle from the app directory into the build tree
build/examples/indextree/indextree.js: app/build/static/js/indextree.js | build/examples/indextree
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

INDEXTREE_SRC := src/examples/indextree/files

build/examples/indextree/demo.json: $(shell find $(INDEXTREE_SRC) -type f) | build/examples/indextree
	indextree-json src > $@

# Helper rule for copying example JSON into build tree
build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
