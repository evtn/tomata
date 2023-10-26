from tomata import Emitter
from typing import Any, Literal

StateKey = Literal["start", "age", "name", "finish"]


# let's pretend this is a database
class Storage:
    def __init__(self) -> None:
        self.data: dict[int, dict[str, Any]] = {}
        self.states: dict[int, str] = {}

    def write_data(self, identity: int, key: str, value: Any):
        if identity not in self.data:
            self.data[identity] = {}

        self.data[identity][key] = value

    def read_data(self, identity: int):
        return self.data.get(identity, {})


class BotEmitter(Emitter[str, StateKey, int]):
    def __init__(self, storage: Storage):
        super().__init__("start")
        self.storage = storage

    def set_state(self, identity, state):
        self.storage.states[identity] = state

    def get_state(self, identity):
        return self.storage.states.get(identity, self.default_state)


storage = Storage()

bot = BotEmitter(storage)


@bot.on("start")
def start_event(*_):
    return (
        "age"  # if user sends a message in default state, we switch to the next state
    )


@bot.on.enter("age")  # also can be written as @bot.on("age", "enter")
def age_enter(*_):
    answer("Please, provide your age")


@bot.on("age")
def age_event(event: str, identity: int, *_):
    try:
        age = int(float(event))  # cool parsing
    except:
        answer("Please, provide your age as a number")
        return  # remain in "age" state by returning None

    storage.write_data(identity, "age", age)
    return "name"


@bot.on.enter("name")
def name_enter(*_):
    answer("Now your name")


@bot.on("name")
def name_event(event: str, identity: int, *_):
    storage.write_data(identity, "name", event)
    return "finish"


@bot.on.leave("name")
def name_leave(*_):
    answer("Cool name huh")


@bot.on.enter("finish")
def finish_enter(event: str, identity: int, *_):
    data = storage.read_data(identity)
    is_accepted = False

    if data["age"] > 850:
        answer("Sorry, you are too old for this")
    elif data["age"] < 1.00000002:
        answer("Sorry, you are too young for this")
    elif data["name"] == "Grass":
        answer("Grass is not accepted. Sorry")
    else:
        answer("Cool, you are accepted!!!")
        is_accepted = True

    storage.write_data(identity, "is_accepted", is_accepted)


@bot.on("finish")
def finish_event(event: str, identity: int, *_):
    status = (
        "accepted" if storage.read_data(identity).get("is_accepted") else "not accepted"
    )
    answer(f"Hi, you have filled this already, you are {status}")


# very real message queue
def get_events():
    # user writes a start command
    yield "/start"
    # bot answers with "Please, provide your age"
    # user is not smart
    yield "ten"
    # bot answers with "Please, provide your age as a number"
    # user gives this:
    yield "10"
    # bot says "Now your name"
    # user gives this:
    yield "Peter"
    # bot replies with something
    yield "What now???"


# mock function for message answering
def answer(text: str):
    print(f"answered: {text}")


for event in get_events():
    print(f"user said: {event}")
    user_id = 9
    bot.emit(event, user_id)
