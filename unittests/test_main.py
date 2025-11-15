"""unittests for ./src/main.py
"""
import types
from src import main as testee


def test_get_input_paths(capsys):
    """unittest for main.get_input_paths
    """
    assert testee.get_input_paths([]) == ('', '')
    assert capsys.readouterr().out == ''
    assert testee.get_input_paths(['left'])
    assert capsys.readouterr().out == ''
    assert testee.get_input_paths(['left', 'right'])
    assert capsys.readouterr().out == ''
    assert testee.get_input_paths(['left', 'right', ''])
    assert capsys.readouterr().out == 'excessive filename arguments truncated\n'


def test_do_compare(monkeypatch, capsys):
    """unittest for main.do_compare
    """
    def mock_compare(left, right):
        """stub
        """
        print(f'called compare_method with args `{left}` and `{right}`')
        return ['compare output']
    def mock_compare_miss(left, right):
        """stub
        """
        print(f'called compare_method with args `{left}` and `{right}`')
        raise ValueError('xxxx', 1, 1)
    monkeypatch.setattr(testee, 'comparetypes', {'x': ('', mock_compare, '')})
    assert testee.do_compare('left', 'right', 'x') == (True, ['compare output'])
    assert capsys.readouterr().out == 'called compare_method with args `left` and `right`\n'
    monkeypatch.setattr(testee, 'comparetypes', {'x': ('', mock_compare_miss, '')})
    ok, traceback = testee.do_compare('left', 'right', 'x')
    assert not ok
    assert traceback[-1][-1] == "ValueError: ('xxxx', 1, 1)\n"
    assert capsys.readouterr().out == 'called compare_method with args `left` and `right`\n'


class MockMainWindow:
    """stub for gui.MainWindow
    """
    def __init__(self, *args):
        print('called MainWindow.__init__() with args', args)
    def meld_input_fout(self, mld):
        """stub
        """
        print('called MainWindow.meld_input_fout() with arg', mld)
    def meld_vergelijking_fout(self, *args):
        """stub
        """
        print('called MainWindow.meld_vergelijking_fout() with args', args)
    def meld(self, *args):
        """stub
        """
        print('called MainWindow.meld() with args', args)
    def go(self, *args):
        """stub
        """
        print('called MainWindow.go with args', args)
    def exit(self):
        """stub
        """
        print('called MainWindow.exit()')


class MockAskOpenFiles:
    """stub for main.AskOpenFiles
    """
    def __init__(self, *args):
        print('called AskOpenFiles.__init__() with args', args)
    def check_input(self, *args):
        """stub
        """
        print('called AskOpenFiles.check_input() with args', args)


class MockShowComparison:
    """stub for main.ShowComparison
    """
    def __init__(self, *args):
        print('called ShowComparison.__init__() with args', args)
    def refresh(self):
        """stub
        """
        print('called ShowComparison.refresh()')


class MockIniFile:
    """stub for main.IniFile
    """
    def __init__(self, arg):
        print('called IniFile.__init__() with arg', arg)
    def read(self):
        """stub
        """
        print('called IniFile.read()')
    def write(self):
        """stub
        """
        print('called IniFile.write()')


class MockComparer:
    """stub for main.Comparer
    """
    def __init__(self, *args):
        """stub for initializing main.Comparer object
        """
        self.gui = MockMainWindow()
        self.ini = MockIniFile('inifilename')
        self.showcomp = MockShowComparison()
        left, right, method = args
        self.lhs_path = left
        self.rhs_path = right
        self.comparetype = method
        print('called Comparer.__init__() with args', args)


class MockFilesGui:
    """stub for gui.AskOpenFilesGui
    """
    def __init__(self, *args, **kwargs):
        print('called AskOpenFilesGui.__init__() with args', args, kwargs)
    def add_ask_for_filename(self, *args, **kwargs):
        """stub
        """
        print('called AskOpenFilesGui.add_ask_for_filename() with args', args, kwargs)
    def build_screen(self, *args, **kwargs):
        """stub
        """
        print('called AskOpenFilesGui.build_screen() with args', args, kwargs)


class MockComparisonGui:
    """stub for gui.ShowComparisonGui
    """
    def __init__(self, *args, **kwargs):
        print('called ShowComparisonGui.__init__() with args', args, kwargs)
    def init_tree(self, *args, **kwargs):
        """stub
        """
        print('called ShowComparisonGui.init_tree() with args', args, kwargs)
    def setup_nodata_columns(self, *args, **kwargs):
        """stub
        """
        print('called ShowComparisonGui.setup_nodata_columns() with args', args, kwargs)
    def show_tree(self, *args, **kwargs):
        """stub
        """
        print('called ShowComparisonGui.show_tree() with args', args, kwargs)
    def refresh_tree(self):
        """stub
        """
        print('called ShowComparisonGui.refresh_tree()')


class MockParser:
    """stub for configparser.ConfigParser
    """
    def __init__(self):
        print('called ConfigParser.__init__()')
    def read(self, fname):
        """stub
        """
        print(f'called ConfigParser.read with arg `{fname}`')
    def has_section(self, name):
        """stub
        """
        print(f'called ConfigParser.has_section with arg `{name}`')
        return True
    def options(self, name):
        """stub
        """
        print(f'called ConfigParser.options with arg `{name}`')
        return ['option1', 'option2']
    def get(self, name, value):
        """stub
        """
        print(f'called ConfigParser.get with args (`{name}`, `{value}`)')
        return value
    def add_section(self, name):
        """stub
        """
        print(f'called ConfigParser.add_section with arg `{name}`')
    def set(self, name, value, item):
        """stub
        """
        print(f'called ConfigParser.set with args (`{name}`, `{value}`, `{item}`)')
    def write(self, stream):
        """stub
        """
        # stream is een io.TextIoWrapper object
        outfilename = testee.pathlib.Path(stream.name).name
        print(f'called ConfigParser.write to file with name `{outfilename}`')


def setup_comparer(monkeypatch, capsys):
    """create object to test methods on
    """
    def mock_init(self, *args):
        """stub for initializing main.Comparer object
        """
        self.gui = MockMainWindow()
        self.ini = MockIniFile('inifilename')
        self.showcomp = MockShowComparison()
        left, right, method = args
        self.lhs_path = left
        self.rhs_path = right
        self.comparetype = method
        print('called Comparer.__init__() with args', args)
    monkeypatch.setattr(testee.Comparer, '__init__', mock_init)
    testobj = testee.Comparer('left', 'right', 'method')
    assert capsys.readouterr().out == (
            'called MainWindow.__init__() with args ()\n'
            'called IniFile.__init__() with arg inifilename\n'
            'called ShowComparison.__init__() with args ()\n'
            "called Comparer.__init__() with args ('left', 'right', 'method')\n")
    return testobj


class TestComparer:
    """unittests for main.Comparer
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for main.Comparer object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called Comparer.__init__ with args', args)
        monkeypatch.setattr(testee.Comparer, '__init__', mock_init)
        testobj = testee.Comparer()
        testobj.gui = MockMainWindow()
        testobj.ini = MockIniFile('inifilename')
        testobj.showcomp = MockShowComparison()
        assert capsys.readouterr().out == ('called Comparer.__init__ with args ()\n'
                                           'called MainWindow.__init__() with args ()\n'
                                           'called IniFile.__init__() with arg inifilename\n'
                                           'called ShowComparison.__init__() with args ()\n')
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for Comparer.__init__
        """
        # testobj = testee.Comparer(fileargs, method)
        # assert capsys.readouterr().out == ("")
        def mock_get_paths(*args):
            """stub
            """
            print('called get_input_paths() with args', args)
            return 'left', 'right'
        def mock_determine_comparetype(self, *args):
            """stub
            """
            print('called Comparer.auto_determine_comparetype() with args', args)
        def mock_doit(self):
            """stub
            """
            print('called Comparer.doit()')
        def mock_about(self):
            """stub
            """
            print('called Comparer.about()')
        def mock_open(self):
            """stub
            """
            print('called Comparer.open()')
            return True
        monkeypatch.setattr(testee.gui, 'MainWindow', MockMainWindow)
        monkeypatch.setattr(testee, 'AskOpenFiles', MockAskOpenFiles)
        monkeypatch.setattr(testee, 'ShowComparison', MockShowComparison)
        monkeypatch.setattr(testee, 'IniFile', MockIniFile)
        monkeypatch.setattr(testee, 'get_input_paths', mock_get_paths)
        monkeypatch.setattr(testee.Comparer, 'auto_determine_comparetype', mock_determine_comparetype)
        monkeypatch.setattr(testee.Comparer, 'doit', mock_doit)
        monkeypatch.setattr(testee.Comparer, 'about', mock_about)
        monkeypatch.setattr(testee.Comparer, 'open', mock_open)
        testobj = testee.Comparer([], '')
        assert testobj.apptitel == "Albert's Compare Tool voor Ini Files"
        assert list(testobj.menudict.keys()) == ["&File", "&Help"]
        assert len(testobj.menudict["&File"]) == len(['Open', 'Go', '', 'Quit'])
        # laatste element is de callback, laat zich niet goed vergelijken dus laat maar
        assert testobj.menudict["&File"][0][:-1] == (testee.ID_OPEN, "&Open/kies", "Ctrl+O",
                                                     "Bepaal de te vergelijken (ini) files")
        assert testobj.menudict["&File"][1][:-1] == (testee.ID_DOIT, "&Vergelijk", "F5",
                                                     "Orden en vergelijk de (ini) files")
        assert testobj.menudict["&File"][2] == ()
        assert testobj.menudict["&File"][3][:-1] == (testee.ID_EXIT, "E&xit", "Ctrl+Q",
                                                     "Terminate the program")
        assert len(testobj.menudict["&Help"]) == len(['About', 'Colors'])
        assert testobj.menudict["&Help"][0][:-1] == (testee.ID_ABOUT, "&About", "Ctrl+H",
                                                     "Information about this program")
        assert testobj.menudict["&Help"][1][:-1] == (testee.ID_COLORS, "&Legenda", "F1",
                                                     "What do the colors indicate?")
        assert testobj.data == {}
        assert testobj.comparetype == ''
        assert testobj.lhs_path == 'left'
        assert testobj.rhs_path == 'right'
        assert capsys.readouterr().out == (
              f"called MainWindow.__init__() with args ({testobj},)\n"
              f"called ShowComparison.__init__() with args ({testobj},)\n"
              "called get_input_paths() with args ([],)\n"
              # "called Comparer.auto_determine_comparetype() with args ('left', 'right')\n"
              "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
              "called IniFile.read()\n"
              f"called AskOpenFiles.__init__() with args ({testobj},)\n"
              # "called AskOpenFiles.check_input() with args ('left', 'right', None)\n"
              # "called Comparer.doit()\n"
              # "called MainWindow.go()\n"
              "called MainWindow.go with args ()\n")
        testobj = testee.Comparer(['Left', 'Right'], 'ini')
        assert testobj.data == {}
        assert testobj.comparetype == 'ini'
        assert testobj.lhs_path == 'left'
        assert testobj.rhs_path == 'right'
        assert capsys.readouterr().out == (
              f"called MainWindow.__init__() with args ({testobj},)\n"
              f"called ShowComparison.__init__() with args ({testobj},)\n"
              "called get_input_paths() with args (['Left', 'Right'],)\n"
              "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
              "called IniFile.read()\n"
              f"called AskOpenFiles.__init__() with args ({testobj},)\n"
              # "called AskOpenFiles.check_input() with args ('left', 'right', 'ini')\n"
              # "called Comparer.doit()\n"
              # "called MainWindow.go()\n")
              "called MainWindow.go with args ()\n")
        monkeypatch.setattr(MockAskOpenFiles, 'check_input', lambda *x: 'melding')
        testobj = testee.Comparer(['Left', 'Right'], 'ini')
        assert capsys.readouterr().out == (
              f"called MainWindow.__init__() with args ({testobj},)\n"
              f"called ShowComparison.__init__() with args ({testobj},)\n"
              "called get_input_paths() with args (['Left', 'Right'],)\n"
              "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
              "called IniFile.read()\n"
              f"called AskOpenFiles.__init__() with args ({testobj},)\n"
              # "called MainWindow.meld_input_fout() with arg melding\n"
              # "called MainWindow.go()\n")
              "called MainWindow.go with args ()\n")
        monkeypatch.setattr(testee, 'get_input_paths', lambda *x: ['', ''])
        testobj = testee.Comparer([], '')
        assert capsys.readouterr().out == (
              f"called MainWindow.__init__() with args ({testobj},)\n"
              f"called ShowComparison.__init__() with args ({testobj},)\n"
              # "called Comparer.auto_determine_comparetype() with args ('', '')\n"
              "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
              "called IniFile.read()\n"
              f"called AskOpenFiles.__init__() with args ({testobj},)\n"
              "called Comparer.about()\n"
              # "called Comparer.open()\n"
              # "called Comparer.doit()\n"
              # "called MainWindow.go()\n")
              "called MainWindow.go with args ()\n")
        monkeypatch.setattr(testee.Comparer, 'open', lambda *x: False)
        testobj = testee.Comparer([], '')
        assert capsys.readouterr().out == (
              f"called MainWindow.__init__() with args ({testobj},)\n"
              f"called ShowComparison.__init__() with args ({testobj},)\n"
              # "called Comparer.auto_determine_comparetype() with args ('', '')\n"
              "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
              "called IniFile.read()\n"
              f"called AskOpenFiles.__init__() with args ({testobj},)\n"
              "called Comparer.about()\n"
              # "called MainWindow.go()\n")
              "called MainWindow.go with args ()\n")

    def test_open(self, monkeypatch, capsys):
        """unittest for Comparer.open
        """
        def mock_show_dialog(*args):
            """stub
            """
            print('called gui.show_dialog() with args', args)
            return False
        def mock_show_dialog_2(*args):
            """stub
            """
            print('called gui.show_dialog() with args', args)
            return True
        def mock_doit(self):
            "stub"
            print('called Comparer.doit')
        monkeypatch.setattr(testee.Comparer, 'doit', mock_doit)
        monkeypatch.setattr(testee.gui, 'show_dialog', mock_show_dialog)
        # testobj = setup_comparer(monkeypatch, capsys)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj_get_input = types.SimpleNamespace(gui='get_input_gui')
        testobj.get_input = testobj_get_input
        testobj.open()
        assert capsys.readouterr().out == (
                f"called gui.show_dialog() with args ({testobj_get_input}, 'get_input_gui')\n")
        monkeypatch.setattr(testee.gui, 'show_dialog', mock_show_dialog_2)
        testobj.open()
        assert capsys.readouterr().out == (
                f"called gui.show_dialog() with args ({testobj_get_input}, 'get_input_gui')\n"
                "called Comparer.doit\n")

    def test_auto_determine_comparetype(self, monkeypatch, capsys):
        """unittest for Comparer.auto_determine_comparetype
        """
        monkeypatch.setattr(testee, 'comparetypes', ['x'])
        # testobj = setup_comparer(monkeypatch, capsys)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.auto_determine_comparetype('test1', 'test2') == ''
        assert testobj.auto_determine_comparetype('test1.x', 'test2.y') == ''
        assert testobj.auto_determine_comparetype('test1.x', 'test2.x') == 'x'

    def test_doit(self, monkeypatch, capsys):
        """unittest for Comparer.doit
        """
        def mock_do_compare(*args):
            """stub
            """
            return True, ['data', 'more data']
        def mock_do_compare_notok(*args):
            """stub
            """
            return False, ['message', 'why']
        def mock_do_compare_nodata(*args):
            """stub
            """
            return True, []
        # testobj = setup_comparer(monkeypatch, capsys)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lhs_path = ''
        testobj.rhs_path = ''
        testobj.comparetype = ''
        testobj.doit()
        assert capsys.readouterr().out == ""
        testobj.comparetype = 'x'
        monkeypatch.setattr(testee, 'do_compare', mock_do_compare_notok)
        testobj.doit()
        assert capsys.readouterr().out == (
                "called MainWindow.meld_vergelijking_fout() with args ('message', 'why')\n")
        monkeypatch.setattr(testee, 'do_compare', mock_do_compare_nodata)
        testobj.doit()
        assert capsys.readouterr().out == ("called MainWindow.meld_vergelijking_fout()"
                                           " with args ('Vergelijking mislukt', [])\n")
        testobj.ini.mru_left = []
        testobj.ini.mru_right = []
        monkeypatch.setattr(testee, 'do_compare', mock_do_compare)
        testobj.doit()
        assert testobj.data == ['data', 'more data']
        assert testobj.ini.mru_left == [testobj.lhs_path]
        assert testobj.ini.mru_right == [testobj.rhs_path]
        assert capsys.readouterr().out == ('called IniFile.write()\ncalled ShowComparison.refresh()\n')
        monkeypatch.setattr(testee, 'do_compare', mock_do_compare)
        testobj.doit()
        assert testobj.data == ['data', 'more data']
        assert testobj.ini.mru_left == [testobj.lhs_path]
        assert testobj.ini.mru_right == [testobj.rhs_path]
        assert capsys.readouterr().out == ('called IniFile.write()\ncalled ShowComparison.refresh()\n')

    def test_about(self, monkeypatch, capsys):
        """unittest for Comparer.about
        """
        def mock_meld(*args):
            """stub
            """
            print('called MainWindow.meld with args', args)
        monkeypatch.setattr(testee, 'abouttext', 'yfiyyuu9')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = types.SimpleNamespace(meld=mock_meld)
        testobj.about()
        assert capsys.readouterr().out == "called MainWindow.meld with args ('yfiyyuu9',)\n"

    def test_legend(self, monkeypatch, capsys):
        """unittest for Comparer.legend
        """
        def mock_meld(*args):
            """stub
            """
            print('called MainWindow.meld with args', args)
        monkeypatch.setattr(testee, 'colors_text', 'yfiyyuu9')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = types.SimpleNamespace(meld=mock_meld)
        testobj.legend()
        assert capsys.readouterr().out == "called MainWindow.meld with args ('yfiyyuu9',)\n"

    def test_exit(self, monkeypatch, capsys):
        """unittest for Comparer.exit
        """
        def mock_exit(*args):
            """stub
            """
            print('called MainWindow.exit')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.gui = types.SimpleNamespace(exit=mock_exit)
        testobj.exit()
        assert capsys.readouterr().out == "called MainWindow.exit\n"


class TestAskOpenFiles:
    """unittests for main.AskOpenFiles
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for main.AskOpenFiles object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called AskOpenFiles.__init__ with args', args)
        monkeypatch.setattr(testee.AskOpenFiles, '__init__', mock_init)
        testobj = testee.AskOpenFiles()
        assert capsys.readouterr().out == 'called AskOpenFiles.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for AskOpenFiles.__init__
        """
        class MockGui:
            "stub(s)"
            def __init__(self, *args, **kwargs):
                print('called AskOpenFilesGui.__init__ with args', args, kwargs)
            def add_ask_for_filename(self, *args, **kwargs):
                print('called AskOpenFilesGui.add_ask_for_filename with args', args, kwargs)
                return f"{kwargs['path']} selector"
            def create_fileselector_grid(self, *args):
                print('called AskOpenFilesGui.create_fileselector_grid with args', args)
            def build_typeselector(self, *args):
                print('called AskOpenFilesGui.build_typeselector with args', args)
            def update_typeselector(self):
                print('called AskOpenFilesGui.update_typeselector')
            def add_buttons(self, *args):
                print('called AskOpenFilesGui.add_buttons with args', args)
        monkeypatch.setattr(testee, 'Comparer', MockComparer)
        testobjparent = testee.Comparer('left', 'right', 'method')
        testobjparent.apptitel = 'xxx'
        testobjparent.ini = types.SimpleNamespace(mru_left=['left'], mru_right=['right'])
        monkeypatch.setattr(testee.gui, 'AskOpenFilesGui', MockGui)
        testobj = testee.AskOpenFiles(testobjparent)
        ctypes = dict(testee.comparetypes)
        ctypes[''] = ('Autodetect',)
        assert capsys.readouterr().out == (
                "called MainWindow.__init__() with args ()\n"
                "called IniFile.__init__() with arg inifilename\n"
                "called ShowComparison.__init__() with args ()\n"
                "called Comparer.__init__() with args ('left', 'right', 'method')\n"
                f"called AskOpenFilesGui.__init__ with args ({testobj},)"
                " {'size': (400, 200), 'title': 'xxx'}\n"
                "called AskOpenFilesGui.add_ask_for_filename with args () {'size': (450, -1),"
                " 'label': 'Vergelijk:', 'browse': 'Zoek', 'path': 'linker',"
                " 'tooltip': 'Geef hier de naam van het {} te vergelijken ini file of kies er een"
                " uit een lijst met recent gebruikte', 'title': 'Selecteer het {} ini file',"
                " 'history': ['left'], 'value': 'left'}\n"
                "called AskOpenFilesGui.add_ask_for_filename with args () {'size': (450, -1),"
                " 'label': 'Met:', 'browse': 'Zoek', 'path': 'rechter',"
                " 'tooltip': 'Geef hier de naam van het {} te vergelijken ini file of kies er een"
                " uit een lijst met recent gebruikte', 'title': 'Selecteer het {} ini file',"
                " 'history': ['right'], 'value': 'right'}\n"
                "called AskOpenFilesGui.create_fileselector_grid with args"
                " ([('Vergelijk:', 'linker selector'), ('Met:', 'rechter selector')],)\n"
                "called AskOpenFilesGui.build_typeselector with args"
                f" ('Soort vergelijking:', {ctypes})\n"
                "called AskOpenFilesGui.update_typeselector\n"
                "called AskOpenFilesGui.add_buttons with args"
                " (('&Gebruiken', 'Klik hier om de vergelijking uit te voeren'),"
                " ('&Afbreken', 'Klik hier om zonder wijzigingen terug te gaan naar het"
                " hoofdscherm'))\n")

    def test_check_input(self, monkeypatch, capsys, tmp_path):
        """unittest for AskOpenFiles.check_input
        """
        def mock_get(arg):
            print('called AskOpenFileGui.get_fbb_result with arg', arg)
            return ''
        def mock_get_2(arg):
            print('called AskOpenFileGui.get_fbb_result with arg', arg)
            return arg if arg == 'left' else ''
        def mock_get_3(arg):
            print('called AskOpenFileGui.get_fbb_result with arg', arg)
            return tmp_path / arg
        def mock_get_4(arg):
            print('called AskOpenFileGui.get_fbb_result with arg', arg)
            return tmp_path / 'xxx'
        def mock_get_rb(arg):
            print('called AskOpenFilesGui.get_radiobox_value with arg', arg)
            return False
        def mock_get_rb_2(arg):
            print('called AskOpenFilesGui.get_radiobox_value with arg', arg)
            return arg == 'rb2'
        def mock_determine(*args):
            print('called Comparer.auto_determine_comparetype with args', args)
            return ''
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.lhs_file = 'left'
        testobj.rhs_file = 'right'
        testobj.gui = types.SimpleNamespace(get_fbb_result=mock_get, get_radiobox_value=mock_get_rb)
        testobj.parent = types.SimpleNamespace(auto_determine_comparetype=mock_determine)
        testobj.options = []
        assert testobj.check_input() == 'Geen linkerbestand opgegeven'
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called Comparer.auto_determine_comparetype with args ('', '')\n")
        testobj.gui.get_fbb_result = mock_get_2
        assert testobj.check_input() == 'Geen rechterbestand opgegeven'
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called Comparer.auto_determine_comparetype with args ('left', '')\n")
        testobj.gui.get_fbb_result = mock_get_3
        assert testobj.check_input() == f'Bestand {tmp_path}/left kon niet gevonden/geopend worden'
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called Comparer.auto_determine_comparetype with args"
                f" ({tmp_path / 'left'!r}, {tmp_path / 'right'!r})\n")
        (tmp_path / 'left').touch()
        assert testobj.check_input() == f'Bestand {tmp_path}/right kon niet gevonden/geopend worden'
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called Comparer.auto_determine_comparetype with args"
                f" ({tmp_path / 'left'!r}, {tmp_path / 'right'!r})\n")
        (tmp_path / 'right').touch()
        assert testobj.check_input() == (
                'Geen vergelijkingsmethode gekozen en niet automatisch te bepalen')
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called Comparer.auto_determine_comparetype with args"
                f" ({tmp_path / 'left'!r}, {tmp_path / 'right'!r})\n")
        testobj.options = [('rb0', ''), ('rb1', 'x'), ('rb2', 'y')]
        monkeypatch.setattr(testee, 'comparetypes', {'z': {}})
        assert testobj.check_input() == (
                'Geen vergelijkingsmethode gekozen en niet automatisch te bepalen')
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called AskOpenFilesGui.get_radiobox_value with arg rb1\n"
                "called AskOpenFilesGui.get_radiobox_value with arg rb2\n"
                "called Comparer.auto_determine_comparetype with args"
                f" ({tmp_path / 'left'!r}, {tmp_path / 'right'!r})\n")
        monkeypatch.setattr(testee, 'comparetypes', {'y': {}})
        testobj.gui.get_radiobox_value = mock_get_rb_2
        assert testobj.check_input() == ''
        assert testobj.parent.lhs_path == tmp_path / 'left'
        assert testobj.parent.rhs_path == tmp_path / 'right'
        assert testobj.parent.comparetype == 'y'
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called AskOpenFilesGui.get_radiobox_value with arg rb1\n"
                "called AskOpenFilesGui.get_radiobox_value with arg rb2\n")
        (tmp_path / 'xxx').touch()
        testobj.gui.get_fbb_result = mock_get_4
        assert testobj.check_input() == "Bestandsnamen zijn gelijk"
        assert capsys.readouterr().out == (
                "called AskOpenFileGui.get_fbb_result with arg left\n"
                "called AskOpenFileGui.get_fbb_result with arg right\n"
                "called AskOpenFilesGui.get_radiobox_value with arg rb1\n"
                "called AskOpenFilesGui.get_radiobox_value with arg rb2\n")


class TestShowComparison:
    """unittests for main.ShowComparison
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for main.ShowComparison object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called ShowComparison.__init__ with args', args)
        monkeypatch.setattr(testee.ShowComparison, '__init__', mock_init)
        testobj = testee.ShowComparison()
        assert capsys.readouterr().out == 'called ShowComparison.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for ShowComparison.__init__
        """
        def mock_refresh(self):
            """stub
            """
            print('called ShowComparison.refresh()')
        monkeypatch.setattr(testee, 'Comparer', MockComparer)
        testobjparent = testee.Comparer('left', 'right', 'method')
        testobjparent.gui = 'ComparerGui'
        monkeypatch.setattr(testee.gui, 'ShowComparisonGui', MockComparisonGui)
        assert capsys.readouterr().out == (
              'called MainWindow.__init__() with args ()\n'
              'called IniFile.__init__() with arg inifilename\n'
              'called ShowComparison.__init__() with args ()\n'
              "called Comparer.__init__() with args ('left', 'right', 'method')\n")
        testobjparent.data = []
        testobj = testee.ShowComparison(testobjparent)
        assert testobj.parent == testobjparent
        # assert testobj.gui == testobjparent.gui
        assert capsys.readouterr().out == (
              "called ShowComparisonGui.__init__() with args ('ComparerGui',) {}\n"
              "called ShowComparisonGui.init_tree() with args ('Document structure',"
              " 'value in `lefthand-side` file', 'value in `righthand-side` file') {}\n"
              "called ShowComparisonGui.setup_nodata_columns() with args ('geen bestanden geladen',"
              " 'niks om te laten zien', 'hier ook niet') {}\n"
              'called ShowComparisonGui.show_tree() with args () {}\n')
        testobjparent.data = ['we have data']
        monkeypatch.setattr(testee.ShowComparison, 'refresh', mock_refresh)
        testobj = testee.ShowComparison(testobjparent)
        assert testobj.parent == testobjparent
        # assert testobj.gui == testobjparent.gui
        assert capsys.readouterr().out == (
              "called ShowComparisonGui.__init__() with args ('ComparerGui',) {}\n"
              "called ShowComparisonGui.init_tree() with args ('Document structure',"
              " 'value in `lefthand-side` file', 'value in `righthand-side` file') {}\n"
              'called ShowComparison.refresh()\n'
              'called ShowComparisonGui.show_tree() with args () {}\n')

    def test_refresh(self, monkeypatch, capsys):
        """unittest for ShowComparison.refresh
        """
        def mock_refresh(self, *args):
            """stub
            """
            print('called comparetype.refresh_compare() with args', args)
        monkeypatch.setattr(testee, 'comparetypes', {'x': ('y', 'z', mock_refresh)})
        # monkeypatch.setattr(testee.ShowComparison, '__init__', mock_init)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.parent = types.SimpleNamespace(comparetype='x')
        testobj.gui = MockComparisonGui()
        assert capsys.readouterr().out == "called ShowComparisonGui.__init__() with args () {}\n"
        testobj.refresh()
        assert capsys.readouterr().out == ('called comparetype.refresh_compare() with args ()\n'
                                           'called ShowComparisonGui.refresh_tree()\n')


class TestIniFile:
    """unittests for main.IniFile
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for main.IniFile object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called IniFile.__init__ with args', args)
        monkeypatch.setattr(testee.IniFile, '__init__', mock_init)
        testobj = testee.IniFile()
        assert capsys.readouterr().out == 'called IniFile.__init__ with args ()\n'
        return testobj

    def test_init(self):
        """unittest for IniFile.__init__
        """
        testobj = testee.IniFile('testfile')
        assert testobj.fname == 'testfile'

    def test_read(self, monkeypatch, capsys):
        """unittest for IniFile.read
        """
        monkeypatch.setattr(testee, 'ConfigParser', MockParser)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.fname = 'testfile'
        testobj.read()
        assert testobj.mru_left == ['file1', 'file2']
        assert testobj.mru_right == ['file1', 'file2']
        assert testobj.horizontal
        assert capsys.readouterr().out == (
                'called ConfigParser.__init__()\n'
                'called ConfigParser.read with arg `testfile`\n'
                'called ConfigParser.has_section with arg `leftpane`\n'
                'called ConfigParser.options with arg `leftpane`\n'
                'called ConfigParser.get with args (`leftpane`, `file1`)\n'
                'called ConfigParser.get with args (`leftpane`, `file2`)\n'
                'called ConfigParser.has_section with arg `rightpane`\n'
                'called ConfigParser.options with arg `rightpane`\n'
                'called ConfigParser.get with args (`rightpane`, `file1`)\n'
                'called ConfigParser.get with args (`rightpane`, `file2`)\n')
        monkeypatch.setattr(MockParser, 'has_section', lambda *x: False)
        testobj.read()
        assert testobj.mru_left == []
        assert testobj.mru_right == []
        assert testobj.horizontal
        assert capsys.readouterr().out == ('called ConfigParser.__init__()\n'
                                           'called ConfigParser.read with arg `testfile`\n')

    def test_write(self, monkeypatch, capsys):
        """unittest for IniFile.write
        """
        monkeypatch.setattr(testee, 'ConfigParser', MockParser)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.fname = 'testfile'
        testobj.mru_left = []
        testobj.mru_right = []
        testobj.write()
        assert capsys.readouterr().out == ('called ConfigParser.__init__()\n'
                                           'called ConfigParser.write to file with name `testfile`\n')
        testobj.mru_left = ['file1', 'file2']
        testobj.mru_right = ['file3', 'file4']
        testobj.write()
        assert capsys.readouterr().out == (
                'called ConfigParser.__init__()\n'
                'called ConfigParser.add_section with arg `leftpane`\n'
                'called ConfigParser.set with args (`leftpane`, `file1`, `file1`)\n'
                'called ConfigParser.set with args (`leftpane`, `file2`, `file2`)\n'
                'called ConfigParser.add_section with arg `rightpane`\n'
                'called ConfigParser.set with args (`rightpane`, `file1`, `file3`)\n'
                'called ConfigParser.set with args (`rightpane`, `file2`, `file4`)\n'
                'called ConfigParser.write to file with name `testfile`\n')
