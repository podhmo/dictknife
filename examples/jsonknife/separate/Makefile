default: clean
	$(MAKE) 00 01 02
TEE := 2>&1 >
OPTS ?=

clean:
	rm -rf dst
dst:
	mkdir -p dst


00: DIR := $(shell ls src | grep 00)
00: dst
	mkdir -p dst/${DIR}
	jsonknife separate --src src/${DIR}/schema.json --dst dst/${DIR}/main.json -f json
	jsonknife bundle --src dst/${DIR}/main.json --dst dst/${DIR}/bundle.json
	dictknife diff -S src/${DIR}/schema.json dst/${DIR}/bundle.json | tee dst/${DIR}/a.diff

# recursion
# https://json-schema.org/understanding-json-schema/structuring.html
01: DIR := $(shell ls src | grep 01)
01: dst
	mkdir -p dst/${DIR}
	jsonknife separate --src src/${DIR}/schema.json --dst dst/${DIR}/main.json -f json
	jsonknife bundle --src dst/${DIR}/main.json --dst dst/${DIR}/bundle.json
	dictknife diff -S src/${DIR}/schema.json dst/${DIR}/bundle.json | tee dst/${DIR}/a.diff

# only definition
02: DIR := $(shell ls src | grep 02)
02: dst
	mkdir -p dst/${DIR}
	jsonknife separate --src src/${DIR}/schema.yaml --dst dst/${DIR}/main.yaml
	jsonknife bundle --src dst/${DIR}/main.yaml --dst dst/${DIR}/bundle.yaml
	dictknife diff -S src/${DIR}/schema.yaml dst/${DIR}/bundle.yaml | tee dst/${DIR}/a.diff
