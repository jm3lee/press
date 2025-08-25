# Build rules for the React quiz interface.
# Included by the main `dep.mk` so that the top-level makefile
# knows how to generate and copy quiz assets.
# See docs/guides/dep-mk.md for details on dependency makefiles.
#
# The `all` target ensures that the compiled JavaScript bundle and any
# accompanying JSON files are present under `build/quiz/`.
all: build/static/js/quiz.js


# Copy the generated bundle from the app directory into the build tree
build/static/js/quiz.js: app/build/static/js/quiz.js | build/static/js
	cp $< $@

# Build the React application with Vite.  The output lives under
# `app/build/static/js/` and mirrors Vite's default output directory.
app/build/static/js/quiz.js: $(wildcard app/quiz/src/*) app/quiz/.init
	cd app/quiz; npm run build


# Install node modules once and mark completion.
app/quiz/.init:
	cd app/quiz; npm install
	touch $@

# Example quiz data used for the demo page
all: build/quiz/demo.json

# Helper rule for copying example JSON quizzes into the build tree
build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
