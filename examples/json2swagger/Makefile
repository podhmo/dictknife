default: 00 01 02

00:
	mkdir -p dst
	swaggerknife json2swagger src/00config.json --name config --dst dst/00config-spec.yaml
	swaggerknife tojsonschema --src dst/00config-spec.yaml --name config --dst dst/00config-schema.json


01:
	mkdir -p dst
	swaggerknife json2swagger src/01* --name person --dst dst/01person-spec.yaml

02:
	mkdir -p dst
	swaggerknife json2swagger src/02with-annotations.yaml --annotate=src/02annotations.yaml --name Top --dst dst/02with-annotations-spec.yaml
