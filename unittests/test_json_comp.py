"""unittests for ./src/json_comp.py
"""
import types
import pytest
from src import json_comp as testee


def test_compare_jsondata(monkeypatch, capsys):
    """unittest for json_comp.compare_jsondata
    """
    def mock_read(arg):
        "stub"
        print(f'called readjson with arg {arg}')
        return ['data']
    def mock_gen(arg):
        "stub"
        nonlocal counter
        counter += 1
        which = 'left' if counter % 2 == 1 else 'right'
        result = ['', (False, '1left'), (False, '2right'), (False, '2left'), (False, '1right'),
                  (False, 'xxx'), (False, 'xxx'), (True, ''), (True, '')][counter]
        print(f'called gen_next from {which} with result {result}')
        return result
    def mock_gen_2(arg):
        "stub"
        nonlocal counter
        counter += 1
        which = 'left' if counter == 1 else 'right'
        result = ['', (True, ''), (False, 'xxx'), (True, '')][counter]
        print(f'called gen_next from {which} with result {result}')
        return result
    # def mock_gen_3(arg):
    #     "stub"
    #     nonlocal counter
    #     counter += 1
    #     which = 'right' if counter == 1 else 'left'
    #     result = ['', (False, 'xxx'), (True, ''), (True, '')][counter]
    #     print(f'called gen_next from {which} with result {result}')
    #     return result
    monkeypatch.setattr(testee, 'readjson', mock_read)
    monkeypatch.setattr(testee, 'gen_next', mock_gen)
    counter = 0
    assert testee.compare_jsondata('oldfile', 'newfile') == [('1left', 'left'),
                                                             ('2left', 'left'),
                                                             ('1right', 'left'),
                                                             ('2right', 'right'),
                                                             ('xxx', 'both')]
    assert capsys.readouterr().out == ("called readjson with arg oldfile\n"
                                       "called readjson with arg newfile\n"
                                       "called gen_next from left with result (False, '1left')\n"
                                       "called gen_next from right with result (False, '2right')\n"
                                       "called gen_next from left with result (False, '2left')\n"
                                       "called gen_next from right with result (False, '1right')\n"
                                       "called gen_next from left with result (False, 'xxx')\n"
                                       "called gen_next from right with result (False, 'xxx')\n"
                                       "called gen_next from left with result (True, '')\n"
                                       "called gen_next from right with result (True, '')\n")
    monkeypatch.setattr(testee, 'gen_next', mock_gen_2)
    counter = 0
    # deze tests helpen niet om de restanten (22->32, 26->32) gecovered te krijgen
    # ze zijn ook niet mogelijk zoalg EOF groter is dan niet-EOF
    # assert testee.compare_jsondata('oldfile', 'newfile') == []
    # assert capsys.readouterr().out == ("")
    # monkeypatch.setattr(testee, 'gen_next', mock_gen_3)
    # counter = 0
    # assert testee.compare_jsondata('oldfile', 'newfile') == []
    # assert capsys.readouterr().out == ("")


def test_refresh_jsoncompare(monkeypatch, capsys):
    """unittest for json_comp.refresh_jsoncompare
    """
    def mock_prepare(data):
        print(f'called prepare_values with arg {data}')
        return data
    class MockGui:
        """testdouble for gui.ShowComparisomnGui object
        """
        def init_tree(self, *args):
            print('called comparergui.init_tree with args', args)
        def build_header(self, *args):
            print('called comparergui.build_header with args', args)
        def build_child(self, *args):
            print('called comparergui.build_child with args', args)
        def set_node_text(self, *args):
            print('called comparergui.set_node_text with args', args)
        def colorize_header(self, *args):
            print('called comparergui.colorize_header with args', args)
        def colorize_child(self, *args):
            print('called comparergui.colorize_child with args', args)
    monkeypatch.setattr(testee, 'prepare_values', mock_prepare)
    comparer = types.SimpleNamespace(gui=MockGui(), parent=types.SimpleNamespace(
        lhs_path='xxx', rhs_path='yyy', data=[]))
    testee.refresh_jsoncompare(comparer)
    assert capsys.readouterr().out == (
            "called comparergui.init_tree with args ('key/value', 'xxx', 'yyy')\n"
            "called prepare_values with arg []\n")
    comparer = types.SimpleNamespace(gui=MockGui(), parent=types.SimpleNamespace(
        lhs_path='xxx', rhs_path='yyy', data=[
            (['top'], 'lvalue', 'rvalue'), (['top', 'ronly'], '', 'rvalue'),
            (['top', 'both'], '', ''), (['top', 'both', 'same'], 'value', 'value'),
            (['top', 'both', 'diff'], 'lvalue', 'rvalue'), (['top', 'lonly'], 'lvalue', '')]))
    testee.refresh_jsoncompare(comparer)
    assert capsys.readouterr().out == (
            "called comparergui.init_tree with args ('key/value', 'xxx', 'yyy')\n"
            "called prepare_values with arg [(['top'], 'lvalue', 'rvalue'),"
            " (['top', 'ronly'], '', 'rvalue'), (['top', 'both'], '', ''),"
            " (['top', 'both', 'same'], 'value', 'value'),"
            " (['top', 'both', 'diff'], 'lvalue', 'rvalue'),"
            " (['top', 'lonly'], 'lvalue', '')]\n"
            "called comparergui.build_header with args ('top',)\n"
            "called comparergui.set_node_text with args (None, 1, 'lvalue')\n"
            "called comparergui.set_node_text with args (None, 2, 'rvalue')\n"
            "called comparergui.colorize_child with args (None, False, False, True)\n"
            "called comparergui.build_child with args (None, 'ronly')\n"
            "called comparergui.set_node_text with args (None, 2, 'rvalue')\n"
            "called comparergui.colorize_child with args (None, True, '', '')\n"
            "called comparergui.colorize_header with args (None, True, '', '')\n"
            "called comparergui.build_child with args (None, 'both')\n"
            "called comparergui.colorize_child with args (None, '', '', '')\n"
            "called comparergui.colorize_header with args (None, '', '', '')\n"
            "called comparergui.build_child with args (None, 'same')\n"
            "called comparergui.set_node_text with args (None, 1, 'value')\n"
            "called comparergui.set_node_text with args (None, 2, 'value')\n"
            "called comparergui.colorize_child with args (None, False, False, False)\n"
            "called comparergui.colorize_header with args (None, False, False, False)\n"
            "called comparergui.colorize_header with args (None, False, False, False)\n"
            "called comparergui.build_child with args (None, 'diff')\n"
            "called comparergui.set_node_text with args (None, 1, 'lvalue')\n"
            "called comparergui.set_node_text with args (None, 2, 'rvalue')\n"
            "called comparergui.colorize_child with args (None, False, False, True)\n"
            "called comparergui.colorize_header with args (None, False, False, True)\n"
            "called comparergui.colorize_header with args (None, False, False, True)\n"
            "called comparergui.build_child with args (None, 'lonly')\n"
            "called comparergui.set_node_text with args (None, 1, 'lvalue')\n"
            "called comparergui.colorize_child with args (None, '', True, '')\n"
            "called comparergui.colorize_header with args (None, '', True, '')\n")


def test_prepare_values():
    """unittest for json_comp.prepare_values
    """
    data = []
    assert testee.prepare_values(data) == []
    data = [(['x'], 'both'), (['w', 'x'], 'left'), (['x', 'z'], 'both'), (['x', 'y', 'z'], 'left'),
            (['x', 'y', 'z'], 'right'), (['x', 'q'], 'right')]
    assert testee.prepare_values(data) == [[[], 'x', 'x'],
                                           [['w'], 'x', ''],
                                           [['x'], 'z', 'z'],
                                           [['x', 'y'], 'z', 'z'],
                                           [['x'], '', 'q']]


def test_readjson(monkeypatch, capsys, tmp_path):
    """unittest for json_comp.readjson
    """
    def mock_load(arg):
        print(f'called json.load with arg {arg}')
        return 'data'
    def mock_read(arg):
        print(f'called read_dict with arg {arg}')
        return 'data was read'
    monkeypatch.setattr(testee.json, 'load', mock_load)
    monkeypatch.setattr(testee, 'read_dict', mock_read)
    filepath = tmp_path / 'mydata.json'
    filename = str(filepath)
    with pytest.raises(FileNotFoundError):
        testee.readjson(filename)
    filepath.write_text('{}')
    assert testee.readjson(filename) == 'data was read'
    assert capsys.readouterr().out == (
            f"called json.load with arg <_io.TextIOWrapper name='{filename}' mode='r'"
            " encoding='UTF-8'>\n"
            "called read_dict with arg data\n")


def test_read_dict(monkeypatch, capsys):
    """unittest for json_comp.read_dict
    """
    def mock_read(arg):
        print(f'called read_list with arg {arg}')
        return 'q', 'r'
    monkeypatch.setattr(testee, 'read_list', mock_read)
    assert testee.read_dict({'b': 'data for b', 'c': ['x', 'y'],
                             'a': {'g': 'data for g', 'h': 'data for h'}}) == [
                                     ['a', 'g', 'data for g'], ['a', 'h', 'data for h'],
                                     ['b', 'data for b'], ['c', 'q'], ['c', 'r']]
    assert capsys.readouterr().out == "called read_list with arg ['x', 'y']\n"


def test_read_list(monkeypatch, capsys):
    """unittest for json_comp.read_list
    """
    def mock_read(arg):
        print(f'called read_list with arg {arg}')
        return 'q', 'r'
    monkeypatch.setattr(testee, 'read_dict', mock_read)
    assert testee.read_list(['x', 'z', 'y']) == [['listitem000', 'x'], ['listitem001', 'y'],
                                                 ['listitem002', 'z']]
    assert capsys.readouterr().out == ""
    assert testee.read_list([['q', 'r'], ['b', 'a']]) == [['listitem000', 'listitem000', 'a'],
                                                          ['listitem000', 'listitem001', 'b'],
                                                          ['listitem001', 'listitem000', 'q'],
                                                          ['listitem001', 'listitem001', 'r']]
    assert capsys.readouterr().out == ""
    assert testee.read_list([{'a': 'data for a', 'b': 'data for b'}]) == [['listitem000', 'q'],
                                                                          ['listitem000', 'r']]
    assert capsys.readouterr().out == (
            "called read_list with arg {'a': 'data for a', 'b': 'data for b'}\n")


def test_gen_next():
    """unittest for json_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, [])
    assert testee.gen_next(x for x in [('a', 'b')]) == (False, ('a', 'b'))
