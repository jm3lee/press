# Build rules for the MagicBar React interface.
# Included by src/dep.mk so build.mk knows how to generate assets.
# See docs/guides/dep-mk.md for details on dependency makefiles.

# Ensure built JS is available under build/static/
all: build/static/js/magicbar.js

# Directory for built assets
build/static/js:
	mkdir -p $@

# Copy the generated bundle from the app directory into the build tree
build/static/js/magicbar.js: app/build/static/js/magicbar.js | build/static/js
	cp $< $@

# Build the React application with Vite; output lives under app/build/static/js
app/build/static/js/magicbar.js: $(wildcard app/magicbar/src/*) app/magicbar/.init
	cd app/magicbar; npm run build

# Install node modules once
app/magicbar/.init:
	cd app/magicbar; npm install
	touch $@

# Example data used for the demo page
all: build/magicbar/demo.json

# Helper rule for copying example JSON into the build tree
build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
