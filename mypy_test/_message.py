from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import Dict, Iterator, List, NamedTuple


COLORS = dict(
    red='\033[91m',
    green='\033[92m',
    yellow='\033[93m',
    blue='\033[94m',
    magenta='\033[95m',
    end='\033[0m',
)
SEV_COLORS = dict(
    fatal='red',
    error='red',
    warning='yellow',
    note='blue',
    reveal='blue',
)


class Severity(Enum):
    FATAL = "fatal"
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"
    REVEAL = "reveal"

    @property
    def color(self) -> str:
        return COLORS[SEV_COLORS[self.value]]

    @property
    def colored(self):
        val = self.value[0].upper()
        return f'{self.color}{val}{COLORS["end"]}'


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

    @property
    def color(self) -> str:
        if self == ChangeType.MISSED:
            return COLORS['red']
        return COLORS['green']

    @property
    def colored(self):
        return f'{self.color}{self.value}{COLORS["end"]}'


class Change(NamedTuple):
    type: ChangeType
    message: Message


GroupedType = Dict[Path, Dict[int, List[Message]]]


def group_messages(messages: Iterator[Message]) -> GroupedType:
    grouped: GroupedType = defaultdict(lambda: defaultdict(list))
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
