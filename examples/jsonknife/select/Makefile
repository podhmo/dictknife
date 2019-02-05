default: 00select 01select 02select 00cut

cmd := jsonknife select --src src/colors.yaml

dst:
	mkdir -p dst

00select: dst
	${cmd} --ref "#/rainbow/yellow" > dst/00select.yaml

01select: dst
	${cmd} --ref "#/rainbow/yellow@yellow" > dst/01select.yaml

02select: dst
	${cmd} --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" > dst/02select.yaml

00cut: dst
	${cmd} --ref "#/rainbow/yellow@yellow" --ref "#/rainbow/indigo@indigo" | jsonknife cut --ref "#/yellow" > dst/00cut.yaml
