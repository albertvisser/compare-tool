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
        super().__init__(parent, wx.ID_ANY, self.master.apptitel, size=(1080, 600),
                         style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)

        self.setup_menu()
        # self.setup_gui()

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
                item_id, itemtitle, shortcut, text, callback = item
                menu.Append(item_id, f'{itemtitle}\t{shortcut}', text)
                self.Connect(item_id, wx.ID_ANY, wx.wxEVT_COMMAND_MENU_SELECTED, callback)
            menubar.Append(menu, title)
        self.SetMenuBar(menubar)

    def go(self):  # , leftpath, rightpath, method):
        "display the screen and start the event loop"
        self.Show(True)
        mld = self.master.inputgetter.check_input()
        if mld:
            wx.MessageBox(mld, self.master.apptitel)
            self.master.open()
        else:
            self.master.doit()  # first_time=True)
        self.app.MainLoop()

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
        # wx.MessageBox(meld, self.master.apptitel)

    def refresh(self):
        """panel opnieuw opbouwen in plaats van een refresh doen
        maar ik vraag me af of dit zo wel werkt - nou kennelijk wel
        """
        self.win.Destroy()
        self.setup_gui()

    def exit(self):
        "quit"
        self.Close(True)


def show_dialog(master, parent):
    """show a dialog and return the result
    """
    dlg = master.gui
    x, y = parent.GetPosition()
    # with cls(parent, -1, parent.parent.apptitel, pos=(x + 50, y + 50)) as dlg:
    dlg.SetPosition((x + 50, y + 50))
    while True:
        ok = dlg.ShowModal() == dlg.GetAffirmativeId()
        if ok:
            mld = dlg.get_results()
            if mld:
                wx.MessageBox(mld, master.parent.apptitel)
            else:
                break
        else:
            break
    #         return False
    # return True
    # return dlg.ShowModal() == dlg.GetAffirmativeId()
    return ok


class AskOpenFilesGui(wx.Dialog):
    """dialog om de te vergelijken bestanden op te geven

    voor elk file een combobox om direct een filenaam op te geven of te kiezen
    uit een lijst met eerder gebruikte, met een button ernaast om de filenaam te
    selecteren met behulp van een file selector dialoog
    de te tonen lijsten worden bewaard in een bestand aangegeven door self.inifile
    """
    def __init__(self, master, size, title):
        self.master = master
        physical_parent = master.parent.gui
        super().__init__(physical_parent, size=size, title=title)
        self.paths = {'left': '', 'right': ''}
        # self.fbbh_left = self.fbbh_right = None
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vsizer)
        self.SetAutoLayout(True)
        self.vsizer.Fit(self)

    def add_ask_for_filename(self, size, label, browse, path, tooltip, title, history, value):
        "add a line for selecting a file"
        callback = self.fbbh1_callback if path == 'linker' else self.fbbh2_callback
        fbbh = filebrowse.FileBrowseButtonWithHistory(self, size=(450, -1),
                                                      labelText='',
                                                      buttonText=browse,
                                                      toolTip=tooltip.format(path),
                                                      dialogTitle=title.format(path),
                                                      changeCallback=callback)
        fbbh.SetHistory(history)
        fbbh.SetValue(value)
        if path == 'linker':
            self.fbbh_left = fbbh
        else:
            self.fbbh_right = fbbh
        return fbbh

    def create_fileselector_grid(self, linedefs):
        "build a grid for the file selector widgets"
        gbox = wx.FlexGridSizer(cols=2, vgap=0, hgap=4)
        for linedef in linedefs:
            caption, selector = linedef
            text = wx.StaticText(self, label=caption)  # , size=(60, -1))
            gbox.Add(text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, 5)
            gbox.Add(selector, 0, wx.ALL, 5)
        self.vsizer.Add(gbox, 0, wx.ALL, 5)

    def build_typeselector(self, comparetext, choices):
        "build a collection of radiobuttons"
        box = wx.BoxSizer(wx.VERTICAL)
        gbox = wx.FlexGridSizer(cols=2, vgap=0, hgap=4)
        gbox.Add(wx.StaticText(self, label=comparetext))
        optionlist = []
        for ix, cmptype in enumerate(sorted(choices)):
            if ix > 0:
                gbox.Add(wx.StaticText(self, label=''))
            text = choices[cmptype][0]
            rb = wx.RadioButton(self, label=text)
            gbox.Add(rb)
            optionlist.append((rb, cmptype))
        box.Add(gbox, 0, wx.ALL, 9)
        self.vsizer.Add(box, 0, wx.ALL, 5)
        return optionlist

    def update_typeselector(self):
        "gebruikte vergelijkingsmethode aangeven bij uitsturen"
        for rb, cmptype in self.master.options:
            rb.SetValue(False)
            if cmptype == self.master.parent.comparetype:
                rb.SetValue(True)

    def add_buttons(self, oktext, canceltext):
        "add the confirm / reject buttons"
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        btn = wx.Button(self, label=oktext[0])
        self.SetAffirmativeId(btn.GetId())
        btn.SetHelpText(oktext[1])
        box.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        btn = wx.Button(self, 403, canceltext[0])
        self.SetEscapeId(btn.GetId())
        btn.SetHelpText(canceltext[1])
        box.Add(btn, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.vsizer.Add(box, 0, wx.EXPAND | wx.ALL, 5)

    def get_results(self):
        """transmit the chosen data
        """
        return self.master.check_input()

    def get_fbb_result(self, fbb):
        """return the filebrowsebutton's selected / entered name
        """
        if fbb == self.fbbh_left:
            return self.paths['left']
        return self.paths['right']

    def get_radiobox_value(self, rb):
        """return the radiobutton's value (checked or not)
        """
        return rb.GetValue()

    def fbbh1_callback(self, evt):
        "callback voor bovenste/linker/source file selector"
        self.paths['left'] = evt.GetString()
        if not hasattr(self, 'fbbh_left'):  # voor wanneer dei widget nog niet gedefinieerd is
            return
        history = self.fbbh_left.GetHistory()
        if self.paths['left'] not in history:
            history.append(self.paths['left'])
            self.fbbh_left.SetHistory(history)
            self.fbbh_left.GetHistoryControl().SetStringSelection(self.paths['left'])

    def fbbh2_callback(self, evt):
        "callback voor onderste/rechter/target file selector"
        self.paths['right'] = evt.GetString()
        if not hasattr(self, 'fbbh_right'):  # voor wanneer de widget nog niet gedefinieerd is
            return
        history = self.fbbh_right.GetHistory()
        if self.paths['right'] not in history:
            history.append(self.paths['right'])
            self.fbbh_right.SetHistory(history)
            self.fbbh_right.GetHistoryControl().SetStringSelection(self.paths['right'])


class ShowComparisonGui(wx.Panel):
    """Part of the main window showing the comparison as a tree
    """
    def __init__(self, parent):
        super().__init__(parent.gui)
        self.parent = parent
        vsizer = wx.BoxSizer(wx.VERTICAL)

        self.tree = gizmos.TreeListCtrl(self, size=(1080, 600), agwStyle=gizmos.TR_DEFAULT_STYLE
                                        | gizmos.TR_HAS_VARIABLE_ROW_HEIGHT
                                        # | 0x100000 | # wx.TR_TOOLTIP_ON_LONG_ITEMS
                                        | gizmos.TR_ELLIPSIZE_LONG_ITEMS
                                        | gizmos.TR_FULL_ROW_HIGHLIGHT)  #
                                        # | CTC.TR_TOOLTIP_ON_LONG_ITEMS
                                        # | HTL.TR_ELLIPSIZE_LONG_ITEMS)
        ## self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        ## self.tree.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.on_left_up)
        ## self.tree.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.on_doubleclick)
        self.rightonly_colour = wx.Colour(wx.BLUE)
        self.leftonly_colour = wx.Colour(wx.GREEN)
        self.difference_colour = wx.Colour(wx.RED)
        ## self.inversetext_colour = wx.Colour(Qt.WHITE)
        self.SetAutoLayout(True)
        self.SetSizer(vsizer)
        vsizer.Fit(self)
        vsizer.Add(self.tree, 1, wx.EXPAND)

    def setup_nodata_columns(self, root_text, leftcaption, rightcaption):
        "set header texts when there's no data to be shown"
        first = self.tree.AppendItem(self.root, root_text)
        self.tree.SetItemText(first, leftcaption)
        self.tree.SetItemText(first, rightcaption)

    def show_tree(self):
        "(do layout and) render the area"
        self.Show(True)

    def refresh_tree(self):
        """after (re)doing the comparison
        """
        self.tree.Expand(self.root)

    # API methods to be called from the specific refresh functions
    def init_tree(self, caption, *args):  # left_title, right_title):
        "setup empty tree with given titles"
        left_title, right_title = self.parent.get_titles(*args)
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
