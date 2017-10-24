default: gen gen2

gen:
	mkdir -p dst
	dictknife concat src/data.yaml --dst dst/person.yaml
	dictknife concat src/data.yaml --dst dst/person.json
	dictknife concat src/data.yaml --dst dst/person.toml

gen2:
	mkdir -p dst
	NAME=FOO AGE=20 dictknife concat src/data.yaml.env --dst dst/person2.yaml
	NAME=FOO AGE=20 dictknife concat src/data.env --dst dst/person2.json --input-format=env --format=json
