package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }
source_command := if os_family() == "windows" { "call" } else { "source" }
# use cmd.exe instead of sh on Window
# set shell := ["cmd.exe", "/c"]


# List all commands
list:
  just --list 

# Run key tests
go:
  just test
  just mypy
  just isort
  just black
  just ruff

# Run all tests, checks and linters
grill:
  just go
  just md
  just readme
  just scripts
  just make-help

# Run pytest (up to first error) and print slowest test times 
test:
  poetry run pytest . -x --durations=5


# Type check
mypy:
  poetry run mypy {{ package }}

# Run isort (black-compatible and float imports to top)
isort:
  poetry run isort --profile black --float-to-top .

# Run black
black:  
  poetry run black .

# Apply ruff
ruff:
  poetry run ruff check . --fix

# Prettify markdown files (use .prettierignore to exclude files)
md:
  npx prettier . --write

# Run Python code and console commands from README.md 
readme:  
  just readme-py
  just readme-console

# Run Python code from README.md
readme-py:
  cat README.md | npx codedown python > scripts/readme/minimal.py
  poetry run python scripts/readme/minimal.py

# Run console examples from README.md
readme-console:
  cat README.md | npx codedown bash > scripts/readme/minimal.sh
  cd scripts/readme && rm -f chart.json entries.linejson && bash -e minimal.sh

# Run command line examples (Linux)
scripts:
  # abacus replaces bx
  cd scripts/abacus && bash -e all.sh
  # cx is shorthand
  cd scripts/cx && bash -e joan.sh

 
# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# Publish to PyPI
publish:
  poetry publish --build

cli:
  cd scripts/abacus && bash -e all.sh 

patch:
  poetry version patch

make-help:
  abacus --help > abacus-help.txt
  abacus chart --help >> abacus-help.txt
  abacus ledger --help >> abacus-help.txt
  abacus report --help >> abacus-help.txt
  abacus account --help >> abacus-help.txt
  abacus-extra --help >> abacus-help.txt
