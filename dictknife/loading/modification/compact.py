from functools import partial
from dictknife.loading.modification import use, is_used


def setup(dispatcher) -> None:
    if is_used(dispatcher, __name__):
        return
    use(dispatcher, __name__)
    dispatcher.dumper.fn_map["json"] = partial(
        dispatcher.dumper.fn_map["json"], indent=None
    )
