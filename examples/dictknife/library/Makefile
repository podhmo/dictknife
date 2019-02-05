%.output : %.py
	python $< > $@

default: $(shell ls *.py | sed 's/\.py$$/.output/g')

clean:
	rm -f *.output

