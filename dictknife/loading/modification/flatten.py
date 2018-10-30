from dictknife.loading.modification import use, is_used
from dictknife.transform import flatten


def setup(dispatcher):
    if is_used(dispatcher, __name__):
        return
    use(dispatcher, __name__)

    def wrap(dump_fn):
        def call(d, *args, **kwargs):
            return dump_fn(flatten(d), *args, **kwargs)

        return call

    for k in list(dispatcher.dumper.fn_map.keys()):
        dispatcher.dumper.fn_map[k] = wrap(dispatcher.dumper.fn_map[k])
