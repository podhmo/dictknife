test:
	python setup.py test

docs: runlib
	$(MAKE) html -C docs
.PHONY: docs

runlib:
	$(MAKE) -C examples/library
	$(MAKE) -C examples/library2

# integration tests (regression tests)
WHERE ?= .
run:
	find ${WHERE} -mindepth 2 -name Makefile | grep -v optional/sheet | grep -v docs | xargs -n 1 -I{} dirname {} | xargs -n 1 make -C || echo *******NG**********

