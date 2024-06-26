import re

from yarl import URL


def camel_to_snake(name: str) -> str:
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def normalize_pg_url(url: str, asynchronous: bool = False) -> str:
    if asynchronous:
        url = URL(url).with_scheme("postgresql+asyncpg").human_repr()
    return url
