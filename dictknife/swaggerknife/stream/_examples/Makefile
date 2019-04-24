OPTS ?= --log DEBUG

prepare:
	jsonknife bundle --src 00separated/main.yaml --dst 00bundle.yaml

00:
	@python -m dictknife.swaggerknife.stream 00bundle.yaml

01:
	@python -m dictknife.swaggerknife.stream ${OPTS} 00separated/main.yaml
02:
	@python -m dictknife.swaggerknife.stream ${OPTS} 01separated/main.yaml
