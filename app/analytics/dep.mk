# Build rules for the engagement analytics React bundle.
# Included by src/dep.mk so the top-level makefile can build assets.

all: build/static/js/analytics.js

build/static/js/analytics.js: app/build/static/js/analytics.js | build/static/js
	cp $< $@

app/build/static/js/analytics.js: $(wildcard app/analytics/src/*) app/analytics/.init
	cd app/analytics; npm run build

app/analytics/.init:
	cd app/analytics; npm install
	touch $@
