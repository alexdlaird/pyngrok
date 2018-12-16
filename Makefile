.PHONY: all virtualenv install local upload

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

local:
	@rm -rf dist
	@( \
		python setup.py sdist; \
		pip install dist/pygrok*.tar.gz; \
	)

upload:
	@( \
		source .venv/bin/activate; \
		python setup.py sdist upload; \
	)
