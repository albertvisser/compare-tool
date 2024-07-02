"""unittests for ./src/xml_comp.py
"""
from src import xml_comp as testee


def test_getattrval():
    """unittest for xml_comp.getattrval
    """
    class MockElement:
        def __init__(self, attrs):
            self._attrs = attrs
        def items(self):
            return self._attrs.items()
    assert testee.getattrval(MockElement({})) == ''
    assert testee.getattrval(MockElement({'x': 'xxx', 'a': 'aaa'})) == 'xxx'
    assert testee.getattrval(MockElement({'data': 'xxx', 'id': 'yyy'})) == 'yyy'
    assert testee.getattrval(MockElement({'name': 'xxx', 'value': 'yyy'})) == 'xxx'


def _test_process_subelements(monkeypatch, capsys):
    """unittest for xml_comp.process_subelements
    """
    pass


def _test_sort_xmldata(monkeypatch, capsys):
    """unittest for xml_comp.sort_xmldata
    """


def test_gen_next():
    """unittest for xml_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, '', '', '')
    assert testee.gen_next(x for x in [(1, 2, 3)]) == (False, 1, 2, 3)


def _test_compare_xmldata(monkeypatch, capsys):
    """unittest for xml_comp.compare_xmldata
    """


def _test_refresh_xmlcompare(monkeypatch, capsys):
    """unittest for xml_comp.refresh_xmlcompare
    """
