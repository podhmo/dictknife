default: 00 01 02 03
OPTS ?= --debug --log=DEBUG

dst:
	mkdir -p dst

00: dst
	jsonknife ${OPTS} examples src/00/person.yaml --ref "#/definitions/person" --dst dst/00.json
01: dst
	cat src/00/person.yaml | jsonknife ${OPTS} examples --ref "#/definitions/person" --dst dst/01.json

02: dst
	jsonknife ${OPTS} examples src/02/error.yaml --ref "#/definitions/error" --dst dst/02.json
03: dst
	jsonknife ${OPTS} select --src src/02/error.yaml | jsonknife ${OPTS} examples --ref "#/definitions/error" --dst dst/03.json
