.PHONY: all virtualenv install nopyc clean test docs local upload

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
		python -m pip install -r requirements.txt -r requirements-dev.txt; \
	)

nopyc:
	find . -name '*.pyc' | xargs rm -f || true
	find . -name __pycache__ | xargs rm -rf || true

clean: nopyc
	rm -rf _build dist pyngrok.egg-info .venv

test: install
	@( \
		source .venv/bin/activate; \
		python `which nosetests` -s --with-coverage --cover-erase --cover-package=. --cover-html --cover-html-dir=_build/coverage; \
	)

docs: install
	@( \
		source .venv/bin/activate; \
		python -m pip install -r docs/requirements.txt; \
		sphinx-build -M html docs _build/docs; \
	)

local:
	@rm -rf pyngrok.egg-info dist
	@( \
		$(PYTHON_BIN) setup.py sdist; \
		$(PYTHON_BIN) -m pip install dist/pyngrok*.tar.gz; \
	)

upload:
	@rm -rf dist
	@( \
		source .venv/bin/activate; \
		python setup.py sdist; \
		python -m twine upload dist/*; \
	)
