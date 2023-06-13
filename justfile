package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }

# Run pytest
test:
  poetry run pytest

# Run all tests, checks and linters
grill:
  just test
  just mypy
  just isort
  just black
  just ruff
  just md
  just readme

# Run Python code and console commands from README.md 
readme:  
  just readme-py
  just readme-console

# Run console examples from README.md
readme-console:
  just {{ readme_command }}

# Run console examples from README.md (Windows) - FIXME:
readme-console-win:
  cat README.md | npx codedown console > cli-example/minimal.sh
  cat cli-example/minimal.sh | python cli-example/call.py > cli-example/minimal.bat
  echo FIXME: Code below will create chart.json and store.json in root dicrectory,
  echo but want it in cli-example.
  cd cli-example & poetry run call "cli-example/minimal.bat"
  echo For example the command below will print just /abacus, not /abacus/cli-example
  cd cli-example & pwd
  echo We do not really know how to switch to a directory in just command runner 
  echo and make poetry understand the directory has changed.

# run console examples from README.md (Linux) - FIXME:
readme-console-linux:
  echo "assume is already created cli-example/minimal.sh"
  echo "how can one make it run on linux?"
  echo "Tried command below, but no success (source not found)"
  echo "source ./cli-example/minimal.sh"


# Run Python code from README.md
readme-py:
  cat README.md | npx codedown python > cli-example/minimal.py
  poetry run python cli-example/minimal.py

# Prettify markdown files
md:
  npx prettier . --write

# Run isort (black-compatible and float imports to top)
isort:
  poetry run isort --profile black --float-to-top .

# Apply ruff
ruff:
  poetry run ruff check . --fix

# Type check
mypy:
  poetry run mypy {{ package }}

# Run black
black:  
  poetry run black .

# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# Launch streamlit app (not in use)
app:
  poetry run streamlit run app/app.py
