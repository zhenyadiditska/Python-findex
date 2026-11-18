from functools import lru_cache
from findex.query import parse_query


@lru_cache(maxsize=256)
def cached_query(query, index):
    print(f"[cache] Calculating: {query}")
    return frozenset(parse_query(query).evaluate(index))
