# CMD ?= python -m dictknife.swaggerknife.stream.jsonschema
CMD ?= python -m dictknife.swaggerknife.stream.jsonschema.codegen

# OPTS ?= --log=DEBUG

default:
	@$(CMD) separated/main.yaml ${OPTS}

00:
	@$(CMD) examples/00*.yaml ${OPTS}
01:
	@$(CMD) examples/01*.yaml ${OPTS}
02:
	@$(CMD) examples/02*.yaml ${OPTS}
03:
	@$(CMD) examples/03*.yaml ${OPTS}
04:
	@$(CMD) examples/04*.yaml ${OPTS}
05:
	@$(CMD) examples/05*.yaml ${OPTS}
