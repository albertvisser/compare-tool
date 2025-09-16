"""unittests for ./src/python_comp.py
"""
import types
from src import python_comp as testee


def test_read_pyfile(tmp_path):
    """unittest for python_comp.read_pyfile
    """
    filepath = tmp_path / 'filename.py'
    filename = str(filepath)
    filepath.touch()
    assert testee.read_pyfile(filename) == {(): []}
    filepath.write_text('"""docstring\n'
                        '"""\n'
                        "\n"
                        "import x\n"
                        "from y import x\n"
                        "# this is a comment\n"
                        "def qqq(rrr):\n"
                        '    """a function"""\n'
                        "    def inner():\n"
                        "        print('qqq')\n"
                        '    print("rrr")\n'
                        "\n"
                        "class Abc:\n"
                        "    abccount = 0\n"
                        "    def __init__(self):\n"
                        "        self.count = 0\n"
                        "        self.abccount += 1\n"
                        "\n"
                        "if __name__ == '__main__':\n"
                        "   qqq('hello')\n")
    assert testee.read_pyfile(filename) == {
            (): ['"""docstring', '"""', 'import x', 'from y import x',
                 "if __name__ == '__main__':", "   qqq('hello')"],
            ('def qqq',): ['def qqq(rrr):', '    """a function"""', '    print("rrr")'],
            ('def qqq', '    def inner'): ['    def inner():', "        print('qqq')"],
            ('class Abc',): ['class Abc:', '    abccount = 0'],
            ('class Abc', '    def __init__'): ['    def __init__(self):',
                                                '        self.count = 0',
                                                '        self.abccount += 1']}
    filepath.write_text("def qqq():\n"
                        "    print('ququ', end='')\n"
                        "    print('lequ')\n")
    assert testee.read_pyfile(filename) == {
            (): [],
            ('def qqq',): ['def qqq():', "    print('ququ', end='')", "    print('lequ')"]}


def test_calc_indent():
    """unittest for python_comp.calc_indent
    """
    assert testee.calc_indent('') == 0
    assert testee.calc_indent('xxxxx') == 0
    assert testee.calc_indent('    xxxxx') == 4


def test_get_construct_name():
    """unittest for python_comp.get_construct_name
    """
    assert testee.get_construct_name('def fun(x, y):') == "def fun"
    assert testee.get_construct_name('class Gargl:') == "class Gargl"
    assert testee.get_construct_name('class Gargl(Argl):') == "class Gargl"
    assert testee.get_construct_name('    def fun(x, y):') == "    def fun"
    assert testee.get_construct_name('    class Gargl:') == "    class Gargl"
    assert testee.get_construct_name('    class Gargl(Argl):') == "    class Gargl"


def test_compare_pydata(monkeypatch, capsys):
    """unittest for python_comp.compare_pydata
    """
    def mock_read(arg):
        "stub"
        print(f'called read_pyfile with arg {arg}')
        return {'x': f'{arg}x', 'y': f'{arg}y', 'z': f'{arg}z'}
    def mock_gen(arg):
        "stub"
        nonlocal count
        count += 1
        gen = 'leftgen' if count % 2 == 1 else 'rightgen'
        result = True, ''
        print(f'called gen_next for {gen} giving result {result}')
        return result
    def mock_gen_2(arg):
        "stub"
        nonlocal count
        count += 1
        gen = 'leftgen' if count % 2 == 1 else 'rightgen'
        result = [(False, 'x'), (False, 'x'), (False, 'z'), (False, 'y'),
                  (False, 'y'), (False, 'z'), (True, ()), (True, ())][count]
        print(f'called gen_next for {gen} giving result {result}')
        return result
    def mock_gen_3(arg):
        "stub"
        nonlocal count
        count += 1
        result = [(False, 'x', 'leftgen'), (False, 'x', 'rightgen'), (False, 'z', 'leftgen'),
                  (False, 'y', 'rightgen'), (True, (), 'leftgen'), (False, 'z', 'rightgen'),
                  (True, (), 'rightgen')][count]
        print(f'called gen_next for {result[2]} giving result {result[:2]}')
        return result[:2]
    monkeypatch.setattr(testee, 'read_pyfile', mock_read)
    monkeypatch.setattr(testee, 'gen_next', mock_gen)
    count = 0
    assert testee.compare_pydata('old', 'new') == []
    assert capsys.readouterr().out == ("called read_pyfile with arg old\n"
                                       "called read_pyfile with arg new\n"
                                       "called gen_next for leftgen giving result (True, '')\n"
                                       "called gen_next for rightgen giving result (True, '')\n")
    count = 0
    monkeypatch.setattr(testee, 'gen_next', mock_gen_2)
    assert testee.compare_pydata('old', 'new') == [('x', 'oldx', []), ('y', 'oldy', []),
                                                   ('y', 'oldy', []), ('z', 'oldz', 'newz')]
    assert capsys.readouterr().out == ("called read_pyfile with arg old\n"
                                       "called read_pyfile with arg new\n"
                                       "called gen_next for leftgen giving result (False, 'x')\n"
                                       "called gen_next for rightgen giving result (False, 'z')\n"
                                       "called gen_next for leftgen giving result (False, 'y')\n"
                                       "called gen_next for rightgen giving result (False, 'y')\n"
                                       "called gen_next for leftgen giving result (False, 'z')\n"
                                       "called gen_next for rightgen giving result (True, ())\n"
                                       "called gen_next for leftgen giving result (True, ())\n")
    count = 0
    monkeypatch.setattr(testee, 'gen_next', mock_gen_3)
    assert testee.compare_pydata('old', 'new') == [('x', 'oldx', []), ('y', 'oldy', []),
                                                   ('z', [], 'newz'), ('z', [], 'newz')]
    assert capsys.readouterr().out == ("called read_pyfile with arg old\n"
                                       "called read_pyfile with arg new\n"
                                       "called gen_next for rightgen giving result (False, 'x')\n"
                                       "called gen_next for leftgen giving result (False, 'z')\n"
                                       "called gen_next for rightgen giving result (False, 'y')\n"
                                       "called gen_next for leftgen giving result (True, ())\n"
                                       "called gen_next for rightgen giving result (False, 'z')\n"
                                       "called gen_next for rightgen giving result (True, ())\n")


class MockGui:
    """testdouble for gui.ShowComparisonGui object
    """
    def init_tree(self, *args):
        "stub"
        print('called comparergui.init_tree with args', args)
    def build_header(self, *args):
        "stub"
        print('called comparergui.build_header with args', args)
        return 'header'
    def build_child(self, *args):
        "stub"
        print('called comparergui.build_child with args', args)
        return 'child'
    def set_node_text(self, *args):
        "stub"
        print('called comparergui.set_node_text with args', args)
    def colorize_header(self, *args):
        "stub"
        print('called comparergui.colorize_header with args', args)
    def colorize_child(self, *args):
        "stub"
        print('called comparergui.colorize_child with args', args)

class MockComparer:
    """testdouble for main.ShowComparison object
    """
    def __init__(self):
        self.gui = MockGui()
        self.parent = types.SimpleNamespace(data='comparer_data', lhs_path='lhs_path',
                                            rhs_path='rhs_path')


def test_refresh_pycompare(monkeypatch, capsys):
    """unittest for python_comp.refresh_pycompare
    """
    def mock_compare(self, *args):
        print("called differ.compare with args", args)
        return ['lvalues'], ['rvalues']
    def mock_prepare(*args):
        print("called prepare_values with args", args)
        return []
    def mock_prepare_2(*args):
        print("called prepare_values with args", args)
        return [('', 'xxx', 'yyy'), (['qqq'], 'aaa', ''), (['qqq', 'rrr'], '', 'bbb'),
                (['qqq'], 'ccc', 'ccc'), (['qqq', 'rrr'], '', '')]
    def mock_add(*args):
        print('called add_new_parentnode with args', args)
        return args[2]
    def mock_add_one(*args):
        args = (args[0], 'parentdict', args[2], args[3], args[4])
        print('called add_functionbody_nodes_one_side with args', args)
    def mock_add_both(*args):
        args = (args[0], 'parentdict', args[2], args[3])
        print('called add_functionbody_nodes_both_sides with args', args)
    monkeypatch.setattr(testee.difflib.Differ, 'compare', mock_compare)
    monkeypatch.setattr(testee, 'prepare_values', mock_prepare)
    monkeypatch.setattr(testee, 'add_new_parentnode', mock_add)
    monkeypatch.setattr(testee, 'add_functionbody_nodes_one_side', mock_add_one)
    monkeypatch.setattr(testee, 'add_functionbody_nodes_both_sides', mock_add_both)
    comparer = MockComparer()
    testee.refresh_pycompare(comparer)
    assert capsys.readouterr().out == ("called comparergui.init_tree with args"
                                       " ('construct', 'code in lhs_path', 'code in rhs_path')\n"
                                       "called prepare_values with args ('comparer_data',)\n")
    monkeypatch.setattr(testee, 'prepare_values', mock_prepare_2)
    testee.refresh_pycompare(comparer)
    assert capsys.readouterr().out == (
            "called comparergui.init_tree with args"
            " ('construct', 'code in lhs_path', 'code in rhs_path')\n"
            "called prepare_values with args ('comparer_data',)\n"
            f"called add_new_parentnode with args ({comparer}, {{}}, ('module level',))\n"
            "called differ.compare with args ('xxx', 'yyy')\n"
            f"called add_functionbody_nodes_both_sides with args ({comparer}, 'parentdict',"
            " ('module level',), (['lvalues'], ['rvalues']))\n"
            f"called add_new_parentnode with args ({comparer},"
            " {('module level',): ('module level',)}, ('qqq',))\n"
            f"called add_functionbody_nodes_one_side with args ({comparer}, 'parentdict',"
            " ('qqq',), 'aaa', 'left')\n"
            f"called add_new_parentnode with args ({comparer},"
            " {('module level',): ('module level',), ('qqq',): ('qqq',)}, ('qqq', 'rrr'))\n"
            f"called add_functionbody_nodes_one_side with args ({comparer}, 'parentdict',"
            " ('qqq', 'rrr'), 'bbb', 'right')\n"
            "called differ.compare with args ('ccc', 'ccc')\n"
            f"called add_functionbody_nodes_both_sides with args ({comparer}, 'parentdict',"
            " ('qqq',), (['lvalues'], ['rvalues']))\n")


def test_prepare_values():
    """unittest for python_comp.prepare_values
    """
    assert testee.prepare_values([]) == []
    assert testee.prepare_values([(['x'], '', ''), (['y'], 'l1', ''), (['y'], '', 'r1'),
                                  (['y', 'z'], 'l2', 'r2')]) == [(['x'], [], []),
                                                                 (['y'], 'l1', 'r1'),
                                                                 (['y', 'z'], 'l2', 'r2')]


def test_add_new_parentnode(capsys):
    """unittest for python_comp.add_new_parentnode
    """
    comparer = MockComparer()
    parentdict = {('x',): 'xxx'}
    assert testee.add_new_parentnode(comparer, {}, ('y',)) == 'header'
    assert capsys.readouterr().out == ("called comparergui.build_header with args ('y',)\n")
    assert testee.add_new_parentnode(comparer, parentdict, ('x', 'y')) == 'child'
    assert capsys.readouterr().out == ("called comparergui.build_child with args ('xxx', 'y')\n")


def test_add_function_body_nodes_one_side(capsys):
    """unittest for python_comp.add_function_body_nodes_one_side
    """
    comparer = MockComparer()
    parentdict = {('pa',): 'parent'}
    testee.add_functionbody_nodes_one_side(comparer, parentdict, ('pa',), ['x', 'y'], 'left')
    assert capsys.readouterr().out == (
            "called comparergui.build_child with args ('parent', 'function body')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 1, 'x')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 1, 'y')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.colorize_header with args ('child', False, True, False)\n"
            "called comparergui.colorize_header with args ('parent', False, True, False)\n")
    testee.add_functionbody_nodes_one_side(comparer, parentdict, ('pa',), ['x', 'y'], 'any')
    assert capsys.readouterr().out == (
            "called comparergui.build_child with args ('parent', 'function body')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 2, 'x')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 2, 'y')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.colorize_header with args ('child', True, False, False)\n"
            "called comparergui.colorize_header with args ('parent', True, False, False)\n")
    parentdict = {('module level',): 'parent'}
    testee.add_functionbody_nodes_one_side(comparer, parentdict, ('module level',), ['x', 'y'],
                                           'left')
    assert capsys.readouterr().out == (
            "called comparergui.build_child with args ('parent', 'code')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 1, 'x')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 1, 'y')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.colorize_header with args ('child', False, True, False)\n"
            "called comparergui.colorize_header with args ('parent', False, True, False)\n")
    testee.add_functionbody_nodes_one_side(comparer, parentdict, ('module level',), ['x', 'y'],
                                           'any')
    assert capsys.readouterr().out == (
            "called comparergui.build_child with args ('parent', 'code')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 2, 'x')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 2, 'y')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.colorize_header with args ('child', True, False, False)\n"
            "called comparergui.colorize_header with args ('parent', True, False, False)\n")


def test_add_function_body_nodes_both_sides(capsys):
    """unittest for python_comp.add_function_body_nodes_both_sides
    """
    comparer = MockComparer()
    parentdict = {('pa',): 'parent'}
    testee.add_functionbody_nodes_both_sides(comparer, parentdict, ('pa',),
                                             ['  xxxx', '- yy y', '+ yyyy', '? zzzz'])
    assert capsys.readouterr().out == (
            "called comparergui.build_child with args ('parent', 'function body')\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 2, 'xxxx')\n"
            "called comparergui.set_node_text with args ('child', 1, 'xxxx')\n"
            "called comparergui.colorize_child with args ('child', False, False, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 1, 'yy y')\n"
            "called comparergui.colorize_child with args ('child', False, True, False)\n"
            "called comparergui.build_child with args ('child', '')\n"
            "called comparergui.set_node_text with args ('child', 2, 'yyyy')\n"
            "called comparergui.colorize_child with args ('child', True, False, False)\n"
            "called comparergui.colorize_header with args ('child', False, False, True)\n"
            "called comparergui.colorize_header with args ('parent', False, False, True)\n")


def test_gen_next():
    """unittest for python_comp.gen_next
    """
    assert testee.gen_next((x for x in [])) == (True, [])
    assert testee.gen_next((x for x in [('a', 'b')])) == (False, ('a', 'b'))
