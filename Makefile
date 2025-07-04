# Makefile for managing the project with Hatch.
# This file provides shortcuts for common development tasks defined in pyproject.toml.

.PHONY: test docs lint format build upload run ci _find-candidates

# Run tests using the 'test' environment defined in pyproject.toml
test:
	hatch run test

# Build the documentation using the 'docs' environment
docs:
	hatch run docs:build

# Run the linter
lint:
	hatch run lint

# Format the code with black
format:
	hatch run format

# Build the sdist and wheel distributions
build:
	hatch build

# Publish the package to a repository (e.g., PyPI)
# This replaces the old 'twine upload' logic.
upload:
	hatch publish

# ==============================================================================
# Integration tests (regression tests) - Preserved from original Makefile
# ==============================================================================

WHERE ?= .

run:
	$(MAKE) --silent _find-candidates | xargs -n 1 make -C || (echo "**********NG**********" && exit 1)

ci:
	$(MAKE) --silent _find-candidates | xargs -n 1 echo "OPTS=--log=WARNING" make --silent -C | bash -x -e || (echo "**********NG**********" && exit 1)
	test -z `git diff` || (echo  "*********DIFF*********" && git diff && exit 2)

_find-candidates:
	@find ${WHERE} -mindepth 2 -name Makefile | grep -v optional/sheet | grep -v docs | xargs -n 1 -I{} dirname {}