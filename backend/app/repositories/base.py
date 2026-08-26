"""Generic repository protocol for persistence abstractions."""

from typing import Generic, Protocol, TypeVar

EntityT = TypeVar("EntityT")
IdentifierT = TypeVar("IdentifierT")


class Repository(Protocol, Generic[EntityT, IdentifierT]):
    """Minimum operations supported by repository implementations."""

    def get(self, identifier: IdentifierT) -> EntityT | None: ...

    def add(self, entity: EntityT) -> EntityT: ...
