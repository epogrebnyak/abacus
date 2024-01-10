package := "abacus"
source_command := if os_family() == "windows" { "call" } else { "source" }
#use cmd.exe instead of sh on Window
#set shell := ["cmd.exe", "/c"]


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
  just boil

boil:  
  just run ./README.md
  just run ./docs/index.md
  just run ./docs/quick_start.md

# Run code and scripts from markdown file
run MD_FILE:
  just run-py {{MD_FILE}}
  just run-sh {{MD_FILE}}

# Run Python code from markdown file
run-py MD_FILE:
  codeblock python {{MD_FILE}} | poetry run python 

# Run script from markdown file
run-sh MD_FILE:
  codeblock bash {{MD_FILE}} > {{MD_FILE}}.sh
  cd {{parent_directory(MD_FILE)}} && bash -e {{file_name(MD_FILE)}}.sh
  rm {{MD_FILE}}.sh
  cd {{parent_directory(MD_FILE)}} && rm -f chart.json entries.linejson starting_balances.json

# Run examples 
scripts:
  cd scripts && abacus extra unlink --yes && readme.bat
  cd scripts/vat && vat.bat
  cd scripts/set && set.bat
  cd scripts/textbook && joan.bat

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

# Run Python code from docs
docs-py:
  poetry run python docs/echo.py docs/quick_start.md | npx codedown python > docs/quick_start.py
  poetry run python docs/quick_start.py
  poetry run python docs/echo.py docs/index.md | npx codedown python > docs/_index.py
  poetry run python docs/_index.py

# Run console examples from docs
docs-cli:
  poetry run python docs/echo.py docs/quick_start.md | npx codedown bash > docs/quick_start.bat
  cd docs && rm -f chart.json entries.linejson && quick_start.bat
  poetry run python docs/echo.py docs/index.md | npx codedown bash > docs/_index.bat
  cd docs && rm -f chart.json entries.linejson && _index.bat

# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  just md
  poetry run mkdocs gh-deploy 

# Publish to PyPI
publish:
  poetry publish --build

patch:
  poetry version patch
