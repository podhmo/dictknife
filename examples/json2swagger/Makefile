default:
	mkdir -p dst
	swaggerknife json2swagger src/config.json --name config --dst dst/config-spec.yaml
	swaggerknife tojsonschema dst/config-spec.yaml --name config --dst dst/config-schema.json
