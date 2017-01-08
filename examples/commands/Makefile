default: concat

concat:
	mkdir -p dst/00concat
	dictknife concat src/00concat/base.yaml src/00concat/cat.yaml > dst/00concat/cat.yaml
	dictknife concat src/00concat/base.yaml src/00concat/dog.json > dst/00concat/dog.yaml

.PHONY: dst
