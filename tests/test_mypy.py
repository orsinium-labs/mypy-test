from pathlib import Path
from textwrap import dedent

from mypy_test._mypy import MyPy


def test_mypy(tmp_path: Path):
    """
    Test all files in the project
    """
    mypy = MyPy(tmp_path / 'cache')
    path = tmp_path / 'sources'
    path.mkdir()
    (path / 'example.py').write_text(dedent("""
        a = 1
        reveal_type(a)
        a = ""
    """))
    mypy.run(str(path))

    files = mypy.all_files
    assert len(files) == 1
    assert files[0] == (path / 'example.py')

    messages = list(mypy.messages)
    assert len(messages) == 2
    for msg in messages:
        assert msg.path == path / 'example.py'

    msg = messages[0]
    assert msg.line == 3
    assert msg.text == 'Revealed type is "builtins.int"'
    assert msg.severity.value == 'note'

    msg = messages[1]
    assert msg.line == 4
    e = 'Incompatible types in assignment (expression has type "str", variable has type "int")'
    assert msg.text == e
    assert msg.severity.value == 'error'


def test_mypy_explodes(tmp_path: Path):
    mypy = MyPy(tmp_path / 'cache')
    path = tmp_path / 'sources'
    path.mkdir()
    (path / 'example.py').write_text(dedent("""
        from . import something
    """))
    mypy.run(str(path))

    files = mypy.all_files
    assert files == []
