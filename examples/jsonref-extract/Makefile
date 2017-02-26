default:
	jsonknife extract --src src/person.yaml --dst dst/extracted.yaml --ref "#/definitions/person"
	python dictplot.py --src dst/extracted.yaml --dst dst/data.yaml
