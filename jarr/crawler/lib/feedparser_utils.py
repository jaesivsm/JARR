from typing import Generator, List, Optional


def reach_in(
    entry, key: str, sub_key: Optional[str] = None
) -> Generator[str, None, None]:
    value = entry.get(key)
    if isinstance(value, str):
        assert sub_key in {None, "value", "href"}, (
            "shouldn't reach for anything else but "
            "'value' if landing on a string value"
        )
        yield value
    elif isinstance(value, list):
        for sub_value in value:
            if isinstance(sub_value, dict):
                if sub_value.get(sub_key):
                    yield sub_value[sub_key]
    elif isinstance(value, dict):
        if value.get(sub_key):
            yield value[sub_key]


def browse_keys(
    entry, keys: List[str], sub_key: Optional[str] = None
) -> Optional[str]:
    for key in keys:
        for value in reach_in(entry, key, sub_key):
            return value
    return None
