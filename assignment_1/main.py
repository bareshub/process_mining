class Place():
    tokens = 0
    
    def __init__(self, name: int):
        assert name >= 0
        self.name = name

    def add_token(self):
        self.tokens += 1
        return self

    def consume_token(self):
        if self.tokens > 0:
            self.tokens -= 1
        return self


class Transition():
    
    def __init__(self, name: str, id: int):
        assert id < 0
        self.name = name
        self.id = id
        self.previous = set()
        self.next = set()

    def add_previous(self, place):
        self.previous.add(place)
        return self

    def add_next(self, place):
        self.next.add(place)
        return self


class PetriNet():

    def __init__(self):
        self.places = {}
        self.transitions = {}

    def add_place(self, name: int):
        self.places[name] = Place(name)
        return self

    def add_transition(self, name: str, id: int):
        self.transitions[id] = Transition(name, id)
        return self

    def add_edge(self, source, target):
        if source < 0:
            self.transitions[source].add_next(self.places[target])
        else:
            self.transitions[target].add_previous(self.places[source])
        return self

    def get_tokens(self, place):
        return self.places[place].tokens

    def is_enabled(self, transition):
        return all(x.tokens > 0 for x in self.transitions[transition].previous)

    def add_marking(self, place):
        self.places[place].add_token()
        return self

    def fire_transition(self, transition):
        if self.is_enabled(transition):
            self.transitions[transition].previous = [x.consume_token() for x in self.transitions[transition].previous]
            self.transitions[transition].next = [x.add_token() for x in self.transitions[transition].next]
        return self