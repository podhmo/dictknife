default: clean 00 01 02 03
OPTS ?= "--log=DEBUG"

dst:
	mkdir -p dst

clean:
	rm -rf dst

00: dst
	# xxx: savedir is not good parameters. emitting onto dst/00/src/00
	python 00migrate.py ${OPTS} --src src/00/main.yaml --savedir dst/00
	diff -ru src/00 dst/00/src/00 > dst/00/main.diff || exit 0
01: dst
	# xxx: savedir is not good parameters. emitting onto dst/01/src/01
	python 2to3.py --sort-keys --src src/2.0.yaml --savedir dst/01
02: dst
	python 2to3.py --sort-keys --src src/separated/2.0/main.yaml --savedir dst/02
03: dst
	python 2to3.py --sort-keys --src src/more2.0.yaml --savedir dst/03
