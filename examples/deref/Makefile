default: orthodox

orthodox:
	jsonknife deref --src src/person.yaml --dst dst/extracted.yaml --ref "#/definitions/person"
	jsonknife examples dst/extracted.yaml --format yaml > dst/data.yaml

ref:
	jsonknife deref --src src/primitive.yaml --ref "#/definitions/name" > dst/00nowrap.yaml
	jsonknife deref --src src/primitive.yaml --ref "#/definitions/name" --wrap name > dst/01wrap.yaml
	jsonknife deref --src src/primitive.yaml --ref "#/definitions/name@#/definitions/NAME" --ref "#/definitions/age@#/definitions/AGE" > dst/02wrap-pair.yaml

# shortcut
# jsonknife samplevalue <(jsonknife extract --src src/person.yaml --ref "#/definitions/person")
