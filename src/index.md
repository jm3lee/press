Welcome to the demo site for **Press**. This page highlights a few features you
can use when writing documentation.

## Emojify Example

The build pipeline runs `emojify` so colon codes are replaced with real emoji:

:muscle:

(The text `:muscle:` above becomes a 💪 icon after processing.)

## Jinja For-loop

Markdown files can include Jinja2 templates. This loop generates three list items:

{% for i in range(0, 3): -%}
- Jinja test {{ i }}
{% endfor %}

When the page is built the loop outputs items numbered 0–2.

## Linking Using Markdown

Standard Markdown links work as expected. During the build each `.md`
extension is rewritten to `.html`.

[Quickstart](quickstart.md)

## Linking Using Jinja2

Press exposes helper filters for links. These all point to the Quickstart page
but format the text differently.

### linktitle
{{"quickstart"|linktitle}}

`linktitle` capitalizes each word of the cited page's title.

### link
{{"quickstart"|link}}

`link` leaves the citation text exactly as defined.

### src/dist/links/press_io_home.yml

Metadata files can describe external links. `press_io_home` is defined in
`src/dist/links/press_io_home.yml` and can be referenced like this:

{{"press_io_home"|link}}

## Quiz Example
{{"quiz"|linktitle}}

The quiz page demonstrates an interactive multiple-choice component built with
React.

## include-filter example

The `include-filter` tool lets you embed other Markdown files. The snippet
below pulls in a prebuilt fragment from `build/static/index/dist.md` at build
time.

```python
include("build/static/index/dist.md")
```

## include_deflist_entry demo

This variant inserts another Markdown file as a definition list entry:

<dl>
```python
include_deflist_entry("src/dist/include-filter/a.md")
include_deflist_entry("src/dist/include-filter/b.md")
```
</dl>
