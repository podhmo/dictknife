defaut: clean 00 01 02 03
OPTS ?= 

clean:
	rm -rf dst

dst:
	mkdir -p dst

# output format
00: dst
	dictknife ${OPTS} cat src/00output-format/person.json --dst dst/00person.json
	dictknife ${OPTS} --compact cat src/00output-format/person.json --dst dst/00person.compact.json
	dictknife ${OPTS} cat src/00output-format/person.json --dst dst/00person.yaml
	dictknife ${OPTS} cat src/00output-format/person.json --dst dst/00person.toml
	dictknife ${OPTS} cat src/00output-format/person.json --dst dst/00person.csv

# nested
01: dst
	dictknife ${OPTS} --flatten cat src/01nested/person.json --dst dst/01nested.flatten.json
	dictknife ${OPTS} cat src/01nested/person.json --dst dst/01nested.csv
	dictknife ${OPTS} --flatten cat src/01nested/person.json --dst dst/01nested.flatten.csv

# unescape
02: dst
	dictknife ${OPTS} --unescape unicode cat src/02unescape/unicode.json --dst dst/02unescape_unicode.json
	dictknife ${OPTS} --unescape url cat src/02unescape/url.json --dst dst/02unescape_url.json

# extra option
03: dst
	dictknife ${OPTS} cat --extra--fullscan src/03extra-option/people.json --dst dst/03people.csv
	dictknife ${OPTS} cat src/03extra-option/people.json -o csv 2>&1 > dst/03people.ng.csv || exit 0

# merge list
# 04:
# 	dictknife ${OPTS} cat 
