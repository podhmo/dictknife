default: 00 01
TEE ?= 2>&1 >

# flatten
00: TARGET ?= person.json
00:
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn flatten -o json ${TEE} $(shell echo $@*/)person.flatten.json
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn flatten -o csv ${TEE} $(shell echo $@*/)person.flatten.csv
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn flatten -o md ${TEE} $(shell echo $@*/)person.flatten.md

# mixcase
01: TARGET ?= input.json
01:
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn snakecase_dict -o json ${TEE} $(shell echo $@*/)output.snakecase.json
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn camelcase_dict -o json ${TEE} $(shell echo $@*/)output.camelcase.json
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn kebabcase_dict -o json ${TEE} $(shell echo $@*/)output.kebabcase.json
	dictknife transform --src $(shell echo $@*/)$(TARGET) --fn pascalcase_dict -o json ${TEE} $(shell echo $@*/)output.pascalcase.json
