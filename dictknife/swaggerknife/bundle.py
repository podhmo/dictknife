from dictknife.jsonknife import get_resolver_from_filename
from dictknife.jsonknife import Bundler


def bundle(src, *, strict=False, cls=Bundler):
    resolver = get_resolver_from_filename(src)
    bundler = cls(resolver)
    return bundler.bundle()
