"""Presentation logic for Compare Tool - PyQT5 version
"""
from os import getcwd
# from os.path import exists
import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.gizmos as gizmos
# import wx.lib.agw.customtreectrl as CTC
# import wx.lib.agw.hypertreelist as HTL
import actif_shared as shared


class AskOpenFiles(wx.Dialog):
    """dialog om de te vergelijken bestanden op te geven

    voor elk file een combobox om direct een filenaam op te geven of te kiezen
    uit een lijst met eerder gebruikte, met een button ernaast om de filenaam te
    selecteren met behulp van een file selector dialoog
    de te tonen lijsten worden bewaard in een bestand aangegeven door self.inifile
    """
    def __init__(self, parent, id, title, size=(400, 200), pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size, pos, style)
        self.parent = parent

        tooltip = ("Geef hier de naam van het {} te vergelijken ini file "
                   "of kies er een uit een lijst met recent gebruikte")
        title = "Selecteer het {} ini file"
        self.fbbh1 = filebrowse.FileBrowseButtonWithHistory(self, -1, size=(450, -1),
                                                            labelText="Vergelijk:",
                                                            buttonText="Zoek",
                                                            toolTip=tooltip.format('eerste'),
                                                            dialogTitle=title.format("eerste"),
                                                            changeCallback=self.fbbh1_callback)
        self.fbbh1.SetHistory(self.parent.ini.mru_left)
        self.fbbh1.SetValue(self.parent.lhs_path)

        self.fbbh2 = filebrowse.FileBrowseButtonWithHistory(self, -1, size=(450, -1),
                                                            labelText="Met:       ",
                                                            buttonText="Zoek",
                                                            toolTip=tooltip.format('tweede'),
                                                            dialogTitle=title.format('tweede'),
                                                            changeCallback=self.fbbh2_callback)
        self.fbbh2.SetHistory(self.parent.ini.mru_right)
        self.fbbh2.SetValue(self.parent.rhs_path)

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.fbbh1, 0, wx.ALL, 5)
        box.Add(self.fbbh2, 0, wx.ALL, 5)
        sizer.Add(box, 0, wx.ALL, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        gbox = wx.FlexGridSizer(cols=2, vgap=0, hgap=4)
        gbox.Add(wx.StaticText(self, label='Soort vergelijking:'))
        self.sel = []
        for ix, type_ in enumerate(sorted(shared.comparetypes)):
            if ix > 0:
                gbox.Add(wx.StaticText(self, label=''))
            text = shared.comparetypes[type_][0]
            rb = wx.RadioButton(self, label=text)
            gbox.Add(rb)
            if self.parent.comparetype == type_:
                rb.SetValue(True)
            self.sel.append((rb, type_))
        box.Add(gbox, 0, wx.ALL, 9)
        sizer.Add(box, 0, wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        btn = wx.Button(self, label="&Gebruiken")
        self.SetAffirmativeId(btn.GetId())
        box.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        btn = wx.Button(self, 403, "&Afbreken")
        self.SetEscapeId(btn.GetId())
        btn.SetHelpText("Klik hier om zonder wijzigingen terug te gaan naar het hoofdscherm")
        box.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def fbbh1_callback(self, evt):
        "callback voor bovenste/linker/source file selector"
        if hasattr(self, 'fbbh1'):
            self.path_left = evt.GetString()
            history = self.fbbh1.GetHistory()
            if self.path_left not in history:
                history.append(self.path_left)
                self.fbbh1.SetHistory(history)
                self.fbbh1.GetHistoryControl().SetStringSelection(self.path_left)

    def fbbh2_callback(self, evt):
        "callback voor onderste/rechter/target file selector"
        if hasattr(self, 'fbbh2'):
            self.path_right = evt.GetString()
            history = self.fbbh2.GetHistory()
            if self.path_right not in history:
                history.append(self.path_right)
                self.fbbh2.SetHistory(history)
                self.fbbh2.GetHistoryControl().SetStringSelection(self.path_right)


class ShowComparison(wx.Panel):
    """Part of the main window showing the comparison as a tree
    """
    def __init__(self, parent):
        # wx.Panel.__init__(self, parent)  # , -1 ,size=(1080, 960))
        super().__init__(parent)
        self.parent = parent

        # als ik deze uitzet vult deze initieel het hele hoofdscherm
        # self.Bind(wx.EVT_SIZE, self.on_size)

        # die show_tooltip switch zorgt ervoor dat de teksten onleesbaar worden
        self.tree = gizmos.TreeListCtrl(self, -1, size=(1080, 600),
                                        agwStyle=gizmos.TR_DEFAULT_STYLE |
                                                 gizmos.TR_HAS_VARIABLE_ROW_HEIGHT |
                                                 # 0x100000 | # wx.TR_TOOLTIP_ON_LONG_ITEMS |
                                                 gizmos.TR_ELLIPSIZE_LONG_ITEMS |
                                                 gizmos.TR_FULL_ROW_HIGHLIGHT)  # |
                                                 # CTC.TR_TOOLTIP_ON_LONG_ITEMS |
                                                 # HTL.TR_ELLIPSIZE_LONG_ITEMS)
        self.rightonly_colour = wx.Colour(wx.BLUE)
        self.leftonly_colour = wx.Colour(wx.GREEN)
        self.difference_colour = wx.Colour(wx.RED)
        ## self.inversetext_colour = wx.Colour(Qt.WHITE)

        self.init_tree("Sectie / Optie:", "waarde in %s" % self.parent.lhs_path,
                       "waarde in %s" % self.parent.rhs_path)

        if not self.parent.data:
            first = self.tree.AppendItem(self.root, 'geen bestanden geladen')
            self.tree.SetItemText(first, "niks om te laten zien", 1)
            self.tree.SetItemText(first, "hier ook niet", 2)

        self.refresh_tree()

        ## self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        ## self.tree.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.on_left_up)
        ## self.tree.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.on_doubleclick)
        ## sizer = wx.BoxSizer(wx.VERTICAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.tree, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.Show(True)

    def refresh_tree(self):
        """(re)do the comparison
        """
        shared.refresh_tree(self)
        self.tree.Expand(self.root)
        # self.tree.ExpandAllChildren(self.root)

    # API methods to be called from the specific refresh functions
    def init_tree(self, caption, left_title, right_title):
        "setup empty tree with given titles"
        self.tree.DeleteAllItems()
        # self.tree.ClearColumns()
        self.tree.AddColumn(caption)
        self.tree.AddColumn(left_title)
        self.tree.AddColumn(right_title)
        self.tree.SetMainColumn(0)  # the one with the tree in it
        self.tree.SetColumnWidth(0, 280)
        self.tree.SetColumnWidth(1, 400)
        self.tree.SetColumnWidth(2, 400)
        self.root = self.tree.AddRoot("")

    def build_header(self, section):
        """create a header item
        """
        return self.tree.AppendItem(self.root, section)

    # def colorize_header(self, item, flags):
    def colorize_header(self, node, rightonly, leftonly, difference):
        """visualize the difference by coloring the header
        """
        if rightonly and not leftonly:
            self.tree.SetItemTextColour(node, self.rightonly_colour)
        if leftonly and not rightonly:
            self.tree.SetItemTextColour(node, self.leftonly_colour)
        if difference or (leftonly and rightonly):
            self.tree.SetItemTextColour(node, self.difference_colour)

    def build_child(self, header, option):
        """create a child under this header
        """
        return self.tree.AppendItem(header, option)

    def colorize_child(self, node, rightonly, leftonly, difference):
        """visualize the difference by coloring the child texts
        """
        if leftonly:  # and not rightonly:
            self.tree.SetItemTextColour(node, self.leftonly_colour)
        elif rightonly:  # and not leftonly:
            self.tree.SetItemTextColour(node, self.rightonly_colour)
        elif difference:  # or (leftonly and rightonly):
            self.tree.SetItemTextColour(node, self.difference_colour)

    def set_node_text(self, node, column, value):
        """set tooltip as well as text so that truncated text can be viewed in full
        self is only used for API's sake
        """
        if value:
            self.tree.SetItemText(node, value, column)
        #  node.setToolTip(column, value)

    def get_parent(self, node):
        """retrieve parent of current node
        """
        return self.tree.GetItemParent(node)


class MainWindow(wx.Frame):
    """Application screen
    """
    def __init__(self, parent, fileargs, method):
        print('in MainWindow, fileargs is,', fileargs, 'method is', method)
        self.lhs_path, self.rhs_path = shared.get_input_paths(fileargs)
        # voor nu gebruiken we een vaste default voor het method argument
        self.comparetype = method
        self.hier = getcwd()
        self.ini = shared.IniFile(self.hier + "/actif.ini")
        self.ini.read()
        self.data = {}
        self.selectedOption = ''

        wx.Frame.__init__(self, parent, wx.ID_ANY, shared.apptitel, size=(1080, 600),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        # self.CreateStatusBar()

        self.setup_menu()
        self.win = ShowComparison(self)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.win, 1, wx.EXPAND)  # | wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        self.Show(True)
        if self.lhs_path and self.rhs_path:
            self.doit()
        else:
            self.about()
            self.open()

    def setup_menu(self):
        """Setting up the menu
        """
        filemenu = wx.Menu()
        filemenu.Append(shared.ID_OPEN, "&Open/kies\tCtrl+O", " Kies de te vergelijken ini files")
        filemenu.Append(shared.ID_DOIT, "&Vergelijk\tF5", " Orden en vergelijk de ini files")
        filemenu.AppendSeparator()
        filemenu.Append(shared.ID_EXIT, "E&xit\tCtrl+Q", " Terminate the program")
        helpmenu = wx.Menu()
        helpmenu.Append(shared.ID_ABOUT, "&About\tF1", " Information about this program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Connect(shared.ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.open)
        self.Connect(shared.ID_DOIT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.doit)
        self.Connect(shared.ID_EXIT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.exit)
        self.Connect(shared.ID_ABOUT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.about)

    def open(self, event=None):
        """ask for files to compare
        """
        x, y = self.GetPosition()
        with AskOpenFiles(self, -1, shared.apptitel, pos=(x + 50, y + 50)) as dlg:
            retry = True
            while retry:
                result = dlg.ShowModal()
                if result == dlg.GetAffirmativeId():
                    self.lhs_path = dlg.path_left
                    self.rhs_path = dlg.path_right
                    for rb, type_ in dlg.sel:
                        if rb.GetValue():
                            self.comparetype = type_
                            break
                    retry = self.doit()
                else:
                    retry = False

    def doit(self, event=None):
        """perform action
        """
        mld = shared.check_input(self.lhs_path, self.rhs_path, self.comparetype)
        if mld:
            wx.MessageBox(mld, shared.apptitel)
            return True
        print('in mainwindow.doit, starting compare')
        ok, data = shared.do_compare(self.lhs_path, self.rhs_path, self.comparetype)
        with open('data.txt', 'w') as out:
            print('got data:', data, file=out)
        if not ok or not data:
            message = data[0] if data else 'Vergelijking mislukt'
            x, y = self.GetPosition()
            with wx.MessageDialog(self, message, shared.apptitel, pos=(x + 50, y + 50),
                                  style=wx.OK | wx.ICON_INFORMATION) as dlg:
                if data:
                    dlg.SetExtendedMessage(''.join(data[1]))
                dlg.ShowModal()
            return True  # True brengt ons terug in de invoerlus in open()
        if self.lhs_path in self.ini.mru_left:
            self.ini.mru_left.remove(self.lhs_path)
        self.ini.mru_left.insert(0, self.lhs_path)
        if self.rhs_path in self.ini.mru_right:
            self.ini.mru_right.remove(self.rhs_path)
        self.ini.mru_right.insert(0, self.rhs_path)
        self.ini.write()
        if data:
            self.selectedOption = data[0]
        self.data = data  # [1:]
        # panel opnieuw opbouwen in plaats van een refresh doen
        self.win.Destroy()
        self.win = ShowComparison(self)
        return False

    def about(self, event=None):
        """opening blurb
        """
        dlg = wx.MessageDialog(self,
                               ("Hulpmiddel om twee ini files te vergelijken, "
                                "maakt niet uit hoe door elkaar de secties en entries ook zitten"),
                               shared.apptitel, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def exit(self, event):
        "quit"
        self.Close(True)


def main(args):
    """main function"""
    ## print a1, a2
    app = wx.App()
    frame = MainWindow(None, (args.input), method=args.method)
    app.MainLoop()
