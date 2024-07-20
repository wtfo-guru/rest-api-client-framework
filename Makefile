SHELL:=/usr/bin/env bash

PROJECT_NAME ?= $(shell basename $$(git rev-parse --show-toplevel) | sed -e "s/^python-//")
PACKAGE_DIR ?= api_client
BUILD_NAME ?= $(shell echo $(PROJECT_NAME) | tr "-" "_")
PROJECT_VERSION ?= $(shell grep ^current_version .bumpversion.cfg | awk '{print $$NF'} | tr '-' '.')
WHEELS ?= /home/jim/kbfs/private/jim5779/wheels
TEST_MASK = tests


.PHONY: update
update:
	poetry update --with test --with docs --with dev

.PHONY: vars
vars:
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PACKAGE_DIR: $(PACKAGE_DIR)"
	@echo "PROJECT_VERSION: $(PROJECT_VERSION)"
	# perl -e 'print "MYPYPATH: $$ENV{MYPYPATH}\n"'

.PHONY: black
black:
	poetry run isort $(PACKAGE_DIR) $(TEST_MASK)
	poetry run black $(PACKAGE_DIR) $(TEST_MASK)

.PHONY: mypy
mypy: black
	# poetry run mypy $(PACKAGE_DIR) $(TEST_MASK)
	poetry run mypy $(PACKAGE_DIR)

.PHONY: lint
lint: mypy
	poetry run flake8 $(PACKAGE_DIR) $(TEST_MASK)
	poetry run doc8 -q docs

.PHONY: sunit
sunit:
	poetry run pytest -s test

.PHONY: unit
unit:
	poetry run pytest test

.PHONY: package
package:
	poetry check
	poetry run pip check
	# poetry run safety check --full-report

.PHONY: test
test: lint package unit

# .PHONY: publish
# publish: clean-build test
# 	manage-tag.sh -u v$(PROJECT_VERSION)
# 	poetry publish --build

# .PHONY: publish-test
# publish-test: clean-build test
# 	manage-tag.sh -u v$(PROJECT_VERSION)
# 	poetry publish --build -r test-pypi

.PHONY: build
build: clean-build test
	manage-tag.sh -u v$(PROJECT_VERSION)
	poetry build
	cp dist/$(BUILD_NAME)-$(PROJECT_VERSION)-py3-none-any.whl $(WHEELS)
	sync-wheels


.PHONY: docs
docs:
	@cd docs && $(MAKE) $@

.PHONY: clean clean-build clean-pyc clean-test
clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr docs/_build
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache
	rm -fr .mypy_cache
	rm -fr .cache

# vim: ft=Makefile
