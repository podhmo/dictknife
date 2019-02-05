this is the tiny examples, for bundling separated files.

two flavor are existed.

- select
- bundle

## select

```bash
$ make select
DEBUG:jsonknife.resolver:load file[1]: 'src/main.json' (where='*root*')
DEBUG:jsonknife.resolver:load file[2]: './api/me.json' (where='./src/main.json')
DEBUG:jsonknife.resolver:load file[3]: '../definitions/user.json' (where='./src/api/me.json')
DEBUG:jsonknife.resolver:load file[4]: './primitive.json' (where='./src/definitions/user.json')
DEBUG:jsonknife.resolver:load file[2]: './api/user.json' (where='./src/main.json')
DEBUG:jsonknife.resolver:load file[3]: '../definitions/user.json' (where='./src/api/user.json')
DEBUG:jsonknife.resolver:load file[4]: './primitive.json' (where='./src/definitions/user.json')
```

## bundle

```bash
$ make bundle
jsonknife --log=DEBUG bundle --src src/main.json > dst/bundle.yaml
DEBUG:jsonknife.resolver:load file[1]: 'src/main.json' (where='*root*')
DEBUG:jsonknife.resolver:load file[2]: './api/me.json' (where='./src/main.json')
DEBUG:jsonknife.resolver:load file[3]: '../definitions/user.json' (where='./src/api/me.json')
DEBUG:jsonknife.resolver:load file[4]: './primitive.json' (where='./src/definitions/user.json')
DEBUG:jsonknife.resolver:load file[2]: './api/user.json' (where='./src/main.json')
DEBUG:jsonknife.resolver:load file[3]: '../definitions/user.json' (where='./src/api/user.json')
DEBUG:jsonknife.bundler:fix ref: './api/me.json#/paths/me' -> '#/paths/me' (where='./src/main.json')
DEBUG:jsonknife.bundler:fix ref: './api/user.json#/paths/users' -> '#/paths/users' (where='./src/main.json')
DEBUG:jsonknife.bundler:fix ref: '../definitions/user.json#/definitions/user' -> '#/definitions/user' (where='./src/api/me.json')
DEBUG:jsonknife.bundler:fix ref: './primitive.json#/definitions/name' -> '#/definitions/name' (where='./src/definitions/user.json')
DEBUG:jsonknife.bundler:fix ref: './primitive.json#/definitions/name' -> '#/definitions/name' (where='./src/definitions/user.json')
DEBUG:jsonknife.bundler:fix ref: '../definitions/user.json#/definitions/userlist' -> '#/definitions/userlist' (where='./src/api/user.json')
```

