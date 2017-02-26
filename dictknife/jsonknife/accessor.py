from dictknife import Accessor


def access_by_json_pointer(doc, query, accessor=Accessor()):
    if query == "":
        return doc
    path = [p.replace("~1", "/").replace("~0", "~") for p in query[1:].split("/")]
    return accessor.access(doc, path)


class StackedAccessor(object):
    def __init__(self, resolver, accessor=Accessor()):
        self.stack = [resolver]
        self.accessor = accessor

    @property
    def resolver(self):
        return self.stack[-1]

    def access_and_stacked(self, ref):
        subresolver, pointer = self.resolver.resolve(ref)
        self.stack.append(subresolver)
        return access_by_json_pointer(subresolver.doc, pointer, accessor=self.accessor)

    def pop_stack(self):
        return self.stack.pop()

    def push_stack(self, resolver):
        return self.stack.append(resolver)
