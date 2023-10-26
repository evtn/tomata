from __future__ import annotations

from typing_extensions import (
    Any,
    Awaitable,
    Callable,
    Generic,
    Literal,
    Optional,
    TypeVar,
    Union,
    TypedDict,
    Dict,
    Hashable,
)

SK = TypeVar("SK", default=str)
Ev = TypeVar("Ev", default=dict)
Id = TypeVar("Id", default=int)

HandlerType = Literal["event", "enter", "leave"]

AsyncHandler = Callable[[Ev, Id, SK], Awaitable[Optional[SK]]]
SyncHandler = Callable[[Ev, Id, SK], Optional[SK]]
Handler = Union[SyncHandler[Ev, Id, SK], AsyncHandler[Ev, Id, SK]]
SyncHandlerStore = Dict[SK, SyncHandler[Ev, Id, SK]]
AsyncHandlerStore = Dict[SK, AsyncHandler[Ev, Id, SK]]

K = TypeVar("K", bound=Hashable)
H = TypeVar("H", bound=Handler[Any, Any, Any])


class HandlersDict(TypedDict, Generic[K, H]):
    event: dict[K, H]
    enter: dict[K, H]
    leave: dict[K, H]
    default: H | None


def make_handlers_dict() -> HandlersDict:
    result: HandlersDict = {"event": {}, "enter": {}, "leave": {}, "default": None}
    return result


class BasicEmitter(Generic[Ev, SK, Id]):
    def __init__(self, default_state: SK):
        self.handlers = make_handlers_dict()
        self.default_state = default_state
