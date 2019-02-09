default: 00 01
OPTS ?= "--log=DEBUG"

dst:
	mkdir -p dst

00: dst
	jsonknife examples src/00/person.yaml --ref "#/definitions/person" --dst dst/00.json
01:
	cat src/00/person.yaml | jsonknife examples --ref "#/definitions/person" --dst dst/01.json
