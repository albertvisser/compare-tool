"""unittests for ./src/wx_gui.py
"""
import types
from mockgui import mockwxwidgets as mockwx
from src import wx_gui as testee


class TestMainWindow:
    """unittest for wx_gui.MainWindow
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for wx_gui.MainWindow object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called MainWindow.__init__ with args', args)
        monkeypatch.setattr(testee.MainWindow, '__init__', mock_init)
        testobj = testee.MainWindow()
        # testobj.app = testee.wx.App()
        assert capsys.readouterr().out == 'called MainWindow.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for MainWindow.__init__
        """
        def mock_setup(self):
            print('called MainWindow.setup_menu')
        monkeypatch.setattr(testee.wx.App, '__init__', mockwx.MockApp.__init__)
        monkeypatch.setattr(testee.wx.Frame, '__init__', mockwx.MockFrame.__init__)
        monkeypatch.setattr(testee.MainWindow, 'setup_menu', mock_setup)
        master = types.SimpleNamespace(apptitel='xxx')
        testobj = testee.MainWindow(master)
        assert capsys.readouterr().out == (
                "called app.__init__ with args ()\n"
                "called frame.__init__ with args"
                f" (None, {testee.wx.ID_ANY}, 'xxx') {{'size': (1080, 600), 'style':"
                f" {testee.wx.DEFAULT_FRAME_STYLE | testee.wx.NO_FULL_REPAINT_ON_RESIZE}}}\n"
                "called MainWindow.setup_menu\n")

    def test_setup_gui(self, monkeypatch, capsys):
        """unittest for MainWindow.setup_gui
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx.Frame, 'SetAutoLayout', mockwx.MockFrame.SetAutoLayout)
        monkeypatch.setattr(testee.wx.Frame, 'SetSizer', mockwx.MockFrame.SetSizer)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(showcomp=types.SimpleNamespace(gui='gui'))
        testobj.setup_gui()
        assert capsys.readouterr().out == (
                f"called BoxSizer.__init__ with args ({testee.wx.VERTICAL},)\n"
                f"called vert sizer.Add with args ('gui', 1, {testee.wx.EXPAND})\n"
                "called Frame.SetAutoLayout with args (True,)\n"
                "called Frame.SetSizer with args (vert sizer,)\n"
                f"called vert sizer.Fit with args ({testobj},)\n")

    def test_setup_menu(self, monkeypatch, capsys):
        """unittest for MainWindow.setup_menu
        """
        def mock_menubar():
            result = mockwx.MockMenuBar()
            assert capsys.readouterr().out == "called MenuBar.__init__ with args ()\n"
            print('called wx.MenuBar')
            return result
        def func(*args):
            "dummy callback, just to get the reference"
        monkeypatch.setattr(testee.wx, 'MenuBar', mock_menubar)
        monkeypatch.setattr(testee.wx, 'Menu', mockwx.MockMenu)
        monkeypatch.setattr(testee.wx.Frame, 'SetMenuBar', mockwx.MockFrame.SetMenuBar)
        monkeypatch.setattr(testee.wx.Frame, 'Connect', mockwx.MockFrame.Connect)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(menudict={})
        testobj.setup_menu()
        assert capsys.readouterr().out == ("called wx.MenuBar\n"
                                           "called Frame.SetMenuBar with args (A MenuBar,)\n")
        testobj.master.menudict = {'first': [],
                                   'last': [[], ['xx', '&Xx', 'yyy', 'text', func]]}
        testobj.setup_menu()
        assert capsys.readouterr().out == (
                "called wx.MenuBar\n"
                "called Menu.__init__ with args ()\n"
                "called menubar.Append with args (A Menu, 'first')\n"
                "called Menu.__init__ with args ()\n"
                "called menu.AppendSeparator with args ()\n"
                "called menu.Append with args ('xx', '&Xx\\tyyy', 'text')\n"
                f"called Frame.Connect with args ('xx', {testee.wx.ID_ANY},"
                f" {testee.wx.wxEVT_COMMAND_MENU_SELECTED}, {func})\n"
                "called menubar.Append with args (A Menu, 'last')\n"
                "called Frame.SetMenuBar with args (A MenuBar,)\n")

    def test_go(self, monkeypatch, capsys):
        """unittest for MainWindow.go
        """
        def mock_check(*args):
            print('called AskOpenFileNames.check_input with args', args)
            return 'message'
        def mock_check_2(*args):
            print('called AskOpenFileNames.check_input with args', args)
            return ''
        def mock_open():
            print('called Comparer.open')
        def mock_doit():
            print('called Comparer.doit')
        monkeypatch.setattr(testee.wx.Frame, 'Show', mockwx.MockFrame.Show)
        monkeypatch.setattr(testee.wx, 'MessageBox', mockwx.mock_messagebox)
        # monkeypatch.setattr(testee.wx.App, 'MainLoop', mock_mainloop)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.app = mockwx.MockApp()
        assert capsys.readouterr().out == "called app.__init__ with args ()\n"
        testobj.master = types.SimpleNamespace(
                apptitel='title', open=mock_open, doit=mock_doit,
                get_input=types.SimpleNamespace(check_input=mock_check))
        testobj.go()
        assert capsys.readouterr().out == (
                "called frame.Show with args (True,)\n"
                "called AskOpenFileNames.check_input with args ()\n"
                "called wx.MessageBox with args ('message', 'title') {}\n"
                "called Comparer.open\n"
                "called app.MainLoop\n")
        testobj.master.get_input.check_input = mock_check_2
        testobj.go()
        assert capsys.readouterr().out == (
                "called frame.Show with args (True,)\n"
                "called AskOpenFileNames.check_input with args ()\n"
                "called Comparer.doit\n"
                "called app.MainLoop\n")

    def test_meld_vergelijking_fout(self, monkeypatch, capsys):
        """unittest for MainWindow.meld_vergelijking_fout
        """
        monkeypatch.setattr(testee.wx, 'MessageDialog', mockwx.MockMessageDialog)
        monkeypatch.setattr(testee.wx.Frame, 'GetPosition', mockwx.MockFrame.GetPosition)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(apptitel='App Title')
        testobj.meld_vergelijking_fout('message', '')
        assert capsys.readouterr().out == (
                "called Frame.GetPosition\n"
                "called Point.__init__ with args (1, 2)\n"
                f"called MessageDialog.__init__ with args ({testobj}, 'message', 'App Title')"
                f" {{'pos': (51, 52), 'style': {testee.wx.OK | testee.wx.ICON_INFORMATION}}}\n"
                "called MessageDialog.ShowModal\n")
        testobj.meld_vergelijking_fout('message', 'data')
        assert capsys.readouterr().out == (
                "called Frame.GetPosition\n"
                "called Point.__init__ with args (1, 2)\n"
                f"called MessageDialog.__init__ with args ({testobj}, 'message', 'App Title')"
                f" {{'pos': (51, 52), 'style': {testee.wx.OK | testee.wx.ICON_INFORMATION}}}\n"
                "called MessageDialog.SetExtendedMessage with args ('data',)\n"
                "called MessageDialog.ShowModal\n")

    def test_meld(self, monkeypatch, capsys):
        """unittest for MainWindow.meld
        """
        monkeypatch.setattr(testee.wx, 'MessageDialog', mockwx.MockMessageDialog)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(apptitel='App Title')
        testobj.meld('melding')
        assert capsys.readouterr().out == (
                f"called MessageDialog.__init__ with args ({testobj}, 'melding', 'App Title',"
                f" {testee.wx.OK | testee.wx.ICON_INFORMATION}) {{}}\n"
                "called MessageDialog.ShowModal\n"
                "called MessageDialog.Destroy\n")

    def test_refresh(self, monkeypatch, capsys):
        """unittest for MainWindow.refresh
        """
        def mock_setup():
            print('called MainWindow.setup_gui')
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.win = mockwx.MockFrame()
        assert capsys.readouterr().out == "called frame.__init__ with args () {}\n"
        testobj.setup_gui = mock_setup
        testobj.refresh()
        assert capsys.readouterr().out == ("called Frame.Destroy with args ()\n"
                                           "called MainWindow.setup_gui\n")

    def test_exit(self, monkeypatch, capsys):
        """unittest for MainWindow.exit
        """
        monkeypatch.setattr(testee.wx.Frame, 'Close', mockwx.MockFrame.Close)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.exit()
        assert capsys.readouterr().out == ("called Frame.Close with arg True\n")


def test_show_dialog(monkeypatch, capsys):
    """unittest for wx_gui.show_dialog
    """
    def mock_show(self):
        print('called Dialog.ShowModal')
        return not mockwx.wx.ID_OK
    def mock_get():
        nonlocal counter
        counter += 1
        print('called dialog.get_results')
        return 'message' if counter == 1 else ''
    monkeypatch.setattr(testee.wx, 'MessageBox', mockwx.mock_messagebox)
    parent = types.SimpleNamespace(parent=types.SimpleNamespace(apptitel='title',
                                                                gui=mockwx.MockFrame()))
    dlg = mockwx.MockDialog(parent)
    dlg.get_results = mock_get
    assert capsys.readouterr().out == ("called frame.__init__ with args () {}\n"
                                       "called Dialog.__init__ with args () {}\n")
    counter = 0
    assert testee.show_dialog(parent, dlg)
    assert capsys.readouterr().out == ("called Frame.GetPosition\n"
                                       "called Point.__init__ with args (1, 2)\n"
                                       "called dialog.SetPosition with args ((51, 52),)\n"
                                       "called Dialog.ShowModal\n"
                                       "called dialog.get_results\n"
                                       "called wx.MessageBox with args ('message', 'title') {}\n"
                                       "called Dialog.ShowModal\n"
                                       "called dialog.get_results\n")
    monkeypatch.setattr(mockwx.MockDialog, 'ShowModal', mock_show)
    assert not testee.show_dialog(parent, dlg)
    assert capsys.readouterr().out == ("called Frame.GetPosition\n"
                                       "called Point.__init__ with args (1, 2)\n"
                                       "called dialog.SetPosition with args ((51, 52),)\n"
                                       "called Dialog.ShowModal\n")


class TestAskOpenFilesGui:
    """unittest for wx_gui.AskOpenFilesGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for wx_gui.AskOpenFilesGui object

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
        assert capsys.readouterr().out == 'called AskOpenFilesGui.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.__init__
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx.Dialog, 'SetAutoLayout', mockwx.MockDialog.SetAutoLayout)
        monkeypatch.setattr(testee.wx.Dialog, 'SetSizer', mockwx.MockDialog.SetSizer)
        monkeypatch.setattr(testee.wx.Dialog, "__init__", mockwx.MockDialog.__init__)
        master = types.SimpleNamespace(parent=types.SimpleNamespace(gui="gui", apptitel="xxx"))
        testobj = testee.AskOpenFilesGui(master, "size", "title")
        assert capsys.readouterr().out == (
                "called Dialog.__init__ with args () {'size': 'size', 'title': 'title'}\n"
                "called BoxSizer.__init__ with args (8,)\n"
                "called dialog.SetSizer with args (vert sizer,)\n"
                "called dialog.SetAutoLayout with args (True,)\n"
                f"called vert sizer.Fit with args ({testobj},)\n")

    def test_add_ask_for_filename(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.add_ask_for_filename
        """
        def callback1():
            "dummy callback"
        def callback2():
            "dummy callback"
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        monkeypatch.setattr(testee.filebrowse, 'FileBrowseButtonWithHistory', mockwx.MockBrowse)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        testobj.fbbh_left = None
        testobj.fbbh_right = None
        testobj.fbbh1_callback = callback1
        testobj.fbbh2_callback = callback2
        result = testobj.add_ask_for_filename('size', 'label', 'browse', 'path', 'tooltip {}',
                                              'title {}', 'history', 'value')
        assert isinstance(result, testee.filebrowse.FileBrowseButtonWithHistory)
        assert testobj.fbbh_left is None
        assert testobj.fbbh_right == result
        assert capsys.readouterr().out == (
                # "called BoxSizer.__init__ with args (4,)\n"
                # f"called StaticText.__init__ with args ({testobj},)"
                # " {'label': 'label', 'size': (60, -1)}\n"
                # "called hori sizer.Add with args <item> (0, 2288, 5)\n"
                f"called FileBrowseButtonWithHistory.__init__ with args ({testobj},)"
                " {'size': (450, -1), 'labelText': '', 'buttonText': 'browse',"
                " 'toolTip': 'tooltip path', 'dialogTitle': 'title path',"
                f" 'changeCallback': {testobj.fbbh2_callback}}}\n"
                "called FileBrowseButtonWithHistory.SetHistory with arg history\n"
                "called FileBrowseButtonWithHistory.SetValue with args ('value',) {}\n")
                # "called hori sizer.Add with args <item> (0, 240, 5)\n"
                # "called vert sizer.Add with args <item> (0, 240, 5)\n")
        testobj.fbbh_right = None
        result = testobj.add_ask_for_filename('size', 'label', 'browse', 'linker', 'tooltip {}',
                                              'title {}', 'history', 'value')
        assert isinstance(result, testee.filebrowse.FileBrowseButtonWithHistory)
        assert testobj.fbbh_left == result
        assert testobj.fbbh_right is None
        assert capsys.readouterr().out == (
                # "called BoxSizer.__init__ with args (4,)\n"
                # f"called StaticText.__init__ with args ({testobj},)"
                # " {'label': 'label', 'size': (60, -1)}\n"
                # "called hori sizer.Add with args <item> (0, 2288, 5)\n"
                f"called FileBrowseButtonWithHistory.__init__ with args ({testobj},)"
                " {'size': (450, -1), 'labelText': '', 'buttonText': 'browse',"
                " 'toolTip': 'tooltip linker', 'dialogTitle': 'title linker',"
                f" 'changeCallback': {testobj.fbbh1_callback}}}\n"
                "called FileBrowseButtonWithHistory.SetHistory with arg history\n"
                "called FileBrowseButtonWithHistory.SetValue with args ('value',) {}\n")
                # "called hori sizer.Add with args <item> (0, 240, 5)\n"
                # "called vert sizer.Add with args <item> (0, 240, 5)\n")

    def test_create_fileselector_grid(self, monkeypatch, capsys):
        """unittest for text_create_fileselector_grid
        """
        monkeypatch.setattr(testee.wx, 'FlexGridSizer', mockwx.MockFlexGridSizer)
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        sel1 = mockwx.MockComboBox()       # niet het correcte type widget,
        sel2 = mockwx.MockButton()     # maar zo kan ik het verschil zien
        assert capsys.readouterr().out == ("called BoxSizer.__init__ with args (8,)\n"
                                           "called ComboBox.__init__ with args () {}\n"
                                           "called Button.__init__ with args () {}\n")
        testobj.create_fileselector_grid([('text1', sel1), ('text2', sel2)])
        assert capsys.readouterr().out == (
                "called FlexGridSizer.__init__ with args () {'cols': 2, 'vgap': 0, 'hgap': 4}\n"
                f"called StaticText.__init__ with args ({testobj},) {{'label': 'text1'}}\n"
                "called FlexGridSizer.Add with args MockStaticText (0, 2288, 5)\n"
                "called FlexGridSizer.Add with args MockComboBox (0, 240, 5)\n"
                f"called StaticText.__init__ with args ({testobj},) {{'label': 'text2'}}\n"
                "called FlexGridSizer.Add with args MockStaticText (0, 2288, 5)\n"
                "called FlexGridSizer.Add with args MockButton (0, 240, 5)\n"
                "called vert sizer.Add with args MockFlexGridSizer (0, 240, 5)\n")

    def test_build_typeselector(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.build_typeselector
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx, 'FlexGridSizer', mockwx.MockFlexGridSizer)
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        monkeypatch.setattr(testee.wx, 'RadioButton', mockwx.MockRadioButton)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        assert testobj.build_typeselector('comparetext', {}) == []
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (8,)\n"
                "called FlexGridSizer.__init__ with args () {'cols': 2, 'vgap': 0, 'hgap': 4}\n"
                f"called StaticText.__init__ with args ({testobj},) {{'label': 'comparetext'}}\n"
                "called FlexGridSizer.Add with args MockStaticText ()\n"
                "called vert sizer.Add with args MockFlexGridSizer (0, 240, 9)\n"
                "called vert sizer.Add with args MockBoxSizer (0, 240, 5)\n")
        result = testobj.build_typeselector('comparetext', {'y': ('yyy',), 'x': ('xxx',)})
        assert len(result) == len(('x', 'y'))
        assert isinstance(result[0][0], testee.wx.RadioButton)
        assert result[0][1] == 'x'
        assert isinstance(result[1][0], testee.wx.RadioButton)
        assert result[1][1] == 'y'
        assert capsys.readouterr().out == (
                "called BoxSizer.__init__ with args (8,)\n"
                "called FlexGridSizer.__init__ with args () {'cols': 2, 'vgap': 0, 'hgap': 4}\n"
                f"called StaticText.__init__ with args ({testobj},) {{'label': 'comparetext'}}\n"
                "called FlexGridSizer.Add with args MockStaticText ()\n"
                f"called RadioButton.__init__ with args ({testobj},) {{'label': 'xxx'}}\n"
                "called FlexGridSizer.Add with args MockRadioButton ()\n"
                f"called StaticText.__init__ with args ({testobj},) {{'label': ''}}\n"
                "called FlexGridSizer.Add with args MockStaticText ()\n"
                f"called RadioButton.__init__ with args ({testobj},) {{'label': 'yyy'}}\n"
                "called FlexGridSizer.Add with args MockRadioButton ()\n"
                "called vert sizer.Add with args MockFlexGridSizer (0, 240, 9)\n"
                "called vert sizer.Add with args MockBoxSizer (0, 240, 5)\n")

    def test_update_typeselector(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.update_typeselector
        """
        rb1 = mockwx.MockRadioButton()
        rb2 = mockwx.MockRadioButton()
        rb3 = mockwx.MockRadioButton()
        assert capsys.readouterr().out == ("called RadioButton.__init__ with args () {}\n"
                                           "called RadioButton.__init__ with args () {}\n"
                                           "called RadioButton.__init__ with args () {}\n")
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(options=[(rb1, 'x'), (rb2, 'y'), (rb3, 'z')],
                                               parent=types.SimpleNamespace(comparetype='y'))
        testobj.update_typeselector()
        assert capsys.readouterr().out == ("called radiobutton.SetValue with args (False,)\n"
                                           "called radiobutton.SetValue with args (False,)\n"
                                           "called radiobutton.SetValue with args (True,)\n"
                                           "called radiobutton.SetValue with args (False,)\n")

    def test_add_buttons(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.add_buttons
        """
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.wx, 'Button', mockwx.MockButton)
        monkeypatch.setattr(testee.wx, 'StaticText', mockwx.MockStaticText)
        monkeypatch.setattr(testee.wx.Dialog, 'SetAffirmativeId', mockwx.MockDialog.SetAffirmativeId)
        monkeypatch.setattr(testee.wx.Dialog, 'SetEscapeId', mockwx.MockDialog.SetEscapeId)
        monkeypatch.setattr(testee.wx.Dialog, 'SetSizer', mockwx.MockDialog.SetSizer)
        monkeypatch.setattr(testee.wx.Dialog, 'SetAutoLayout', mockwx.MockDialog.SetAutoLayout)

        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.vsizer = mockwx.MockBoxSizer(testee.wx.VERTICAL)
        assert capsys.readouterr().out == "called BoxSizer.__init__ with args (8,)\n"
        testobj.add_buttons('oktext', 'canceltext')
        assert capsys.readouterr().out == (
            f"called BoxSizer.__init__ with args ({testee.wx.HORIZONTAL},)\n"
            f"called StaticText.__init__ with args ({testobj},) {{'size': (155, -1)}}\n"
            "called hori sizer.Add with args"
            f" MockStaticText (0, {testee.wx.ALIGN_CENTRE | testee.wx.ALL}, 5)\n"
            f"called Button.__init__ with args ({testobj},) {{'label': 'o'}}\n"
            "called Button.GetId\n"
            "called dialog.SetAffirmativeId with args ('id',)\n"
            "called Button.SetHelpText with arg 'k'\n"
            "called hori sizer.Add with args"
            f" MockButton (0, {testee.wx.ALIGN_CENTRE | testee.wx.ALL}, 5)\n"
            f"called Button.__init__ with args ({testobj}, 403, 'c') {{}}\n"
            "called Button.GetId\n"
            "called dialog.SetEscapeId with args ('id',)\n"
            "called Button.SetHelpText with arg 'a'\n"
            "called hori sizer.Add with args"
            f" MockButton (0, {testee.wx.ALIGN_CENTRE | testee.wx.ALL}, 5)\n"
            "called vert sizer.Add with args"
            f" MockBoxSizer (0, {testee.wx.EXPAND | testee.wx.ALL}, 5)\n")

    def test_get_results(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.get_results
        """
        def mock_check():
            print('called Comparer.check_input')
            return 'got it'
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.master = types.SimpleNamespace(check_input=mock_check)
        assert testobj.get_results() == 'got it'
        assert capsys.readouterr().out == "called Comparer.check_input\n"

    def test_get_fbb_result(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.get_fbb_result
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.paths = {'left': 'aaa', 'right': 'bbb'}
        testobj.fbbh_left = 'xx'
        assert testobj.get_fbb_result('xx') == 'aaa'
        assert testobj.get_fbb_result('pp') == 'bbb'

    def test_get_radiobox_value(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.get_radiobox_value
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        rb = mockwx.MockCheckBox()
        rb.SetValue(True)
        assert capsys.readouterr().out == ("called CheckBox.__init__ with args () {}\n"
                                           "called checkbox.SetValue with args (True,)\n")
        assert testobj.get_radiobox_value(rb)
        assert capsys.readouterr().out == "called checkbox.GetValue\n"

    def test_fbbh1_callback(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.fbbh1_callback
        """
        evt = mockwx.MockEvent()
        assert capsys.readouterr().out == "called event.__init__ with args ()\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.paths = {'left': 'aaa', 'right': 'bbb'}
        testobj.fbbh1_callback(evt)
        assert capsys.readouterr().out == "called event.GetString\n"
        testobj.fbbh_left = mockwx.MockBrowse()
        assert capsys.readouterr().out == (
                "called FileBrowseButtonWithHistory.__init__ with args () {}\n")
        testobj.fbbh1_callback(evt)
        assert testobj.paths['left'] == 'qqq'
        assert capsys.readouterr().out == (
                "called event.GetString\n"
                "called FileBrowseButtonWithHistory.GetHistory\n"
                "called FileBrowseButtonWithHistory.SetHistory with arg ['qqq']\n"
                "called FileBrowseButtonWithHistory.GetHistoryControl\n"
                "called ComboBox.__init__ with args () {}\n"
                "called combobox.SetStringSelection with args ('qqq',)\n")
        testobj.paths['left'] = ''
        testobj.fbbh1_callback(evt)
        assert testobj.paths['left'] == 'qqq'
        assert capsys.readouterr().out == (
                "called event.GetString\n"
                "called FileBrowseButtonWithHistory.GetHistory\n")

    def test_fbbh2_callback(self, monkeypatch, capsys):
        """unittest for AskOpenFilesGui.fbbh2_callback
        """
        evt = mockwx.MockEvent()
        assert capsys.readouterr().out == "called event.__init__ with args ()\n"
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.paths = {'left': 'aaa', 'right': 'bbb'}
        testobj.fbbh2_callback(evt)
        assert capsys.readouterr().out == "called event.GetString\n"
        testobj.fbbh_right = mockwx.MockBrowse()
        assert capsys.readouterr().out == (
                "called FileBrowseButtonWithHistory.__init__ with args () {}\n")
        testobj.fbbh2_callback(evt)
        assert testobj.paths['right'] == 'qqq'
        assert capsys.readouterr().out == (
                "called event.GetString\n"
                "called FileBrowseButtonWithHistory.GetHistory\n"
                "called FileBrowseButtonWithHistory.SetHistory with arg ['qqq']\n"
                "called FileBrowseButtonWithHistory.GetHistoryControl\n"
                "called ComboBox.__init__ with args () {}\n"
                "called combobox.SetStringSelection with args ('qqq',)\n")
        testobj.paths['right'] = ''
        testobj.fbbh2_callback(evt)
        assert testobj.paths['right'] == 'qqq'
        assert capsys.readouterr().out == (
                "called event.GetString\n"
                "called FileBrowseButtonWithHistory.GetHistory\n")


class TestShowComparisonGui:
    """unittest for wx_gui.ShowComparisonGui
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for wx_gui.ShowComparisonGui object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called ShowComparisonGui.__init__ with args', args)
        monkeypatch.setattr(testee.ShowComparisonGui, '__init__', mock_init)
        testobj = testee.ShowComparisonGui()
        assert capsys.readouterr().out == 'called ShowComparisonGui.__init__ with args ()\n'
        return testobj

    def test_init(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.__init__
        """
        def mock_init(self, *args):
            """stub
            """
            print('called Panel.__init__ with args', args)
        monkeypatch.setattr(testee.wx.Panel, '__init__', mock_init)
        monkeypatch.setattr(testee.wx.Panel, 'SetSizer', mockwx.MockPanel.SetSizer)
        monkeypatch.setattr(testee.wx.Panel, 'SetAutoLayout', mockwx.MockPanel.SetAutoLayout)
        monkeypatch.setattr(testee.wx, 'BoxSizer', mockwx.MockBoxSizer)
        monkeypatch.setattr(testee.gizmos, 'TreeListCtrl', mockwx.MockTree)
        monkeypatch.setattr(testee.wx, 'Colour', mockwx.MockColour)
        parent = 'parent'
        testobj = testee.ShowComparisonGui(parent)
        assert testobj.parent == 'parent'
        assert isinstance(testobj.tree, testee.gizmos.TreeListCtrl)
        assert isinstance(testobj.rightonly_colour, testee.wx.Colour)
        assert isinstance(testobj.leftonly_colour, testee.wx.Colour)
        assert isinstance(testobj.difference_colour, testee.wx.Colour)
        assert capsys.readouterr().out == (
                "called Panel.__init__ with args ('parent',)\n"
                f"called BoxSizer.__init__ with args ({testee.wx.VERTICAL},)\n"
                f"called Tree.__init__ with args ({testobj},) {{'size': (1080, 600),"
                f" 'agwStyle': {testee.gizmos.TR_DEFAULT_STYLE
                | testee.gizmos.TR_HAS_VARIABLE_ROW_HEIGHT
                | testee.gizmos.TR_ELLIPSIZE_LONG_ITEMS | testee.gizmos.TR_FULL_ROW_HIGHLIGHT}}}\n"
                "called colour.__init__ with args (wx.Colour(-1, -1, -1, 255),)\n"
                "called colour.__init__ with args (wx.Colour(-1, -1, -1, 255),)\n"
                "called colour.__init__ with args (wx.Colour(-1, -1, -1, 255),)\n"
                "called Panel.SetAutoLayout with args (True,)\n"
                "called Panel.SetSizer with args (vert sizer,)\n"
                f"called vert sizer.Fit with args ({testobj},)\n"
                f"called vert sizer.Add with args MockTree (1, {testee.wx.EXPAND})\n")

    def test_setup_nodata_columns(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.setup_nodata_columns
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        testobj.root = mockwx.MockTreeItem('root')
        assert capsys.readouterr().out == ("called Tree.__init__ with args () {}\n"
                                           "called TreeItem.__init__ with args ('root',)\n")
        testobj.setup_nodata_columns('root_text', 'leftcaption', 'rightcaption')
        assert capsys.readouterr().out == (
                "called tree.AppendItem with args (root, 'root_text')\n"
                "called tree.SetItemText with args ('appended item', 'leftcaption')\n"
                "called tree.SetItemText with args ('appended item', 'rightcaption')\n")

    def test_show_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.finish_init
        """
        monkeypatch.setattr(testee.wx.Panel, 'Show', mockwx.MockPanel.Show)
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.show_tree()
        assert capsys.readouterr().out == (
                "called Panel.Show with args (True,)\n")

    def test_refresh_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.refresh_tree
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.root = 'root'
        testobj.tree = mockwx.MockTree()
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        testobj.refresh_tree()
        assert capsys.readouterr().out == "called tree.Expand with args ('root',)\n"

    def test_init_tree(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.init_tree
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        testobj.init_tree('caption', 'left_title', 'right_title')
        assert testobj.root == 'The Root'
        assert capsys.readouterr().out == ("called Tree.__init__ with args () {}\n"
                                           "called tree.DeleteAllItems\n"
                                           "called tree.AddColumn with args ('caption',)\n"
                                           "called tree.AddColumn with args ('left_title',)\n"
                                           "called tree.AddColumn with args ('right_title',)\n"
                                           "called tree.SetMainColumn with args (0,)\n"
                                           "called tree.SetColumnWidth with args (0, 280)\n"
                                           "called tree.SetColumnWidth with args (1, 400)\n"
                                           "called tree.SetColumnWidth with args (2, 400)\n"
                                           "called tree.AddRoot with args ('',)\n")

    def test_build_header(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.build_header
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        testobj.root = 'root'
        assert testobj.build_header('section') == "appended item"
        assert capsys.readouterr().out == "called tree.AppendItem with args ('root', 'section')\n"

    def test_colorize_header(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.colorize_header
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        testobj.rightonly_colour = 'rrr'
        testobj.leftonly_colour = 'lll'
        testobj.difference_colour = 'ddd'
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        testobj.colorize_header('node', True, True, False)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'ddd')\n")
        testobj.colorize_header('node', True, False, False)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'rrr')\n")
        testobj.colorize_header('node', False, True, False)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'lll')\n")
        testobj.colorize_header('node', False, False, False)
        assert capsys.readouterr().out == ""
        testobj.colorize_header('node', True, True, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'ddd')\n")
        testobj.colorize_header('node', True, False, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'rrr')\n"
                "called tree.SetItemTextColour with args ('node', 'ddd')\n")
        testobj.colorize_header('node', False, True, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'lll')\n"
                "called tree.SetItemTextColour with args ('node', 'ddd')\n")
        testobj.colorize_header('node', False, False, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'ddd')\n")

    def test_build_child(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.build_child
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        assert testobj.build_child('header', 'option') == "appended item"
        assert capsys.readouterr().out == "called tree.AppendItem with args ('header', 'option')\n"

    def test_colorize_child(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.colorize_child
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        testobj.rightonly_colour = 'rrr'
        testobj.leftonly_colour = 'lll'
        testobj.difference_colour = 'ddd'
        testobj.colorize_child('node', True, True, False)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'lll')\n")
        testobj.colorize_child('node', True, False, False)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'rrr')\n")
        testobj.colorize_child('node', False, True, False)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'lll')\n")
        testobj.colorize_child('node', False, False, False)
        assert capsys.readouterr().out == ""
        testobj.colorize_child('node', True, True, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'lll')\n")
        testobj.colorize_child('node', True, False, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'rrr')\n")
        testobj.colorize_child('node', False, True, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'lll')\n")
        testobj.colorize_child('node', False, False, True)
        assert capsys.readouterr().out == (
                "called tree.SetItemTextColour with args ('node', 'ddd')\n")

    def test_set_node_text(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.set_node_text
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        testobj.set_node_text('node', 'column', 'value')
        assert capsys.readouterr().out == (
                "called tree.SetItemText with args ('node', 'value', 'column')\n")
        testobj.set_node_text('node', 'column', '')
        assert capsys.readouterr().out == ""

    def test_get_parent(self, monkeypatch, capsys):
        """unittest for ShowComparisonGui.get_parent
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.tree = mockwx.MockTree()
        assert capsys.readouterr().out == "called Tree.__init__ with args () {}\n"
        assert testobj.get_parent('node') == "parent"
        assert capsys.readouterr().out == ("called tree.GetItemParent with args ('node',)\n")
