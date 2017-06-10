from collections import OrderedDict
from dictknife import Accessor
from dictknife.pp import pp, indent

a = Accessor(OrderedDict)
d = OrderedDict()

# assign
a.assign(d, ['a', 'b', 'c'], 'v')
with indent(2, 'assign:\n'):
    print(d)
    pp(d)
    print()

# access
with indent(2, '\naccess: ["a", "b", "c"]\n'):
    print(['a', 'b', 'c'], a.access(d, ['a', 'b', 'c']))
    # print(['a', 'b', 'x'], a.access(d, ['a', 'b', 'x']))  # error

# exists
with indent(2, '\nexists:\n'):
    import copy  # NOQA
    d2 = copy.deepcopy(d)

    print(['a', 'b', 'c'], a.exists(d2, ['a', 'b', 'c']))
    print(['a', 'b', 'x'], a.exists(d2, ['a', 'b', 'x']))

# maybe_remove
with indent(2, '\nmaybe_remove:\n'):
    import copy  # NOQA
    d2 = copy.deepcopy(d)

    print(['a', 'b', 'x'], a.maybe_remove(d2, ['a', 'b', 'x']))
    print(['a', 'b', 'c'], a.maybe_remove(d2, ['a', 'b', 'c']))
    pp(d2)
    print()

# maybe_access_container (this is not good name!!)
with indent(2, '\nmaybe_access_container:\n'):
    print(['a', 'b', 'x'], a.maybe_access_container(d, ['a', 'b', 'x']))
    print(['a', 'b', 'c'], a.maybe_access_container(d, ['a', 'b', 'c']))
