default: clean 00 01 02 03 04
OPTS ?= "--log=DEBUG"
EXTRA_OPTS := --sort-keys

dst:
	mkdir -p dst

clean:
	rm -rf dst

validate:
	for i in `ls src/*.yaml| grep 3`; do $(MAKE) -s validate-one FILE=$$i; done
validate-one: FILE ?= src/3.0.yaml
validate-one:
	echo ${FILE}
	docker-compose run --rm -w /project validator ${FILE}

00: dst
	# xxx: savedir is not good parameters. emitting onto dst/00/src/00
	python 00migrate.py ${OPTS} --src src/00/main.yaml --savedir dst/00
	diff -ru src/00 dst/00/src/00 > dst/00/main.diff || exit 0
01: dst
	# xxx: savedir is not good parameters. emitting onto dst/01/src/01
	python 2to3.py ${OPTS} ${EXTRA_OPTS} --src src/2.0.yaml --savedir dst/01
02: dst
	python 2to3.py ${OPTS} ${EXTRA_OPTS} --src src/separated/2.0/main.yaml --savedir dst/02
	jsonknife bundle --src dst/02/main.yaml --dst dst/02/bundle.yaml
03: dst
	python 2to3.py ${OPTS} ${EXTRA_OPTS} --src src/more2.0.yaml --savedir dst/03
04: dst
	python 2to3.py ${OPTS} ${EXTRA_OPTS} --src src/separated/more2.0/main.yaml --savedir dst/04
	jsonknife bundle --src dst/04/main.yaml --dst dst/04/bundle.yaml

2to3:
	python 2to3.py ${OPTS} --src src/more2.0.yaml --dry-run --savedir dst/xxxx

