import logging
import importlib
from dictknife.langhelpers import pairrsplit
from .interfaces import Visitor, Node, Registry

logger = logging.getLogger(__name__)


class DictRegistry(Registry):
    def __init__(self, *, logger=logger) -> None:
        self.logger = logger
        self.ref_visitor_mapping = {}

    def resolve_visitor_from_ref(self, s: str) -> Visitor:
        self.logger.debug("resolve visitor: %s", s)
        try:
            return self.ref_visitor_mapping[s]
        except KeyError:
            # todo: send event?
            self.logger.info("resolve visitor: %s is not found, (error=%r)", s, e)
            return None

    def resolve_node_from_string(self, s: str) -> Node:
        """<module name>:<symbol name>"""
        try:
            self.logger.debug("resolve node: %s", s)
            module_name, symbol_name = pairrsplit(s, ":")
            m = importlib.import_module(module_name)
            if not symbol_name:
                return m
            return getattr(m, symbol_name)
        except (ImportError, AttributeError) as e:
            # todo: send event?
            self.logger.info("resolve node: %s is not found, (error=%r)", s, e)
            return None
