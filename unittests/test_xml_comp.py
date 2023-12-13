import pytest
import xml_comp as testee


def _test_getattrval(monkeypatch, capsys):
    pass

def _test_process_subelements(monkeypatch, capsys):
    pass

def _test_sort_xmldata(monkeypatch, capsys):
    pass

def test_gen_next():
    assert testee.gen_next(x for x in []) == (True, '', '', '')
    assert testee.gen_next(x for x in [(1, 2, 3)]) == (False, 1, 2, 3)

def _test_compare_xmldata(monkeypatch, capsys):
    pass

def _test_refresh_xmlcompare(monkeypatch, capsys):
    pass
