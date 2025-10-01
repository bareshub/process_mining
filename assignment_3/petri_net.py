"""
Module containing the definition of a Petri net.
"""
from dataclasses import dataclass, field


@dataclass
class Place():
    """
    Class representing the Place of a Petri net.
    A place represents a state of the business process.
    """
    name: int
    tokens: int = 0

    def __post_init__(self):
        assert self.name > 0, "Place name must be > 0"

    def add_token(self):
        """
        Adds a token to the place.
        """
        self.tokens += 1
        return self

    def consume_token(self):
        """
        Consumes a token to the place if any.
        """
        if self.tokens > 0:
            self.tokens -= 1
        return self

    def __hash__(self):
        return hash(self.name)


@dataclass
class Transition():
    """
    Class representing the Transition of a Petri net.
    A transition represent an activity of the business process.
    """
    name: str
    id: int = -1
    previous: set = field(default_factory=set)
    next: set = field(default_factory=set)

    def __post_init__(self):
        assert self.id < 0, "Transition id must be < 0"

    def add_previous(self, place):
        """
        Adds a Place previous to the Transition.
        """
        self.previous.add(place)
        return self

    def add_next(self, place):
        """
        Adds a Place next to the Transition.
        """
        self.next.add(place)
        return self

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


@dataclass
class PetriNet():
    """
    Class representing a Petri net (P, T, F)
    Where:
    - P is a finite set of places
    - T is a finite set of transitions such that T ∩ P = ∅
    - F is a flow relation - subset of all possible connections between P and T
    """
    places: dict[int, Place] = field(default_factory=dict)
    transitions: dict[int, Transition] = field(default_factory=dict)

    def transition_name_to_id(self, transition_name) -> int | None:
        """
        Return the id of a transition given its name, or None if not found.
        """
        for transition_id, transition in self.transitions.items():
            if transition.name == transition_name:
                return transition_id
        return None

    def add_place(self, name: int):
        """
        Adds a place to the Petri net.
        """
        self.places[name] = Place(name)
        return self

    def add_transition(self, name: str, id: int):
        """
        Adds a transition to the Petri net.
        """
        if self.transitions.get(id) is None:
            self.transitions[id] = Transition(name, id)
        return self

    def add_edge(self, source, target):
        """
        Adds a flow relation / edge between a place and a transition.
        """
        if source < 0:
            self.transitions[source].add_next(self.places[target])
        else:
            self.transitions[target].add_previous(self.places[source])
        return self

    def get_tokens(self, place):
        """
        Returns the tokens in the place.
        """
        return self.places[place].tokens

    def is_enabled(self, transition):
        """
        Returns True if the transition is enabled.
        A transition is enable if each previous place contains at least one token.
        """
        return all(x.tokens > 0 for x in self.transitions[transition].previous)

    def add_marking(self, place):
        """
        Adds a marking (token) to a place.
        """
        self.places[place].add_token()
        return self

    def fire_transition(self, transition):
        """
        Fires a transition, if enabled.
        """
        if self.is_enabled(transition):
            for p in self.transitions[transition].previous:
                p.consume_token()

            for p in self.transitions[transition].next:
                p.add_token()

        return self
