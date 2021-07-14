import re
import tokenize
from typing import Iterator, Optional, NamedTuple
from ._message import Message, Severity
from pathlib import Path

REX = re.compile(r"""
    (?P<severity>[FENWR]):          # severity
    ((?P<col>\d+):)?                # column number (optional)
    \s+(?P<message>.+)              # error message
    (\s+\[(?P<code>[a-z-]+)\])?     # error code
""", re.VERBOSE)


class Source(NamedTuple):
    path: Path

    @property
    def tokens(self) -> Iterator[tokenize.TokenInfo]:
        with self.path.open('r') as stream:
            yield from tokenize.generate_tokens(stream.readline)

    @property
    def messages(self) -> Iterator[Message]:
        for token in self.tokens:
            if token.type != tokenize.COMMENT:
                continue
            message = self._parse_comment(token)
            if message is not None:
                yield message

    def _parse_comment(self, token: tokenize.TokenInfo) -> Optional[Message]:
        comment = token.string[1:].strip()
        match = REX.match(comment)
        if match is None:
            return None

        severity = self._parse_severity(match.group('severity'))
        text = match.group('message')
        if severity == Severity.REVEAL:
            severity = Severity.NOTE
            text = f'Revealed type is "{text}"'

        line = token.start[0]
        # if the comment takes the whole line, it is a block comment
        if token.string.strip() == token.line.strip():
            line += 1

        return Message(
            path=self.path,
            severity=severity,
            line=line,
            column=int(match.group('col') or 0),
            text=text,
            code=match.group('code'),
        )

    def _parse_severity(self, sev: str) -> Severity:
        if sev == 'F':
            return Severity.FATAL
        if sev == 'E':
            return Severity.ERROR
        if sev == 'W':
            return Severity.WARNING
        if sev == 'N':
            return Severity.NOTE
        if sev == 'R':
            return Severity.REVEAL
        raise RuntimeError('unreachable')
