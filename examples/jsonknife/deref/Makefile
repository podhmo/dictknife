default: bundle deref

bundle:
	swaggerknife --log=DEBUG bundle --src src/main.json | tee bundle.yaml

deref:
	jsonknife --log=DEBUG deref --src src/main.json | tee deref.yaml
