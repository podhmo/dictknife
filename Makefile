docs: runlib
	$(MAKE) html -C docs
.PHONY: docs

runlib:
	make -C examples/library

run:
	for i in `find . -name Makefile | grep -v docs`; do make -C `dirname $$i`; done
