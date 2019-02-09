default: bundle select

OPTS ?= "--log=DEBUG"

dst:
	mkdir -p dst

bundle: dst
	jsonknife ${OPTS} bundle --src src/main.json > dst/bundle.yaml

select: dst
	jsonknife ${OPTS} select --src src/main.json > dst/select.yaml
