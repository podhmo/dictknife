import logging

logger = logging.getLogger(__name__)


def _get_modifications_history(dispatcher):
    if not hasattr(dispatcher, "_modifications"):
        dispatcher._modifications = set()
    return dispatcher._modifications


def is_used(dispatcher, name) -> bool:
    return name in _get_modifications_history(dispatcher)


def use(dispatcher, name) -> None:
    logger.debug("use modification, %s", name)
    _get_modifications_history(dispatcher).add(name)
