# read examples.as as YAML file
# prepend commands with bx
# run commands from console


import yaml
import subprocess
import os
import sys              
import pathlib

doc = pathlib.Path("example.as").read_text()

from dataclasses import dataclass    
@dataclass
class Key:
    term: str    

@dataclass
class Command:
    term: str    

def parse(doc):
    for line in doc.splitlines():
        if line.startswith("#"):
            continue
        if line.startswith(" "):
            yield Command(line.strip())
        if line.endswith(":"):
            yield Key(line[:-1])

elements = list(parse(doc))

prefix = None
for element in elements:
    match element:
        case Key(term):
            prefix = "bx " + term
            continue
        case Command(term):
            command = term
            if prefix:
                print(prefix + " " + command)    
