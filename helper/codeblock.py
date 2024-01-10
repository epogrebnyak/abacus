"""Extract code blocks from markdown file. Inspired by https://github.com/earldouglas/codedown. 
 
   Usage:

    python codeblock.py python README.md

"""

import sys
from pathlib import Path
from markdown_it import MarkdownIt


def get_format():
    return sys.argv[1]


def get_text():
    return Path(sys.argv[2]).read_text()


def strip(text: str) -> str:
    return "\n".join([line.strip() for line in text.split("\n")])


def codeblock(
    info: str,
    text: str,
) -> str:
    md = MarkdownIt("commonmark")
    tokens = [t for t in md.parse(strip(text)) if t.type == "fence" and t.info == info]
    return "\n".join([t.content for t in tokens])


def main():
    print(codeblock(info=get_format(), text=get_text()))
