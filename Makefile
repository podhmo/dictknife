test:
	python setup.py test

docs: runlib
	$(MAKE) html -C docs
.PHONY: docs

lint:
	flake8 --show-source --ignore=E501,E121,W503 dictknife

format:
#	pip install -e .[dev]
	black dictknife setup.py
.PHONY: format

build:
#	pip install wheel
	python setup.py sdist bdist_wheel
.PHONY: build

upload:
#	pip install twine
	twine check dist/dictknife-$(shell cat VERSION)*.gz
	twine check dist/dictknife-$(shell cat VERSION)*.whl
	twine upload dist/dictknife-$(shell cat VERSION)*.gz
	twine upload dist/dictknife-$(shell cat VERSION)*.whl
.PHONY: upload

# integration tests (regression tests)
WHERE ?= .
run:
	$(MAKE) --silent _find-candidates | xargs -n 1 make -C || (echo "**********NG**********" && exit 1)
ci:
	$(MAKE) --silent _find-candidates | xargs -n 1 echo "OPTS=--log=WARNING" make --silent -C | bash -x -e || (echo "**********NG**********" && exit 1)
	test -z `git diff` || (echo  "*********DIFF*********" && git diff && exit 2)
_find-candidates:
	@find ${WHERE} -mindepth 2 -name Makefile | grep -v optional/sheet | grep -v docs | xargs -n 1 -I{} dirname {}