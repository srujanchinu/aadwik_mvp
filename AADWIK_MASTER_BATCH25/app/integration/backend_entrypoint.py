from dataclasses import dataclass
from typing import Callable, Any


@dataclass(frozen=True)
class BackendEntrypoint:
    name: str
    handler: Callable[..., Any]

    def call(self, **kwargs):
        return self.handler(**kwargs)


def make_entrypoint(name: str, handler: Callable[..., Any]) -> BackendEntrypoint:
    if not name or not callable(handler):
        raise ValueError("name and callable handler are required")
    return BackendEntrypoint(name, handler)
