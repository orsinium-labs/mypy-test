import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import List, NoReturn

from ._message import COLORS, group_messages, make_diff
from ._mypy import MyPy
from ._source import Source


def main(argv: List[str]) -> int:
    # run mypy, read results
    with TemporaryDirectory() as tmpdir:
        mypy = MyPy(root=Path(tmpdir))
        mypy.run(*argv)
        if not mypy.ok:
            print('{red}Cannot file mypy report.{end}'.format(**COLORS), end=' ')
            print('Probably, mypy execution failed.')
            return 1
        all_actual = group_messages(mypy.messages)
        cur_dir = Path().absolute()
        code = 0
        paths = mypy.all_files

    # parse files, show diffs
    for path in paths:
        source = Source(path=path)
        actual = all_actual.get(path, {})
        expected = group_messages(source.messages).get(path, {})
        diff = make_diff(actual=actual, expected=expected)
        if not diff:
            continue
        code += 1
        print('{magenta}{p}{end}'.format(p=path.relative_to(cur_dir), **COLORS))
        for change in diff:
            print('  {type} line {line}: # {sev}: {msg}'.format(
                type=change.type.colored,
                line=change.message.line,
                sev=change.message.severity.colored,
                msg=change.message.text,
            ))
    return code


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
