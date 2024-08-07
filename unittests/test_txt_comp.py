"""unittests for ./src/txt_comp.py
"""
from src import txt_comp as testee

def test_gen_next():
    """unittest for txt_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, '')
    assert testee.gen_next(x for x in ['next line']) == (False, 'next line')


def test_get_file(tmp_path):
    """unittest for txt_comp.get_file
    """
    fname = 'filename'
    as_utf = tmp_path / f'{fname}_unicode'
    as_utf.write_text('this\nis\nsome\ntëxt\n', encoding='utf-8')
    as_latin = tmp_path / f'{fname}_latin8'
    as_latin.write_text('this\nis\nsome\ntëxt\n', encoding='latin-1')
    assert testee.get_file(as_utf) == ['is\n', 'some\n', 'this\n', 'tëxt\n']
    assert testee.get_file(as_latin) == ['is\n', 'some\n', 'this\n', 'tëxt\n']


def test_compare_txtdata_old(monkeypatch, capsys):
    """unittest for txt_comp.compare_txtdata
    """
    getcounter = 0
    def mock_get(fname):
        """stub
        """
        nonlocal getcounter
        print(f'called get_file with fname `{fname}`')
        getcounter += 1
        if getcounter == 1:
            return ['waarde1', 'waarde3', 'waarde5']
        return ['waarde2', 'waarde3', 'waarde4']
    monkeypatch.setattr(testee, 'get_file', mock_get)
    assert testee.compare_txtdata('fn1', 'fn2') == [['', 'waarde1', ''], ['', '', 'waarde2'],
                                                    ['waarde3', '', ''],
                                                    ['', '', 'waarde4'], ['', 'waarde5', '']]
    assert capsys.readouterr().out == ('called get_file with fname `fn1`\n'
                                       'called get_file with fname `fn2`\n')


def test_compare_txtdata(monkeypatch, capsys):
    """unittest for txt_comp.compare_txtdata
    """
    def mock_get(fname):
        """stub
        """
        print(f'called get_file with fname `{fname}`')
        return ['data']
    counter = 0
    def mock_next(gen):
        nonlocal counter
        _data = [(False, 'xxx', 'left'), (True, '', 'right'), (True, '', 'left')][counter]
        result = ('EOF' if _data[0] else '', _data[1])
        print(f'called gen_next from {_data[2]} side returning {result}')
        counter += 1
        return _data[:2]
    def mock_next_2(gen):
        nonlocal counter
        _data = [(True, '', 'left'), (False, 'xxx', 'right'), (True, '', 'right')][counter]
        result = ('EOF' if _data[0] else '', _data[1])
        print(f'called gen_next from {_data[2]} side returning {result}')
        counter += 1
        return _data[:2]
    def mock_next_3(gen):
        nonlocal counter
        _data = [(False, 'aaa', 'left'), (False, 'bbb', 'right'), (False, 'bbb', 'left'),
                 (False, 'ggg', 'left'), (False, 'eee', 'right'),
                 (False, 'fff', 'right'), (False, 'hhh', 'right'),
                 (True, '', 'left'), (False, 'iii', 'right'), (True, '', 'right')][counter]
        result = ('EOF' if _data[0] else '', _data[1])
        print(f'called gen_next from {_data[2]} side returning {result}')
        counter += 1
        return _data[:2]
    def mock_next_4(gen):
        nonlocal counter
        _data = [(False, 'bbb', 'left'), (False, 'aaa', 'right'), (False, 'bbb', 'right'),
                 (False, 'eee', 'left'), (False, 'ggg', 'right'),
                 (False, 'fff', 'left'), (False, 'hhh', 'left'),
                 (True, '', 'right'), (False, 'iii', 'left'), (True, '', 'left')][counter]
        result = ('EOF' if _data[0] else '', _data[1])
        print(f'called gen_next from {_data[2]} side returning {result}')
        counter += 1
        return _data[:2]
    monkeypatch.setattr(testee, 'get_file', mock_get)
    monkeypatch.setattr(testee, 'gen_next', mock_next)
    assert testee.compare_txtdata('fn1', 'fn2') == [['', 'xxx', '']]
    assert capsys.readouterr().out == ("called get_file with fname `fn1`\n"
                                       "called get_file with fname `fn2`\n"
                                       "called gen_next from left side returning ('', 'xxx')\n"
                                       "called gen_next from right side returning ('EOF', '')\n"
                                       "called gen_next from left side returning ('EOF', '')\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_2)
    assert testee.compare_txtdata('fn1', 'fn2') == [['', '', 'xxx']]
    assert capsys.readouterr().out == ("called get_file with fname `fn1`\n"
                                       "called get_file with fname `fn2`\n"
                                       "called gen_next from left side returning ('EOF', '')\n"
                                       "called gen_next from right side returning ('', 'xxx')\n"
                                       "called gen_next from right side returning ('EOF', '')\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_3)
    assert testee.compare_txtdata('fn1', 'fn2') == [['', 'aaa', ''], ['bbb', '', ''],
                                                    ['', '', 'eee'], ['', '', 'fff'],
                                                    ['', 'ggg', ''], ['', '', 'hhh'],
                                                    ['', '', 'iii']]
    assert capsys.readouterr().out == ("called get_file with fname `fn1`\n"
                                       "called get_file with fname `fn2`\n"
                                       "called gen_next from left side returning ('', 'aaa')\n"
                                       "called gen_next from right side returning ('', 'bbb')\n"
                                       "called gen_next from left side returning ('', 'bbb')\n"
                                       "called gen_next from left side returning ('', 'ggg')\n"
                                       "called gen_next from right side returning ('', 'eee')\n"
                                       "called gen_next from right side returning ('', 'fff')\n"
                                       "called gen_next from right side returning ('', 'hhh')\n"
                                       "called gen_next from left side returning ('EOF', '')\n"
                                       "called gen_next from right side returning ('', 'iii')\n"
                                       "called gen_next from right side returning ('EOF', '')\n"
                                       )
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_4)
    assert testee.compare_txtdata('fn1', 'fn2') == [['', '', 'aaa'], ['bbb', '', ''],
                                                    ['', 'eee', ''], ['', 'fff', ''],
                                                    ['', '', 'ggg'], ['', 'hhh', ''],
                                                    ['', 'iii', '']]
    assert capsys.readouterr().out == ("called get_file with fname `fn1`\n"
                                       "called get_file with fname `fn2`\n"
                                       "called gen_next from left side returning ('', 'bbb')\n"
                                       "called gen_next from right side returning ('', 'aaa')\n"
                                       "called gen_next from right side returning ('', 'bbb')\n"
                                       "called gen_next from left side returning ('', 'eee')\n"
                                       "called gen_next from right side returning ('', 'ggg')\n"
                                       "called gen_next from left side returning ('', 'fff')\n"
                                       "called gen_next from left side returning ('', 'hhh')\n"
                                       "called gen_next from right side returning ('EOF', '')\n"
                                       "called gen_next from left side returning ('', 'iii')\n"
                                       "called gen_next from left side returning ('EOF', '')\n")


class MockComparer:
    """stub for main.Comparer object
    """
    def __init__(self):
        print('called Comparer.__init__()')


class MockGui:
    """stub for gui.ShowComparisonGui object
    """
    def __init__(self):
        print('called ShowComparisonGui.__init__()')
        self.nodecounter = 0
    def init_tree(self, *args):
        """stub
        """
        print('called ShowComparisonGui.init_tree() with args', args)
    def build_header(self, *args):
        """stub
        """
        self.nodecounter += 1
        print('called ShowComparisonGui.build_header() with args', args)
        return f'node{self.nodecounter}'
    def set_node_text(self, *args):
        """stub
        """
        print('called ShowComparisonGui.set_node_text() with args', args)
    def colorize_child(self, *args):
        """stub
        """
        print('called ShowComparisonGui.colorize_child() with args', args)


class MockShowComparison:
    """stub for main.ShowComparison object
    """
    def __init__(self):
        self.parent = MockComparer()
        self.gui = MockGui()


def test_refresh_txtcompare(capsys):
    """unittest for txt_comp.refresh_txtcompare
    """
    testobj = MockShowComparison()
    testobj.parent.lhs_path = 'left'
    testobj.parent.rhs_path = 'right'
    testobj.parent.data = [('b1', 'l1', 'r1'), ('b2', 'l2', ''), ('b3', '', 'r2'), ('b4', '', '')]
    testee.refresh_txtcompare(testobj)
    assert capsys.readouterr().out == (
            "called Comparer.__init__()\n"
            "called ShowComparisonGui.__init__()\n"
            "called ShowComparisonGui.init_tree() with args ('Text in both files', 'left',"
            " 'right')\n"
            "called ShowComparisonGui.build_header() with args ('b1',)\n"
            "called ShowComparisonGui.set_node_text() with args ('node1', 1, 'l1')\n"
            "called ShowComparisonGui.set_node_text() with args ('node1', 2, 'r1')\n"
            "called ShowComparisonGui.colorize_child() with args ('node1', True, True, False)\n"
            "called ShowComparisonGui.build_header() with args ('b2',)\n"
            "called ShowComparisonGui.set_node_text() with args ('node2', 1, 'l2')\n"
            "called ShowComparisonGui.set_node_text() with args ('node2', 2, '')\n"
            "called ShowComparisonGui.colorize_child() with args ('node2', False, True, False)\n"
            "called ShowComparisonGui.build_header() with args ('b3',)\n"
            "called ShowComparisonGui.set_node_text() with args ('node3', 1, '')\n"
            "called ShowComparisonGui.set_node_text() with args ('node3', 2, 'r2')\n"
            "called ShowComparisonGui.colorize_child() with args ('node3', True, False, False)\n"
            "called ShowComparisonGui.build_header() with args ('b4',)\n"
            "called ShowComparisonGui.set_node_text() with args ('node4', 1, '')\n"
            "called ShowComparisonGui.set_node_text() with args ('node4', 2, '')\n"
            "called ShowComparisonGui.colorize_child() with args ('node4', False, False, False)\n"
            '')
