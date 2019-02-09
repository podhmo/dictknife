default: 00 01 02 03 04 05 06 07 08 09 10
OPTS ?=

dst:
	mkdir -p dst
00: dst
	python 00*.py src/00/main.yaml > dst/00.yaml
01: dst
	python 01*.py src/00/main.yaml > dst/01.yaml
02: dst
	python 02*.py src/00/main.yaml > dst/02.yaml

## commands
# all
03: dst
	jsonknife ${OPTS} bundle --src src/03/main.yaml > dst/03.yaml
# onefile
04: dst
	jsonknife ${OPTS} bundle --src src/03/person.yaml > dst/04.yaml
# one definition (xxx)
05: dst
	jsonknife ${OPTS} bundle --src "src/03/person.yaml#/definitions/person" > dst/05.yaml
# one definition, no ref
06: dst
	jsonknife ${OPTS} bundle --src "src/03/primitive/name.yaml#/definitions/point" > dst/06.yaml
# one definition, external file ref
07: dst
	jsonknife ${OPTS} bundle --src "src/03/team.yaml#/definitions/team" > dst/07.yaml
# fix conflict, when same data reference
08: dst
	jsonknife ${OPTS} bundle --src "src/08/config.json" > dst/08.yaml
09: dst
	jsonknife ${OPTS} bundle --src "src/08/config2.json" > dst/09.yaml
10: dst
	jsonknife ${OPTS} bundle --src "src/10/main.json#/definitions/x" --extra "src/08/config.json#/definitions/db" > dst/10.yaml
