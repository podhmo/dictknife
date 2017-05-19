default: orthodox

orthodox:
	jsonknife deref --src src/person.yaml --dst dst/extracted.yaml --ref "#/definitions/person"
	jsonknife examples dst/extracted.yaml > dst/data.json

ref:
	jsonknife deref --src src/primitive.yaml --ref "#/definitions/name" > dst/00nounwrap.yaml
	jsonknife deref --src src/primitive.yaml --ref "#/definitions/name" --unwrap name > dst/01unwrap.yaml
	jsonknife deref --src src/primitive.yaml --ref "#/definitions/name@#/definitions/NAME" --ref "#/definitions/age@#/definitions/AGE" > dst/02unwrap-pair.yaml

# shortcut
# jsonknife samplevalue <(jsonknife extract --src src/person.yaml --ref "#/definitions/person")
