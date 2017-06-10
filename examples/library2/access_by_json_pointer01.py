from dictknife.jsonknife import access_by_json_pointer


d = {
    "/foo/bar/boo": "foo",
}

q = "~1foo~1bar~1boo"
print("access : {}".format(q))
print(access_by_json_pointer(d, q))
