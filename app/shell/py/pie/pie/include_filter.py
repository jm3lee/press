#!/usr/bin/env python3

import os
import re
import sys

import yaml

figcount = 0
heading_level = 0

outdir = None
infilename = None
outfilename = None
outfile = None
infile = None


def parse_metadata_or_print_first_line(f):
    for line in f:
        if line.strip() == "---":
            y = ""
            for line in f:
                if line.strip() == "---":
                    break
                y += line
            return yaml.safe_load(y)
        else:
            print(line, end="", file=outfile)
            break


def include(filename):
    print("include", filename)
    with open(filename, "r", encoding="utf-8") as f:
        metadata = parse_metadata_or_print_first_line(f)
        if metadata and metadata.get("title"):
            print("#" * (heading_level + 1) + " " + metadata["title"], file=outfile)
        for line in f:
            if line.startswith("#"):
                line = "#" * heading_level + line
            print(line, end="", file=outfile)


def yield_lines(infile):
    for line in infile:
        if line.strip() == "```":
            break
        yield line


def eval_code():
    for line in infile:
        if line.strip() == "```":
            break
        else:
            eval(line)


def new_filestem(stem):
    counter = 0
    while os.path.exists(f"{stem}{counter}.svg") or os.path.exists(
        f"{stem}{counter}.mmd"
    ):
        counter += 1
    return f"{stem}{counter}"


def mermaid(mmd_filename, alt_text, ref_id):
    print(mmd_filename)
    global figcount
    stem = new_filestem(f"{outdir}/diagram")
    with open(mmd_filename, "r", encoding="utf-8") as inmmd, open(
        f"{stem}.mmd", "w", encoding="utf-8"
    ) as outmmd:
        for line in inmmd:
            if line.strip() != "```mermaid":
                continue
            for line in inmmd:
                if line.strip() == "```":
                    break
                outmmd.write(line)
    os.system(f"npx mmdc -i {stem+'.mmd'} -o {stem+'.png'}")
    print(
        f'![{alt_text}](./{os.path.basename(stem+".png")}){{ {ref_id} }}',
        file=outfile,
    )
    figcount += 1


def md_to_html_links(line):
    # Compile a pattern that captures:
    # 1) The link text inside [   ]
    # 2) The link URL (without .md) inside (   )
    pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\.md\)")

    # Use a replacement with the captured groups, changing `.md` to `.html`
    result = pattern.sub(r"[\1](\2.html)", line)
    return result


def main():
    global outdir, infilename, outfilename, infile, outfile

    outdir = sys.argv[1]
    infilename = sys.argv[2]
    outfilename = sys.argv[3]

    with open(infilename, "r", encoding="utf-8") as infile, open(
        outfilename, "w", encoding="utf-8"
    ) as outfile:
        for line in infile:
            if line.strip() == "```python":
                # FIXME Terrible. Some times, there is one statement with a
                # multiline string. Some times, there are multiple statements.
                # Probably need a proper parser here.
                lines = list(yield_lines(infile))
                try:
                    eval("".join(lines))
                except:
                    for l in lines:
                        eval(l)
            else:
                if line.startswith("#"):
                    parts = line.split(" ")
                    heading_level = len(parts[0])
                line = md_to_html_links(line)
                print(line, end="", file=outfile)
