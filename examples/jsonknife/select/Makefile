default: 00 01 02 03 04 05 06 07 08 09

OPTS ?= --debug --log=DEBUG

dst:
	mkdir -p dst

00: dst
	jsonknife ${OPTS} select --src src/colors.yaml --ref "#/rainbow/yellow" --dst dst/00select.yaml

01: dst
	jsonknife ${OPTS} select --src src/colors.yaml --ref "#/rainbow/yellow@yellow" --dst dst/01select.yaml

02: dst
	jsonknife ${OPTS} select --src src/colors.yaml --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" --dst dst/02select.yaml

# backword compatibility. --unwrap x --wrap y == --ref "x@y"
03: dst
	jsonknife ${OPTS} select --src src/colors.yaml --unwrap "#/rainbow/yellow" --wrap "yellow" --dst dst/03select.yaml

# empty ref
04: dst
	jsonknife ${OPTS} select --src src/person.json --ref "@person" --dst dst/04person.json
05:
	jsonknife ${OPTS} select --src src/people.csv --ref "#/0@first" --dst dst/05first.json
06:
	jsonknife ${OPTS} select --src src/people.csv --ref "#/-1@last" --dst dst/06last.json
07:
	jsonknife ${OPTS} select --src src/people.csv --ref "@people" --dst dst/07people.json
08:
	jsonknife ${OPTS} select --src src/people.csv --dst dst/08data.json
09:
	dictknife cat src/people.csv -o json | jsonknife ${OPTS} select --ref "@people" --dst dst/08people.json

