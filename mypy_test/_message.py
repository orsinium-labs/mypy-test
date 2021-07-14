from collections import defaultdict
from enum import Enum
from typing import Dict, List, NamedTuple
from pathlib import Path


class Severity(Enum):
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"
    REVEAL = "reveal"


class Message(NamedTuple):
    path: Path
    line: int
    column: int
    severity: Severity
    text: str
    code: str


class ChangeType(Enum):
    MISSED = '-'
    UNEXPECTED = '+'


class Change(NamedTuple):
    type: ChangeType
    message: Message


GroupedType = Dict[Path, Dict[int, List[Message]]]


def group_messages(messages: List[Message]) -> GroupedType:
    grouped: GroupedType = defaultdict(defaultdict(list))  # type: ignore
    for message in messages:
        grouped[message.path][message.line].append(message)
    return dict(grouped)


def make_diff(expected: Dict[int, List[Message]], actual: Dict[int, List[Message]]) -> List[Change]:
    diff: List[Change] = []
    lines = set(expected) | set(actual)
    for line in sorted(lines):
        expected_messages = {f"{m.severity}{m.text}": m for m in expected.get(line, [])}
        actual_messages = {f"{m.severity}{m.text}": m for m in actual.get(line, [])}
        for text, expected_message in expected_messages.items():
            if text not in actual_messages:
                diff.append(Change(
                    type=ChangeType.MISSED,
                    message=expected_message,
                ))
        for text, actual_message in actual_messages.items():
            if text not in expected_messages:
                diff.append(Change(
                    type=ChangeType.UNEXPECTED,
                    message=actual_message,
                ))
    return diff
