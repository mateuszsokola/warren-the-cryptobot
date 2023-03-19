from typing import Any, List


def to_hashmap(entries: List) -> dict[int, Any]:
    by_indexes = list(map(lambda e: e.id, entries))
    hash_map = {key: value for key, value in zip(by_indexes, entries)}

    return hash_map
