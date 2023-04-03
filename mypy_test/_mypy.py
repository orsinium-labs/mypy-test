import re
import subprocess
import sys
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional
from xml.etree import ElementTree

from ._message import Message, Severity


REX = re.compile(r"""
    (?P<path>.+?):                  # absolute file path
    (?P<line>\d+):                  # line number
    (?P<col>\d+):\s                 # column number
    (?P<severity>[a-z]+):\s         # severity
    (?P<message>.+?)                # error message
    (\s+\[(?P<code>[a-z-]+)\])?     # error code
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
        stdout: Optional[int] = subprocess.DEVNULL
        if '-v' in args or '--show-traceback' in args:
            stdout = None
        subprocess.run(cmd, stdout=stdout)

    @property
    def ok(self) -> bool:
        jpath = self.root / 'junit.xml'
        cpath = self.root / 'cobertura.xml'
        return jpath.is_file() and cpath.is_file()

    @property
    def all_files(self) -> List[Path]:
        root = ElementTree.parse(str(self.root / 'cobertura.xml')).getroot()
        root_path = Path(root.find('sources').find('source').text)  # type: ignore
        root_path = root_path.absolute()
        files = []
        pkgs = root.find('packages')
        for pkg in (pkgs or []):
            rel_path = pkg.find('classes').find('class').get('filename')  # type: ignore
            assert isinstance(rel_path, str)
            path = root_path.joinpath(rel_path).resolve()
            files.append(path)
        return files

    @property
    def messages(self) -> Iterator[Message]:
        root = ElementTree.parse(str(self.root / 'junit.xml')).getroot()
        failure = root.find('testcase').find('failure')  # type: ignore
        if failure is None:
            return
        lines = (failure.text or '').splitlines()
        for line in lines:
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
