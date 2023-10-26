# Welcome to `tomata` readme!

This is a generic state automata-ish module allowing you to build an typed event-driven stateful flow with minimal setup.

The basic flow is:

1. You define your own emitter class, inheriting from `tomata.Emitter`. There you define `get_state` and `set_state` methods to provide the state storage.
2. You create an instance of emitter
3. You register handlers for the state changes and events with `emitter.on(state_key, handler_type = "event")`
4. In your main loop, you call `emitter.emit(event, identity)` with arbitrary event and identity values (identity is passed to `get_state`, `set_state` and handler, event is passed to handler)

If you want to dive into examples, go to [examples](https://github.com/evtn/tomata/tree/lord/examples) folder.


## Concepts

tomata works around several concepts (in *italic* in text):

### Event

**Event** is an arbitrary value to process. It is passed to all the *handlers*

### State

**State** is some key to denote the current state. *Handlers* are called depending on which state is currently active

### Identity

**Identity** is a key that is used to differentiate between states of different entites. An identity could be, for example, a user id or a string hash.

### Handler

**Handler** is a function called on any event. There are three types of handlers: `enter`, `event` and `leave`.

- `enter` handlers are called when *state* switches **to** the one tied to handler
- `event` handlers are called when *emitter* emits an event. Handlers of this type can change the *state* by returning the next *state* key
- `leave` handlers are called when *state* switches **from** the one tied to handler

### Emitter

**Emitter** is the main object of the module. It consumes *events* and calls *handlers* as a result. *Handlers* can request a *state* change, *emitter* also handles that.

To work with events, you need your own `Emitter` class (and an instance). It manages calling your handlers and changing the state.

A minimal `Emitter` class has to define `get_state` and `set_state`:


```python
from tomata import Emitter

class MyEmitter(Emitter):
    def set_state(self, identity, state):
        ...

    def get_state(self, identity):
        ...
``` 

Those methods should handle how to store the state (for example, get_state could retrieve the state from database and set_state could write it into the database).

You can also define `__init__` for your emitter class:

```python
...
class MyEmitter(Emitter):
    def __init__(self):
        default_state = "start"
        super().__init__(default_state)
        ...
    
    ...
```

If you love type hints, we've got you covered:

```python
from tomata import Emitter
from typing import Literal

StateKey = Literal["start", "age", "name", "finish"]
Event = str
Identity = int

class MyEmitter(Emitter[Event, StateKey, Identity]):
    def __init__(self):
        super().__init__("start")
    
    def get_state(self, identity: Identity) -> StateKey:
        ...
    
    def set_state(self, identity: Identity, state: StateKey) -> None:
        ...

```

...or, if you are on Python 3.12:

```python
from tomata import Emitter
from typing import Literal

# those types are arbitrary, you can actually use anything as your event / state / identity
type Event = str
type StateKey = Literal["start", "age", "name", "finish"]
type Identity = int

class MyEmitter(Emitter[Event, StateKey, Identity]):
    def __init__(self):
        super().__init__("start")
    
    def get_state(self, identity: Identity) -> StateKey:
        ...
    
    def set_state(self, identity: Identity, state: StateKey) -> None:
        ...

```

## Defining handlers

Let's say, you want to run some code when state `cake_shooting` is active and some event comes by:

```python

em = MyEmitter()

...


@em.on("cake_shooting")
def cake_shooting(event: Event, identity: Identity, state: StateKey):
    # event and identity are provided through emit, state is the current state.
    if not event:
        return "no_cake" # new state
    
    cake = catch_cake(event)
    eat_cake(cake)
```

Now, if you want to run some code when state was switched to `cake_shooting`, use `enter` handler:

```python

em = MyEmitter()

...


@em.on.enter("cake_shooting")
def cake_shooting(event: Event, identity: Identity, state: StateKey):
    # event and identity are provided through emit, state is the current state.
    ...
```

Same goes for when state was switched from state, just use `.leave` handler


## Emitting events

After you've set up your emitter and handlers, it's time to emit some events:

```python
emitter = MyEmitter()

from json import load
from typing import TypedDict

class EventData(TypedDict):
    data: Event
    identity: Identity
    

with open("events.json") as file:
    events: list[EventData] = load(file)


for event in events:
    emitter.emit(event["data"], event["identity"])

```

## Default handler

You can set a default (fallback) handler to handle events when no other handler is found:

```python

@em.on.default
def default_handler(event, identity, state):
    ...

```

At the moment, you can't define a default `enter` and `leave` handlers, because it doesn't really seem useful (but feel free to open an issue if you find a good use-case)

## Async 

To use async, replace Emitter with AsyncEmitter:


```python
from tomata import AsyncEmitter
from typing import Literal


type StateKey = Literal["start", "age", "name", "finish"]
type Event = str
type Identity = int


class MyEmitter(AsyncEmitter[Event, StateKey, Identity]):
    def __init__(self):
        super().__init__("start")
    
    async def get_state(self, identity: Identity) -> StateKey:
        ...
    
    async def set_state(self, identity: Identity, state: StateKey) -> None:
        ...


em = MyEmitter()

# AsyncEmitter can call both async and sync handlers

@em.on("funny_pineapple")
async def funny_pineapple(event: Event, identity: Identity, state: StateKey):
    ...

@em.on("sad_pineapple")
def sad_pineapple(event: Event, identity: Identity, state: StateKey):
    ...

```

## Advanced behaviour

Let's say, you want to redefine handler storage.
You can easily do that by defining your own `get_handler` and `set_handler` methods.

Let's make an Emitter where state would be a dictionary, and the handler would be called on state["type"]

```python
from tomata import Emitter
from tomata.base import make_handlers_dict

Event = dict[str, str]
State = dict[str, str]
Identity = int

class AdvancedEmitter(Emitter[Event, State, Identity])
    handlers: dict[HandlerType, SyncHandlerStore[str, Event, Identity]]  
        
    def get_state(self, identity: Identity) -> State:
        ...
    
    def set_state(self, identity: Identity, state: State) -> None:
        ...
    
    def get_handler(
        self, state: SK, handler_type: HandlerType
    ) -> SyncHandler[Ev, Id, SK] | None:
        store = self.handlers[handler_type]
        
        key = state.get("type", self.default_state) 
        
        return store.get(key)

    def set_handler(
        self,
        state: SK,
        handler_type: HandlerType,
        handler: SyncHandler[Ev, Id, SK],
    ):
        key = state.get("type", self.default_state)
        
        store = self.handlers[handler_type]
        
        store[key] = handler


em = AdvancedEmitter({"type": "start"})

@em.on({"type": "start"})
def start_event(event: Event, identity: Identity, state: State):
    new_state = {**state, "type": "ongoing"}
    new_state["count"] = new_state.get("count", 0)
    
    return new_state
```

To redefine setting fallback handler logic, define your own `set_default(handler)` and `get_default()` methods.


### AsyncEmitter methods

To extend AsyncEmitter, you have to remember two things:

- Some methods (`[get|set]_state`, `get_handler`, `get_default`) are async. This means you have to define them with `async def` even if you don't plan to use await in them. 
    *`emit` is obviously async, but if you don't need an async `emit`, take a look at synchronous `Emitter`*

- In `set_handler` and `set_default`, you have to async-ify the handlers. To do that, use `tomata.async_emitter.make_async` function, which takes any handler and makes it async

Otherwise, the extension process should be just as with `Emitter`.