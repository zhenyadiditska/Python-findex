import logging
from functools import lru_cache

from findex.index_model import Index
from findex.query import parse_query

logger = logging.getLogger(__name__)


@lru_cache(maxsize=256)
def cached_query(query: str, index: Index) -> frozenset[str]:
    logger.debug("Calculating query: %s", query)
    return frozenset(parse_query(query).evaluate(index))