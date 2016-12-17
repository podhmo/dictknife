this is tiny json-reference linker.

```bash
$ make
python linker.py --logging src/main.json | tee output.json
INFO:__main__:ref ./api/me.json#paths/me (on src/main.json)
INFO:__main__:ref ../definitions/user.json#/definitions/user (on ./src/api/me.json)
INFO:__main__:ref ./primitive.json#/definitions/name (on ./src/definitions/user.json)
INFO:__main__:ref ./primitive.json#/definitions/name (on ./src/definitions/user.json)
INFO:__main__:ref #/definitions/user (on ./src/definitions/user.json)
INFO:__main__:ref ./api/user.json#paths/users (on src/main.json)
INFO:__main__:ref ../definitions/user.json#/definitions/userlist (on ./src/api/user.json)
```

