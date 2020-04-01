default: 00 01 02 03
TEE ?= 2>&1 >

# flatten
00: TARGET ?= person.json
00:
	dictknife transform $(shell echo $@*/)$(TARGET) --fn flatten -o json ${TEE} $(shell echo $@*/)person.flatten.json
	dictknife transform $(shell echo $@*/)$(TARGET) --fn flatten -o csv ${TEE} $(shell echo $@*/)person.flatten.csv
	dictknife transform $(shell echo $@*/)$(TARGET) --fn flatten -o md ${TEE} $(shell echo $@*/)person.flatten.md

# mixcase
01: TARGET ?= input.json
01:
	dictknife transform $(shell echo $@*/)$(TARGET) --fn snakecase_dict -o json ${TEE} $(shell echo $@*/)output.snakecase.json
	dictknife transform $(shell echo $@*/)$(TARGET) --fn camelcase_dict -o json ${TEE} $(shell echo $@*/)output.camelcase.json
	dictknife transform $(shell echo $@*/)$(TARGET) --fn kebabcase_dict -o json ${TEE} $(shell echo $@*/)output.kebabcase.json
	dictknife transform $(shell echo $@*/)$(TARGET) --fn pascalcase_dict -o json ${TEE} $(shell echo $@*/)output.pascalcase.json

# unflatten
02: TARGET ?= person.flatten.json
02:
	dictknife transform $(shell echo $@*/)$(TARGET) --fn unflatten -o json ${TEE} $(shell echo $@*/)person.flatten.unflatten.json
	dictknife diff $(shell echo 00*/)person.json  $(shell echo $@*/)person.flatten.unflatten.json ${TEE} $(shell echo $@*/)a.diff

# stdin
03: TARGET ?= person.json
03:
	cat $(shell echo $@*/)$(TARGET) | dictknife transform -i json --code "lambda d: {k.upper():v for k,v in d.items()}" -o json ${TEE} $(shell echo $@*/)person.upcase.json
