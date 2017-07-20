"""Presentation logic for Compare Tool - PyQT5 version
"""
# ik laat het "synchronized scrollen" even zitten en daarmee ook de keuze verticaal / horizontaal
import wx
import  wx.lib.filebrowsebutton as filebrowse
import  wx.gizmos as gizmos
#import images
from ConfigParser import SafeConfigParser
from conf_comp import inicomp
from os import getcwd
from os.path import exists
ID_OPEN = 101
ID_DOIT = 102
ID_EXIT=109
ID_ABOUT=120
apptitel = "Albert's compare-tool voor ini-files"

class MainWindow(wx.Frame):
    def __init__(self,parent,id,title,appargs=()):
        self.hier = getcwd()
        self.inifile = self.hier + "/actif.ini"
        f = self.readini()
        self.padLeft = 'linkerbestand'
        self.padRight = 'rechterbestand'
        self.data = {}
        self.selectedOption = ''

        wx.Frame.__init__(self,parent,wx.ID_ANY, title, size = (800,600),
                                     style=wx.DEFAULT_FRAME_STYLE|wx.NO_FULL_REPAINT_ON_RESIZE)
        self.CreateStatusBar() # A Statusbar in the bottom of the window
        # Setting up the menu.
        filemenu= wx.Menu()
        filemenu.Append(ID_OPEN, "&Open/kies"," Kies de te vergelijken ini files")
        filemenu.Append(ID_DOIT, "&Vergelijk"," Orden en vergelijk de ini files")
        filemenu.AppendSeparator()
        filemenu.Append(ID_EXIT,"E&xit"," Terminate the program")
        helpmenu= wx.Menu()
        helpmenu.Append(ID_ABOUT, "&About"," Information about this program")
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        self.Show(True)
        self.Connect(ID_OPEN, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.OnOpen)
        self.Connect(ID_DOIT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.OnDoit)
        self.Connect(ID_EXIT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.OnExit)
        self.Connect(ID_ABOUT, -1, wx.wxEVT_COMMAND_MENU_SELECTED, self.OnAbout)
        self.win = ToonVertN(self)
        #~ self.ToonScherm()
        #~ print appargs
        if len(appargs) == 2 and appargs[0] is not None and appargs[1] is not None:
            self.padLeft = appargs[0]
            self.padRight = appargs[1]
            self.OnDoit(None)
        else:
            self.OnOpen()

    def readini(self):
        # inlezen mru-gegevens
        self.mruLeft = []
        self.mruRight = []
        self.LeftRight = False
        #~ self.matchCase = False
        s = SafeConfigParser()
        s.read(self.inifile)
        if s.has_section("leftpane"):
            for i in range(len(s.options("leftpane"))):
                ky = ("file%i"  % (i+1))
                self.mruLeft.append(s.get("leftpane",ky))
        if s.has_section("rightpane"):
            for i in range(len(s.options("rightpane"))):
                ky = ("file%i"  % (i+1))
                self.mruRight.append(s.get("rightpane",ky))
        if s.has_section("options"):
            if s.has_option("options","LeftRight"):
                if s.getboolean("options","LeftRight"):
                    self.LeftRight = True

    def schrijfini(self):
        s = SafeConfigParser()
        if len(self.mruLeft) > 0:
            s.add_section("leftpane")
            for x in enumerate(self.mruLeft):
                i = x[0]+1
                s.set("leftpane",("file%i" % i),x[1])
        if len(self.mruRight) > 0:
            s.add_section("rightpane")
            for x in enumerate(self.mruRight):
                s.set("rightpane",("file%i" % (x[0]+1)),x[1])
        s.add_section("options")
        s.set("options","LeftRight",str(self.LeftRight))
        s.write(file(self.inifile,"w"))

    def OnOpen(self, event=None):
        x,y = self.GetPositionTuple()
        dlg = OpenWindowN(self, -1, apptitel,pos=(x+50,y+50))
        dlg.ShowModal()
        if self.Go:
            self.OnDoit(event)

    def OnDoit(self, event):
        if self.doCompare():
            if self.padLeft in self.mruLeft:
                self.mruLeft.remove(self.padLeft)
            self.mruLeft.insert(0,self.padLeft)
            if self.padRight in self.mruRight:
                self.mruRight.remove(self.padRight)
            self.mruRight.insert(0,self.padRight)
            self.schrijfini()
            if self.data:
                self.selectedOption = self.data.keys()[0]
            self.ToonScherm()

    def doCompare(self):
        doitok = True
        if self.padLeft != "":
            if not exists(self.padLeft):
                fout = ('Bestand %s kon niet gevonden/geopend worden' % self.padLeft)
                doitok = False
        else:
            fout ='Geen linkerbestand opgegeven'
            doitok = False
        if self.padRight != "":
            if not exists(self.padRight):
                fout = ('Bestand %s kon niet gevonden/geopend worden' % self.padRight)
                doitok = False
        else:
            fout ='Geen rechterbestand opgegeven'
            doitok = False
        if not doitok:
            x,y = self.GetPositionTuple()
            dlg = wx.MessageDialog(self,'Fout: '+ fout , apptitel,pos=(x+50,y+50), style=wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            h = inicomp(self.padLeft,self.padRight)
            if h.ft != "":
                doitok = False
                x,y = self.GetPositionTuple()
                dlg = wx.MessageDialog(self,'Fout: '+ h.ft , apptitel,pos=(x+50,y+50), style=wx.OK | wx.ICON_INFORMATION)
                dlg.ShowModal()
                dlg.Destroy()
            else:
                self.data = {}
                for i in range(len(h.olist)):
                    if h.olist[i][0] == "[":
                        k = h.olist[i][1:-1]
                        self.data[k] = []
                    else:
                        self.data[k].append((h.olist[i],h.llist[i],h.rlist[i]))
        return doitok

    def OnHori(self, event):
        self.LeftRight = False
        self.ToonScherm()

    def OnVert(self, event):
        self.LeftRight = True
        self.ToonScherm()

    def OnAbout(self, event):
        dlg = wx.MessageDialog(self,
                "Hulpmiddel om twee ini files te vergelijken, maakt niet uit hoe door elkaar de secties en entries ook zitten",
                apptitel,wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()

    def OnExit(self, event):
        self.Close(True)

    def ToonScherm(self):
        self.win.Destroy()
        if self.LeftRight:
            self.win = ToonVertN(self)
            #~ self.win.tree.SetSize(self.win.GetSize())
        else:
            self.win = ToonHori(self)
            self.Fit()

class OpenWindowN(wx.Dialog):
    def __init__(self,parent,id,title,size=(400,200),pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self,parent,wx.ID_ANY, title, size, pos, style)
        self.parent = parent

        self.fbbh1 = filebrowse.FileBrowseButtonWithHistory(
            self, -1, size=(450, -1),
            labelText = "Vergelijk:",
            buttonText = "Zoek",
            toolTip = "Geef hier de naam van het eerste te vergelijken ini file of kies er een uit een lijst met recent gebruikte",
            dialogTitle = "Selecteer het eerste ini file",
            #~ startDirectory = self.fbbh1.GetValue(),
            #~ fileMask - File mask (glob pattern, such as .) to use in file dialog
            #~ fileMode - wx.OPEN or wx.SAVE, indicates type of file dialog to use
            changeCallback = self.fbbh1Callback
            )
        self.fbbh1.SetHistory(self.parent.mruLeft)

        self.fbbh2 = filebrowse.FileBrowseButtonWithHistory(
            self, -1, size=(450, -1),
            labelText = "Met:       ",
            buttonText = "Zoek",
            toolTip = "Geef hier de naam van het tweede te vergelijken ini file of kies er een uit een lijst met recent gebruikte",
            dialogTitle = "Selecteer het tweede ini file",
            changeCallback = self.fbbh2Callback
            )
        self.fbbh2.SetHistory(self.parent.mruRight)

        sizer = wx.BoxSizer(wx.VERTICAL)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.fbbh1, 0, wx.ALL, 5)
        box.Add(self.fbbh2, 0, wx.ALL, 5)
        sizer.Add(box, 0, wx.ALL, 20)

        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "",size=(155,-1))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        pbDoIt = wx.Button(self,402,"Gebruiken")
        self.Bind(wx.EVT_BUTTON, self.OnClick, pbDoIt)
        pbDoIt.SetDefault()
        pbDoIt.SetSize(pbDoIt.GetBestSize())
        box.Add(pbDoIt, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        pbCancel = wx.Button(self,403,"Afbreken")
        self.Bind(wx.EVT_BUTTON, self.OnClick, pbCancel)
        pbCancel.SetDefault()
        pbCancel.SetSize(pbCancel.GetBestSize())
        pbCancel.SetHelpText("Klik hier om zonder wijzigingen terug te gaan naar het hoofdscherm")
        box.Add(pbCancel, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 5)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

        #~ self.Bind(wx.EVT_CHAR, self.OnChar)

    def fbbh1Callback(self, evt):
        if hasattr(self, 'fbbh1'):
            self.vraagDirL = evt.GetString()
            history = self.fbbh1.GetHistory()
            if self.vraagDirL not in history:
                history.append(self.vraagDirL)
                self.fbbh1.SetHistory(history)
                self.fbbh1.GetHistoryControl().SetStringSelection(self.vraagDirL)

    def fbbh2Callback(self, evt):
        if hasattr(self, 'fbbh2'):
            self.vraagDirR = evt.GetString()
            history = self.fbbh2.GetHistory()
            if self.vraagDirR not in history:
                history.append(self.vraagDirR)
                self.fbbh2.SetHistory(history)
                self.fbbh2.GetHistoryControl().SetStringSelection(self.vraagDirR)

    def OnClick(self, event):
        e = event.GetId()
        if e == 402:
            self.parent.padLeft = self.vraagDirL
            self.parent.padRight = self.vraagDirR
            self.parent.Go = True
            self.Destroy()
        elif e == 403:
            self.parent.Go = False
            self.Destroy()

    #~ def OnChar(self, evt):
        #~ if evt.GetKeyCode() == wx.WXK_ESCAPE:
            #~ self.parent.Go = False
            #~ self.Destroy()
        #~ evt.Skip()


class ToonVertN(wx.Panel):
    """ gebaseerd op gizmos.TreeListCtrl """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent, -1 ,size=(800,600)) # Hallo, afmetingen graag !
        self.parent = parent

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.tree = gizmos.TreeListCtrl(self, -1,
                                    style =
                                        wx.TR_DEFAULT_STYLE
                                        #~ wx.TR_TWIST_BUTTONS
                                        #~ | wx.TR_ROW_LINES
                                        #~ | wx.TR_NO_LINES
                                        | wx.TR_FULL_ROW_HIGHLIGHT
                                   )

        # create columns
        self.tree.AddColumn("Sectie / Optie:")
        self.tree.AddColumn("waarde in %s" % self.parent.padLeft)
        self.tree.AddColumn("waarde in %s" % self.parent.padRight)
        self.tree.AddColumn("")
        self.tree.SetMainColumn(0) # the one with the tree in it...
        self.tree.SetColumnWidth(0, 156)
        self.tree.SetColumnWidth(1, 317)
        self.tree.SetColumnWidth(2, 317)
        self.tree.SetColumnWidth(3, 20)

        self.root = self.tree.AddRoot("")
        #~ self.tree.SetItemText(self.root, "", 1)
        #~ self.tree.SetItemText(self.root, "", 2)

        for x in self.parent.data.keys():
            child = self.tree.AppendItem(self.root, x)

            for y in self.parent.data[x]:
                last = self.tree.AppendItem(child, y[0])
                self.tree.SetItemText(last, y[1], 1)
                self.tree.SetItemText(last, y[2], 2)

        self.tree.Expand(self.root)

        self.tree.GetMainWindow().Bind(wx.EVT_RIGHT_UP, self.OnRightUp)
        self.tree.GetMainWindow().Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.tree.GetMainWindow().Bind(wx.EVT_LEFT_DCLICK, self.OnDblClick)
        #~ sizer = wx.BoxSizer(wx.VERTICAL)
        #~ sizer.Add(self.tree, 1, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL)
        #~ self.SetAutoLayout(True)
        #~ self.SetSizer(sizer)
        #~ sizer.Fit(self)
        #~ self.Show(True)
        self.tree.SetSize(self.GetSize())

    def OnRightUp(self, evt):
        # zou context menuutje moeten openen met keuze voor toon waarden links-rechts, deze keuze opent het schermpje
        pos = evt.GetPosition()
        #~ print self.tree.HitTest(pos)
        item, flags, col = self.tree.HitTest(pos)
        #~ if item:
            #~ print ('Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col)))

    def OnLeftUp(self, evt):
        # bij links klikken op de geselecteerde regel de default keuze toon waarden links-rechts uitvoeren
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        #~ if item:
            #~ print ('Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col)))

    def OnDblClick(self, evt):
        # de default keuze toon waarden links-rechts uitvoeren voor de regel waarop geklikt is
        pos = evt.GetPosition()
        item, flags, col = self.tree.HitTest(pos)
        if item:
            if self.tree.GetItemText(item, 1):
                #~ print ('Flags: %s, Col:%s, Text: %s' % (flags, col, self.tree.GetItemText(item, col)))
                x,y = self.GetPositionTuple()
                self.data = (self.tree.GetItemText(item, 0),self.tree.GetItemText(item, 1),self.tree.GetItemText(item, 2))
                dlg = OptionsWindow(self, -1, apptitel,pos=(x+50,y+50))
                dlg.ShowModal()
                #~ if self.Go:
                    #~ self.OnDoit(event)
            elif self.tree.GetItemText(item, 0):
                if self.tree.IsExpanded(item):
                    self.tree.Collapse(item)
                else:
                    self.tree.Expand(item)

    def OnDoit(self,evt):
        pass

    def OnSize(self, evt):
        self.tree.SetSize(self.GetSize())


class OptionsWindow(wx.Dialog):
    def __init__(self,parent,id,title,size=(400,200),pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE):
        wx.Dialog.__init__(self,parent,wx.ID_ANY, title, size, pos, style)
        self.parent = parent
        self.outL = ""
        self.outR = ""

        sizer = wx.BoxSizer(wx.VERTICAL)
        #~ regel1 - veld met option titel
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "option naam:",size=(155,-1))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        label = wx.StaticText(self, -1, self.parent.data[0])
        box.Add(label, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.ALL, 5)

        #~ regel2 - invul veld met option waarde in eerste bestand + knop: wijzig
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "waarde in eerste bestand:",size=(155,-1))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.txtL = wx.TextCtrl(self, -1,self.parent.data[1],size=(400, 32), style=wx.TE_MULTILINE)
        box.Add(self.txtL, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 5)
        button = wx.Button(self,401,"Originele waarde")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1)

        #~ regel3 - invul veld met option waarde in tweede bestand + knop wijzig
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "waarde in tweede bestand:",size=(155,-1))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        self.txtR = wx.TextCtrl(self, -1,self.parent.data[2],size=(400, 32), style=wx.TE_MULTILINE)
        box.Add(self.txtR, 0, wx.GROW|wx.ALIGN_CENTRE|wx.ALL, 5)
        button = wx.Button(self,402,"Originele waarde")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1)

        #~ regel4 - knop klaar/cancel (enige)
        box = wx.BoxSizer(wx.HORIZONTAL)
        label = wx.StaticText(self, -1, "",size=(155,-1))
        box.Add(label, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        button = wx.Button(self,403,"Bijwerken in ini files en terug")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        button = wx.Button(self,404,"Terug, niks bijwerken")
        self.Bind(wx.EVT_BUTTON, self.OnClick, button)
        button.SetSize(button.GetBestSize())
        box.Add(button, 0, wx.ALIGN_CENTRE|wx.ALL, 5)
        sizer.Add(box, 0, wx.GROW|wx.ALIGN_CENTER_VERTICAL|wx.ALL, 1)

        self.SetSizer(sizer)
        self.SetAutoLayout(True)
        sizer.Fit(self)

    def OnClick(self, event):
        e = event.GetId()
        if e == 401:
            self.txtL.SetValue(self.parent.data[1])
        elif e == 402:
            self.txtR.SetValue(self.parent.data[2])
        elif e == 403:
            self.outL = self.txtL.GetValue()
            self.outR = self.txtR.GetValue()
            self.parent.Go = True
            self.Destroy()
        elif e == 404:
            self.parent.Go = False
            self.Destroy()

def main(a1=None, a2=None):
    #~ print a1, a2
    app = wx.PySimpleApp()
    appargs = (a1,a2)
    frame = MainWindow(None, -1, apptitel, appargs)
    app.MainLoop()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(a1=sys.argv[1],a2=sys.argv[2])
    else:
        main()
        ## main(a1="c:\\Program Files\\totalcmd\\wincmd.ini",a2="c:\\Program Files\\totalcmdbeta\\wincmd.ini")
        #~ main(a1="afrift.ini",a2="afriftftc.ini")
        #~ main(a1="sync_scrollbars.txt",a2="afriftftc.ini")
