import sys
import re
import subprocess
from typing import Iterator, List, NamedTuple
from pathlib import Path
from xml.etree import ElementTree
from ._message import Message, Severity


REX = re.compile(r"""
    (?P<path>.+?):                  # absolute file path
    (?P<line>\d+):                  # line number
    (?P<col>\d+):\s                 # column number
    (?P<severity>[a-z]+):\s         # severity
    (?P<message>.+?)              # error message
    (\s+\[(?P<code>[a-z-]+)\])?        # error code
    $
""", re.VERBOSE)


class MyPy(NamedTuple):
    root: Path

    def run(self, *args: str) -> None:
        cmd = [
            sys.executable, '-m', 'mypy',
            '--junit-xml', str(self.root / 'junit.xml'),
            '--cobertura-xml-report', str(self.root),
            '--show-column-numbers',
            '--show-error-codes',
            '--show-absolute-path',
        ]
        cmd.extend(args)
        subprocess.run(cmd, stdout=subprocess.DEVNULL)

    @property
    def all_files(self) -> List[Path]:
        root = ElementTree.parse(str(self.root / 'cobertura.xml')).getroot()
        root_path = Path(root.find('sources').find('source').text)  # type: ignore
        root_path = root_path.absolute()
        files = []
        for pkg in root.find('packages'):  # type: ignore
            rel_path = pkg.find('classes').find('class').get('filename')  # type: ignore
            path = root_path.joinpath(rel_path)  # type: ignore
            files.append(path)
        return files

    @property
    def messages(self) -> Iterator[Message]:
        root = ElementTree.parse(str(self.root / 'junit.xml')).getroot()
        text = root.find('testcase').find('failure').text  # type: ignore
        for line in text.splitlines():  # type: ignore
            line = line.strip()
            if not line:
                continue
            yield self._parse_message(line)

    def _parse_message(self, text: str) -> Message:
        match = REX.match(text)
        assert match
        return Message(
            path=Path(match.group('path')).absolute(),
            line=int(match.group('line')),
            column=int(match.group('col')),
            severity=Severity(match.group('severity')),
            text=match.group('message'),
            code=match.group('code'),
        )
