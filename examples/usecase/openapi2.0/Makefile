PWD ?= .
SRC ?= ${PWD}/src/main.yaml
DST ?= ${PWD}/dst/openapi.yaml

gen:
	mkdir -p `dirname {DST}`
	swaggerknife bundle --src ${SRC} --dst ${DST}
	swaggerknife bundle --src ${SRC} --dst `echo ${DST} | sed 's/\.yaml/.flatten.yaml/'` --flatten

diff:
	diff -u ${DST} `echo ${DST} | sed 's/\.yaml/.flatten.yaml/'`
