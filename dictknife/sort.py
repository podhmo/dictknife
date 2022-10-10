from collections import defaultdict
from .langhelpers import reify

# key order (alphabetical, order)
# value order (str, int)


def sort_flexibly(x):
    if hasattr(x, "__next__"):
        return _unwrap(_wrap(list(x)))
    return _unwrap(_wrap(x))


def _wrap(ob):
    if isinstance(ob, (list, tuple)):
        ks = set()
        wobs = []
        for x in ob:
            wob = _wrap(x)
            if hasattr(wob, "update_keys"):
                wob.update_keys(ks)
            wobs.append(wob)
        return _Collection(wobs)
    elif hasattr(ob, "keys"):
        wob = ob.__class__()
        for k in sorted(ob):
            wob[k] = _wrap(ob[k])
        return _Dict(wob)
    else:
        return _Atom(ob)


def _unwrap(wob):
    return wob.unwrap()


# uid (<one|mix>, <type>, <primitive, collection>, <value>)
ONE_0 = 0
MIXED_0 = 1

STR_1 = 0
NUM_1 = 1
ANY_1 = 2
EMPTY_1 = 3
MISSING_1 = 4

PRIMITIVE_2 = 0
DICT_2 = 1
COLLECTION_2 = 2


class _Atom:
    def __init__(self, value):
        self.value = value

    @reify
    def uid(self):
        v = self.value
        if isinstance(v, str):
            return (ONE_0, STR_1, PRIMITIVE_2, v.lower())
        elif isinstance(v, (float, int)):
            return (ONE_0, NUM_1, PRIMITIVE_2, v)
        elif v is None:
            return (ONE_0, EMPTY_1, PRIMITIVE_2, v)
        else:
            return (ONE_0, ANY_1, PRIMITIVE_2, v)

    def unwrap(self):
        return self.value


class _Collection:
    def __init__(self, value):
        self.value = value

    @reify
    def uid(self):
        if not self.value:
            return (MIXED_0, EMPTY_1, COLLECTION_2, None)
        self.value = sorted(self.value, key=lambda x: x.uid)
        uids = [x.uid for x in self.value]
        r = [
            ONE_0 if len(set((uid[0], uid[1]) for uid in uids)) == 1 else MIXED_0,
            uids[0][1],
            COLLECTION_2,
        ]
        for uid in uids:
            r.extend(uid)
        return tuple(r)

    def unwrap(self):
        self.uid  # xxx: for sort
        return [x.unwrap() for x in self.value]


class _Dict:
    def __init__(self, value):
        self.value = value
        self.keys = None

    def update_keys(self, keys):
        keys.update(self.value.keys())
        self.keys = keys

    @reify
    def uid(self):
        if not self.value:
            return (MIXED_0, EMPTY_1, DICT_2, None)
        d = defaultdict(list)
        vs = {}
        for k in sorted(self.keys or self.value.keys()):
            uid = self.value.get(k, _MISSING).uid
            d[(uid[0], uid[1], uid[2])].append(k)
            vs[k] = uid[3:]

        if len(d) == 1:
            uid = next(iter(d))
            r = [ONE_0, uid[1], DICT_2]
        else:
            r = [MIXED_0, ANY_1, DICT_2]
        for uid_prefix, ks in sorted(d.items()):
            for k in ks:
                r.extend(uid_prefix)
                r.extend(vs.get(k))
        return tuple(r)

    def unwrap(self):
        self.uid  # xxx

        d = self.value
        for k in list(d.keys()):
            d[k] = d[k].unwrap()
        return d


class _MISSING:
    uid = (MIXED_0, MISSING_1, PRIMITIVE_2, None)
