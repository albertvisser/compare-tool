"""Presentation logic for Compare Tool - wxPython version
"""
import wx
import wx.lib.filebrowsebutton as filebrowse
from wx.lib import gizmos
# import wx.lib.agw.customtreectrl as CTC
# import wx.lib.agw.hypertreelist as HTL


class MainWindow(wx.Frame):
    """Application screen
    """
    def __init__(self, master):
        self.app = wx.App()
        self.master = master
        parent = None
        super().__init__(self, parent, wx.ID_ANY, self.master.apptitel, size=(1080, 600),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.setup_menu()
        self.setup_gui()

    def setup_gui(self):
        "(re)build the screen"
        self.win = self.master.showcomp.gui
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(self.win, 1, wx.EXPAND)  # | wx.ALL)
        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)

    def setup_menu(self):
        """Setting up the menu
        """
        menubar = wx.MenuBar()
        for title, options in self.master.menudict.items():
            menu = wx.Menu()
            for item in options:
                if not item:
                    menu.AppendSeparator()
                    continue
                item_id, title, shortcut, text, callback = item
                menu.Append(item_id, '\t'.join((title, shortcut)), text)
                self.Connect(item_id, wx.NewId(), wx.wxEVT_COMMAND_MENU_SELECTED, callback)
            menubar.Append(menu, title)
        self.SetMenuBar(menubar)

    def go(self):
        "display the screen and start the event loop"
        self.Show(True)
        self.app.MainLoop()

    def meld_input_fout(self, mld):
        "show invalid input message"
        wx.MessageBox(mld, self.master.apptitel)

    def meld_vergelijking_fout(self, message, data):
        "show comparison error(s)"
        x, y = self.GetPosition()
        with wx.MessageDialog(self, message, self.master.apptitel, pos=(x + 50, y + 50),
                              style=wx.OK | wx.ICON_INFORMATION) as dlg:
            if data:
                dlg.SetExtendedMessage(''.join(data))
            dlg.ShowModal()

    def meld(self, melding):
        "show a message"
        dlg = wx.MessageDialog(self, melding, self.master.apptitel, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def refresh(self):
        """panel opnieuw opbouwen in plaats van een refresh doen
        maar ik vraag me af of dit zo wel werkt
        """
        self.win.Destroy()
        self.setup_gui()

    def exit(self, event):
        "quit"
        self.Close(True)


def show_dialog(parent, cls):
    """show a dialog and return the result
    """
    x, y = parent.GetPosition()
    with cls(parent, -1, parent.master.apptitel, pos=(x + 50, y + 50)) as dlg:
        result = dlg.ShowModal() == dlg.GetAffirmativeId()
        if result:
            dlg.accept()
    return result


class AskOpenFilesGui(wx.Dialog):
    """dialog om de te vergelijken bestanden op te geven

    voor elk file een combobox om direct een filenaam op te geven of te kiezen
    uit een lijst met eerder gebruikte, met een button ernaast om de filenaam te
    selecteren met behulp van een file selector dialoog
    de te tonen lijsten worden bewaard in een bestand aangegeven door self.inifile
    """
    def __init__(self, parent, title, size):
        self.logical_parent = parent
        physical_parent = parent.gui
        super().__init__(self, physical_parent, pos=wx.DefaultPosition, title=title, size=size,
                         style=wx.DEFAULT_DIALOG_STYLE)

    def add_ask_for_filename(self, size, label, browse, path, tooltip, title, history, value):
        "add a line for selecting a file"
        callback = self.fbbh1_callback if path == 'linker' else self.fbbh2_callback
        fbbh = filebrowse.FileBrowseButtonWithHistory(self, -1, size=(450, -1),
                                                      labelText=label,
                                                      buttonText=browse,
                                                      toolTip=tooltip.format(path),
                                                      dialogTitle=title.format(path),
                                                      changeCallback=callback)
        fbbh.SetHistory(history)
        fbbh.SetValue(value)
        return fbbh

    def build_screen(self, leftfile, rightfile, comparetext, choices, oktext, canceltext):
        "do the screen layout"
        self.fbbh1, self.fbbh2 = leftfile, rightfile
        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.fbbh1, 0, wx.ALL, 5)
        box.Add(self.fbbh2, 0, wx.ALL, 5)
        sizer.Add(box, 0, wx.ALL, 5)

        box = wx.BoxSizer(wx.VERTICAL)
        gbox = wx.FlexGridSizer(cols=2, vgap=0, hgap=4)
        gbox.Add(wx.StaticText(self, label=comparetext))
        self.sel = []
        for ix, type_ in enumerate(sorted(choices)):
            if ix > 0:
                gbox.Add(wx.StaticText(self, label=''))
            text = choices[type_][0]
            rb = wx.RadioButton(self, label=text)
            gbox.Add(rb)
            if self.logical_parent.comparetype == type_:
                rb.SetValue(True)
            self.sel.append((rb, type_))
        box.Add(gbox, 0, wx.ALL, 9)
        sizer.Add(box, 0, wx.ALL, 5)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        btn = wx.Button(self, label=oktext[0])
        self.SetAffirmativeId(btn.GetId())
        btn.SetHelpText(oktext[1])
        box.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        btn = wx.Button(self, 403, canceltext[0])
        self.SetEscapeId(btn.GetId())
        btn.SetHelpText(canceltext[1])
        box.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.EXPAND | wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def accept(self):
        """transmit the chosen data
        """
        self.master.parent.lhs_path = self.path_left
        self.master.parent.rhs_path = self.path_right
        for rb, type_ in self.sel:
            if rb.GetValue():
                self.master.parent.comparetype = type_
                break

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


class ShowComparisonGui(wx.Panel):
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

    def setup_nodata_columns(self, root_text, leftcaption, rightcaption):
        "set header texts when there's no data to be shown"
        first = self.tree.AppendItem(self.root, root_text)
        self.tree.SetItemText(first, leftcaption)
        self.tree.SetItemText(first, rightcaption)

    def finish_init(self):
        "(do layout and) render the area"
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
        """after (re)doing the comparison
        """
        self.tree.Expand(self.root)

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
