# Quiz Workflow

This document explains how multiple-choice quizzes are stored in the repository, how they are processed during the build, and how they appear on the website.

## 1. Source JSON

Each quiz lives under `src/quiz/` as a JSON array. Every element has three fields:

- `q` – the question text (can contain Jinja templates for links or icons).
- `c` – a list of answer choices, also Jinja-capable.
- `a` – a two-element array `[correct_index, explanation]`.

Example from `src/quiz/demo.json`:

```json
[
  {
    "q": "Which of the following best describes the {{sagittal['name']|lower}} plane?",
    "c": [
      "Divides the body into anterior and posterior portions",
      "Divides the body into superior and inferior portions",
      "Divides the body into left and right portions",
      "Divides the body into medial and lateral portions"
    ],
    "a": [
      2,
      "The sagittal plane is a vertical plane that runs front to back, splitting the body into left and right sections. The midsagittal (median) plane creates equal halves, while parasagittal planes create unequal left and right parts."
    ]
  }
]
```

## 2. Rendering JSON

During the build the React quiz interface is compiled with Vite.  The
`app/quiz/dep.mk` makefile also copies the JSON files so they are
served from `/quiz/`:

```make
all: build/quiz/quiz.js build/quiz/demo.json

build/quiz/quiz.js: app/build/static/js/quiz.js | build/quiz
cp $< $@

app/build/static/js/quiz.js: $(wildcard app/quiz/src/*) app/quiz/.init
cd app/quiz; npm run build

build/quiz/demo.json: src/quiz/demo.json
mkdir -p $(dir $@)
cp $< $@
```

The resulting assets live under `build/quiz/` and are served directly by the site.

## 3. Interactive Quiz Component

For dynamic quizzes, the React component `app/quiz/src/Quiz.jsx` fetches a JSON file and handles user interaction:

```jsx
const Quiz = ({ src = "/study/key_terms.json" }) => {
  const [questions, setQuestions] = useState([]);
  const [selected, setSelected] = useState({});
  const [showAnswers, setShowAnswers] = useState(false);
  const [score, setScore] = useState(null);

  useEffect(() => {
    fetch(src)
      .then((res) => res.json())
      .then(setQuestions)
      .catch(console.error);
  }, [src]);
  ...
}
```

It renders each question, lets the user pick choices, and displays the score when submitted. The component is bundled by Vite into `build/quiz/quiz.js`.

A page can embed the quiz with:

```html
<div id="quiz-root" data-src="/quiz/demo.json"></div>
<script type="module" src="/quiz/quiz.js" defer></script>
```

`main.jsx` mounts the `Quiz` component onto `#quiz-root` using the `data-src` attribute to locate the JSON file.

## 4. Styling

Both the site CSS (`src/style.css`) and the React bundle’s stylesheet (`app/quiz/src/index.css`) define classes like `.quiz-container`, `.question`, `.choice`, and `.answer` to style quizzes consistently.

## Summary

1. Quizzes are defined as JSON under `src/quiz/`.
2. `app/quiz/dep.mk` compiles the React app and copies quizzes to `build/quiz/`.
3. The React `Quiz` component fetches the built JSON for an interactive version and is included via `quiz.js`.

