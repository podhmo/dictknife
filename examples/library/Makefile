%.output : %.py
	python $< > $@

default: $(shell ls *.py | grep -v '.output' | sed 's/\.py$$/.output/g')

clean:
	rm -f *.output

