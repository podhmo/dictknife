00:
	mkdir -p dst
	python 00*.py | tee dst/00.json
01:
	dictknife cat -i spreadsheet '1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms#/Class Data!A1:E' -o json | tee dst/01.json
02:
	dictknife cat -i spreadsheet 'https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit#gid=0' -o json | tee dst/02.json
