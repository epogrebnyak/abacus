import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text()
for line in text.split("\n"):
    print(line.strip())
