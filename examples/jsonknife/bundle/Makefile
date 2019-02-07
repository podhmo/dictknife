default: 00 01 02 03 04 05 06 07
dst:
	mkdir -p dst
00: dst
	python 00*.py src/main.yaml > dst/00.yaml
01: dst
	python 01*.py src/main.yaml > dst/01.yaml
02: dst
	python 02*.py src/00/main.yaml > dst/02.yaml

## commands
# all
03: dst
	jsonknife bundle --src src/01/main.yaml > dst/03.yaml
# onefile
04: dst
	jsonknife bundle --src src/01/person.yaml > dst/04.yaml
# one definition (xxx)
05: dst
	jsonknife bundle --src "src/01/person.yaml#/definitions/person" > dst/05.yaml
# one definition, no ref
06: dst
	jsonknife bundle --src "src/01/primitive/name.yaml#/definitions/point" > dst/06.yaml
# one definition, external file ref
07: dst
	jsonknife bundle --src "src/01/team.yaml#/definitions/team" > dst/07.yaml
