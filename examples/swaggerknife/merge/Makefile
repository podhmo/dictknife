default: 00 01 02

dst:
	mkdir -p dst

00: dst
	swaggerknife merge src/*.json --dst dst/00ref.json
01: dst
	swaggerknife merge src/*.json --style=whole --dst dst/01whole.json

# conflicted
02: dst
	(swaggerknife merge src/*.json src/conflicted/*.json --strict --dst dst/02ref.json |& tee dst/02conflicted.error) || echo ok
