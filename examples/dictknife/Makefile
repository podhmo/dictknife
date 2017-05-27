default: concat transform diff

concat:
	mkdir -p dst/00concat
	dictknife concat src/00concat/base.yaml src/00concat/cat.yaml > dst/00concat/cat.yaml
	dictknife concat src/00concat/base.yaml src/00concat/dog.json > dst/00concat/dog.yaml

concat2:
	mkdir -p dst/03concat
	dictknife concat src/03concat/abc.yaml src/03concat/xyz.yaml > dst/03concat/abcxyz.yaml

transform:
	mkdir -p dst/01transform
	dictknife transform --function misc/transform.py:lift --config '{"name": "person"}' --src src/01transform/properties.yaml > dst/01transform/person.yaml
	dictknife transform --code 'lambda d,**kwargs: {"definitions": {"person": d}}' --src src/01transform/properties.yaml > dst/01transform/person2.json

diff:
	mkdir -p dst/02diff
	dictknife diff src/02diff/left.yaml src/02diff/right.json > dst/02diff/person.diff

linecat:
	mkdir -p dst/04linecat
	dictknife linecat --src src/04linecat/log.txt --format json > dst/04linecat/log.json

.PHONY: dst
