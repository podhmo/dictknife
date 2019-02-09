dst/%.output : src/%.py
	python $< 2>&1 > $@

default: clean dst $(shell ls src/*.py | sed 's@src/@dst/@g; s@\.py$$@.output@g')
dst:
	mkdir -p dst
clean:
	rm -rf dst
