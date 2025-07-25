#!/usr/bin/env python3

import json
import logging
import os
import re
import sys

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from xmera.utils import read_json, read_utf8

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
)
logger = logging.getLogger("render")
index_json = None  # See main().

_whitespace_word_pattern = re.compile(r"(\S+)")


def get_tracking_options(desc):
    if "link" in desc:
        if "tracking" in desc:
            if desc["tracking"] == False:
                return 'rel="noopener noreferrer" target="_blank"'
    return ""


def get_link_class(desc):
    if "link" in desc:
        link_options = desc["link"]
        if isinstance(link_options, dict) and "class" in link_options:
            return link_options["class"]
    return "internal-link"


def linktitle(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    if not isinstance(desc, dict):
        return desc

    citation = desc["citation"]
    url = desc["url"]
    icon = desc.get("icon")
    a_attribs = get_tracking_options(desc)

    def cap_match(m):
        word = m.group(1)
        if word in ("of",):
            return word
        return word[0].upper() + word[1:]

    citation = _whitespace_word_pattern.sub(cap_match, citation)

    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


def link_icon_title(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    icon = desc["icon"]
    a_attribs = get_tracking_options(desc)

    def cap_match(m):
        word = m.group(1)
        return word[0].upper() + word[1:]

    citation = _whitespace_word_pattern.sub(cap_match, citation)
    return (
        f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    )


def linkcap(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    if not isinstance(desc, dict):
        return desc

    citation = desc["citation"]
    citation = citation[0].upper() + citation[1:]
    url = desc["url"]
    icon = desc.get("icon")
    a_attribs = get_tracking_options(desc)
    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


def linkicon(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    icon = desc.get("icon")
    a_attribs = get_tracking_options(desc)
    if icon:
        return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{icon} {citation}</a>"""
    return f"""<a href="{url}" class="{get_link_class(desc)}" {a_attribs}>{citation}</a>"""


def link(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    a_attribs = get_tracking_options(desc)
    return f"""<a href="{url}" {a_attribs}>{citation}</a>"""


def extract_front_matter(file_path: str) -> dict | None:
    """
    Read a Markdown file and return its YAML front matter as a dict,
    or None if there's no valid front matter block.
    """
    front_matter_lines = []
    in_block = False

    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip() == "---":
                if not in_block:
                    in_block = True
                else:
                    # closing delimiter
                    break
            elif in_block:
                front_matter_lines.append(line)

    if in_block and front_matter_lines:
        try:
            return yaml.safe_load("".join(front_matter_lines))
        except yaml.YAMLError:
            return None
    return None


def process_directory(root_dir: str) -> None:
    """
    Walk `root_dir` recursively, find all .md files, and:
      - If front matter exists and has a 'title', print:
          TITLE: <title> | FILE: <path>
      - Otherwise, write a warning to stderr.
    """
    for dirpath, _, files in os.walk(root_dir):
        for fname in files:
            if not fname.lower().endswith(".md"):
                continue

            full_path = os.path.join(dirpath, fname)
            fm = extract_front_matter(full_path)

            if fm and isinstance(fm, dict) and "title" in fm:
                print(f'TITLE: {fm["title"]} | FILE: {full_path}')
            else:
                print(
                    f"WARNING: No front matter or title in {full_path}", file=sys.stderr
                )


def get_origins(name):
    j = index_json[name]
    for i in j["origins"]:
        if i in index_json:
            yield index_json[i]
        else:
            yield i


def get_insertions(name):
    j = index_json[name]
    for i in j["insertions"]:
        if i in index_json:
            yield index_json[i]
        else:
            yield i


def get_actions(name):
    j = index_json[name]
    yield from j["actions"]


def get_translations(name):
    j = index_json[name]
    yield from j["translations"].items()


def get_desc(name):
    d = index_json.get(name)
    if d:
        return d
    return name


def render_jinja(snippet):
    logger.info(snippet)
    return env.from_string(snippet).render(**index_json)


def to_alpha_index(i):
    return ("a", "b", "c", "d")[i]


def read_yaml(filename):
    y = yaml.safe_load(read_utf8(filename))
    logging.info(y["toc"])
    yield from y["toc"]


def create_env():
    env = Environment(loader=FileSystemLoader("/data"), undefined=StrictUndefined)
    env.filters["link"] = link
    env.filters["linktitle"] = linktitle
    env.filters["linkcap"] = linkcap
    env.filters["link_icon_title"] = link_icon_title
    env.filters["linkicon"] = linkicon
    env.filters["get_desc"] = get_desc
    env.globals["get_origins"] = get_origins
    env.globals["get_insertions"] = get_insertions
    env.globals["get_actions"] = get_actions
    env.globals["get_translations"] = get_translations
    env.globals["render_jinja"] = render_jinja
    env.globals["to_alpha_index"] = to_alpha_index
    env.globals["read_json"] = read_json
    env.globals["read_yaml"] = read_yaml
    return env


env = create_env()


def main():
    global index_json
    index_json = read_json(sys.argv[1])
    template = env.get_template(sys.argv[2])
    print(template.render(**index_json))


if __name__ == "__main__":
    main()
