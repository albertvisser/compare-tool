"""unittests for ./src/qt_gui.py
"""
import types
import pytest
from mockgui import mockqtwidgets as mockqtw
from src import qt_gui as testee


class TestMainWindow:
    """unittest for qt_gui.MainWindow
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for qt_gui.MainWindow object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called MainWindow.__init__ with args', args)
        monkeypatch.setattr(testee.MainWindow, '__init__', mock_init)
        testmaster = types.SimpleNamespace()
        testobj = testee.MainWindow(testmaster)
        assert capsys.readouterr().out == f"called MainWindow.__init__ with args ({testmaster},)\n"
        testobj.master = testmaster
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for MainWindow.__init__
        """
        def mock_init(self, *args):
            print('called MainWindow.__init__ with args', args)
        def mock_setup(self):
            print('called MainWindow.setup_menu')
        monkeypatch.setattr(testee.qtw.QApplication, '__init__', mockqtw.MockApplication.__init__)
        monkeypatch.setattr(testee.qtw.QMainWindow, '__init__', mock_init)
        # mockqtw.MockMainWindow.__init__)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'resize', mockqtw.MockMainWindow.resize)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'setWindowTitle',
                            mockqtw.MockMainWindow.setWindowTitle)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'setWindowIcon',
                            mockqtw.MockMainWindow.setWindowIcon)
        monkeypatch.setattr(testee.gui, 'QIcon', mockqtw.MockIcon)
        monkeypatch.setattr(testee.MainWindow, 'setup_menu', mock_setup)
        master = types.SimpleNamespace(apptitel='Comparer')
        testobj = testee.MainWindow(master)
        assert testobj.menuactions == {}
        assert capsys.readouterr().out == ('called Application.__init__\n'
                                           "called MainWindow.__init__ with args (None,)\n"
                                           "called MainWindow.resize with args (1024, 600)\n"
                                           "called MainWindow.setWindowTitle with arg `Comparer`\n"
                                           "called Icon.__init__ with arg `inicomp.png`\n"
                                           "called MainWindow.setWindowIcon\n"
                                           "called MainWindow.setup_menu\n")

    def test_setup_menu(self, monkeypatch, capsys):
        """unittest for MainWindow.setup_menu
        """
        monkeypatch.setattr(testee.qtw, 'QMenuBar', mockqtw.MockMenuBar)
        monkeypatch.setattr(testee.qtw, 'QMenu', mockqtw.MockMenu)
        monkeypatch.setattr(testee.gui, 'QAction', mockqtw.MockAction)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'menuBar', mockqtw.MockMainWindow.menuBar)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.menudict = {'x': [(11, 'xx', 'yy', 'zz', 'fun1'), ()]}
        testobj.menuactions = {}
        testobj.setup_menu()
        assert len(testobj.menuactions) == 1
        assert isinstance(testobj.menuactions[11], testee.gui.QAction)
        assert capsys.readouterr().out == ("called MainWindow.menuBar\n"
                                           "called MenuBar.__init__\n"
                                           "called MenuBar.addMenu with arg  x\n"
                                           "called Menu.__init__ with args ('x',)\n"
                                           f"called Action.__init__ with args ('xx', {testobj})\n"
                                           "called Signal.connect with args ('fun1',)\n"
                                           "called Action.setShortcut with arg `yy`\n"
                                           "called Action.setStatusTip with arg 'zz'\n"
                                           "called Menu.addAction\n"
                                           "called Menu.addSeparator\n"
                                           "called Action.__init__ with args ('-----', None)\n")

    def test_go(self, monkeypatch, capsys):
        """unittest for MainWindow.go
        """
        monkeypatch.setattr(testee.qtw.QMainWindow, 'setCentralWidget',
                            mockqtw.MockMainWindow.setCentralWidget)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'show', mockqtw.MockMainWindow.show)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.showcomp = types.SimpleNamespace(gui='results')
        testobj.app = mockqtw.MockApplication()
        assert capsys.readouterr().out == 'called Application.__init__\n'
        with pytest.raises(SystemExit):
            testobj.go()
        assert capsys.readouterr().out == (
                "called MainWidget.setCentralWindow with arg of type `<class 'str'>`\n"
                "called MainWindow.show\n"
                "called Application.exec\n")

    def test_meld_input_fout(self, monkeypatch, capsys):
        """unittest for MainWindow.meld_input_fout
        """
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.apptitel = 'Comparer'
        testobj.meld_input_fout('ahem')
        assert capsys.readouterr().out == (
                f"called MessageBox.critical with args `{testobj}` `Comparer` `ahem`\n")

    def test_meld_vergelijking_fout(self, monkeypatch, capsys):
        """unittest for MainWindow.meld_vergelijking_fout
        """
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.apptitel = 'Comparer'
        testobj.meld_vergelijking_fout('A message', '')
        assert capsys.readouterr().out == (
                f"called MessageBox.__init__ with args ({testobj},) {{}}\n"
                "called MessageBox.setWindowTitle with arg `Comparer`\n"
                "called MessageBox.setText with arg `A message`\n"
                "called MessageBox.exec\n")
        testobj.meld_vergelijking_fout('A message', ['with', 'text'])
        assert capsys.readouterr().out == (
                f"called MessageBox.__init__ with args ({testobj},) {{}}\n"
                "called MessageBox.setWindowTitle with arg `Comparer`\n"
                "called MessageBox.setText with arg `A message`\n"
                "called MessageBox.setInformativeText with arg `<pre>withtext</pre>`\n"
                "called MessageBox.exec\n")

    def test_meld(self, monkeypatch, capsys):
        """unittest for MainWindow.meld
        """
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master.apptitel = 'Comparer'
        testobj.meld('there there')
        assert capsys.readouterr().out == (
                f"called MessageBox.information with args `{testobj}` `Comparer` `there there`\n")

    def test_refresh(self, monkeypatch, capsys):
        """unittest for MainWindow.refresh
        """
        def mock_refresh():
            print('called ShowComparisonGui.refresh_tree')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.win = types.SimpleNamespace(refresh_tree=mock_refresh)
        testobj.refresh()
        assert capsys.readouterr().out == ("called ShowComparisonGui.refresh_tree\n")

    def test_keyPressEvent(self, monkeypatch, capsys):
        """unittest for MainWindow.keyPressEvent
        """
        class KeyEvent1:
            def key(self):
                return testee.core.Qt.Key.Key_Escape
            def __str__(self):
                return 'EscapeKey'
        class KeyEvent2:
            def key(self):
                return 'other'
            def __str__(self):
                return 'Not Escape'
        def mock_event(self, event):
            print(f'called MainWindow.keyPressEvent with arg `{event}`')
        def mock_close(self):
            print('called MainWindow.close')
        monkeypatch.setattr(testee.qtw.QMainWindow, 'keyPressEvent', mock_event)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'close', mock_close)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.keyPressEvent(KeyEvent1())
        assert capsys.readouterr().out == ("called MainWindow.close\n")
        testobj.keyPressEvent(KeyEvent2())
        assert capsys.readouterr().out == ("called MainWindow.keyPressEvent with arg `Not Escape`\n")

    def test_exit(self, monkeypatch, capsys):
        """unittest for MainWindow.exit
        """
        def mock_close(self):
            print('called MainWindow.close')
        monkeypatch.setattr(testee.qtw.QMainWindow, 'close', mock_close)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.exit()
        assert capsys.readouterr().out == ("called MainWindow.close\n")


def test_show_dialog(monkeypatch, capsys):
    """unittest for qt_gui.show_dialog
    """
    def mock_exec(cls):
        print('called Dialog.exec')
        return True
    mockparent = 'parent'
    monkeypatch.setattr(testee.qtw.QDialog, '__init__', mockqtw.MockDialog.__init__)
    monkeypatch.setattr(testee.qtw.QDialog, 'exec', mockqtw.MockDialog.exec)
    cls = testee.qtw.QDialog('xxx')
    assert not testee.show_dialog(mockparent, cls)
    assert capsys.readouterr().out == ("called Dialog.__init__ with args xxx () {}\n"
                                       "called Dialog.exec\n")
    monkeypatch.setattr(testee.qtw.QDialog, 'exec', mock_exec)
    cls = testee.qtw.QDialog('xxx')
    assert testee.show_dialog(mockparent, cls)
    assert capsys.readouterr().out == ("called Dialog.__init__ with args xxx () {}\n"
                                       "called Dialog.exec\n")


class TestAskOpenFilesGui:
    """unittest for qt_gui.AskOpenFilesGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for qt_gui.AskOpenFilesGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called AskOpenFilesGui.__init__ with args', args)
        monkeypatch.setattr(testee.AskOpenFilesGui, '__init__', mock_init)
        testobj = testee.AskOpenFilesGui()
        testobj.master = types.SimpleNamespace(parent=types.SimpleNamespace(gui='mastergui',
                                                                            apptitel="Comparer"))
        assert capsys.readouterr().out == 'called AskOpenFilesGui.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.__init__
        """
        monkeypatch.setattr(testee.qtw.QDialog, '__init__', mockqtw.MockDialog.__init__)
        testmaster = types.SimpleNamespace(parent=types.SimpleNamespace(gui='mastergui'))
        # breakpoint()
        testee.AskOpenFilesGui(testmaster, 'size')
        assert capsys.readouterr().out == 'called Dialog.__init__ with args mastergui () {}\n'

    def test_add_ask_for_filename(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.add_ask_for_filename
        """
        def mock_button(*args, **kwargs):
            print('called FileBrowseButton with args', args, kwargs)
            return 'result'
        monkeypatch.setattr(testee, 'FileBrowseButton', mock_button)
        testobj = self.setup_testobj(monkeypatch, capsys)
        assert testobj.add_ask_for_filename('size', 'label', 'browse', 'path', 'tooltip', 'title',
                                            'history', 'value') == "result"
        assert capsys.readouterr().out == (
                f"called FileBrowseButton with args ({testobj},)"
                " {'caption': 'label', 'button': 'browse', 'text': 'value', 'items': 'history'}\n")

    def test_build_screen(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.build_screen
        """
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QGridLayout', mockqtw.MockGridLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QRadioButton', mockqtw.MockRadioButton)
        monkeypatch.setattr(testee.qtw, 'QDialogButtonBox', mockqtw.MockButtonBox)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mockqtw.MockDialog.setLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        leftfile = mockqtw.MockComboBox()
        rightfile = mockqtw.MockComboBox()
        assert capsys.readouterr().out == "called ComboBox.__init__\ncalled ComboBox.__init__\n"
        choices = {'y': ('yyy',), 'x': ('xxx',)}
        testobj.master.parent.comparetype = 'y'
        testobj.build_screen(leftfile, rightfile, 'comparetext', choices, 'oktext', 'canceltext')
        assert len(testobj.sel) == len(choices)
        assert isinstance(testobj.sel[0][0], testee.qtw.QRadioButton)
        assert testobj.sel[0][1] == 'x'
        assert isinstance(testobj.sel[1][0], testee.qtw.QRadioButton)
        assert testobj.sel[1][1] == 'y'
        assert capsys.readouterr().out == (
            "called VBox.__init__\n"
            "called HBox.__init__\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockComboBox'>\n"
            "called VBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockHBoxLayout'>\n"
            "called HBox.__init__\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockComboBox'>\n"
            "called VBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockHBoxLayout'>\n"
            "called HBox.__init__\n"
            "called HBox.addSpacing\n"
            "called Grid.__init__\n"
            "called Label.__init__ with args ('comparetext',)\n"
            "called Grid.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockLabel'>"
            " at (0, 0)\n"
            f"called RadioButton.__init__ with args ('xxx', {testobj}) {{}}\n"
            "called Grid.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockRadioButton'>"
            " at (0, 1)\n"
            f"called RadioButton.__init__ with args ('yyy', {testobj}) {{}}\n"
            "called Grid.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockRadioButton'>"
            " at (1, 1)\n"
            "called RadioButton.setChecked with arg `True`\n"
            "called HBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockGridLayout'>\n"
            "called HBox.addStretch\n"
            "called VBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockHBoxLayout'>\n"
            "called ButtonBox.__init__ with args ()\n"
            "called ButtonBox.addButton with args (1,)\n"
            "called ButtonBox.addButton with args (2,)\n"
            f"called Signal.connect with args ({testobj.accept},)\n"
            f"called Signal.connect with args ({testobj.reject},)\n"
            "called HBox.__init__\n"
            "called HBox.addStretch\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockButtonBox'>\n"
            "called HBox.addStretch\n"
            "called VBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockHBoxLayout'>\n"
            "called Dialog.setLayout\n")

    def test_accept(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.accept
        """
        class mock_button:
            def __init__(self, *args, **kwargs):
                print('called FileBrowseButton with args', args, kwargs)
                self.input = mockqtw.MockComboBox(self)
                self.input.setCurrentText(args[0])
        def mock_check_nok(*args):
            print('called Comparer.check_input with args', args)
            return 'A message'
        def mock_check_ok(*args):
            print('called Comparer.check_input with args', args)
            return ''
        def mock_accept(self):
            print('called Dialog.accept')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.browse1 = mock_button('left side')
        testobj.browse2 = mock_button('right side')
        check1 = mockqtw.MockCheckBox()
        check2 = mockqtw.MockCheckBox()
        check2.setChecked(True)
        testobj.sel = [(check1, 'xxx'), (check2, 'yyy')]
        assert capsys.readouterr().out == ("called FileBrowseButton with args ('left side',) {}\n"
                                           "called ComboBox.__init__\n"
                                           "called ComboBox.setCurrentText with arg `left side`\n"
                                           "called FileBrowseButton with args ('right side',) {}\n"
                                           "called ComboBox.__init__\n"
                                           "called ComboBox.setCurrentText with arg `right side`\n"
                                           "called CheckBox.__init__\n"
                                           "called CheckBox.__init__\n"
                                           "called CheckBox.setChecked with arg True\n")
        monkeypatch.setattr(testee.qtw.QDialog, 'accept', mock_accept)
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        testobj.master.check_input = mock_check_nok
        testobj.accept()
        assert capsys.readouterr().out == (
                "called ComboBox.currentText\n"
                "called ComboBox.currentText\n"
                "called CheckBox.isChecked\n"
                "called CheckBox.isChecked\n"
                "called Comparer.check_input with args ('current text', 'current text', 'yyy')\n"
                f"called MessageBox.critical with args `{testobj}` `Comparer` `A message`\n")
        testobj.master.check_input = mock_check_ok
        testobj.accept()
        assert testobj.master.parent.lhs_path == 'current text'
        assert testobj.master.parent.rhs_path == 'current text'
        assert testobj.master.parent.comparetype == 'yyy'
        assert capsys.readouterr().out == (
                "called ComboBox.currentText\n"
                "called ComboBox.currentText\n"
                "called CheckBox.isChecked\n"
                "called CheckBox.isChecked\n"
                "called Comparer.check_input with args ('current text', 'current text', 'yyy')\n"
                "called Dialog.accept\n")
        testobj.sel = []
        testobj.accept()
        assert testobj.master.parent.lhs_path == 'current text'
        assert testobj.master.parent.rhs_path == 'current text'
        assert testobj.master.parent.comparetype == ''
        assert capsys.readouterr().out == (
                "called ComboBox.currentText\n"
                "called ComboBox.currentText\n"
                "called Comparer.check_input with args ('current text', 'current text', '')\n"
                "called Dialog.accept\n")


class TestShowComparisonGui:
    """unittest for qt_gui.ShowComparisonGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for qt_gui.ShowComparisonGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called ShowComparisonGui.__init__ with args', args)
        monkeypatch.setattr(testee.ShowComparisonGui, '__init__', mock_init)
        testparent = types.SimpleNamespace()
        testobj = testee.ShowComparisonGui(testparent)
        assert capsys.readouterr().out == (
                f'called ShowComparisonGui.__init__ with args ({testparent},)\n')
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.__init__
        """
        def mock_init(self, *args):
            """stub
            """
            print('called ShowComparisonGui.__init__ with args', args)
        monkeypatch.setattr(testee.qtw.QTreeWidget, '__init__', mock_init)
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'setColumnCount',
                            mockqtw.MockTreeWidget.setColumnCount)
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'header', mockqtw.MockTreeWidget.header)
        testee.ShowComparisonGui('parent')
        assert capsys.readouterr().out == ("called ShowComparisonGui.__init__ with args ('parent',)\n"
                                           "called Tree.setColumnCount with arg `3`\n"
                                           "called Tree.header\ncalled Header.__init__\n"
                                           "called Header.resizeSection with args (0, 200)\n"
                                           "called Header.resizeSection with args (1, 350)\n")

    def test_setup_nodata_columns(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.setup_nodata_columns
        """
        def mock_add(arg):
            print(f'called ShowComparisonGui.addTopLevelItem with arg {arg}')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.addTopLevelItem = mock_add
        monkeypatch.setattr(testee.qtw, 'QTreeWidgetItem', mockqtw.MockTreeItem)
        root = testobj.setup_nodata_columns('root_text', 'leftcaption', 'rightcaption')
        assert capsys.readouterr().out == (
                "called TreeItem.__init__ with args ()\n"
                "called TreeItem.setText with args (1, 'leftcaption')\n"
                "called TreeItem.setText with args (2, 'rightcaption')\n"
                f'called ShowComparisonGui.addTopLevelItem with arg {root}\n')

    def test_finish_init(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.finish_init
        """
        def mock_show():
            print('called ShowComparisonGui.show')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.show = mock_show
        testobj.finish_init()
        assert capsys.readouterr().out == 'called ShowComparisonGui.show\n'

    def test_refresh_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.refresh_tree

        method is empty, so test is too
        """

    def test_init_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.init_tree
        """
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'clear', mockqtw.MockTreeWidget.clear)
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'setHeaderLabels',
                            mockqtw.MockTreeWidget.setHeaderLabels)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.init_tree('caption', 'left_title', 'right_title')
        assert capsys.readouterr().out == (
                "called Tree.clear\n"
                "called Tree.setHeaderLabels with arg `['caption', 'left_title', 'right_title']`\n")

    def test_build_header(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.build_header
        """
        def mock_set(*args):
            print('called ShowComparisonGui.set_node_text with args', args)
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'addTopLevelItem',
                            mockqtw.MockTreeWidget.addTopLevelItem)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.set_node_text = mock_set
        node = testobj.build_header('section')
        assert isinstance(node, testee.qtw.QTreeWidgetItem)
        assert capsys.readouterr().out == (
                f"called ShowComparisonGui.set_node_text with args ({node}, 0, 'section')\n"
                "called Tree.addTopLevelItem\n")

    def test_colorize_header(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.colorize_header
        """
        monkeypatch.setattr(testee, 'rightonly_colour', 'right')
        monkeypatch.setattr(testee, 'leftonly_colour', 'left')
        monkeypatch.setattr(testee, 'difference_colour', 'both')
        testobj = self.setup_testobj(monkeypatch, capsys)
        node = mockqtw.MockTreeItem()
        assert capsys.readouterr().out == "called TreeItem.__init__ with args ()\n"
        testobj.colorize_header(node, True, False, True)     # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'right')\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n")
        testobj.colorize_header(node, True, False, False)
        assert capsys.readouterr().out == "called TreeItem.setForeground with args (0, 'right')\n"
        testobj.colorize_header(node, False, True, True)     # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'left')\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n")
        testobj.colorize_header(node, False, True, False)
        assert capsys.readouterr().out == "called TreeItem.setForeground with args (0, 'left')\n"
        testobj.colorize_header(node, True, True, True)      # kan dit?
        assert capsys.readouterr().out == "called TreeItem.setForeground with args (0, 'both')\n"
        testobj.colorize_header(node, True, True, False)    # kan dit?
        assert capsys.readouterr().out == "called TreeItem.setForeground with args (0, 'both')\n"
        testobj.colorize_header(node, False, False, True)
        assert capsys.readouterr().out == "called TreeItem.setForeground with args (0, 'both')\n"
        testobj.colorize_header(node, False, False, False)  # kan dit?
        assert capsys.readouterr().out == ("")

    def test_build_child(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.build_child
        """
        def mock_set(*args):
            print('called ShowComparisonGui.set_node_text with args', args)
        testobj = self.setup_testobj(monkeypatch, capsys)
        header = mockqtw.MockTreeItem()
        assert capsys.readouterr().out == "called TreeItem.__init__ with args ()\n"
        testobj.set_node_text = mock_set
        node = testobj.build_child(header, 'option')
        assert isinstance(node, testee.qtw.QTreeWidgetItem)
        assert capsys.readouterr().out == (
                f"called ShowComparisonGui.set_node_text with args ({node}, 0, 'option')\n"
                "called TreeItem.addChild\n")

    def test_colorize_child(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.colorize_child
        """
        monkeypatch.setattr(testee, 'rightonly_colour', 'right')
        monkeypatch.setattr(testee, 'leftonly_colour', 'left')
        monkeypatch.setattr(testee, 'difference_colour', 'both')
        testobj = self.setup_testobj(monkeypatch, capsys)
        node = mockqtw.MockTreeItem()
        assert capsys.readouterr().out == "called TreeItem.__init__ with args ()\n"
        testobj.colorize_child(node, True, False, True)  # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'right')\n"
                                           "called TreeItem.setForeground with args (2, 'right')\n")
        testobj.colorize_child(node, True, False, False)
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'right')\n"
                                           "called TreeItem.setForeground with args (2, 'right')\n")
        testobj.colorize_child(node, False, True, True)  # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'left')\n"
                                           "called TreeItem.setForeground with args (1, 'left')\n")
        testobj.colorize_child(node, False, True, False)
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'left')\n"
                                           "called TreeItem.setForeground with args (1, 'left')\n")
        testobj.colorize_child(node, True, True, True)  # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'left')\n"
                                           "called TreeItem.setForeground with args (1, 'left')\n")
        testobj.colorize_child(node, True, True, False)  # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'left')\n"
                                           "called TreeItem.setForeground with args (1, 'left')\n")
        testobj.colorize_child(node, False, False, True)
        assert capsys.readouterr().out == ("called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.setForeground with args (1, 'both')\n"
                                           "called TreeItem.setForeground with args (2, 'both')\n")
        testobj.colorize_child(node, False, False, False)  # kan dit?
        assert capsys.readouterr().out == ("")

    def test_set_node_text(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.set_node_text
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        node = mockqtw.MockTreeItem()
        assert capsys.readouterr().out == "called TreeItem.__init__ with args ()\n"
        testobj.set_node_text(node, 1, 'text')
        assert capsys.readouterr().out == (
                "called TreeItem.setText with args (1, 'text')\n"
                "called TreeItem.setTextAlignment with args"
                f" (1, {testee.core.Qt.AlignmentFlag.AlignTop!r})\n"
                "called TreeItem.setTooltip with args (1, 'text')\n")

    def test_get_parent(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.get_parent
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        node = mockqtw.MockTreeItem()
        assert capsys.readouterr().out == "called TreeItem.__init__ with args ()\n"
        assert testobj.get_parent(node) == 'parent'
        assert capsys.readouterr().out == "called TreeItem.parent\n"


class TestFileBrowseButton:
    """unittest for qt_gui.FileBrowseButton
    """
    def test_init(self, monkeypatch, capsys):
        """unittest for FileBrowseButton.__init__
        """
        monkeypatch.setattr(testee.qtw.QFrame, '__init__', mockqtw.MockFrame.__init__)
        monkeypatch.setattr(testee.qtw.QFrame, 'setFrameStyle', mockqtw.MockFrame.setFrameStyle)
        monkeypatch.setattr(testee.qtw.QFrame, 'setLayout', mockqtw.MockFrame.setLayout)
        # monkeypatch.setattr(testee.qtw.QFrame.Shape, 'Panel', 2)
        # monkeypatch.setattr(testee.qtw.QFrame.Shadow, 'Raised', 16)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QComboBox', mockqtw.MockComboBox)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QPushButton', mockqtw.MockPushButton)
        testobj = testee.FileBrowseButton('parent')
        assert capsys.readouterr().out == (
            "called Frame.__init__\n"
            "called Frame.setFrameStyle with arg `34`\n"
            "called VBox.__init__\n"
            "called HBox.__init__\n"
            "called ComboBox.__init__\n"
            "called ComboBox.setEditable with arg `True`\n"
            "called ComboBox.setMaximumWidth with arg `300`\n"
            "called ComboBox.addItems with arg []\n"
            "called ComboBox.setEditText with arg ``\n"
            "called Label.__init__ with args ('',)\n"
            "called Label.setMinimumWidth with arg `120`\n"
            "called Label.setMaximumWidth with arg `120`\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockLabel'>\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockComboBox'>\n"
            f"called PushButton.__init__ with args ('', {testobj}) {{'clicked': {testobj.browse}}}\n"
            "called PushButton.setMaximumWidth with arg `68`\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockPushButton'>\n"
            "called VBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockHBoxLayout'>\n"
            "called Frame.setLayout with arg of type <class 'mockgui.mockqtwidgets.MockVBoxLayout'>"
            "\n")
        testobj = testee.FileBrowseButton('parent', caption="xxx", button="yyy", text="zzz",
                                          items=['a', 'b'])
        assert capsys.readouterr().out == (
            "called Frame.__init__\n"
            "called Frame.setFrameStyle with arg `34`\n"
            "called VBox.__init__\n"
            "called HBox.__init__\n"
            "called ComboBox.__init__\n"
            "called ComboBox.setEditable with arg `True`\n"
            "called ComboBox.setMaximumWidth with arg `300`\n"
            "called ComboBox.addItems with arg ['a', 'b']\n"
            "called ComboBox.setEditText with arg `zzz`\n"
            "called Label.__init__ with args ('xxx',)\n"
            "called Label.setMinimumWidth with arg `120`\n"
            "called Label.setMaximumWidth with arg `120`\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockLabel'>\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockComboBox'>\n"
            f"called PushButton.__init__ with args ('yyy', {testobj})"
            f" {{'clicked': {testobj.browse}}}\n"
            "called PushButton.setMaximumWidth with arg `68`\n"
            "called HBox.addWidget with arg of type <class 'mockgui.mockqtwidgets.MockPushButton'>\n"
            "called VBox.addLayout with arg of type <class 'mockgui.mockqtwidgets.MockHBoxLayout'>\n"
            "called Frame.setLayout with arg of type <class 'mockgui.mockqtwidgets.MockVBoxLayout'>"
            "\n")

    def test_browse(self, monkeypatch, capsys):
        """unittest for FileBrowseButton.browse
        """
        def mock_init(self, *args):
            """stub
            """
            print('called FileBrowseButton.__init__ with args', args)
        def mock_get(parent, *args, **kwargs):
            print('called FileDialog.getOpenFilename with args', args, kwargs)
            return 'xxx', True
        monkeypatch.setattr(testee.FileBrowseButton, '__init__', mock_init)
        monkeypatch.setattr(testee.qtw.QFileDialog, 'getOpenFileName',
                            mockqtw.MockFileDialog.getOpenFileName)
        testobj = testee.FileBrowseButton('parent')
        testobj.input = mockqtw.MockComboBox()
        assert capsys.readouterr().out == (
                "called FileBrowseButton.__init__ with args ('parent',)\n"
                "called ComboBox.__init__\n")
        testobj.browse()
        assert capsys.readouterr().out == (
            "called ComboBox.currentText\n"
            f"called FileDialog.getOpenFileName with args {testobj}"
            " ('Kies een bestand', 'current text') {}\n")
        monkeypatch.setattr(testee.qtw.QFileDialog, 'getOpenFileName', mock_get)
        testobj.browse()
        assert capsys.readouterr().out == (
            "called ComboBox.currentText\n"
            "called FileDialog.getOpenFilename with args ('Kies een bestand', 'current text') {}\n"
            "called ComboBox.setEditText with arg `xxx`\n")
