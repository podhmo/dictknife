default: clean
	$(MAKE) 00 01 02 03 04 05 06
TEE := 2>&1 >
OPTS ?=

clean:
	rm -rf dst
dst:
	mkdir -p dst
00: DIR := $(shell ls src | grep 00)
00: dst
	mkdir -p dst/${DIR}
	python 00*.py src/00*/main.yaml ${TEE} dst/${DIR}/bundle.yaml
	python 01with-version*.py src/00*/main.yaml ${TEE} dst/${DIR}/with-version.yaml
	python 02xref.py src/00*/main.yaml ${TEE} dst/${DIR}/xref.yaml

## commands
01: DIR := $(shell ls src | grep 01)
01: dst
	mkdir -p dst/${DIR}
	jsonknife ${OPTS} bundle --src src/${DIR}/main.yaml ${TEE} dst/${DIR}/bundle.yaml
	jsonknife ${OPTS} bundle --src src/${DIR}/person.yaml ${TEE} dst/${DIR}/onefile-person.yaml
	jsonknife ${OPTS} bundle --src "src/${DIR}/person.yaml#/definitions/person" ${TEE} dst/${DIR}/onedefinition-hasref.yaml
	jsonknife ${OPTS} bundle --src "src/${DIR}/primitive/name.yaml#/definitions/point" ${TEE} dst/${DIR}/onedefinition-primitive.yaml
	jsonknife ${OPTS} bundle --src "src/${DIR}/team.yaml#/definitions/team" ${TEE} dst/${DIR}/onedefinition-external-object.yaml

# regression test for nodup
02: DIR := $(shell ls src | grep 02)
02: dst
	mkdir -p dst/${DIR}
	jsonknife ${OPTS} bundle --src "src/${DIR}/config.json" ${TEE} dst/${DIR}/config.yaml
	jsonknife ${OPTS} bundle --src "src/${DIR}/config2.json" ${TEE} dst/${DIR}/config2.yaml

03: DIR := $(shell ls src | grep 03)
03: DIR2 := $(shell ls src | grep 02)
03: dst
	mkdir -p dst/${DIR}
	jsonknife ${OPTS} bundle --src "src/${DIR}/main.json#/definitions/x" --extra "src/${DIR2}/config.json#/definitions/db" ${TEE} dst/${DIR}/bundle.yaml

# conflictted
04: DIR := $(shell ls src | grep 04)
04: dst
	mkdir -p dst/${DIR}
	jsonknife ${OPTS} bundle --src src/${DIR}/main.yaml --dst dst/${DIR}/bundle.yaml

# conflict on samefile
05: DIR := $(shell ls src | grep 05)
05: dst
	mkdir -p dst/${DIR}
	jsonknife ${OPTS} bundle --src src/${DIR}/main.yaml --dst dst/${DIR}/bundle.yaml

06: DIR := $(shell ls src | grep 06)
06: dst
	mkdir -p dst/${DIR}
	jsonknife ${OPTS} bundle --src src/${DIR}/main.yaml --dst dst/${DIR}/bundle.yaml
	jsonknife ${OPTS} bundle --flavor=openapiv2 --src src/${DIR}/main.v2.yaml --dst dst/${DIR}/bundle.v2.yaml
