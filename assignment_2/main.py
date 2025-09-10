import xml.etree.ElementTree as ET
import datetime as DT


class Event:
    def __init__(self, task, case_id, user_id, timestamp):
        self.task = task
        self.case_id = case_id
        self.user_id = user_id
        self.time = timestamp


Log = dict[str, list[Event]]
EventXES = dict[str, str | int | DT.datetime]
LogXES = dict[str, list[EventXES]]
DependencyGraph = dict[str, dict[str, int]]


def log_as_dictionary(log: str):
    """Reads a CSV-like string into a dictionary.

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


def dependency_graph_inline(log: Log):
    """Extracts the dependency graph (direct follow relationships of the Alpha
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
            eventA, eventB = events[i], events[i+1]

            result.setdefault(eventA.task, {}).setdefault(eventB.task, 0)
            result[eventA.task][eventB.task] += 1

    return result


def parse_value_from_tag(value, tag):
    match tag:
        case x if 'int' in x:
            result = int(value)
        case x if 'date' in x:
            result = DT.datetime.fromisoformat(value[:-6])
        case _:
            result = value
    return result


def read_from_file(filename: str):
    """Reads an XES file into a dictionary.

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
            eventXES: EventXES = {}
            for attribute in event:
                eventXES[attribute.attrib['key']] = parse_value_from_tag(
                    value=attribute.attrib['value'],
                    tag=attribute.tag
                )
            result[case_id].append(eventXES)

    return result


def dependency_graph_file(log: LogXES):
    """Extracts the dependency graph (direct follow relationships of the Alpha
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
            eventA, eventB = events[i], events[i+1]
            nameA, nameB = eventA['concept:name'], eventB['concept:name']

            result.setdefault(nameA, {}).setdefault(nameB, 0)
            result[nameA][nameB] += 1

    return result
