# Build rules for the React quiz interface.
# Included by the main `dep.mk` so that `build.mk` knows how to
# generate and copy quiz assets.
#
# The `all` target ensures that the compiled JavaScript bundle and any
# accompanying JSON files are present under `build/quiz/`.
all: build/quiz/quiz.js

# Directory for built quiz assets
build/quiz:
	mkdir -p $@

# Copy the generated bundle from the app directory into the build tree
build/quiz/quiz.js: dist/app/build/static/js/quiz.js | build/quiz
	cp $< $@

# Build the React application with Vite.  The output lives under
# `dist/app/build/static/js/` and mirrors Vite's default output directory.
dist/app/build/static/js/quiz.js: $(wildcard dist/app/quiz/src/*) dist/app/quiz/.init
	cd dist/app/quiz; npm run build


# Install node modules once and mark completion.
dist/app/quiz/.init:
	cd dist/app/quiz; npm install
	touch $@

# Example quiz data used for the demo page
all: build/quiz/demo.json

# Helper rule for copying example JSON quizzes into the build tree
build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
