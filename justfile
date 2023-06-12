package := "abacus"
command := if os_family() == "windows" { "poetry run minimal.bat" } else { "bash source ./minimal.sh" }

# run pytest
test:
  poetry run pytest

# run all tests and checks
grill:
  just test
  just mypy
  just ruff
  just readme-py
  just readme-console
  just isort
  just black
  just md

# run console examples from README.md (FIXME)
readme-console:
  cat README.md | npx codedown console > minimal.sh
  cat minimal.sh | python call.py > minimal.bat
  {{ command }}

# run Python code from README.md
readme-py:
  cat README.md | npx codedown python > minimal.py
  poetry run python minimal.py

# prettify markdown
md:
  npx prettier . --write

isort:
  poetry run isort --float-to-top .

# apply ruff linter
ruff:
  poetry run ruff check . --fix

# type check
mypy:
  poetry run mypy abacus

# use black and isort
black:  
  poetry run black .

# build and serve docs
docs:
  poetry run mkdocs serve 

# publish docs
docs-publish:
  poetry run mkdocs gh-deploy 

# launch streamlit app (depreciated)
app:
  poetry run streamlit run app/app.py
