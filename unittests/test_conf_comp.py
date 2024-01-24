"""unittests for ./conf_comp.py
"""
import conf_comp as testee

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
    # conceptuele test: maak een config file zonder header
    # laat Configparser het lezen -> geeft fout
    # voer deze methode uit
    # laat Configparser de gecorrigeerde versie lezen -> geeft geen fout


def test_compare_configs(monkeypatch, capsys):
    """unittest for conf_comp.compare_configs
    """
    counter = 0
    def mock_sort(fname):
        """stub
        """
        print(f'called sort_inifile with fname `{fname}`')
        return fname
    def mock_next(arg):
        """stub
        """
        nonlocal counter
        print('called gen_next with arg', arg)
        counter += 1
        if counter == 1:
            return True, '', '', ''
        return True, '', '', ''
    def mock_next_2(arg):
        """stub
        """
        nonlocal counter
        print('called gen_next with arg', arg)
        counter += 1
        if counter == 1:
            return True, '', '', ''
        if counter == 2:
            return False, 'a', 'b', 'c'
        return True, 'a', 'b', 'c'
    def mock_next_3(arg):
        """stub
        """
        nonlocal counter
        print('called gen_next with arg', arg)
        counter += 1
        if counter == 1:
            return False, 'x', 'y', 'z'
        if counter == 3:
            return True, 'x', 'y', 'z'
        return True, '', '', ''
    def mock_next_4(arg):
        """stub
        """
        print('called gen_next with arg', arg)
        nonlocal counter
        counter += 1
        if counter == 1:
            return False, 'x', 'y', 'z'
        if counter == 2:
            return False, 'a', 'b', 'c'
        if counter == 3:
            return False, 'd', 'e', 'f'
        if counter == 5:
            return False, 'xx', 'yy', 'zz'
        return True, '', '', ''
    monkeypatch.setattr(testee, 'sort_inifile', mock_sort)
    monkeypatch.setattr(testee, 'gen_next', mock_next)
    assert testee.compare_configs('fn1', 'fn2') == []
    assert capsys.readouterr().out == ("called sort_inifile with fname `fn1`\n"
                                       "called sort_inifile with fname `fn2`\n"
                                       "called gen_next with arg fn1\n"
                                       "called gen_next with arg fn2\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_2)
    assert testee.compare_configs('fn1', 'fn2') == [(('a', 'b'), '', 'c')]
    assert capsys.readouterr().out == ("called sort_inifile with fname `fn1`\n"
                                       "called sort_inifile with fname `fn2`\n"
                                       "called gen_next with arg fn1\n"
                                       "called gen_next with arg fn2\n"
                                       "called gen_next with arg fn2\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_3)
    assert testee.compare_configs('fn1', 'fn2') == [(('x', 'y'), 'z', '')]
    assert capsys.readouterr().out == ("called sort_inifile with fname `fn1`\n"
                                       "called sort_inifile with fname `fn2`\n"
                                       "called gen_next with arg fn1\n"
                                       "called gen_next with arg fn2\n"
                                       "called gen_next with arg fn1\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_4)
    assert testee.compare_configs('fn1', 'fn2') == [(('a', 'b'), '', 'c'),
                                                    (('d', 'e'), '', 'f'),
                                                    (('x', 'y'), 'z', ''),
                                                    (('xx', 'yy'), 'zz', '')]
    assert capsys.readouterr().out == ("called sort_inifile with fname `fn1`\n"
                                       "called sort_inifile with fname `fn2`\n"
                                       "called gen_next with arg fn1\n"
                                       "called gen_next with arg fn2\n"
                                       "called gen_next with arg fn2\n"
                                       "called gen_next with arg fn2\n"
                                       "called gen_next with arg fn1\n"
                                       "called gen_next with arg fn1\n")
    # andere mogelijkheden
    # sect01, opt01, val01 = sect01, opt01, val01
    # sect01, opt02, val00 < sect01, opt02, val01
    # sect01, opt03, val01 > sect01, opt03, val00,


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


def _test_refresh_inicompare(monkeypatch, capsys):
    """unittest for conf_comp.refresh_inicompare
    """
    assert testee.refresh_inicompare()
