import sys
from typing import List, NoReturn
from pathlib import Path

from ._message import group_messages, make_diff, COLORS
from ._mypy import MyPy
from ._source import Source


def main(argv: List[str]) -> int:
    root = Path()
    mypy = MyPy(root=root)
    mypy.run(*argv)
    all_actual = group_messages(mypy.messages)
    cur_dir = Path().absolute()
    code = 0
    for path in mypy.all_files:
        source = Source(path=path)
        actual = all_actual.get(path, {})
        expected = group_messages(source.messages).get(path, {})
        diff = make_diff(actual=actual, expected=expected)
        if not diff:
            continue
        code += 1
        print(path.relative_to(cur_dir))
        for change in diff:
            print('  {type} {line} {sev} {msg}'.format(
                type=change.type.colored,
                line=change.message.line,
                sev=change.message.severity.colored,
                msg=change.message.text,
                **COLORS,
            ))
    return code


def entrypoint() -> NoReturn:
    sys.exit(main(sys.argv[1:]))
