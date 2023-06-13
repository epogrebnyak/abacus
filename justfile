package := "abacus"
readme_command := if os_family() == "windows" { "readme-console-win" } else { "readme-console-linux" }

# Run all tests, checks and linters
grill:
  just test
  just mypy
  just isort
  just black
  just ruff
  just md

# Run pytest (up to first error)
test:
  poetry run pytest -x

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

# Run console examples from README.md
readme-console:
  just {{ readme_command }}

# Run console examples from README.md (Windows):
readme-console-win:
  cat README.md | npx codedown bash > cli-example/minimal.sh
  cat cli-example/minimal.sh | python cli-example/call.py > cli-example/minimal.bat
  poetry run call "cli-example/minimal.bat" --directory cli-example

# run console examples from README.md (Linux):
readme-console-linux:
  cat README.md | npx codedown bash > cli-example/minimal.sh
  poetry run bash -c "cd cli-example && source minimal.sh"

# Run Python code from README.md
readme-py:
  cat README.md | npx codedown python > cli-example/minimal.py
  poetry run  cli-example/minimal.py
  

# Build and serve docs
docs:
  poetry run mkdocs serve 

# Publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# Launch streamlit app (not in use)
app:
  poetry run streamlit run app/app.py
