default: 00 01 02
OPTS ?= --log=DEBUG

dst:
	mkdir -p dst
00: dst
	jsonknife ${OPTS} cut --src src/main.yaml --ref "#/definitions/y" --dst dst/00.yaml
01: dst
	jsonknife ${OPTS} cut --src src/main.yaml --ref "#/definitions/z" --ref "#/definitions/y" --dst dst/00.yaml
02: dst
	jsonknife ${OPTS} cut --src src/x.yaml --ref "#/definitions/x/properties/score" --dst dst/02.yaml
