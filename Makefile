.PHONY: all virtualenv install nopyc clean test docs local validate-release upload

SHELL := /usr/bin/env bash
PYTHON_BIN ?= python

all: virtualenv install

virtualenv:
	@if [ ! -d "venv" ]; then \
		$(PYTHON_BIN) -m pip install virtualenv --user; \
		$(PYTHON_BIN) -m virtualenv venv; \
	fi

install: virtualenv
	@( \
		source venv/bin/activate; \
		python -m pip install -r requirements.txt -r requirements-dev.txt; \
	)

nopyc:
	find . -name '*.pyc' | xargs rm -f || true
	find . -name __pycache__ | xargs rm -rf || true

clean: nopyc
	rm -rf _build dist *.egg-info venv

test: install
	@( \
		source venv/bin/activate; \
		python -m coverage run -m unittest discover -v -b && python -m coverage xml && python -m coverage html && python -m coverage report; \
	)

docs: install
	@( \
		source venv/bin/activate; \
		python -m pip install -r docs/requirements.txt; \
		sphinx-build -M html docs _build/docs -n; \
	)

local:
	@rm -rf *.egg-info dist
	@( \
		$(PYTHON_BIN) setup.py sdist; \
		$(PYTHON_BIN) -m pip install dist/*.tar.gz; \
	)

validate-release:
	@if [[ "${VERSION}" == "" ]]; then echo "VERSION is not set" & exit 1 ; fi

	@if [[ $$(grep "__version__ = \"${VERSION}\"" setup.py) == "" ]] ; then echo "Version not bumped in setup.py" & exit 1 ; fi
	@if [[ $$(grep "__version__ = \"${VERSION}\"" pyngrok/ngrok.py) == "" ]] ; then echo "Version not bumped in pyngrok/ngrok.py" & exit 1 ; fi

upload:
	@rm -rf *.egg-info dist
	@( \
		source venv/bin/activate; \
		python -m pip install twine
		python setup.py sdist; \
		python -m twine upload dist/*; \
	)
