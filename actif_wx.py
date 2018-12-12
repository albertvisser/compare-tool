"""Presentation logic for Compare Tool - PyQT5 version
"""
# ik laat het "synchronized scrollen" even zitten en daarmee ook de keuze verticaal / horizontaal
# import images
from configparser import ConfigParser
from conf_comp import compare_configs, compare_configs_2, MissingSectionHeaderError
from os import getcwd
from os.path import exists
import wx
import wx.lib.filebrowsebutton as filebrowse
import wx.lib.gizmos.treelistctrl as TLC
ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
apptitel = "Albert's compare-tool voor ini-files"


class MainWindow(wx.Frame):
    """Application screen
    """
    def __init__(self, parent, id, title, appargs=None):
        if appargs is None: appargs = ()
        self.hier = getcwd()
        self.inifile = self.hier + "/actif.ini"
        self.readini()
        self.lhs_path = 'linkerbestand'
        self.rhs_path = 'rechterbestand'
        self.data = {}
        self.selectedOption = ''

        wx.Frame.__init__(self, parent, wx.ID_ANY, title, size=(1080, 600),
                          style=wx.DEFAULT_FRAME_STYLE | wx.NO_FULL_REPAINT_ON_RESIZE)
        self.CreateStatusBar()

        filemenu = wx.Menu()
        filemenu.Append(ID_OPEN, "&Open/kies", " Kies de te vergelijken ini files")
        filemenu.Append(ID_DOIT, "&Vergelijk", " Orden en vergelijk de ini files")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT, "E&xit", " Terminate the program")
        helpmenu = wx.Menu()
        helpmenu.Append(ID_ABOUT, "&About", " Information about this program")

        menuBar = wx.MenuBar()
        menuBar.Append(filemenu, "&File")
        menuBar.Append(helpmenu, "&Help")
        self.SetMenuBar(menuBar)
        self.Connect(ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.open)
        self.Connect(ID_DOIT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.doit)
        self.Connect(ID_EXIT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.exit)
        self.Connect(ID_ABOUT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.about)
        self.win = ShowComparison(self)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # hsizer = wx.BoxSizer(wx.HORIZONTAL)
        vsizer.Add(self.win, 1, wx.EXPAND | wx.ALL)
        # vsizer.Add(hsizer, 0, wx.EXPAND | wx.ALL)
        self.SetAutoLayout(True)
        ## self.SetSizer(sizer)
        self.SetSizer(vsizer)
        # sizer.Fit(self)
        # vsizer.SetSizeHints(self)
        vsizer.Fit(self)
        self.Show(True)
        ## self.toon_scherm()
        ## print appargs
        if len(appargs) == 2 and appargs[0] is not None and appargs[1] is not None:
            self.lhs_path = appargs[0]
            self.rhs_path = appargs[1]
            self.doit(None)
        else:
            self.open()

    def readini(self):
        """inlezen mru-gegevens
        """
        self.mru_left = []
        self.mru_right = []
        self.orient_vert = True
        ## self.matchCase = False
        s = ConfigParser()
        s.read(self.inifile)
        if s.has_section("leftpane"):
            ## for i in range(len(s.options("leftpane"))):
            for subscript, _ in enumerate(s.options("leftpane")):
                ky = "file%i" % (subscript + 1)
                self.mru_left.append(s.get("leftpane", ky))
        if s.has_section("rightpane"):
            ## for i in range(len(s.options("rightpane"))):
            for subscript, _ in enumerate(s.options("rightpane")):
                ky = "file%i" % (subscript + 1)
                self.mru_right.append(s.get("rightpane", ky))
        ## if s.has_section("options"):
            ## if s.has_option("options","orient_vert"):
                ## if s.getboolean("options","orient_vert"):
                    ## self.orient_vert = True

    def schrijfini(self):
        """save parameters
        """
        s = ConfigParser()
        if len(self.mru_left) > 0:
            s.add_section("leftpane")
            for x in enumerate(self.mru_left):
                i = x[0] + 1
                s.set("leftpane", ("file%i" % i), x[1])
        if len(self.mru_right) > 0:
            s.add_section("rightpane")
            for x in enumerate(self.mru_right):
                s.set("rightpane", ("file%i" % (x[0] + 1)), x[1])
        ## s.add_section("options")
        ## s.set("options","orient_vert",str(self.orient_vert))
        with open(self.inifile, "w") as _out:
            s.write(_out)

    def open(self, event=None):
        """ask for files to compare
        """
        x, y = self.GetPosition()
        dlg = AskOpenFiles(self, -1, apptitel, pos=(x + 50, y + 50))
        dlg.ShowModal()
        if self.go:
            self.doit(event)

    def doit(self, event):
        """perform action
        """
        # TODO: implement this
        ## mld = check_input(self.linkerpad, self.rechterpad, self.selectiontype)
        ## if mld:
            ## qtw.QMessageBox.critical(self, apptitel, mld)
            ## if first_time:
                ## self.open()
            ## return
        if self.do_compare():
            if self.lhs_path in self.mru_left:
                self.mru_left.remove(self.lhs_path)
            self.mru_left.insert(0, self.lhs_path)
            if self.rhs_path in self.mru_right:
                self.mru_right.remove(self.rhs_path)
            self.mru_right.insert(0, self.rhs_path)
            self.schrijfini()
            if self.data:
                self.selectedOption = self.data[0]
            # panel opnieuw opbouwen in plaats van een refresh doen
            self.toon_scherm()

    def do_compare(self):
        """do the actual comparison
        """
        doitok = True
        if self.lhs_path != "":
            if not exists(self.lhs_path):
                fout = ('Bestand %s kon niet gevonden/geopend worden' % self.lhs_path)
                doitok = False
        else:
            fout = 'Geen linkerbestand opgegeven'
            doitok = False
        if self.rhs_path != "":
            if not exists(self.rhs_path):
                fout = ('Bestand %s kon niet gevonden/geopend worden' % self.rhs_path)
                doitok = False
        else:
            fout = 'Geen rechterbestand opgegeven'
            doitok = False
        if not doitok:
            x, y = self.GetPositionTuple()
            dlg = wx.MessageDialog(self, 'Fout: ' + fout, apptitel, pos=(x + 50, y + 50),
                                   style=wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            compare_func = compare_configs
            try:
                self.data = compare_func(self.lhs_path, self.rhs_path)
            except MissingSectionHeaderError:
                compare_func = compare_configs_2
                self.data = compare_func(self.lhs_path, self.rhs_path)
            ## if h.ft != "":
                ## doitok = False
                ## x,y = self.GetPositionTuple()
                ## dlg = wx.MessageDialog(self,'Fout: '+ h.ft , apptitel,pos=(x+50,y+50), style=wx.OK | wx.ICON_INFORMATION)
                ## dlg.ShowModal()
                ## dlg.Destroy()
            ## else:
                ## self.data = {}
                ## for i in range(len(h.olist)):
                    ## if h.olist[i][0] == "[":
                        ## k = h.olist[i][1:-1]
                        ## self.data[k] = []
                    ## else:
                        ## self.data[k].append((h.olist[i],h.llist[i],h.rlist[i]))
        return doitok

    def on_hori(self, event):
        "currently not used: change orientation to horizontal (b under a)"
        self.orient_vert = False
        self.ToonScherm()

    def on_vert(self, event):
        "currently not used: change orientation to vertical (b next to a)"
        self.orient_vert = True
        self.ToonScherm()

    def about(self, event):
        """opening blurb
        """
        dlg = wx.MessageDialog(self,
                               ("Hulpmiddel om twee ini files te vergelijken, "
                                "maakt niet uit hoe door elkaar de secties en entries ook zitten"),
                               apptitel, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def exit(self, event):
        "quit"
        self.Close(True)

    def toon_scherm(self):
        "(re)show comparison screen"
        self.win.Destroy()
        if self.orient_vert:
            self.win = ShowComparison(self)
            ## self.win.tree.SetSize(self.win.GetSize())
        ## else:
            ## self.win = ToonHori(self)
            ## self.Fit()


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
        self.fbbh1.SetHistory(self.parent.mru_left)

        self.fbbh2 = filebrowse.FileBrowseButtonWithHistory(self, -1, size=(450, -1),
                                                            labelText="Met:       ",
                                                            buttonText="Zoek",
                                                            toolTip=tooltip.format('tweede'),
                                                            dialogTitle=title.format('tweede'),
                                                            changeCallback=self.fbbh2_callback)
        self.fbbh2.SetHistory(self.parent.mru_right)

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.fbbh1, 0, wx.ALL, 5)
        box.Add(self.fbbh2, 0, wx.ALL, 5)
        sizer.Add(box, 0, wx.ALL, 20)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        pbDoIt = wx.Button(self, 402, "Gebruiken")
        self.Bind(wx.EVT_BUTTON, self.OnClick, pbDoIt)
        pbDoIt.SetDefault()
        pbDoIt.SetSize(pbDoIt.GetBestSize())
        box.Add(pbDoIt, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        pbCancel = wx.Button(self, 403, "Afbreken")
        self.Bind(wx.EVT_BUTTON, self.OnClick, pbCancel)
        pbCancel.SetDefault()
        pbCancel.SetSize(pbCancel.GetBestSize())
        pbCancel.SetHelpText("Klik hier om zonder wijzigingen terug te gaan naar het hoofdscherm")
        box.Add(pbCancel, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        ## self.Bind(wx.EVT_CHAR, self.OnChar)

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

    def OnClick(self, event):
        "reimplement standard event handler"
        e = event.GetId()
        if e == 402:
            self.parent.lhs_path = self.path_left
            self.parent.rhs_path = self.path_right
            self.parent.go = True
            self.Destroy()
        elif e == 403:
            self.parent.go = False
            self.Destroy()

    ## def OnChar(self, evt):
        ## if evt.GetKeyCode() == wx.WXK_ESCAPE:
            ## self.parent.go = False
            ## self.Destroy()
        ## evt.Skip()


class ShowComparison(wx.Panel):
    """Part of the main window showing the comparison as a tree
    """
    """ gebruikt wx.lib.gizmos.treelistctrl """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)  # , -1 ,size=(1080, 960))
        self.parent = parent

        self.Bind(wx.EVT_SIZE, self.on_size)

        self.tree = TLC.TreeListCtrl(self, -1, size=(1080, 600),
                                     # style=TLC.TR_DEFAULT_STYLE | TLC.TR_FULL_ROW_HIGHLIGHT)
                                     style=wx.TR_DEFAULT_STYLE | wx.TR_FULL_ROW_HIGHLIGHT)

        # create columns
        self.tree.AddColumn("Sectie / Optie:")
        self.tree.AddColumn("waarde in %s" % self.parent.lhs_path)
        self.tree.AddColumn("waarde in %s" % self.parent.rhs_path)
        ## self.tree.AddColumn("")
        self.tree.SetMainColumn(0)  # the one with the tree in it...
        self.tree.SetColumnWidth(0, 280)
        self.tree.SetColumnWidth(1, 400)
        self.tree.SetColumnWidth(2, 400)
        ## self.tree.SetColumnWidth(3, 20)

        self.root = self.tree.AddRoot("")

        if len(self.parent.data) == 0:
            first = self.tree.AppendItem(self.root, 'geen bestanden geladen')
            self.tree.SetItemText(first, "niks om te laten zien", 1)
            self.tree.SetItemText(first, "hier ook niet", 2)

        current_section = ''
        for node, lvalue, rvalue in self.parent.data:

            section, option = node
            if section != current_section:
                header = self.tree.AppendItem(self.root, section)
                current_section = section

            child = self.tree.AppendItem(header, option)
            text = lvalue
            if text is None:
                text = '(no value)'
            self.tree.SetItemText(child, text, 1)
            text = rvalue
            if text is None:
                text = '(no value)'
            self.tree.SetItemText(child, text, 2)

        self.tree.ExpandAllChildren(self.root)

        ## self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.on_right_up)
        ## self.tree.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.on_left_up)
        ## self.tree.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.on_doubleclick)
        ## sizer = wx.BoxSizer(wx.VERTICAL)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        # hsizer = wx.BoxSizer(wx.HORIZONTAL)
        ## sizer.Add(self.tree, 1, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        vsizer.Add(self.tree, 1, wx.EXPAND)
        # vsizer.Add(hsizer, 1, wx.EXPAND)
        self.SetAutoLayout(True)
        ## self.SetSizer(sizer)
        self.SetSizer(vsizer)
        ## sizer.Fit(self)
        # vsizer.SetSizeHints(self)
        vsizer.Fit(self)
        self.Show(True)
        ## self.tree.SetSize(self.tree.GetMainWindow().GetSize())

    def on_right_up(self, evt):
        """ zou context menuutje moeten openen met keuze voor
        `wijzig oriëntatie` en `toon waarden links-rechts`
        deze laatste keuze opent het `OptionsWindow'
        """
        pos = evt.GetPosition()
        ## print self.tree.HitTest(pos)
        item, flags, col = self.tree.HitTest(pos)
        ## if item:
            ## print ('Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col)))
        print('Show context menu for line')

    def on_left_up(self, evt):
        """bij links klikken op de geselecteerde regel de default keuze
        `toon waarden links-rechts` uitvoeren
        """
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        ## if item:
            ## print ('Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col)))
        print('Show details screen for line')

    def on_doubleclick(self, evt):
        """de default keuze `toon waarden links-rechts` uitvoeren voor de regel
        waarop geklikt is of de node collapsem dan wel expanden
        """
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        print('Also show details screen for line')
        if item:
            if self.tree.GetItemText(item, 1):
                ## print ('Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col)))
                x, y = self.GetPosition()
                self.data = (self.tree.GetItemText(item, 0),
                             self.tree.GetItemText(item, 1),
                             self.tree.GetItemText(item, 2))
                dlg = OptionsWindow(self, -1, apptitel, pos=(x + 50, y + 50))
                dlg.ShowModal()
                ## if self.go:
                    ## self.doit(event)
            elif self.tree.GetItemText(item, 0):
                if self.tree.IsExpanded(item):
                    self.tree.Collapse(item)
                else:
                    self.tree.Expand(item)

    def doit(self, evt):
        "per abuis gedefinieerd denk ik"
        pass

    def on_size(self, evt):
        "grootte aanpassen"
        self.tree.SetSize(self.tree.GetMainWindow().GetSize())


class OptionsWindow(wx.Dialog):
    """dialoog om beide te vergelijken waarden onder elkaar te laten zien
    """
    def __init__(self, parent, id, title, size=(400, 200), pos=wx.DefaultPosition,
                 style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self, parent, wx.ID_ANY, title, size, pos, style)
        self.parent = parent
        self.outL = ""
        self.outR = ""

        sizer = wx.BoxSizer(wx.VERTICAL)
        # regel1 - veld met option titel
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "option naam:", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        label = wx.StaticText(self, -1, self.parent.data[0])
        box.Add(label, 0, wx.GROW | wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.ALL, 5)

        # regel2 - invul veld met option waarde in eerste bestand + knop: wijzig
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "waarde in eerste bestand:", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.txtL = wx.TextCtrl(self, -1, self.parent.data[1], size=(400, 32),
                                style=wx.TE_MULTILINE)
        box.Add(self.txtL, 0, wx.GROW | wx.ALIGN_CENTRE | wx.ALL, 5)
        button = wx.Button(self, 401, "Originele waarde")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)

        # regel3 - invul veld met option waarde in tweede bestand + knop wijzig
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "waarde in tweede bestand:", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        self.txtR = wx.TextCtrl(self, -1, self.parent.data[2], size=(400, 32),
                                style=wx.TE_MULTILINE)
        box.Add(self.txtR, 0, wx.GROW | wx.ALIGN_CENTRE | wx.ALL, 5)
        button = wx.Button(self, 402, "Originele waarde")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)

        # regel4 - knop klaar/cancel (enige)
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "", size=(155, -1))
        box.Add(label, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        button = wx.Button(self, 403, "Bijwerken in ini files en terug")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        button = wx.Button(self, 404, "Terug, niks bijwerken")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE | wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW | wx.ALIGN_CENTER_VERTICAL | wx.ALL, 1)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnClick(self, event):
        "reimplemented standard event handler"
        e = event.GetId()
        if e == 401:
            self.txtL.SetValue(self.parent.data[1])
        elif e == 402:
            self.txtR.SetValue(self.parent.data[2])
        elif e == 403:
            self.outL = self.txtL.GetValue()
            self.outR = self.txtR.GetValue()
            self.parent.go = True
            self.Destroy()
        elif e == 404:
            self.parent.go = False
            self.Destroy()


def main(a1=None, a2=None):
    """main function"""
    ## print a1, a2
    app = wx.App()
    appargs = (a1, a2)
    frame = MainWindow(None, -1, apptitel, appargs)
    app.MainLoop()
