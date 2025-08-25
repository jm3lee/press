# Build rules for the React daily quiz interface.
# Included by the main `dep.mk` so that `build.mk` knows how to
# generate and copy daily quiz assets.
# See docs/guides/dep-mk.md for details on dependency makefiles.
#
# The `all` target ensures that the compiled JavaScript bundle and any
# accompanying JSON files are present under `build/daily-quiz/`.
all: build/static/js/daily-quiz.js


# Copy the generated bundle from the app directory into the build tree
build/static/js/daily-quiz.js: app/build/static/js/daily-quiz.js | build/static/js
	cp $< $@

# Build the React application with Vite.  The output lives under
# `app/build/static/js/` and mirrors Vite's default output directory.
app/build/static/js/daily-quiz.js: $(wildcard app/daily-quiz/src/*) app/daily-quiz/.init
	cd app/daily-quiz; npm run build


# Install node modules once and mark completion.
app/daily-quiz/.init:
	cd app/daily-quiz; npm install
	touch $@

# Example quiz data used for the demo page
all: build/daily-quiz/demo.json

# Helper rule for copying example JSON quizzes into the build tree
build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
