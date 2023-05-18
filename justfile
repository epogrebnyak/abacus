package := "abacus"

# run pytest
test:
  poetry run pytest

# run all tests and checks
grill:
  just test
  just examples
  just lint 
  just ruff
  just mypy
  just md

# run code from readme
readme:
  cat README.md | npx codedown python | poetry run python 

# run all code examples
examples:
  just readme
  poetry run python readme.py
  poetry run python minimal.py


# run readme.py
md:
  npx prettier . --write

# apply ruff linter
ruff:
  poetry run ruff check . --fix

# type check
mypy:
  poetry run mypy abacus

# use black and isort
lint:  
  poetry run isort .
  poetry run black .

# build documentation (must change to mkdocstrings)
docs:
  poetry run sphinx-build -a docs docs/site

# show documentation in browser
show:
  start docs/site/index.html

# publish documentation to Github Pages
pages:
  poetry run ghp-import docs/site 

# create rst source for API documentation (must change to mkdocstrings)
apidoc:
  sphinx-apidoc -o docs src/{{package}}

# launch streamlit app (depreciated)
app:
  poetry run streamlit run app.py
