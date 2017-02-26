default: orthodox

orthodox:
	jsonknife extract --src src/person.yaml --dst dst/extracted.yaml --ref "#/definitions/person"
	jsonknife samplevalue dst/extracted.yaml > dst/data.json

# shortcut
# jsonknife samplevalue <(jsonknife extract --src src/person.yaml --ref "#/definitions/person")
