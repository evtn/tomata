from __future__ import annotations
import inspect

from typing_extensions import (
    Awaitable,
    Generic,
    TypeGuard,
    TypeVar,
    Union,
)

from tomata.base import (
    AsyncHandler,
    BasicEmitter,
    Ev,
    Handler,
    HandlerType,
    HandlersDict,
    Id,
    SK,
)

_T = TypeVar("_T")

AwaitableOrValue = Union[Awaitable[_T], _T]


def is_async(cov: AwaitableOrValue[_T]) -> TypeGuard[Awaitable[_T]]:
    return hasattr(cov, "__await__")


def make_async(handler: Handler[Ev, Id, SK]) -> AsyncHandler[Ev, Id, SK]:
    if inspect.iscoroutinefunction(handler):
        return handler

    async def ahandler(event: Ev, identity: Id, state: SK) -> SK | None:
        return handler(event, identity, state)  # type: ignore

    return ahandler


class AsyncEmitter(BasicEmitter[Ev, SK, Id]):
    handlers: HandlersDict[SK, AsyncHandler[Ev, Id, SK]]

    def __init__(self, default_state: SK):
        super().__init__(default_state)
        self.on = AsyncOn(self)

    async def emit(self, event: Ev, identity: Id):
        current_state = await self.get_state(identity)
        handler = (
            await self.get_handler(current_state, "event") or await self.get_default()
        )

        if not handler:
            return

        next_state = await handler(event, identity, current_state)

        if not next_state:
            return

        await self.leave_state(current_state, event, identity)
        await self.set_state(identity, next_state)
        await self.enter_state(next_state, event, identity, current_state)

    async def set_state(self, identity: Id, state: SK):
        return NotImplemented

    async def get_state(self, identity: Id) -> SK:
        return NotImplemented

    async def leave_state(self, state: SK, event: Ev, identity: Id):
        leave_handler = await self.get_handler(state, "leave")

        if not leave_handler:
            return

        return await leave_handler(event, identity, state)

    async def enter_state(self, state: SK, event: Ev, identity: Id, prev_state: SK):
        enter_handler = await self.get_handler(state, "enter")

        if not enter_handler:
            return

        await enter_handler(event, identity, state)

    async def get_handler(
        self, state: SK, handler_type: HandlerType
    ) -> AsyncHandler[Ev, Id, SK] | None:
        store = self.handlers[handler_type]
        return store.get(state)

    def set_handler(
        self,
        state: SK,
        handler_type: HandlerType,
        handler: Handler[Ev, Id, SK],
    ):
        self.handlers[handler_type][state] = make_async(handler)

    async def get_default(self) -> AsyncHandler[Ev, Id, SK] | None:
        return self.handlers["default"]

    def set_default(self, handler: Handler[Ev, Id, SK]):
        self.handlers["default"] = make_async(handler)


class AsyncOn(Generic[Ev, SK, Id]):
    def __init__(self, emitter: AsyncEmitter[Ev, SK, Id]):
        self.emitter = emitter

    def __call__(self, state: SK, handler_type: HandlerType = "event"):
        def decorator(handler: Handler[Ev, Id, SK]) -> Handler[Ev, Id, SK]:
            self.emitter.set_handler(state, handler_type, handler)
            return handler

        return decorator

    def enter(self, key: SK):
        return self(key, "enter")

    def event(self, key: SK):
        return self(key, "event")

    def leave(self, key: SK):
        return self(key, "leave")

    def default(self, handler: Handler[Ev, Id, SK]):
        self.emitter.set_default(handler)
        return handler
