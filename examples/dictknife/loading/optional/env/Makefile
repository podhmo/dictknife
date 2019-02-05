default: 00 01

NAME := foo
AGE := 20

dst:
	mkdir -p dst

00: dst
	dictknife cat src/data.env --dst dst/person.json -i env
01: dst
	dictknife cat src/data.yaml.env --dst dst/person.yaml
