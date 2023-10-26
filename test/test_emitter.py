from tomata import Emitter


class DictEmitter(Emitter[dict, str, int]):
    def __init__(self, default_state: str):
        self.storage: dict[int, str] = {}
        super().__init__(default_state)

    def get_state(self, identity: int) -> str:
        return self.storage.get(identity, self.default_state)

    def set_state(self, identity: int, state: str):
        self.storage[identity] = state


class TestClass:
    def test_basic(self):
        em = DictEmitter("a")

        def switch_to_b(*_):
            return "b"

        def switch_to_c(*_):
            return "c"

        em.on("a")(switch_to_b)
        em.on("b")(switch_to_c)

        em.emit({}, 2)
        em.emit({}, 2)
        em.emit({}, 1)

        assert em.get_state(0) == "a"
        assert em.get_state(1) == "b"
        assert em.get_state(2) == "c"

        assert len(em.storage) == 2

    def test_enter(self):
        em = DictEmitter("a")
        side_effect_store = {}

        def switch_to_b(*_):
            return "b"

        def enter_a(*_):
            side_effect_store["test"] = 1

        def enter_b(*_):
            side_effect_store["test"] = 0

        em.on("a")(switch_to_b)
        em.on.enter("a")(enter_a)
        em.on.enter("b")(enter_b)

        em.emit({}, 0)

        assert side_effect_store["test"] == 0

    def test_leave(self):
        em = DictEmitter("a")
        side_effect_store = {}

        def switch_to_b(*_):
            return "b"

        def enter_a(*_):
            side_effect_store["test"] = 1

        def enter_b(*_):
            side_effect_store["test"] = 0

        em.on("a")(switch_to_b)
        em.on.leave("a")(enter_a)
        em.on.leave("b")(enter_b)

        em.emit({}, 0)

        assert side_effect_store["test"] == 1

    def test_condition(self):
        em = DictEmitter("a")

        @em.on("a")
        @em.on("b")
        @em.on("c")
        def switch(event, identity, state):
            if identity > 50:
                return "no"

            if state == "c":
                return

            if event.get("next"):
                return event["next"]

        em.emit({"next": "b"}, 0)
        assert em.get_state(0) == "b"

        em.emit({"next": "c"}, 1)
        em.emit({"next": "a"}, 1)
        # because handler doesn't allow switching from "c" state
        assert em.get_state(1) == "c"

        em.emit({"next": "c"}, 2)
        assert em.get_state(2) == "c"

        em.emit({"next": "b"}, 51)
        assert em.get_state(51) == "no"

        em.emit({}, 52)
        assert em.get_state(52) == "no"

        em.emit({}, 8)
        assert em.get_state(8) == "a"
