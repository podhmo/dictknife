default: deref bundle
	diff -u dst/deref.yaml dst/bundle.yaml

deref:
	jsonknife deref --src spec/swagger.yaml | tee dst/deref.yaml

bundle:
	swaggerknife bundle --src spec/swagger.yaml | tee dst/bundle.yaml
