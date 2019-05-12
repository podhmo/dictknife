# CMD ?= python -m dictknife.swaggerknife.stream.jsonschema
CMD ?= python -m dictknife.swaggerknife.stream.jsonschema.codegen

# OPTS ?= --log=DEBUG
default: TARGET?=main
default:
	$(MAKE) ${TARGET}

main:
	@$(CMD) separated/main.yaml ${OPTS}
dst:
	mkdir -p dst
00: dst
	@$(CMD) examples/00*.yaml ${OPTS} | tee dst/00.py
01: dst
	@$(CMD) examples/01*.yaml ${OPTS} | tee dst/01.py
02: dst
	@$(CMD) examples/02*.yaml ${OPTS} | tee dst/02.py
03: dst
	@$(CMD) examples/03*.yaml ${OPTS} | tee dst/03.py
04: dst
	@$(CMD) examples/04*.yaml ${OPTS} | tee dst/04.py
05: dst
	@$(CMD) examples/05*.yaml ${OPTS} | tee dst/05.py
06: dst
	@$(CMD) examples/06*.yaml ${OPTS} | tee dst/06.py
07: dst
	@$(CMD) examples/07*.yaml ${OPTS} | tee dst/07.py

xxx: TARGET ?= default
xxx: CMD := python -m dictknife.swaggerknife.stream.jsonschema
xxx:
	$(MAKE) CMD="${CMD}" ${TARGET}
