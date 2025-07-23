all: build/quiz/quiz.js

build/quiz:
	mkdir -p $@

build/quiz/quiz.js: app/build/static/js/quiz.js | build/quiz
	cp $< $@

app/build/static/js/quiz.js: $(wildcard app/quiz/src/*) app/quiz/.init
	cd app/quiz; npm run build

app/quiz/.init:
	cd app/quiz; npm install 
	touch $@

all: build/quiz/demo.json

build/%.json: %.json
	mkdir -p $(dir $@)
	cp $< $@
