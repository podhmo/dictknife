dst/%.output : %.py
	python $< > $@

default: clean dst $(shell ls *.py | sed 's@^@dst/@g; s@\.py$$@.output@g')
dst:
	mkdir -p dst
clean:
	rm -rf dst

