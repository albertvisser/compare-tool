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
        class MockShowComp:
            "stub"
            gui = 'ShowCompGui'
        class MockAskOpenFiles:
            "stub"
            def check_input(self):
                print('called AskOpenFiles.check_input')
                return 'msg'
        class MockComparer:
            "stub"
            apptitel = 'xxx'
            showcomp = MockShowComp()
            inputgetter = MockAskOpenFiles()
            # def meld_input_fout(self, msg):
            #     print(f"called Comparer.meld_input_fout with arg '{msg}'")
            def open(self):
                print('called Comparer.open')
            def doit(self):
                print('called Comparer.doit')
        def mock_input():
            print('called AskOpenFiles.check_input')
            return ''
        monkeypatch.setattr(testee.qtw.QMainWindow, 'setCentralWidget',
                            mockqtw.MockMainWindow.setCentralWidget)
        monkeypatch.setattr(testee.qtw.QMainWindow, 'show', mockqtw.MockMainWindow.show)
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = MockComparer()
        testobj.app = mockqtw.MockApplication()
        assert capsys.readouterr().out == 'called Application.__init__\n'
        with pytest.raises(SystemExit):
            testobj.go()  # 'left', 'right', 'method')
        assert capsys.readouterr().out == (
                "called MainWidget.setCentralWidget with arg `str`\n"
                "called MainWindow.show\n"
                "called AskOpenFiles.check_input\n"
                f"called MessageBox.critical with args `{testobj}` `xxx` `msg`\n"
                "called Comparer.open\n"
                "called Application.exec\n")
        testobj.master.inputgetter.check_input = mock_input
        with pytest.raises(SystemExit):
            testobj.go()  # 'left', 'right', 'method')
        assert capsys.readouterr().out == (
                "called MainWidget.setCentralWidget with arg `str`\n"
                "called MainWindow.show\n"
                "called AskOpenFiles.check_input\n"
                "called Comparer.doit\n"
                "called Application.exec\n")

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
                "called MessageBox.setTextFormat with arg `TextFormat.MarkdownText`\n"
                "called MessageBox.setInformativeText with arg ````\nwithtext```\n`\n"
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
            "stub"
            def key(self):
                return testee.core.Qt.Key.Key_Escape
            def __str__(self):
                return 'EscapeKey'
        class KeyEvent2:
            "stub"
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
    class MockGui:
        "stub"
        def exec(self):
            print('called Dialog.exec')
            return result
        def update_typeselector(self):
            print('called dialog.update_typeselector')
    master = types.SimpleNamespace(gui=MockGui())
    parent = 'parent'
    result = 'xxx'
    assert not testee.show_dialog(master, parent)
    assert capsys.readouterr().out == ('called dialog.update_typeselector\n'
                                       "called Dialog.exec\n")
    result = testee.qtw.QDialog.DialogCode.Accepted
    assert testee.show_dialog(master, parent)
    assert capsys.readouterr().out == ('called dialog.update_typeselector\n'
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
        monkeypatch.setattr(testee.qtw.QDialog, 'setWindowTitle', mockqtw.MockDialog.setWindowTitle)
        monkeypatch.setattr(testee.qtw.QDialog, 'setLayout', mockqtw.MockDialog.setLayout)
        monkeypatch.setattr(testee.qtw, 'QVBoxLayout', mockqtw.MockVBoxLayout)
        testmaster = types.SimpleNamespace(parent=types.SimpleNamespace(gui='mastergui'))
        testee.AskOpenFilesGui(testmaster, 'size', 'title')
        assert capsys.readouterr().out == ("called Dialog.__init__ with args mastergui () {}\n"
                                           "called Dialog.setWindowTitle with args ('title',)\n"
                                           "called VBox.__init__\n"
                                           "called Dialog.setLayout with arg MockVBoxLayout\n")

    def test_add_ask_for_filename(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.add_ask_for_filename
        """
        def mock_button(*args, **kwargs):
            print('called FileBrowseButton with args', args, kwargs)
            return 'result'
        monkeypatch.setattr(testee, 'FileBrowseButton', mock_button)
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockqtw.MockVBoxLayout()
        assert capsys.readouterr().out == "called VBox.__init__\n"
        assert testobj.add_ask_for_filename('size', 'label', 'browse', 'path', 'tooltip', 'title',
                                            'history', 'value') == "result"
        assert capsys.readouterr().out == (
                "called HBox.__init__\n"
                f"called FileBrowseButton with args ({testobj},)"
                " {'caption': 'label', 'button': 'browse', 'text': 'value', 'items': 'history'}\n"
                "called HBox.addWidget with arg result\n"
                "called VBox.addLayout with arg MockHBoxLayout\n")

    def test_create_fileselector_grid(self, monkeypatch, capsys):
        """unittest for text_create_fileselector_grid
        """
        monkeypatch.setattr(testee.qtw, 'QGridLayout', mockqtw.MockGridLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockqtw.MockVBoxLayout()
        sel1 = mockqtw.MockComboBox()       # niet het correcte type widget,
        sel2 = mockqtw.MockPushButton()     # maar zo kan ik het verschil zien
        assert capsys.readouterr().out == ("called VBox.__init__\n"
                                           "called ComboBox.__init__\n"
                                           "called PushButton.__init__ with args () {}\n")
        testobj.create_fileselector_grid([('text1', sel1), ('text2', sel2)])
        assert capsys.readouterr().out == (
            "called Grid.__init__\n"
            "called Label.__init__ with args ('text1',)\n"
            "called Grid.addWidget with arg MockLabel at (0, 0)\n"
            "called Grid.addWidget with arg MockComboBox at (0, 1)\n"
            "called Label.__init__ with args ('text2',)\n"
            "called Grid.addWidget with arg MockLabel at (1, 0)\n"
            "called Grid.addWidget with arg MockPushButton at (1, 1)\n"
            "called VBox.addLayout with arg MockGridLayout\n")

    def test_build_typeselector(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.build_typeselector
        """
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QGridLayout', mockqtw.MockGridLayout)
        monkeypatch.setattr(testee.qtw, 'QLabel', mockqtw.MockLabel)
        monkeypatch.setattr(testee.qtw, 'QRadioButton', mockqtw.MockRadioButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockqtw.MockVBoxLayout()
        assert capsys.readouterr().out == "called VBox.__init__\n"
        choices = {'y': ('yyy',), 'x': ('xxx',)}
        testobj.master.parent.comparetype = 'y'
        result = testobj.build_typeselector('comparetext', choices)
        assert len(result) == len(choices)
        assert isinstance(result[0][0], testee.qtw.QRadioButton)
        assert result[0][1] == 'x'
        assert isinstance(result[1][0], testee.qtw.QRadioButton)
        assert result[1][1] == 'y'
        assert capsys.readouterr().out == (
            "called HBox.__init__\n"
            "called HBox.addSpacing\n"
            "called Grid.__init__\n"
            "called Label.__init__ with args ('comparetext',)\n"
            "called Grid.addWidget with arg MockLabel at (0, 0)\n"
            f"called RadioButton.__init__ with args ('xxx', {testobj}) {{}}\n"
            "called Grid.addWidget with arg MockRadioButton at (0, 1)\n"
            f"called RadioButton.__init__ with args ('yyy', {testobj}) {{}}\n"
            "called Grid.addWidget with arg MockRadioButton at (1, 1)\n"
            "called HBox.addLayout with arg MockGridLayout\n"
            "called HBox.addStretch\n"
            "called VBox.addLayout with arg MockHBoxLayout\n")

    def test_add_buttons(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.add_buttons
        """
        monkeypatch.setattr(testee.qtw, 'QHBoxLayout', mockqtw.MockHBoxLayout)
        monkeypatch.setattr(testee.qtw, 'QDialogButtonBox', mockqtw.MockButtonBox)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockqtw.MockVBoxLayout()
        assert capsys.readouterr().out == "called VBox.__init__\n"
        testobj.add_buttons('oktext', 'canceltext')
        assert capsys.readouterr().out == (
            "called ButtonBox.__init__ with args ()\n"
            "called ButtonBox.addButton with args (1,)\n"
            "called ButtonBox.addButton with args (2,)\n"
            f"called Signal.connect with args ({testobj.accept},)\n"
            f"called Signal.connect with args ({testobj.reject},)\n"
            "called HBox.__init__\n"
            "called HBox.addStretch\n"
            "called HBox.addWidget with arg MockButtonBox\n"
            "called HBox.addStretch\n"
            "called VBox.addLayout with arg MockHBoxLayout\n")

    def test_update_typeselector(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.upate_typeselector
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        check1 = mockqtw.MockCheckBox()
        check2 = mockqtw.MockCheckBox()
        check3 = mockqtw.MockCheckBox()
        assert capsys.readouterr().out == ("called CheckBox.__init__\n"
                                           "called CheckBox.__init__\n"
                                           "called CheckBox.__init__\n")
        testobj.master = types.SimpleNamespace(parent=types.SimpleNamespace(comparetype='type2'),
                                               options=((check1, 'type1'), (check2, 'type2'),
                                                        (check3, 'type3')))
        testobj.update_typeselector()
        assert capsys.readouterr().out == ("called CheckBox.setChecked with arg False\n"
                                           "called CheckBox.setChecked with arg False\n"
                                           "called CheckBox.setChecked with arg True\n"
                                           "called CheckBox.setChecked with arg False\n")

    def test_accept(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.accept
        """
        def mock_check_nok(*args):
            print('called Comparer.check_input with args', args)
            return 'A message'
        def mock_check_ok(*args):
            print('called Comparer.check_input with args', args)
            return ''
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(parent=types.SimpleNamespace(apptitel='xxx'))
        monkeypatch.setattr(testee.qtw, 'QMessageBox', mockqtw.MockMessageBox)
        monkeypatch.setattr(testee.qtw.QDialog, 'accept', mockqtw.MockDialog.accept)
        testobj.master.check_input = mock_check_nok
        testobj.accept()
        assert capsys.readouterr().out == (
                "called Comparer.check_input with args ()\n"
                f"called MessageBox.critical with args `{testobj}` `xxx` `A message`\n")
        testobj.master.check_input = mock_check_ok
        testobj.accept()
        assert capsys.readouterr().out == (
                "called Comparer.check_input with args ()\n"
                "called Dialog.accept\n")

    def test_get_fbb_result(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.get_fbb_result
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        fbb = types.SimpleNamespace(input=mockqtw.MockComboBox())
        fbb.input.setCurrentText('xxx')
        assert capsys.readouterr().out == ("called ComboBox.__init__\n"
                                           "called ComboBox.setCurrentText with arg `xxx`\n")
        assert testobj.get_fbb_result(fbb) == 'current text'
        assert capsys.readouterr().out == "called ComboBox.currentText\n"

    def test_get_radiobox_value(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.get_radiobox_value
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        rb = mockqtw.MockRadioButton()
        rb.setChecked(True)
        assert capsys.readouterr().out == ("called RadioButton.__init__ with args () {}\n"
                                           "called RadioButton.setChecked with arg `True`\n")
        assert testobj.get_radiobox_value(rb)
        assert capsys.readouterr().out == "called RadioButton.isChecked\n"


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
        parent = types.SimpleNamespace(gui='ShowComparisonGui')
        testobj = testee.ShowComparisonGui(parent)
        assert testobj.parent == parent
        assert capsys.readouterr().out == (
                "called ShowComparisonGui.__init__ with args ('ShowComparisonGui',)\n"
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

    def test_show_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.finish_init
        """
        def mock_show():
            print('called ShowComparisonGui.show')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.show = mock_show
        testobj.show_tree()
        assert capsys.readouterr().out == 'called ShowComparisonGui.show\n'

    def test_refresh_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.refresh_tree

        method is empty, so test is too
        """

    def test_init_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.init_tree
        """
        def mock_get():
            print('called Comparer.get_titles')
            return 'left_title', 'right_title'
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'clear', mockqtw.MockTreeWidget.clear)
        monkeypatch.setattr(testee.qtw.QTreeWidget, 'setHeaderLabels',
                            mockqtw.MockTreeWidget.setHeaderLabels)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.parent = types.SimpleNamespace(get_titles=mock_get)
        testobj.init_tree('caption')  # , 'left_title', 'right_title')
        assert capsys.readouterr().out == (
                "called Tree.clear\n"
                "called Comparer.get_titles\n"
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
        def mock_foreground(*args):
            print('called TreeItem.foreground with args', args)
            return testee.nocolour
        def mock_foreground_2(*args):
            print('called TreeItem.foreground with args', args)
            return testee.leftonly_colour
        def mock_foreground_3(*args):
            print('called TreeItem.foreground with args', args)
            return testee.rightonly_colour
        def mock_foreground_4(*args):
            print('called TreeItem.foreground with args', args)
            return testee.difference_colour
        monkeypatch.setattr(testee, 'nocolour', 'nodiff')
        monkeypatch.setattr(testee, 'rightonly_colour', 'right')
        monkeypatch.setattr(testee, 'leftonly_colour', 'left')
        monkeypatch.setattr(testee, 'difference_colour', 'both')
        testobj = self.setup_testobj(monkeypatch, capsys)
        node = mockqtw.MockTreeItem()
        node.foreground = mock_foreground
        assert capsys.readouterr().out == "called TreeItem.__init__ with args ()\n"
        testobj.colorize_header(node, True, False, True)     # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'right')\n"
                                           # "called TreeItem.setForeground with args (0, 'both')\n")
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, True, False, False)
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'right')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, False, True, True)     # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'left')\n"
                                           # "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, False, True, False)
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'left')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, True, True, True)      # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, True, True, False)    # kan dit?
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, False, False, True)
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, False, False, False)  # kan dit?
        assert capsys.readouterr().out == "called TreeItem.foreground with args (0,)\n"
        node.foreground = mock_foreground_2
        testobj.colorize_header(node, True, '', '')
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        testobj.colorize_header(node, '', True, '')
        assert capsys.readouterr().out == "called TreeItem.foreground with args (0,)\n"
        testobj.colorize_header(node, '', '', True)
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        node.foreground = mock_foreground_3
        testobj.colorize_header(node, True, '', '')
        assert capsys.readouterr().out == "called TreeItem.foreground with args (0,)\n"
        testobj.colorize_header(node, '', True, '')
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.text with arg 2\n")
        node.setText(1, 'x')
        node.setText(2, 'y')
        assert capsys.readouterr().out == ("called TreeItem.setText with args (1, 'x')\n"
                                           "called TreeItem.setText with args (2, 'y')\n")
        testobj.colorize_header(node, '', '', True)
        assert capsys.readouterr().out == ("called TreeItem.foreground with args (0,)\n"
                                           "called TreeItem.setForeground with args (0, 'both')\n"
                                           "called TreeItem.text with arg 1\n"
                                           "called TreeItem.setForeground with args (1, 'both')\n"
                                           "called TreeItem.text with arg 2\n"
                                           "called TreeItem.setForeground with args (2, 'both')\n")
        node.foreground = mock_foreground_4
        testobj.colorize_header(node, 'any', 'any', 'any')
        assert capsys.readouterr().out == "called TreeItem.foreground with args (0,)\n"

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
            "called HBox.addWidget with arg MockComboBox\n"
            f"called PushButton.__init__ with args ('', {testobj}) {{'clicked': {testobj.browse}}}\n"
            "called PushButton.setMaximumWidth with arg `68`\n"
            "called HBox.addWidget with arg MockPushButton\n"
            "called VBox.addLayout with arg MockHBoxLayout\n"
            "called Frame.setLayout with arg MockVBoxLayout"
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
            "called HBox.addWidget with arg MockComboBox\n"
            f"called PushButton.__init__ with args ('yyy', {testobj})"
            f" {{'clicked': {testobj.browse}}}\n"
            "called PushButton.setMaximumWidth with arg `68`\n"
            "called HBox.addWidget with arg MockPushButton\n"
            "called VBox.addLayout with arg MockHBoxLayout\n"
            "called Frame.setLayout with arg MockVBoxLayout"
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
