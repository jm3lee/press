## Emjoify Example

:muscle:

## Jinja For-loop

{% for i in range(0, 3): -%}
- Jinja test {{i}}
{% endfor %}

## Linking Using Markdown

[Quickstart](quickstart.md)

## Linking Using Jinja2

### linktitle
{{"quickstart"|linktitle}}

### link
{{quickstart|link}}

### src/links/press_io.yml

{{press_io_home|link}}

## Quiz Example
{{"quiz"|linktitle}}

## include-filter example

`dist/` content:

```python
include("build/static/index/dist.md")
```
