%.output : %.py
	python $< > $@

default: $(shell ls *.py | sed 's/\.py$$/.output/g')
	for i in `find . -name "Makefile" -mindepth 2`; do $(MAKE) -C `dirname $$i`; done

clean:
	rm -f *.output

