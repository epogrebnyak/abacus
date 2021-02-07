"""Provide pyproject.toml contents as python file.

Based on Poetry mechanism to split authors name and email from pyproject.toml:
    https://github.com/python-poetry/poetry/blob/35058edf97e24ef1ac2b77563c84eed66d46939e/poetry/packages/package.py

"""
import os
import toml
import re
from typing import Tuple

AUTHOR_REGEX = re.compile(r"^(?P<name>[- .,\w\d'’\"()\{\}]+)(?: <(?P<email>.+?)>)?$")
PATH = os.path.join("..", "pyproject.toml")

def extract_author(s: str) -> Tuple[str, str]:
    m = AUTHOR_REGEX.match(s)
    name = m.group("name")
    email = m.group("email")
    return name, email


def get_toml(path=PATH):
    return toml.load("path)["tool"]["poetry"]


d = get_toml()
project = d["name"]
version = d["version"]
author_name, author_email = extract_author(d["authors"][0])
