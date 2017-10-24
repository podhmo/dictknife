default: 00deref 01deref 02deref 00cut

00deref:
	mkdir -p dst
	jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow" > dst/00deref.yaml

01deref:
	jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow@yellow" > dst/01deref.yaml

02deref:
	jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" > dst/02deref.yaml

00cut:
	jsonknife deref --src src/colors.yaml --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" | jsonknife cut --ref "#/yellow" > dst/00cut.yaml
