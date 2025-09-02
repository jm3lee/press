# Key Terms Data Flow

This document explains how the `keyterms.json` file is transformed into the final `keyterms.html` page. See [Metadata Fields](metadata-fields.md) for a description of the metadata associated with each term.

## Source JSON

The canonical list of terms lives at `src/keyterms/index.json`. Each entry maps an identifier to metadata about the term:

```json
{
  "abduction": {
    "term": "Abduction",
    "def": "Movement of a limb or body part away from the midline.<br>Opposite: {{ linktitle(\"adduction\") }}."
  },
  ...
}
```

## Build Steps

1. **Copy to the build directory** – Generic make rules copy JSON files from
   `src/` to `build/`:

```
build/%.json: %.json
    cp $< $@
```

This rule produces `build/keyterms/index.json` from `src/keyterms/index.json`.

2. **Render Markdown** – The Markdown file `src/keyterms/index.md` loads the JSON data with `read_json` and iterates over each term:

```
{% set keyterms = read_json("build/keyterms/index.json") %}
{% for k, v in keyterms.items() | sort %}
  <dt id="{{ k }}">{{ v['term'] }}</dt>
  <dd>
    {{ render_jinja(v['def']) }}
  </dd>
  {% if 'ex' in v %}
  <dd>
    Examples:
    <ul class="examples">
    {% for ex in v['ex'] %}
      <li>{{ render_jinja(ex) }}</li>
    {% endfor %}
    </ul>
  </dd>
  {% endif %}
{% endfor %}
```

3. **Convert to HTML** – `render-html` converts the preprocessed Markdown into
`build/keyterms/index.html`:

```
build/%.html: build/%.md build/%.yml $(HTML_TEMPLATE) | build
    render-html --template $(HTML_TEMPLATE) $< $@ -c build/$*.yml
```

## Verification

`tests/test_keyterms_in_html.py` ensures that every term ID from the JSON
file appears in the generated HTML:

```python
json_path = Path('src/keyterms/index.json')
html_path = Path('build/keyterms/index.html')
for key in json.loads(json_path.read_text()):
    assert soup.find(id=key) is not None
```

Together, these steps keep the key term definitions synchronized with the HTML
page.
