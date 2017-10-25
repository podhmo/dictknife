PWD ?= .
SRC ?= ${PWD}/src/main.yaml
DST ?= ${PWD}/dst/openapi.yaml

default:
	mkdir -p `dirname {DST}`
	swaggerknife bundle --src ${SRC} --dst ${DST}
