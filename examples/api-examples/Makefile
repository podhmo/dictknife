default: bundle select

dst:
	mkdir -p dst

bundle: dst
	jsonknife --log=DEBUG bundle --src src/main.json > dst/bundle.yaml

select: dst
	jsonknife --log=DEBUG select --src src/main.json > dst/select.yaml
