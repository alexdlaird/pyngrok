.PHONY: all virtualenv install local upload docs

SHELL := /usr/bin/env bash
PYTHON_BIN ?= python

all: virtualenv install

virtualenv:
	@if [ ! -d ".venv" ]; then \
		$(PYTHON_BIN) -m pip install virtualenv --user; \
		$(PYTHON_BIN) -m virtualenv .venv; \
	fi

install: virtualenv
	@( \
		source .venv/bin/activate; \
		python -m pip install -r requirements.txt; \
	)

nopyc:
	find . -name '*.pyc' | xargs rm -f || true
	find . -name __pycache__ | xargs rm -rf || true

clean: nopyc
	rm -rf build dist pyngrok.egg-info venv

test: virtualenv
	@( \
		source .venv/bin/activate; \
		python `which nosetests` -s --with-coverage --cover-erase --cover-package=. --cover-html --cover-html-dir=htmlcov; \
	)

docs: virtualenv
	@( \
		source .venv/bin/activate; \
		python -m pip install -r docs/requirements.txt; \
		sphinx-build -M html docs _build; \
	)

local:
	@rm -rf dist
	@( \
		python setup.py sdist; \
		python -m pip install dist/pyngrok*.tar.gz; \
	)

upload:
	@rm -rf dist
	@( \
		source .venv/bin/activate; \
		python setup.py sdist; \
		python -m twine upload dist/*; \
	)
