from dictknife import deepequal

a = {
    "errors": [{
        "error": "invalid",
        "field": "email"
    }, {
        "error": "required",
        "field": "name"
    }],
    "success": False
}

b = {
    "success": False,
    "errors": [{
        "error": "required",
        "field": "name"
    }, {
        "error": "invalid",
        "field": "email"
    }]
}

print("=")
print("\t", a == b)
print("deepequal")
print("\t", deepequal(a, b, normalize=True))
