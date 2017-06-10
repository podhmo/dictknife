%.output : %.py
	python $< main.yaml > $@

default: $(shell ls *.py | sed 's/\.py$$/.output/g')

clean:
	rm -f *.output
