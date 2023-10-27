from __future__ import annotations


from typing_extensions import (
    Generic,
)

from .base import (
    BasicEmitter,
    Ev,
    HandlerType,
    HandlersDict,
    Id,
    SK,
    SyncHandler,
)


class Emitter(BasicEmitter[Ev, SK, Id]):
    handlers: HandlersDict[SK, SyncHandler[Ev, Id, SK]]

    def __init__(self, default_state: SK):
        super().__init__(default_state)
        self.on = On(self)

    def emit(self, event: Ev, identity: Id):
        current_state = self.get_state(identity)
        handler = self.get_handler(current_state, "event") or self.get_default()

        if not handler:
            return None

        next_state = handler(event, identity, current_state)

        if not next_state:
            return

        self.leave_state(current_state, event, identity)
        self.set_state(identity, next_state)
        self.enter_state(next_state, event, identity, current_state)

    def set_state(self, identity: Id, state: SK):
        return NotImplemented

    def get_state(self, identity: Id) -> SK:
        return NotImplemented

    def leave_state(self, state: SK, event: Ev, identity: Id):
        leave_handler = self.get_handler(state, "leave")

        if not leave_handler:
            return

        leave_handler(event, identity, state)

    def enter_state(self, state: SK, event: Ev, identity: Id, prev_state: SK):
        enter_handler = self.get_handler(state, "enter")

        if not enter_handler:
            return

        enter_handler(event, identity, state)

    def get_handler(
        self, state: SK, handler_type: HandlerType
    ) -> SyncHandler[Ev, Id, SK] | None:
        store = self.handlers[handler_type]
        return store.get(state)

    def set_handler(
        self,
        state: SK,
        handler_type: HandlerType,
        handler: SyncHandler[Ev, Id, SK],
    ):
        self.handlers[handler_type][state] = handler

    def get_default(self) -> SyncHandler[Ev, Id, SK] | None:
        return self.handlers["default"]

    def set_default(self, handler: SyncHandler[Ev, Id, SK]):
        self.handlers["default"] = handler


class On(Generic[Ev, SK, Id]):
    def __init__(self, emitter: Emitter[Ev, SK, Id]):
        self.emitter = emitter

    def __call__(self, state: SK, handler_type: HandlerType = "event"):
        def decorator(handler: SyncHandler[Ev, Id, SK]):
            self.emitter.set_handler(state, handler_type, handler)
            return handler

        return decorator

    def enter(self, key: SK):
        return self(key, "enter")

    def event(self, key: SK):
        return self(key, "event")

    def leave(self, key: SK):
        return self(key, "leave")

    def default(self, handler: SyncHandler[Ev, Id, SK]):
        self.emitter.set_default(handler)
        return handler
