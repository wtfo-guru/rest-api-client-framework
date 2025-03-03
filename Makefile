SHELL:=/usr/bin/env bash

PROJECT_NAME ?= $(shell basename $$(git rev-parse --show-toplevel) | sed -e "s/^python-//")
PACKAGE_DIR ?= api_client
PROJECT_VERSION ?= $(shell grep ^current_version .bumpversion.cfg | awk '{print $$NF'})
BUILD_VERSION ?= $(shell echo $(PROJECT_VERSION) | tr '-' '.')
BUILD_NAME ?= $(shell echo $(PROJECT_NAME) | tr "-" "_")
TEST_DIR = tests


.PHONY: update
update:
	poetry update --with test --with docs --with dev
	pre-commit-update-repo.sh

.PHONY: vars
vars:
	@echo "PROJECT_NAME: $(PROJECT_NAME)"
	@echo "PACKAGE_DIR: $(PACKAGE_DIR)"
	@echo "PROJECT_VERSION: $(PROJECT_VERSION)"
	# perl -e 'print "MYPYPATH: $$ENV{MYPYPATH}\n"'

.PHONY: black
black:
	poetry run isort $(PACKAGE_DIR) $(TEST_DIR)
	poetry run black $(PACKAGE_DIR) $(TEST_DIR)

.PHONY: mypy
mypy: black
	# poetry run mypy $(PACKAGE_DIR) $(TEST_DIR)
	poetry run mypy $(PACKAGE_DIR)

.PHONY: lint
lint: mypy
	poetry run flake8 $(PACKAGE_DIR) $(TEST_DIR)
	poetry run doc8 -q docs

.PHONY: sunit
sunit:
	poetry run pytest -s $(TEST_DIR)

.PHONY: unit
unit:
	poetry run pytest $(TEST_DIR)

.PHONY: package
package:
	poetry check
	poetry run pip check

.PHONY: safety
safety:
	poetry run safety scan --full-report

.PHONY: test
test: safety ghtest
	poetry run coverage-badge -f -o coverage.svg

.PHONY: ghtest
ghtest: lint package unit

# .PHONY: publish
# publish: clean-build test
# 	manage-tag.sh -u v$(PROJECT_VERSION)
# 	poetry publish --build

# .PHONY: publish-test
# publish-test: clean-build test
# 	manage-tag.sh -u v$(PROJECT_VERSION)
# 	poetry publish --build -r test-pypi

.PHONY: tag
tag:
	manage-tag.sh -u v$(PROJECT_VERSION)

.PHONY: build
build: clean-build test tag
	poetry build
	sync-wheels.sh dist/$(BUILD_NAME)-$(PROJECT_VERSION)-py3-none-any.whl $(WHEELS)

docs/pages/changelog.rst: CHANGELOG.md
	m2r2 --overwrite CHANGELOG.md
	mv -f ./CHANGELOG.rst ./docs/pages/changelog.rst

docs/pages/contributing.rst: CONTRIBUTING.md
	m2r2 --overwrite CONTRIBUTING.md
	mv -f ./CONTRIBUTING.rst ./docs/pages/contributing.rst

.PHONY: release
release: test docs/pages/changelog.rst docs/pages/contributing.rst
	$(eval OK := $(shell check-release-okay))
	@if [ "$(OK)" == "YES" ]; then\
		bump-release;\
	else\
		echo $(OK);\
	fi

.PHONY: docs
docs: docs/pages/changelog.rst docs/pages/contributing.rst
# TODO: check if doc8 is in virtual environment if yes rebuild virtual environment
# TODO: dynamically determin vitual environment python version
# poetry env remove 3.10
# poetry update --with docs
#	@cd docs && SPHINXOPTS="-vvW" BUILD="SPHINXBUILD="poetry run sphinx-build" $(MAKE) html
	$(error "Docs are built automatically by https://readthedocs.org")

.PHONY: clean clean-build clean-pyc clean-test clean-docs
clean: clean-build clean-pyc clean-test clean-docs ## remove all build, test, coverage and Python artifacts

clean-docs: ## remove docs artifacts
	rm -fr docs/_build docs/node_modules/
	rm -f docs/.linthtmlrc.yaml docs/package-lock.json docs/package.json

clean-build: ## remove build artifacts
	rm -fr build/
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
