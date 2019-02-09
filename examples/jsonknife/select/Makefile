default: 00 01 02 03

OPTS ?= --debug --log=DEBUG
cmd := jsonknife ${OPTS} select --src src/colors.yaml

dst:
	mkdir -p dst

00: dst
	${cmd} --ref "#/rainbow/yellow" > dst/00select.yaml

01: dst
	${cmd} --ref "#/rainbow/yellow@yellow" > dst/01select.yaml

02: dst
	${cmd} --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" > dst/02select.yaml

# backword compatibility. --unwrap x --wrap y == --ref "x@y"
03: dst
	${cmd} --unwrap "#/rainbow/yellow" --wrap "yellow" > dst/03select.yaml
