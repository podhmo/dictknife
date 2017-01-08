default: concat transform

concat:
	mkdir -p dst/00concat
	dictknife concat src/00concat/base.yaml src/00concat/cat.yaml > dst/00concat/cat.yaml
	dictknife concat src/00concat/base.yaml src/00concat/dog.json > dst/00concat/dog.yaml

transform:
	mkdir -p dst/01transform
	dictknife transform --function misc/transform.py:lift --src src/01transform/properties.yaml --name person > dst/01transform/person.yaml
	dictknife transform --code 'lambda d,name=None: {"definitions": {name: d}}' --src src/01transform/properties.yaml --name person > dst/01transform/person2.json

.PHONY: dst
