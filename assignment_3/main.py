"""
Module containing the implementation of the Alpha Algorithm.
"""
from itertools import count, combinations

from petri_net import PetriNet, Transition
from dependency_graph_utils import DependencyGraph, EventXES, LogXES, dependency_graph_file, read_from_file

transitions_counter = count(start=-1, step=-1)
places_counter = count(start=1, step=1)


def sublists(lst):
    """
    Return all non-empty sublists (subsets).
    """
    # TODO remove duplicates
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


def find_places(dg: DependencyGraph, t_w: list[Transition]):
    """
    Finds places looking for all possible pair of subsets t_w where:
    - for each a1, a2 in A, a1 # a2
    - for each b1, b2 in B, b1 # b2
    - for each a1, a2 in A and b1, b2 in B, an -> bn
    """
    result: list[tuple[list[Transition], list[Transition]]] = []

    n = len(t_w)
    combinations = []

    for i in range(n):
        for j in range(i+1, n+1):  # j exclusive
            left = t_w[i:j]
            for k in range(j, n):
                for l in range(k+1, n+1):
                    right = t_w[k:l]
                    combinations.append([left, right])
    return combinations


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
    petri_net.add_marking(start)

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

    # for tid, t in petri_net.transitions.items():
    #     print(f"Previous of {tid}: {t.previous}\n")
    #     print(f"Next of {tid}: {t.next}\n")

    return petri_net


if __name__ == '__main__':
    mined_model = alpha(read_from_file("extension-log.xes"))

    def check_enabled(pn):
        ts = ["record issue", "inspection", "intervention authorization", "action not required",
              "work mandate", "no concession", "work completion", "issue completion"]
        for t in ts:
            print(pn.is_enabled(pn.transition_name_to_id(t)))
        print("")

    trace = ["record issue", "inspection", "intervention authorization",
             "work mandate", "work completion", "issue completion"]
    for a in trace:
        check_enabled(mined_model)
        mined_model.fire_transition(mined_model.transition_name_to_id(a))
    # # letters = ["a", "b", "c", "d", "e"]
    # # results = sublists(letters)
    # # print("Total combinations:", len(results))
    # # for c in results:
    # #     print(c)

    # # dict[CaseId, list[EventXES]]

    # log_xes_sample: LogXES = {
    #     'case_1': [
    #         {'concept:name': 'a'},
    #         {'concept:name': 'b'},
    #         {'concept:name': 'c'},
    #         {'concept:name': 'd'},
    #     ],
    #     'case_2': [
    #         {'concept:name': 'a'},
    #         {'concept:name': 'c'},
    #         {'concept:name': 'b'},
    #         {'concept:name': 'd'},
    #     ],
    #     'case_3': [
    #         {'concept:name': 'a'},
    #         {'concept:name': 'e'},
    #         {'concept:name': 'd'},
    #     ]
    # }

    # pn = alpha(log_xes_sample)

    # # log_xes = read_from_file('extension-log-3.xes')
    # # pn = alpha(log_xes)
