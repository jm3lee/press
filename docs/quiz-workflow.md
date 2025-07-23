# Quiz Workflow

This document explains how multiple-choice quizzes are stored in the repository, how they are processed during the build, and how they appear on the website.

## 1. Source JSON

Each quiz lives under `src/study/` as a JSON array. Every element has three fields:

- `q` – the question text (can contain Jinja templates for links or icons).
- `c` – a list of answer choices, also Jinja-capable.
- `a` – a two-element array `[correct_index, explanation]`.

Example from `src/study/key_terms.json`:

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

During the build, these source files are processed with the `render-study-json` CLI. The rule in `dep.mk` declares:

```make
BUILD_SUBDIRS += build/study
STUDY_JSONS := $(patsubst src/%,build/%,$(wildcard src/study/*.json))
prebuild: $(STUDY_JSONS)
build/study/%.json: study/%.json | build/static/index.json
        render-study-json build/static/index.json $< > $@
```

The `render-study-json` command expands the quiz file using
variables from the index and optionally writes the output to a file:

```python
parser = argparse.ArgumentParser()
parser.add_argument("index")
parser.add_argument("study")
parser.add_argument("-o", "--output")
args = parser.parse_args()

index_json = read_json(args.index)
study_json = read_json(args.study)
rendered = render_study(index_json, study_json)
output = json.dumps(rendered)
if args.output:
    Path(args.output).write_text(output, encoding="utf-8")
else:
    print(output)
```

The rendered JSON is written to `build/study/*.json` and served directly by the site.

## 3. Interactive Quiz Component

For dynamic quizzes, the React component `search-ui/src/Quiz.jsx` fetches a JSON file and handles user interaction:

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

It renders each question, lets the user pick choices, and displays the score when submitted. The component is bundled by Vite into `build/static/js/bundle.js`.

A page can embed the quiz with:

```html
<div id="quiz-root" data-src="/study/deltoid.json"></div>
<script type="module" src="/static/js/bundle.js" defer></script>
```

`main.jsx` mounts the `Quiz` component onto `#quiz-root` using the `data-src` attribute to locate the JSON file.

## 4. Styling

Both the site CSS (`src/style.css`) and the React bundle’s stylesheet (`search-ui/src/index.css`) define classes like `.quiz-container`, `.question`, `.choice`, and `.answer` to style quizzes consistently.

## Summary

1. Quizzes are defined as JSON under `src/study/`.
2. `render-study-json` expands Jinja expressions and outputs `build/study/*.json`.
3. The React `Quiz` component fetches the built JSON for an interactive version and is included via `bundle.js`.

