"""unittests for ./src/main.py
"""
import types
from src import main

def test_determine_comparetype(monkeypatch):
    """unittest for main.determine_comparetype
    """
    monkeypatch.setattr(main, 'comparetypes', ['x'])
    assert main.auto_determine_comparetype('test1', 'test2') == ''
    assert main.auto_determine_comparetype('test1.x', 'test2.y') == ''
    assert main.auto_determine_comparetype('test1.x', 'test2.x') == 'x'


def test_get_input_paths(capsys):
    """unittest for main.get_input_paths
    """
    assert main.get_input_paths([]) == ('', '')
    assert capsys.readouterr().out == ''
    assert main.get_input_paths(['left'])
    assert capsys.readouterr().out == ''
    assert main.get_input_paths(['left', 'right'])
    assert capsys.readouterr().out == ''
    assert main.get_input_paths(['left', 'right', ''])
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
    def mock_compare_parse(left, right):
        """stub
        """
        print(f'called compare_method with args `{left}` and `{right}`')
        raise main.ParseError('yyyy')
    monkeypatch.setattr(main, 'comparetypes', {'x': ('', mock_compare, '')})
    assert main.do_compare('left', 'right', 'x') == (True, ['compare output'])
    assert capsys.readouterr().out == 'called compare_method with args `left` and `right`\n'
    monkeypatch.setattr(main, 'comparetypes', {'x': ('', mock_compare_miss, '')})
    ok, traceback = main.do_compare('left', 'right', 'x')
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
    def go(self):
        """stub
        """
        print('called MainWindow.go()')
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

def test_comparer_init(monkeypatch, capsys):
    """unittest for main.Comparer.init
    """
    def mock_get_paths(*args):
        """stub
        """
        print('called get_input_paths() with args', args)
        return 'left', 'right'
    def mock_determine_comparetype(*args):
        """stub
        """
        print('called auto_determine_comparetype() with args', args)
    def mock_doit(self):
        """stub
        """
        print('called comparer.doit()')
    def mock_about(self):
        """stub
        """
        print('called comparer.about()')
    def mock_open(self):
        """stub
        """
        print('called comparer.open()')
        return True
    def mock_meld_fout(self, *args):
        """stub
        """
        print('called gui.meld_input_fout() with args', args)
    monkeypatch.setattr(main.gui, 'MainWindow', MockMainWindow)
    monkeypatch.setattr(main, 'AskOpenFiles', MockAskOpenFiles)
    monkeypatch.setattr(main, 'ShowComparison', MockShowComparison)
    monkeypatch.setattr(main, 'IniFile', MockIniFile)
    monkeypatch.setattr(main, 'get_input_paths', mock_get_paths)
    monkeypatch.setattr(main, 'auto_determine_comparetype', mock_determine_comparetype)
    monkeypatch.setattr(main.Comparer, 'doit', mock_doit)
    monkeypatch.setattr(main.Comparer, 'about', mock_about)
    monkeypatch.setattr(main.Comparer, 'open', mock_open)
    testobj = main.Comparer([], '')
    assert testobj.apptitel == "Albert's Compare Tool voor Ini Files"
    assert list(testobj.menudict.keys()) == ["&File", "&Help"]
    assert len(testobj.menudict["&File"]) == len(['Open', 'Go', '', 'Quit'])
    # laatste element is de callback, laat zich niet goed vergelijken dus laat maar
    assert testobj.menudict["&File"][0][:-1] == (main.ID_OPEN, "&Open/kies", "Ctrl+O",
                                                 "Bepaal de te vergelijken (ini) files")
    assert testobj.menudict["&File"][1][:-1] == (main.ID_DOIT, "&Vergelijk", "F5",
                                                 "Orden en vergelijk de (ini) files")
    assert testobj.menudict["&File"][2] == ()
    assert testobj.menudict["&File"][3][:-1] == (main.ID_EXIT, "E&xit", "Ctrl+Q",
                                                 "Terminate the program")
    assert len(testobj.menudict["&Help"]) == len(['About', 'Colors'])
    assert testobj.menudict["&Help"][0][:-1] == (main.ID_ABOUT, "&About", "Ctrl+H",
                                                 "Information about this program")
    assert testobj.menudict["&Help"][1][:-1] == (main.ID_COLORS, "&Legenda", "F1",
                                                 "What do the colors indicate?")
    assert testobj.data == {}
    assert testobj.selected_option == ''
    assert testobj.comparetype is None
    assert testobj.lhs_path == 'left'
    assert testobj.rhs_path == 'right'
    assert capsys.readouterr().out == (
          f"called MainWindow.__init__() with args ({testobj},)\n"
          f"called ShowComparison.__init__() with args ({testobj},)\n"
          "called get_input_paths() with args ([],)\n"
          "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
          "called IniFile.read()\n"
          f"called AskOpenFiles.__init__() with args ({testobj},)\n"
          "called auto_determine_comparetype() with args ('left', 'right')\n"
          "called AskOpenFiles.check_input() with args ('left', 'right', None)\n"
          "called comparer.doit()\n"
          "called MainWindow.go()\n")
    testobj = main.Comparer(['Left', 'Right'], 'ini')
    assert testobj.data == {}
    assert testobj.selected_option == ''
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
          "called AskOpenFiles.check_input() with args ('left', 'right', 'ini')\n"
          "called comparer.doit()\n"
          "called MainWindow.go()\n")
    monkeypatch.setattr(MockAskOpenFiles, 'check_input', lambda *x: 'melding')
    testobj = main.Comparer(['Left', 'Right'], 'ini')
    assert capsys.readouterr().out == (
          f"called MainWindow.__init__() with args ({testobj},)\n"
          f"called ShowComparison.__init__() with args ({testobj},)\n"
          "called get_input_paths() with args (['Left', 'Right'],)\n"
          "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
          "called IniFile.read()\n"
          f"called AskOpenFiles.__init__() with args ({testobj},)\n"
          "called MainWindow.meld_input_fout() with arg melding\n"
          "called MainWindow.go()\n")
    monkeypatch.setattr(main, 'get_input_paths', lambda *x: ['', ''])
    testobj = main.Comparer([], '')
    assert capsys.readouterr().out == (
          f"called MainWindow.__init__() with args ({testobj},)\n"
          f"called ShowComparison.__init__() with args ({testobj},)\n"
          "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
          "called IniFile.read()\n"
          f"called AskOpenFiles.__init__() with args ({testobj},)\n"
          "called comparer.about()\n"
          "called comparer.open()\n"
          "called comparer.doit()\n"
          "called MainWindow.go()\n")
    monkeypatch.setattr(main.Comparer, 'open', lambda *x: False)
    testobj = main.Comparer([], '')
    assert capsys.readouterr().out == (
          f"called MainWindow.__init__() with args ({testobj},)\n"
          f"called ShowComparison.__init__() with args ({testobj},)\n"
          "called IniFile.__init__() with arg /home/albert/projects/compare-tool/actif.ini\n"
          "called IniFile.read()\n"
          f"called AskOpenFiles.__init__() with args ({testobj},)\n"
          "called comparer.about()\n"
          "called MainWindow.go()\n")

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

def test_comparer_open(monkeypatch, capsys):
    """unittest for main.Comparer.open
    """
    def mock_show_dialog(*args):
        """stub
        """
        print('called gui.show_dialog() with args', args)
        return True
    monkeypatch.setattr(main.Comparer, '__init__', mock_init)
    monkeypatch.setattr(main.gui, 'show_dialog', mock_show_dialog)
    testobj = main.Comparer('left', 'right', 'method')
    testobj_get_input = types.SimpleNamespace(gui='get_input_gui')
    testobj.get_input = testobj_get_input
    assert testobj.open()
    assert capsys.readouterr().out == (
            'called MainWindow.__init__() with args ()\n'
            'called IniFile.__init__() with arg inifilename\n'
            'called ShowComparison.__init__() with args ()\n'
            "called Comparer.__init__() with args ('left', 'right', 'method')\n"
            f"called gui.show_dialog() with args ({testobj_get_input}, 'get_input_gui')\n")

def test_comparer_doit(monkeypatch, capsys):
    """unittest for main.Comparer.doit
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
    monkeypatch.setattr(main.Comparer, '__init__', mock_init)
    testobj = main.Comparer('left', 'right', 'method')
    monkeypatch.setattr(main, 'do_compare', mock_do_compare_notok)
    testobj.doit()
    assert capsys.readouterr().out == (
            'called MainWindow.__init__() with args ()\n'
            'called IniFile.__init__() with arg inifilename\n'
            'called ShowComparison.__init__() with args ()\n'
            "called Comparer.__init__() with args ('left', 'right', 'method')\n"
            "called MainWindow.meld_vergelijking_fout() with args ('message', 'why')\n")
    monkeypatch.setattr(main, 'do_compare', mock_do_compare_nodata)
    testobj.doit()
    assert capsys.readouterr().out == ("called MainWindow.meld_vergelijking_fout()"
                                       " with args ('Vergelijking mislukt', [])\n")
    testobj.ini.mru_left = [testobj.lhs_path]
    testobj.ini.mru_right = [testobj.rhs_path]
    monkeypatch.setattr(main, 'do_compare', mock_do_compare)
    testobj.doit()
    assert testobj.data == ['data', 'more data']
    assert testobj.selected_option == 'data'
    assert capsys.readouterr().out == ('called IniFile.write()\ncalled ShowComparison.refresh()\n')

def test_comparer_about(monkeypatch, capsys):
    """unittest for main.Comparer.about
    """
    monkeypatch.setattr(main.Comparer, '__init__', mock_init)
    testobj = main.Comparer('left', 'right', 'method')
    testobj.about()
    assert capsys.readouterr().out == (
            'called MainWindow.__init__() with args ()\n'
            'called IniFile.__init__() with arg inifilename\n'
            'called ShowComparison.__init__() with args ()\n'
            "called Comparer.__init__() with args ('left', 'right', 'method')\n"
            "called MainWindow.meld() with args ('Met dit programma kun je twee (ini) files"
            " met elkaar vergelijken,\\nmaakt niet uit hoe door elkaar de secties en entries"
            " ook zitten.\\n\\nHet is ook bruikbaar voor XML en HTML bestanden.',)\n")

def test_comparer_legend(monkeypatch, capsys):
    """unittest for main.Comparer.legend
    """
    monkeypatch.setattr(main.Comparer, '__init__', mock_init)
    testobj = main.Comparer('left', 'right', 'method')
    testobj.legend()
    assert capsys.readouterr().out == (
            'called MainWindow.__init__() with args ()\n'
            'called IniFile.__init__() with arg inifilename\n'
            'called ShowComparison.__init__() with args ()\n'
            "called Comparer.__init__() with args ('left', 'right', 'method')\n"
            "called MainWindow.meld() with args ('Rood: aan beide kanten aanwezig, verschillend\\n"
            "Groen: alleen aanwezig in linkerfile\\nBlauw: alleen aanwezig in rechterfile',)\n")

def test_comparer_exit(monkeypatch, capsys):
    """unittest for main.Comparer.exit
    """
    monkeypatch.setattr(main.Comparer, '__init__', mock_init)
    testobj = main.Comparer('left', 'right', 'method')
    testobj.exit()
    assert capsys.readouterr().out == (
            'called MainWindow.__init__() with args ()\n'
            'called IniFile.__init__() with arg inifilename\n'
            'called ShowComparison.__init__() with args ()\n'
            "called Comparer.__init__() with args ('left', 'right', 'method')\n"
            "called MainWindow.exit()\n")

class MockComparer:
    """stub for main.Comparer
    """
    def __init__(self, *args):
        mock_init(self, *args)

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

def test_askopenfiles_init(monkeypatch, capsys):
    """unittest for main.AskOpenFiles.init
    """
    monkeypatch.setattr(main, 'Comparer', MockComparer)
    testobjparent = main.Comparer('left', 'right', 'method')
    testobjparent.ini = types.SimpleNamespace(mru_left=['left'], mru_right=['right'])
    monkeypatch.setattr(main.gui, 'AskOpenFilesGui', MockFilesGui)
    testobj = main.AskOpenFiles(testobjparent)
    assert capsys.readouterr().out == (
            "called MainWindow.__init__() with args ()\n"
            "called IniFile.__init__() with arg inifilename\n"
            "called ShowComparison.__init__() with args ()\n"
            "called Comparer.__init__() with args ('left', 'right', 'method')\n"
            f"called AskOpenFilesGui.__init__() with args ({testobj},) {{'size': (400, 200)}}\n"
            "called AskOpenFilesGui.add_ask_for_filename() with args () {'size': (450, -1),"
            " 'label': 'Vergelijk:', 'browse': 'Zoek', 'path': 'linker',"
            " 'tooltip': 'Geef hier de naam van het {} te vergelijken ini file of kies er een"
            " uit een lijst met recent gebruikte', 'title': 'Selecteer het {} ini file',"
            " 'history': ['left'], 'value': 'left'}\n"
            "called AskOpenFilesGui.add_ask_for_filename() with args () {'size': (450, -1),"
            " 'label': 'Met:', 'browse': 'Zoek', 'path': 'rechter',"
            " 'tooltip': 'Geef hier de naam van het {} te vergelijken ini file of kies er een"
            " uit een lijst met recent gebruikte', 'title': 'Selecteer het {} ini file',"
            " 'history': ['right'], 'value': 'right'}\n"
            "called AskOpenFilesGui.build_screen() with args (None, None,"
            f" 'Soort vergelijking:', {main.comparetypes})"
            " {'oktext': ('&Gebruiken', 'Klik hier om de vergelijking uit te voeren'),"
            " 'canceltext': ('&Afbreken', 'Klik hier om zonder wijzigingen terug te gaan naar het"
            " hoofdscherm')}\n")

def test_askopenfiles_check(monkeypatch, capsys):
    """unittest for main.AskOpenFiles.check
    """
    def mock_init(self, *args):
        """stub
        """
        print('called AskOpenFiles.__init__() with args', args)
    counter = 0
    def mock_exists(*args):
        """stub
        """
        nonlocal counter
        counter += 1
        if counter == 1:
            return True
        return False
    monkeypatch.setattr(main.AskOpenFiles, '__init__', mock_init)
    testobj = main.AskOpenFiles('parent')
    assert capsys.readouterr().out == "called AskOpenFiles.__init__() with args ('parent',)\n"
    assert testobj.check_input('', '', '') == 'Geen linkerbestand opgegeven'
    assert testobj.check_input('x', '', '') == 'Geen rechterbestand opgegeven'
    monkeypatch.setattr(main.pathlib.Path, 'exists', lambda *x: False)
    assert testobj.check_input('x', 'y', '') == 'Bestand x kon niet gevonden/geopend worden'
    monkeypatch.setattr(main.pathlib.Path, 'exists', mock_exists)
    assert testobj.check_input('x', 'y', '') == 'Bestand y kon niet gevonden/geopend worden'
    monkeypatch.setattr(main.pathlib.Path, 'exists', lambda *x: True)
    assert testobj.check_input('x', 'x', '') == "Bestandsnamen zijn gelijk"
    assert testobj.check_input('x', 'y', '') == 'Geen vergelijkingsmethode gekozen'
    assert testobj.check_input('x', 'y', 'z') == 'Geen vergelijkingsmethode gekozen'
    monkeypatch.setattr(main, 'comparetypes', {'z': {}})
    assert testobj.check_input('x', 'y', 'z') == ''

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
    def finish_init(self, *args, **kwargs):
        """stub
        """
        print('called ShowComparisonGui.finish_init() with args', args, kwargs)
    def refresh_tree(self):
        """stub
        """
        print('called ShowComparisonGui.refresh_tree()')

def test_showcomparison_init(monkeypatch, capsys):
    """unittest for main.ShowComparison.init
    """
    def mock_refresh(self):
        """stub
        """
        print('called ShowComparison.refresh()')
    monkeypatch.setattr(main, 'Comparer', MockComparer)
    testobjparent = main.Comparer('left', 'right', 'method')
    testobjparent.gui = 'ComparerGui'
    monkeypatch.setattr(main.gui, 'ShowComparisonGui', MockComparisonGui)
    assert capsys.readouterr().out == (
          'called MainWindow.__init__() with args ()\n'
          'called IniFile.__init__() with arg inifilename\n'
          'called ShowComparison.__init__() with args ()\n'
          "called Comparer.__init__() with args ('left', 'right', 'method')\n")
    testobjparent.data = []
    testobj = main.ShowComparison(testobjparent)
    assert testobj.parent == testobjparent
    # assert testobj.gui == testobjparent.gui
    assert capsys.readouterr().out == (
          "called ShowComparisonGui.__init__() with args ('ComparerGui',) {}\n"
          "called ShowComparisonGui.init_tree() with args ('Document structure',"
          " 'value in `lefthand-side` file', 'value in `righthand-side` file') {}\n"
          "called ShowComparisonGui.setup_nodata_columns() with args ('geen bestanden geladen',"
          " 'niks om te laten zien', 'hier ook niet') {}\n"
          'called ShowComparisonGui.finish_init() with args () {}\n')
    testobjparent.data = ['we have data']
    monkeypatch.setattr(main.ShowComparison, 'refresh', mock_refresh)
    testobj = main.ShowComparison(testobjparent)
    assert testobj.parent == testobjparent
    # assert testobj.gui == testobjparent.gui
    assert capsys.readouterr().out == (
          "called ShowComparisonGui.__init__() with args ('ComparerGui',) {}\n"
          "called ShowComparisonGui.init_tree() with args ('Document structure',"
          " 'value in `lefthand-side` file', 'value in `righthand-side` file') {}\n"
          'called ShowComparison.refresh()\n'
          'called ShowComparisonGui.finish_init() with args () {}\n')

def test_showcomparison_refresh(monkeypatch, capsys):
    """unittest for main.ShowComparison.refresh
    """
    def mock_init(self, parent):
        """stub
        """
        print('called ShowComparison.__init__() with args', parent)
        self.parent = parent
        self.gui = MockComparisonGui()
    def mock_refresh(self, *args):
        """stub
        """
        print('called comparetype.refresh_compare() with args', args)
    monkeypatch.setattr(main, 'comparetypes', {'x': ('y', 'z', mock_refresh)})
    monkeypatch.setattr(main.ShowComparison, '__init__', mock_init)
    testobj = main.ShowComparison(types.SimpleNamespace(comparetype='x'))
    assert capsys.readouterr().out == ("called ShowComparison.__init__() with args"
                                       " namespace(comparetype='x')\n"
                                       'called ShowComparisonGui.__init__() with args () {}\n')
    testobj.refresh()
    assert capsys.readouterr().out == ('called comparetype.refresh_compare() with args ()\n'
                                       'called ShowComparisonGui.refresh_tree()\n')

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
        outfilename = main.pathlib.Path(stream.name).name
        print(f'called ConfigParser.write to file with name `{outfilename}`')

def test_inifile_init():
    """unittest for main.IniFile.init
    """
    testobj = main.IniFile('testfile')
    assert testobj.fname == 'testfile'

def test_inifile_read(monkeypatch, capsys):
    """unittest for main.IniFile.read
    """
    monkeypatch.setattr(main, 'ConfigParser', MockParser)
    testobj = main.IniFile('testfile')
    testobj.read()
    assert testobj.mru_left == ['file1', 'file2']
    assert testobj.mru_right == ['file1', 'file2']
    assert testobj.horizontal
    assert capsys.readouterr().out == ('called ConfigParser.__init__()\n'
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

def test_inifile_write(monkeypatch, capsys, tmp_path):
    """unittest for main.IniFile.write
    """
    monkeypatch.setattr(main, 'ConfigParser', MockParser)
    testfilename = tmp_path / 'testfile'
    testobj = main.IniFile(testfilename)
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
