test:
	python setup.py test

docs: runlib
	$(MAKE) html -C docs
.PHONY: docs

runlib:
	$(MAKE) -C examples/library
	$(MAKE) -C examples/library2

run:
	for i in `find . -name Makefile | grep -v docs`; do make -C `dirname $$i`; done
