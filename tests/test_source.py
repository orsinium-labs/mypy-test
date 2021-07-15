from pathlib import Path
from textwrap import dedent

from mypy_test._source import Source


def test_source(tmp_path: Path):
    """
    Test all files in the project
    """
    path = tmp_path / 'example.py'
    path.write_text(dedent("""
        a = 1
        reveal_type(a)  # R: builtins.int

        # E: Incompatible types in assignment (expression has type "str", variable has type "int")
        a = ""
    """))
    source = Source(path=path)

    messages = list(source.messages)
    assert len(messages) == 2

    msg = messages[0]
    assert msg.line == 3
    assert msg.text == 'Revealed type is "builtins.int"'
    assert msg.severity.value == 'note'

    msg = messages[1]
    assert msg.line == 6
    e = 'Incompatible types in assignment (expression has type "str", variable has type "int")'
    assert msg.text == e
    assert msg.severity.value == 'error'
