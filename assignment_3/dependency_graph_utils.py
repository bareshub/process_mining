"""
Module containing utils functions to parse, read or log a dependency graph.
Supported files extensions are:
- XES
"""
import xml.etree.ElementTree as ET
import datetime as DT
from dataclasses import dataclass


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
