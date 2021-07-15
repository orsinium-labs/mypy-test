from pathlib import Path

from mypy_test import main


ROOT = Path(__file__).parent.parent


def test_good():
    path = ROOT / 'examples' / 'good.py'
    assert main([str(path)]) == 0


def test_empty():
    path = ROOT / 'examples' / 'empty.py'
    assert main([str(path)]) == 0


def test_bad():
    path = ROOT / 'examples' / 'bad.py'
    assert main([str(path)]) == 1


def test_all():
    path = ROOT / 'examples'
    assert main([str(path)]) == 1
