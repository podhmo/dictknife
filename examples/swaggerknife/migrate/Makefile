default: clean 00
OPTS ?= "--log=DEBUG"

dst:
	mkdir -p dst

clean:
	rm -rf dst

00: dst
	# xxx: savedir is not good parameters. emitting onto dst/00/src/00
	python 00migrate.py --src src/00/main.yaml --savedir dst/00
	diff -ru src/00 dst/00/src/00 > dst/00/main.diff || exit 0
