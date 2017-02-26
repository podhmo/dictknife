default: concat transform diff

concat:
	mkdir -p dst/00concat
	dictknife concat src/00concat/base.yaml src/00concat/cat.yaml > dst/00concat/cat.yaml
	dictknife concat src/00concat/base.yaml src/00concat/dog.json > dst/00concat/dog.yaml

transform:
	mkdir -p dst/01transform
	dictknife transform --function misc/transform.py:lift --config '{"name": "person"}' --src src/01transform/properties.yaml > dst/01transform/person.yaml
	dictknife transform --code 'lambda d,**kwargs: {"definitions": {"person": d}}' --src src/01transform/properties.yaml > dst/01transform/person2.json

diff:
	mkdir -p dst/02diff
	dictknife diff src/02diff/left.yaml src/02diff/right.json > dst/02diff/person.diff

.PHONY: dst
