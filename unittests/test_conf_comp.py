"""unittests for ./src/conf_comp.py
"""
import types
import textwrap
from src import conf_comp as testee

def test_gen_next():
    """unittest for conf_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, '', '', '')
    assert testee.gen_next(x for x in [(1, 2, 3)]) == (False, 1, 2, 3)


class MockParser(dict):
    """stub for configparser.ConfigParser
    """
    def __init__(self, *args, **kwargs):
        print('called ConfigParser.__init__() with args', args, kwargs)
        self.counter = 0
    def read(self, *args, **kwargs):
        """stub
        """
        print('called ConfigParser.read() with args', args, kwargs)
        self.counter += 1
        if self.counter == 1:
            raise UnicodeDecodeError('utf-8', b'\x00\x00', 1, 1, 'error')
        self['section2'] = {'option2': 'value4', 'option1': 'value3'}
        self['section1'] = {'option2': 'value2', 'option1': 'value1'}
    def sections(self):
        """stub
        """
        print('called ConfigParser.sections()')
        return ['section2', 'section1']
    def options(self, name):
        """stub
        """
        print(f'called ConfigParser.options() for section `{name}`')
        return ['option2', 'option1']


def test_sort_inifile(monkeypatch, capsys):
    """unittest for conf_comp.sort_inifile
    """
    def mock_read_without_fail(self, *args, **kwargs):
        """stub
        """
        print('called ConfigParser.read() with args', args, kwargs)
        self['section2'] = {'option2': 'value4', 'option1': 'value3'}
        self['section1'] = {'option2': 'value2', 'option1': 'value1'}
    monkeypatch.setattr(testee, 'ConfigParser', MockParser)
    testgen = testee.sort_inifile('filename')
    assert next(testgen) == ('section1', 'option1', 'value1')
    assert next(testgen) == ('section1', 'option2', 'value2')
    assert next(testgen) == ('section2', 'option1', 'value3')
    assert next(testgen) == ('section2', 'option2', 'value4')
    try:
        next(testgen)
        shouldnothappen = True
    except StopIteration:
        shouldnothappen = False
    assert not shouldnothappen
    assert capsys.readouterr().out == (
            "called ConfigParser.__init__() with args () {'allow_no_value': True,"
            " 'interpolation': None}\n"
            "called ConfigParser.read() with args ('filename',) {}\n"
            "called ConfigParser.read() with args ('filename',) {'encoding': 'latin-1'}\n"
            "called ConfigParser.sections()\n"
            "called ConfigParser.options() for section `section1`\n"
            "called ConfigParser.options() for section `section2`\n")
    monkeypatch.setattr(MockParser, 'read', mock_read_without_fail)
    monkeypatch.setattr(testee, 'ConfigParser', MockParser)
    testgen = testee.sort_inifile('filename')
    assert next(testgen) == ('section1', 'option1', 'value1')  # de rest geloven we wel
    assert capsys.readouterr().out == (
            "called ConfigParser.__init__() with args () {'allow_no_value': True,"
            " 'interpolation': None}\n"
            "called ConfigParser.read() with args ('filename',) {}\n"
            "called ConfigParser.sections()\n"
            "called ConfigParser.options() for section `section1`\n")


def test_check_inifile(monkeypatch, capsys):
    """unittest for conf_comp.check_inifile
    """
    counter = 0
    def mock_read(self, *args, **kwargs):
        """stub
        """
        nonlocal counter
        counter += 1
        print('called path.read() with args', str(self), args, kwargs)
        if counter == 1:
            raise UnicodeDecodeError('utf-8', b'\x00\x00', 1, 1, 'error')
        return 'zonder section header\n'
    def mock_read_2(self, *args, **kwargs):
        """stub
        """
        print('called path.read() with args', str(self), args, kwargs)
        return '[met section header]\nen de rest\n'
    def mock_write(self, data):
        """stub
        """
        print(f'called path.write() with args `{self}` `{data}`')   # , str(), )
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read)
    monkeypatch.setattr(testee.pathlib.Path, 'write_text', mock_write)
    assert testee.check_inifile('filename') == '/tmp/filename'
    assert capsys.readouterr().out == (
            'called path.read() with args filename () {}\n'
            "called path.read() with args filename () {'encoding': 'latin-1'}\n"
            'called path.write() with args `/tmp/filename`'
            ' `[  --- generated first header ---  ]\nzonder section header\n`\n')
    monkeypatch.setattr(testee.pathlib.Path, 'read_text', mock_read_2)
    assert testee.check_inifile('filename') == '/tmp/filename'
    assert capsys.readouterr().out == (
            'called path.read() with args filename () {}\n'
            'called path.write() with args `/tmp/filename`'
            ' `[met section header]\nen de rest\n`\n')
    # conceptuele test: maak een config file zonder header
    # laat Configparser het lezen -> geeft fout
    # voer deze methode uit
    # laat Configparser de gecorrigeerde versie lezen -> geeft geen fout


# 50->66, 54->66
def test_compare_configs(monkeypatch, capsys):
    """unittest for conf_comp.compare_configs
    """
    counter = 0
    def mock_sort(fname):
        """stub
        """
        print(f'called sort_inifile with fname `{fname}`')
        return fname
    counter = 0
    def mock_next(arg):
        """stub: alleen rechts content
        """
        nonlocal counter
        _data = [(True, '', '', '', 'left'),
                 (False, 'sectionA', 'keyX', 'value1', 'right'),
                 (False, 'sectionB', 'keyX', 'value1', 'right'),
                 (True, '', '', '', 'right')][counter]
        result = ('EOF' if _data[0] else '', _data[1:-1])
        print(f'called gen_next from {_data[-1]} side returning {result}')
        counter += 1
        return _data[:-1]
    def mock_next_2(arg):
        """stub: alleen links content
        """
        nonlocal counter
        _data = [(False, 'sectionA', 'keyX', 'value1', 'left'),
                 (True, '', '', '', 'right'),
                 (False, 'sectionB', 'keyX', 'value1', 'left'),
                 (True, '', '', '', 'left')][counter]
        result = ('EOF' if _data[0] else '', _data[1:-1])
        print(f'called gen_next from {_data[-1]} side returning {result}')
        counter += 1
        return _data[:-1]
    def mock_next_3(arg):
        """stub
        """
        nonlocal counter
        _data = [(False, 'sectionA', 'keyX', 'value1', 'left'),
                 (False, 'sectionA', 'keyX', 'value1', 'right'),
                 (False, 'sectionB', 'keyX', 'value1', 'left'),
                 (False, 'sectionB', 'keyX', 'value1', 'right'),
                 (True, '', '', '', 'left'),
                 (True, '', '', '', 'right')][counter]
        result = ('EOF' if _data[0] else '', _data[1:-1])
        print(f'called gen_next from {_data[-1]} side returning {result}')
        counter += 1
        return _data[:-1]
    def mock_next_4(arg):
        """stub
        """
        nonlocal counter
        _data = [(False, 'sectionA', 'keyS', 'value1', 'left'),
                 (False, 'sectionA', 'keyX', 'value1', 'right'),
                 (False, 'sectionA', 'keyV', 'value1', 'left'),
                 (False, 'sectionA', 'keyX', 'value0', 'left'),
                 (False, 'sectionA', 'keyZ', 'value1', 'right'),
                 (False, 'sectionB', 'keyS', 'value1', 'right'),
                 (False, 'sectionB', 'keyY', 'value1', 'left'),
                 (False, 'sectionB', 'keyU', 'value1', 'right'),
                 (False, 'sectionB', 'keyY', 'value1', 'right'),
                 (True, '', '', '', 'left'),
                 (True, '', '', '', 'right')][counter]
        result = ('EOF' if _data[0] else '', _data[1:-1])
        print(f'called gen_next from {_data[-1]} side returning {result}')
        counter += 1
        return _data[:-1]
    monkeypatch.setattr(testee, 'sort_inifile', mock_sort)
    monkeypatch.setattr(testee, 'gen_next', mock_next)
    assert testee.compare_configs('fn1', 'fn2') == [(('sectionA', 'keyX'), '', 'value1'),
                                                    (('sectionB', 'keyX'), '', 'value1')]
    assert capsys.readouterr().out == (
            "called sort_inifile with fname `fn1`\n"
            "called sort_inifile with fname `fn2`\n"
            "called gen_next from left side returning ('EOF', ('', '', ''))\n"
            "called gen_next from right side returning ('', ('sectionA', 'keyX', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionB', 'keyX', 'value1'))\n"
            "called gen_next from right side returning ('EOF', ('', '', ''))\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_2)
    assert testee.compare_configs('fn1', 'fn2') == [(('sectionA', 'keyX'), 'value1', ''),
                                                    (('sectionB', 'keyX'), 'value1', '')]
    assert capsys.readouterr().out == (
            "called sort_inifile with fname `fn1`\n"
            "called sort_inifile with fname `fn2`\n"
            "called gen_next from left side returning ('', ('sectionA', 'keyX', 'value1'))\n"
            "called gen_next from right side returning ('EOF', ('', '', ''))\n"
            "called gen_next from left side returning ('', ('sectionB', 'keyX', 'value1'))\n"
            "called gen_next from left side returning ('EOF', ('', '', ''))\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_3)
    assert testee.compare_configs('fn1', 'fn2') == [(('sectionA', 'keyX'), 'value1', 'value1'),
                                                    (('sectionB', 'keyX'), 'value1', 'value1')]
    assert capsys.readouterr().out == (
            "called sort_inifile with fname `fn1`\n"
            "called sort_inifile with fname `fn2`\n"
            "called gen_next from left side returning ('', ('sectionA', 'keyX', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionA', 'keyX', 'value1'))\n"
            "called gen_next from left side returning ('', ('sectionB', 'keyX', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionB', 'keyX', 'value1'))\n"
            "called gen_next from left side returning ('EOF', ('', '', ''))\n"
            "called gen_next from right side returning ('EOF', ('', '', ''))\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_4)
    assert testee.compare_configs('fn1', 'fn2') == [(('sectionA', 'keyS'), 'value1', ''),
                                                    (('sectionA', 'keyV'), 'value1', ''),
                                                    (('sectionA', 'keyX'), 'value0', 'value1'),
                                                    (('sectionA', 'keyZ'), 'value1', ''),
                                                    (('sectionB', 'keyS'), '', 'value1'),
                                                    (('sectionB', 'keyU'), '', 'value1'),
                                                    (('sectionB', 'keyY'), 'value1', 'value1')]
    assert capsys.readouterr().out == (
            "called sort_inifile with fname `fn1`\n"
            "called sort_inifile with fname `fn2`\n"
            "called gen_next from left side returning ('', ('sectionA', 'keyS', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionA', 'keyX', 'value1'))\n"
            "called gen_next from left side returning ('', ('sectionA', 'keyV', 'value1'))\n"
            "called gen_next from left side returning ('', ('sectionA', 'keyX', 'value0'))\n"
            "called gen_next from right side returning ('', ('sectionA', 'keyZ', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionB', 'keyS', 'value1'))\n"
            "called gen_next from left side returning ('', ('sectionB', 'keyY', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionB', 'keyU', 'value1'))\n"
            "called gen_next from right side returning ('', ('sectionB', 'keyY', 'value1'))\n"
            "called gen_next from left side returning ('EOF', ('', '', ''))\n"
            "called gen_next from right side returning ('EOF', ('', '', ''))\n")


def test_compare_configs_safe(monkeypatch, capsys):
    """unittest for conf_comp.compare_configs_safe
    """
    def mock_check(fname):
        """stub
        """
        print(f'called check_inifile with arg `{fname}`')
        return fname
    def mock_compare(*args):
        """stub
        """
        print('called compare_configs with args', args)
        return 'configs_compared'
    monkeypatch.setattr(testee, 'check_inifile', mock_check)
    monkeypatch.setattr(testee, 'compare_configs', mock_compare)
    assert testee.compare_configs_safe('left', 'right') == 'configs_compared'
    assert capsys.readouterr().out == ('called check_inifile with arg `left`\n'
                                       'called check_inifile with arg `right`\n'
                                       "called compare_configs with args ('left', 'right')\n")


def test_refresh_inicompare(capsys):
    """unittest for conf_comp.refresh_inicompare
    """
    class MockCompareGui:
        """stub
        """
        def __init__(self, arg):
            print('called ComparerGui.__init__')
        def init_tree(self, *args):
            print('called ComparerGui.init_tree with args', args)
        def build_header(self, section):
            print('called ComparerGui.build_header with arg', section)
            return f"header for '{section}'"
        def colorize_header(self, *args):
            print('called ComparerGui.colorize_header with args', args)
        def build_child(self, *args):
            print('called ComparerGui.build_child with args', args)
            option = args[1]
            return f"child for '{option}'"
        def colorize_child(self, *args):
            print('called ComparerGui.colorize_child with args', args)
        def set_node_text(self, *args):
            print('called ComparerGui.set_node_text with args', args)
    class MockComparer:
        """stub
        """
        def __init__(self):
            print('called Comparer.__init__')
            self.gui = MockCompareGui(self)
            self.parent = types.SimpleNamespace()
    comparer = MockComparer()
    assert capsys.readouterr().out == "called Comparer.__init__\ncalled ComparerGui.__init__\n"
    comparer.parent.lhs_path = 'old file'
    comparer.parent.rhs_path = 'new file'
    comparer.parent.data = []
    testee.refresh_inicompare(comparer)
    assert capsys.readouterr().out == ("called ComparerGui.init_tree with args"
                                       " ('Section/Option', 'old file', 'new file')\n")
    comparer.parent.data = [(('SectionA', 'OptionX'), 'ValueL1', 'ValueR1'),
                            (('SectionA', 'OptionY'), 'ValueL2', 'ValueR2'),
                            (('SectionB', 'OptionX'), None, 'ValueR3'),
                            (('SectionB', 'OptionY'), '', 'ValueR4'),
                            (('SectionC', 'OptionS'), None, None),
                            (('SectionC', 'OptionU'), '', None),
                            (('SectionC', 'OptionX'), None, ''),
                            (('SectionC', 'OptionY'), '', ''),
                            (('SectionD', 'OptionX'), 'ValueL3', None),
                            (('SectionD', 'OptionY'), 'ValueL4', ''),
                            (('SectionE', 'OptionY'), 'Value', 'Value')]
    testee.refresh_inicompare(comparer)
    assert capsys.readouterr().out == textwrap.dedent("""\
        called ComparerGui.init_tree with args ('Section/Option', 'old file', 'new file')
        called ComparerGui.build_header with arg SectionA
        called ComparerGui.build_child with args ("header for 'SectionA'", 'OptionX')
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 1, 'ValueL1')
        called ComparerGui.colorize_child with args ("child for 'OptionX'", False, False, True)
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 2, 'ValueR1')
        called ComparerGui.build_child with args ("header for 'SectionA'", 'OptionY')
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 1, 'ValueL2')
        called ComparerGui.colorize_child with args ("child for 'OptionY'", False, False, True)
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 2, 'ValueR2')
        called ComparerGui.colorize_header with args ("header for 'SectionA'", False, False, True)
        called ComparerGui.build_header with arg SectionB
        called ComparerGui.build_child with args ("header for 'SectionB'", 'OptionX')
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 1, '(no value)')
        called ComparerGui.colorize_child with args ("child for 'OptionX'", False, False, True)
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 2, 'ValueR3')
        called ComparerGui.build_child with args ("header for 'SectionB'", 'OptionY')
        called ComparerGui.colorize_child with args ("child for 'OptionY'", True, False, True)
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 1, '')
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 2, 'ValueR4')
        called ComparerGui.colorize_header with args ("header for 'SectionB'", True, False, True)
        called ComparerGui.build_header with arg SectionC
        called ComparerGui.build_child with args ("header for 'SectionC'", 'OptionS')
        called ComparerGui.set_node_text with args ("child for 'OptionS'", 1, '(no value)')
        called ComparerGui.set_node_text with args ("child for 'OptionS'", 2, '(no value)')
        called ComparerGui.build_child with args ("header for 'SectionC'", 'OptionU')
        called ComparerGui.colorize_child with args ("child for 'OptionU'", True, False, False)
        called ComparerGui.set_node_text with args ("child for 'OptionU'", 1, '')
        called ComparerGui.set_node_text with args ("child for 'OptionU'", 2, '(no value)')
        called ComparerGui.build_child with args ("header for 'SectionC'", 'OptionX')
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 1, '(no value)')
        called ComparerGui.colorize_child with args ("child for 'OptionX'", True, True, False)
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 2, '')
        called ComparerGui.build_child with args ("header for 'SectionC'", 'OptionY')
        called ComparerGui.colorize_child with args ("child for 'OptionY'", True, True, False)
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 1, '')
        called ComparerGui.colorize_child with args ("child for 'OptionY'", True, True, False)
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 2, '')
        called ComparerGui.colorize_header with args ("header for 'SectionC'", True, True, False)
        called ComparerGui.build_header with arg SectionD
        called ComparerGui.build_child with args ("header for 'SectionD'", 'OptionX')
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 1, 'ValueL3')
        called ComparerGui.colorize_child with args ("child for 'OptionX'", False, False, True)
        called ComparerGui.set_node_text with args ("child for 'OptionX'", 2, '(no value)')
        called ComparerGui.build_child with args ("header for 'SectionD'", 'OptionY')
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 1, 'ValueL4')
        called ComparerGui.colorize_child with args ("child for 'OptionY'", False, True, True)
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 2, '')
        called ComparerGui.colorize_header with args ("header for 'SectionD'", False, True, True)
        called ComparerGui.build_header with arg SectionE
        called ComparerGui.build_child with args ("header for 'SectionE'", 'OptionY')
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 1, 'Value')
        called ComparerGui.set_node_text with args ("child for 'OptionY'", 2, 'Value')
        called ComparerGui.colorize_header with args ("header for 'SectionE'", False, False, False)
        """)
