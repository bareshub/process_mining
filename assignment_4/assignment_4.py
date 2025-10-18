"""
Module containing the implementation of the Conformance checking with token replay.
"""
import xml.etree.ElementTree as ET
import datetime as DT
from itertools import count, combinations
from dataclasses import dataclass, field


transitions_counter = count(start=-1, step=-1)
places_counter = count(start=1, step=1)


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
    previous: set[Place] = field(default_factory=set)
    next: set[Place] = field(default_factory=set)

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

    def get_tokens(self, place: Place):
        """
        Returns the tokens in the place.
        """
        return self.places[place].tokens

    def is_enabled(self, transition_id: int):
        """
        Returns True if the transition is enabled.
        A transition is enable if each previous place contains at least one token.
        """
        return all(x.tokens > 0 for x in self.transitions[transition_id].previous)

    def count_missing_tokens_to_fire(self, transition_id: int):
        """
        Returns the number of missing token to make a transition enable.
        """
        return sum(1 for x in self.transitions[transition_id].previous if x.tokens == 0)

    def add_missing_tokens_to_fire(self, transition_id: int):
        """
        Returns the number of missing token to make a transition enable.
        """
        for x in self.transitions[transition_id].previous:
            if x.tokens == 0:
                x.add_token()

    def add_token(self, place_id: int):
        """
        Adds a token to a place.
        """
        self.places[place_id].add_token()
        return self

    def fire_transition(self, transition_id: int):
        """
        Fires a transition, if enabled.
        """
        if self.is_enabled(transition_id):
            for p in self.transitions[transition_id].previous:
                p.consume_token()

            for p in self.transitions[transition_id].next:
                p.add_token()

        return self

    def count_consumed_tokens(self, transition_id: int):
        return sum(1 for x in self.transitions[transition_id].previous)

    def count_produced_tokens(self, transition_id: int):
        return sum(1 for x in self.transitions[transition_id].next)

    def clone(self) -> "PetriNet":
        """
        Return a deep copy of the Petri net: new Place and Transition objects
        with the same ids, names, tokens and connectivity.
        """
        new = PetriNet()

        new.places = {}
        new.transitions = {}

        for pid, place in self.places.items():
            new.places[pid] = Place(place.name, place.tokens)

        for tid, trans in self.transitions.items():
            new_trans = Transition(trans.name, trans.id)

            new_trans.previous = set()
            new_trans.next = set()

            for p in trans.previous:
                new_place = new.places.get(p.name)
                if new_place is None:
                    new_place = Place(p.name, p.tokens)
                    new.places[p.name] = new_place
                new_trans.previous.add(new_place)

            for p in trans.next:
                new_place = new.places.get(p.name)
                if new_place is None:
                    new_place = Place(p.name, p.tokens)
                    new.places[p.name] = new_place
                new_trans.next.add(new_place)

            new.transitions[tid] = new_trans

        return new


@dataclass
class Event:
    """
    Class representing the Event of a Log.
    """
    task: str
    case_id: str
    user_id: str
    timestamp: DT.datetime | str


CaseId = str
EventName = str
EventType = str | int | DT.datetime
Activity = str
Frequency = int

Log = dict[CaseId, list[Event]]
EventXES = dict[EventName, EventType]
LogXES = dict[CaseId, list[EventXES]]
DependencyGraph = dict[Activity, dict[Activity, Frequency]]


def log_as_dictionary(log: str) -> Log:
    """
    Reads a CSV-like string into a dictionary.

    Returns
    -------
    Log
        a dictionary indexed by the case id.
        Each value of the returned dictionary is a list of events.

    Example of CSV-like string:
    Task_A;case_1;user_1;2025-09-18 19:14:14
    """

    result: Log = {}

    for event_raw in log.strip().split('\n'):
        if not event_raw:
            continue
        (task, case_id, user_id, timestamp) = event_raw.split(';')

        result.setdefault(case_id, [])
        result[case_id].append(Event(task, case_id, user_id, timestamp))

    return result


def dependency_graph_inline(log: Log) -> DependencyGraph:
    """
    Extracts the dependency graph (direct follow relationships of the Alpha
    Algorithm) from a Log.

    Returns
    -------
    DependencyGraph
        a dictionary where each key is the source activity and the value is
        also a dictionary with key as second activity of the relation and the
        value is the frequency of that relation.
    """

    result: DependencyGraph = {}

    for _, events in log.items():
        for i in range(len(events) - 1):
            event_a, event_b = events[i], events[i+1]

            result.setdefault(event_a.task, {}).setdefault(event_b.task, 0)
            result[event_a.task][event_b.task] += 1

    return result


def parse_value_from_tag(value, tag):
    """
    Parses the value depending on the tag type.
    """
    match tag:
        case x if 'int' in x:
            result = int(value)
        case x if 'date' in x:
            result = DT.datetime.fromisoformat(value[:-6])
        case _:
            result = value
    return result


def read_from_file(filename: str) -> LogXES:
    """
    Reads an XES file into a dictionary.

    Returns
    -------
    LogXES
        a dictionary indexed by the the case_id.
        Each value of the dictionary is a list of events.
    """

    result: LogXES = {}

    tree = ET.parse(filename)
    root = tree.getroot()

    for trace in root.findall('{http://www.xes-standard.org/}trace'):
        case_id = ""
        for info in trace.findall('{http://www.xes-standard.org/}string'):
            if 'concept:name' in info.attrib.values():
                case_id = info.attrib['value']

        result[case_id] = []

        for event in trace.findall('{http://www.xes-standard.org/}event'):
            event_xes: EventXES = {}
            for attribute in event:
                event_xes[attribute.attrib['key']] = parse_value_from_tag(
                    value=attribute.attrib['value'],
                    tag=attribute.tag
                )
            result[case_id].append(event_xes)

    return result


def dependency_graph_file(log: LogXES) -> DependencyGraph:
    """
    Extracts the dependency graph (direct follow relationships of the Alpha
    Algorithm) from a LogXES.

    Returns
    -------
    DependencyGraph
        a dictionary where each key is the source activity and the value is
        also a dictionary with key as second activity of the relation and the
        value is the frequency of that relation.
    """

    result: DependencyGraph = {}

    for _, events in log.items():
        for i in range(len(events) - 1):
            event_a, event_b = events[i], events[i+1]
            name_a, name_b = event_a['concept:name'], event_b['concept:name']

            result.setdefault(name_a, {}).setdefault(name_b, 0)
            result[name_a][name_b] += 1

    return result


def sublists(lst):
    """
    Return all non-empty sublists (subsets).
    """
    result = []
    for sublen in range(1, len(lst) + 1):
        for combo in combinations(lst, sublen):
            result.append(list(combo))
    return result


def update_initial_transition(event_list: list[EventXES]) -> Transition:
    """
    Returns the initial Transition (task) from the event list.
    t_i = { t ∈ T | ∃(σ ∈ W)t = first(σ) }
    """
    first_transition = event_list[0]['concept:name']
    transition_id = next(transitions_counter)

    return Transition(first_transition, transition_id)


def update_final_transition(event_list: list[EventXES]) -> Transition:
    """
    Returns the last Transition (task) from the event list.
    t_o = { t ∈ T | ∃(σ ∈ W)t = last(σ) }
    """
    last_transition = event_list[-1]['concept:name']
    transition_id = next(transitions_counter)

    return Transition(last_transition, transition_id)


def is_direct(dg: DependencyGraph, t_a: Transition, t_b: Transition) -> bool:
    """
    Returns whether t_a -> t_b (direct relation).
    """
    if t_a.name in dg and t_b.name in dg[t_a.name]:
        if t_b.name not in dg or t_a.name not in dg[t_b.name]:
            return True
    return False


def are_direct(dg: DependencyGraph, t_list_a: list[Transition], t_list_b: list[Transition]):
    """
    Returns whether t_a -> t_b (direct relation) between each element of t_list_a and t_list_b.
    """
    for t_a in t_list_a:
        for t_b in t_list_b:
            if not is_direct(dg, t_a, t_b):
                return False
    return True


def are_choices(dg: DependencyGraph, t_list: list[Transition]):
    """
    Returns whether t_a # t_b (choice relation) between each element of t_list.
    """
    for t_a in t_list:
        for t_b in t_list:
            if t_a != t_b and not is_choice(dg, t_a, t_b):
                return False
    return True


def is_parallel(dg: DependencyGraph, t_a: Transition, t_b: Transition) -> bool:
    """
    Returns whether t_a || t_b (parallel relation).
    """
    if t_a.name in dg and t_b.name in dg[t_a.name]:
        if t_b.name in dg and t_a.name in dg[t_b.name]:
            return True
    return False


def is_choice(dg: DependencyGraph, t_a: Transition, t_b: Transition) -> bool:
    """
    Returns whether t_a # t_b (choice relation).
    """
    if t_a.name not in dg or t_b.name not in dg[t_a.name]:
        if t_b.name not in dg or t_a.name not in dg[t_b.name]:
            return True
    return False


def alpha(log: LogXES) -> PetriNet:
    """
    - T is the set of activities (tasks)
    - T* is the set of all finite sequences over T
    - σ ∈ T* is a trace, all tasks in σ belong to the same case
    - W ⊆ T* is a workflow log
    """
    dg = dependency_graph_file(log)

    t_w: list[Transition] = []
    t_i: Transition | None = None
    t_o: Transition | None = None

    t_x_choice: list[Transition] = []
    t_x_direct: list[Transition] = []

    # Calculating t_i, t_o and t_w
    for _, event_list in log.items():
        if t_i is None:
            t_i = update_initial_transition(event_list)
            t_w.append(t_i)

        if t_o is None:
            t_o = update_final_transition(event_list)
            t_w.append(t_o)

        for event in event_list:
            event_name = event['concept:name']
            if Transition(event_name) not in t_w:
                t_w.append(Transition(event_name, next(transitions_counter)))

    # Calculating x_w
    x_w: list[tuple[list[Transition], list[Transition]]] = []
    for t in t_w:
        t_x_choice.clear()
        t_x_direct.clear()

        for t_y in t_w:
            if t == t_y:
                continue

            if is_choice(dg, t, t_y):
                t_x_choice.append(t_y)

            if is_direct(dg, t, t_y):
                t_x_direct.append(t_y)

        choice_sublists: list[list[Transition]] = sublists(t_x_choice)
        direct_sublists: list[list[Transition]] = sublists(t_x_direct)

        for dsl in direct_sublists:
            if len(dsl) > 1 and not are_choices(dg, dsl):
                continue

            x_w.append(([t], dsl))
            for csl in choice_sublists:
                if are_direct(dg, csl, dsl) and are_choices(dg, csl):
                    x_w.append((
                        csl + [t],
                        dsl
                    ))

    # Calculating y_w
    y_w: list[tuple[list[Transition], list[Transition]]] = x_w.copy()
    for x in y_w.copy():
        for y in y_w.copy():
            if x == y:
                continue

            if set(x[0]).issubset(set(y[0])) and set(x[1]).issubset(set(y[1])):
                y_w.remove(x)
                break

    # Calculating p_w
    p_w: list[str] = []

    place_transitions_mapping: dict[
        str,
        tuple[list[Transition], list[Transition]]
    ] = {}

    start = next(places_counter)
    p_w.append(start)

    for y in y_w:
        p_y = next(places_counter)
        p_w.append(p_y)
        place_transitions_mapping[p_y] = y

    end = next(places_counter)
    p_w.append(end)

    # Calculating f_w
    petri_net = PetriNet()

    # add all places
    for p in p_w:
        petri_net.add_place(p)

    # add token in the start place
    petri_net.add_token(start)

    # add start transition
    petri_net.add_transition(name=t_i.name, id=t_i.id)
    petri_net.add_edge(start, petri_net.transition_name_to_id(t_i.name))

    # add end transition
    petri_net.add_transition(name=t_o.name, id=t_o.id)
    petri_net.add_edge(petri_net.transition_name_to_id(t_o.name), end)

    # add all transitions
    for place, transitions in place_transitions_mapping.items():
        for t_left in transitions[0]:
            petri_net.add_transition(t_left.name, t_left.id)
            petri_net.add_edge(t_left.id, place)
        for t_right in transitions[1]:
            petri_net.add_transition(t_right.name, t_right.id)
            petri_net.add_edge(place, t_right.id)

    return petri_net


def fitness_token_replay(log: LogXES, model: PetriNet):
    """
    Computes the conformance using the token reply approach.
    """
    c_sum, p_sum, m_sum, r_sum = 0, 0, 0, 0

    for events in log.values():
        trace = [
            model.transition_name_to_id(e['concept:name']) for e in events
        ]

        test_model = model.clone()
        c, p, m, r = 0, 1, 0, 0

        for transition_id in trace:
            if not test_model.is_enabled(transition_id):
                m += test_model.count_missing_tokens_to_fire(transition_id)
                test_model.add_missing_tokens_to_fire(transition_id)

            test_model.fire_transition(transition_id)

            c += test_model.count_consumed_tokens(transition_id)
            p += test_model.count_produced_tokens(transition_id)

        last_place_id = max(test_model.places.keys())
        if test_model.places[last_place_id].tokens == 0:
            test_model.places[last_place_id].add_token()
            m += 1

        test_model.places[last_place_id].consume_token()
        c += 1

        r = sum(p.tokens for p in test_model.places.values())

        c_sum += c
        p_sum += p
        m_sum += m
        r_sum += r

        # print(f"{[e['concept:name'] for e in events]}", trace, (m, c, r, p))

    fitness = 1/2 * (1 - m_sum / c_sum) + 1/2 * (1 - r_sum / p_sum)
    return fitness
