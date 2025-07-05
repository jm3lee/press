#!/usr/bin/env python3

import json
import logging
import os
import re
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("render_template")
index_json = None  # See main().

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from xmera.utils import read_json

_whitespace_word_pattern = re.compile(r"(\S+)")


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

    def cap_match(m):
        word = m.group(1)
        return word[0].upper() + word[1:]

    citation = _whitespace_word_pattern.sub(cap_match, citation)

    if icon:
        return f"""<a href="{url}" class="internal-link">{icon} {citation}</a>"""
    return f"""<a href="{url}" class="internal-link">{citation}</a>"""


def link_icon_title(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    icon = desc["icon"]

    def cap_match(m):
        word = m.group(1)
        return word[0].upper() + word[1:]

    citation = _whitespace_word_pattern.sub(cap_match, citation)
    return f"""<a href="{url}" class="internal-link">{icon} {citation}</a>"""


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
    if icon:
        return f"""<a href="{url}" class="internal-link">{icon} {citation}</a>"""
    return f"""<a href="{url}" class="internal-link">{citation}</a>"""


def linkicon(desc):
    """
    Capitalize the first character of each word in the string,
    preserving ALL whitespace (spaces, tabs, newlines).
    """
    citation = desc["citation"]
    url = desc["url"]
    icon = desc.get("icon")
    if icon:
        return f"""<a href="{url}" class="internal-link">{icon} {citation}</a>"""
    return f"""<a href="{url}" class="internal-link">{citation}</a>"""


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
    env = create_env()
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


def get_desc(name):
    d = index_json.get(name)
    if d:
        return d
    return name


def load_mc(filename):
    j = read_json(filename)
    return j


def render_jinja(snippet):
    env = create_env()
    return env.from_string(snippet).render(**index_json)


def to_alpha_index(i):
    return ("a", "b", "c", "d")[i]


def create_env():
    env = Environment(loader=FileSystemLoader("/data"), undefined=StrictUndefined)
    env.filters["linktitle"] = linktitle
    env.filters["linkcap"] = linkcap
    env.filters["link_icon_title"] = link_icon_title
    env.filters["linkicon"] = linkicon
    env.filters["get_desc"] = get_desc
    env.globals["get_origins"] = get_origins
    env.globals["get_insertions"] = get_insertions
    env.globals["get_actions"] = get_actions
    env.globals["load_mc"] = load_mc
    env.globals["render_jinja"] = render_jinja
    env.globals["to_alpha_index"] = to_alpha_index
    return env


def main():
    global index_json
    index_json = read_json(sys.argv[1])
    env = create_env()
    template = env.get_template(sys.argv[2])
    print(template.render(**index_json))


if __name__ == "__main__":
    main()
