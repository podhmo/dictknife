dst/%.output : src/%.py
	python $< &> $@

default: clean dst $(shell ls src/*.py | sed 's@src/@dst/@g; s@\.py$$@.output@g')
dst:
	mkdir -p dst
clean:
	rm -rf dst
