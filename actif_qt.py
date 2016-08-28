#! -*- coding: utf-8 -*-
from configparser import ConfigParser
from os import getcwd
import os.path
import traceback
import PyQt4.QtGui as gui
import PyQt4.QtCore as core
from conf_comp import compare_configs, compare_configs_2, MissingSectionHeaderError
from xml_comp import compare_xmldata, ParseError

ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
apptitel = "Albert's compare-tool voor ini-files"
rightonly_colour = core.Qt.blue
leftonly_colour = core.Qt.green
difference_colour = core.Qt.red
## inversetext_colour = core.Qt.white
comparetypes = {
    'ini': ('ini files', compare_configs),
    'ini2': ('ini files, allowing for missing first header', compare_configs_2),
    'xml': ('XML files', compare_xmldata),
    }

def check_input(linkerpad, rechterpad, seltype):
    if linkerpad == "":
        return 'Geen linkerbestand opgegeven'
    else:
        if not os.path.exists(linkerpad):
            return 'Bestand {} kon niet gevonden/geopend worden'.format(
                linkerpad)
    if rechterpad == "":
        return 'Geen rechterbestand opgegeven'
    else:
        if not os.path.exists(rechterpad):
            return 'Bestand {} kon niet gevonden/geopend worden'.format(
                rechterpad)
    if seltype not in comparetypes:
        return 'Geen vergelijkingsmethode gekozen'


class FileBrowseButton(gui.QFrame):
    """Combination widget showing a text field and a button
    making it possible to either manually enter a filename or select
    one using a FileDialog
    """
    def __init__(self, parent, caption="", text="", items=None):
        self.parent = parent
        if items is None: items = []
        super().__init__(parent)
        self.setFrameStyle(gui.QFrame.Panel | gui.QFrame.Raised);
        vbox = gui.QVBoxLayout()
        box = gui.QHBoxLayout()
        ## self.input = gui.QLineEdit(text, self)
        self.input = gui.QComboBox(self)
        self.input.setEditable(True)
        self.input.setMaximumWidth(300)
        self.input.addItems(items)
        self.input.setEditText(text)
        lbl = gui.QLabel(caption)
        lbl.setMinimumWidth(100)
        lbl.setMaximumWidth(100)
        box.addWidget(lbl)
        box.addWidget(self.input)
        self.button = gui.QPushButton('Browse', self, clicked=self.browse)
        self.button.setMaximumWidth(68)
        box.addWidget(self.button)
        vbox.addLayout(box)
        self.setLayout(vbox)

    def browse(self):
        startdir = str(self.input.currentText()) or os.getcwd()
        path = gui.QFileDialog.getOpenFileName(self, 'Kies een bestand', startdir)
        if path:
            self.input.setEditText(path)


class AskOpenFiles(gui.QDialog):
    """dialog om de te vergelijken bestanden op te geven

    voor elk file een combobox om direct een filenaam op te geven of te kiezen
    uit een lijst met eerder gebruikte, met een button ernaast om de filenaam te
    selecteren met behulp van een file selector dialoog
    de te tonen lijsten worden bewaard in een bestand aangegeven door self.inifile
    """
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        ## self.resize(680, 400)
        self.sizer = gui.QVBoxLayout()

        hsizer = gui.QHBoxLayout()
        browse = FileBrowseButton(self, caption='Linker bestand:  ',
            text=self.parent.linkerpad,
            items=self.parent.mru_left)
        hsizer.addWidget(browse)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse1 = browse

        hsizer = gui.QHBoxLayout()
        browse = FileBrowseButton(self, caption='Rechter bestand: ',
            text=self.parent.rechterpad,
            items=self.parent.mru_right)
        hsizer.addWidget(browse)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse2 = browse

        hsizer = gui.QHBoxLayout()
        hsizer.addSpacing(10)
        gsizer = gui.QGridLayout()
        gsizer.addWidget(gui.QLabel('Soort vergelijking:'), 0, 0)
        self.sel = []
        for ix, type in enumerate(sorted(comparetypes)):
            text = comparetypes[type][0]
            rb = gui.QRadioButton(text, self)
            gsizer.addWidget(rb, ix, 1)
            if self.parent.selectiontype == type:
                rb.setChecked(True)
            self.sel.append((rb, type))
        hsizer.addLayout(gsizer)
        hsizer.addStretch()
        self.sizer.addLayout(hsizer)


        buttonbox = gui.QDialogButtonBox()
        btn = buttonbox.addButton(gui.QDialogButtonBox.Ok)
        btn = buttonbox.addButton(gui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        hsizer = gui.QHBoxLayout()
        hsizer.addStretch()
        hsizer.addWidget(buttonbox)
        hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.setLayout(self.sizer)

    def accept(self):
        linkerpad = self.browse1.input.currentText()
        rechterpad = self.browse2.input.currentText()
        selectiontype = ''
        for ix, sel in enumerate(self.sel):
            if sel[0].isChecked():
                selectiontype = sel[1]
                break
        mld = check_input(linkerpad, rechterpad, selectiontype)
        if mld:
            gui.QMessageBox.critical(self, apptitel, mld)
            return
        self.parent.linkerpad = linkerpad
        self.parent.rechterpad = rechterpad
        self.parent.selectiontype = selectiontype
        super().accept()


class ShowComparison(gui.QTreeWidget):

    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHeaderLabels(['Document structure', 'value in "lefthand-side" file',
            'value in "righthand-side" file'])
        hdr = self.header()
        hdr.resizeSection(0, 100)
        hdr.resizeSection(0, 350)
        hdr.resizeSection(1, 350)
        root = gui.QTreeWidgetItem()
        root.setText(1, 'nothing to show')
        root.setText(2, 'also nothing to show')
        self.addTopLevelItem(root)
        self.show()

    def refresh_tree(self):
        if self.parent.selectiontype in ('ini', 'ini2'):
            self.refresh_inicompare()
        elif self.parent.selectiontype == 'xml':
            self.refresh_xmlcompare()

    def refresh_inicompare(self):
        self.setHeaderLabels(['Section/Option', self.parent.linkerpad,
            self.parent.rechterpad])
        self.clear()
        current_section = ''
        for x in self.parent.data:
            node, lvalue, rvalue = x
            section, option = node
            if section != current_section:
                if current_section:
                    self.colorize_header(header, rightonly, leftonly, difference)
                header = gui.QTreeWidgetItem()
                header.setText(0, section)
                self.addTopLevelItem(header)
                current_section = section
                rightonly = leftonly = difference = False
            child = gui.QTreeWidgetItem()
            child.setText(0, option)
            if lvalue is None: lvalue = '(no value)'
            if lvalue == '':
                rightonly = True
                child.setTextColor(0, rightonly_colour)
                child.setTextColor(2, rightonly_colour)
            child.setText(1, lvalue)
            if rvalue is None: rvalue = '(no value)'
            if rvalue == '':
                leftonly = True
                child.setTextColor(0, leftonly_colour)
                child.setTextColor(1, leftonly_colour)
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
                child.setTextColor(0, difference_colour)
                child.setTextColor(1, difference_colour)
                child.setTextColor(2, difference_colour)
            child.setText(2, rvalue)
            header.addChild(child)
        self.colorize_header(header, rightonly, leftonly, difference)

    def refresh_xmlcompare(self):
        self.setHeaderLabels(['Element/Attribute', self.parent.linkerpad,
            self.parent.rechterpad])
        self.clear()
        current_elems = []
        count = 0
        for x in self.parent.data:
            node, lvalue, rvalue = x
            elems, attr = node
            if elems != current_elems:
                if not current_elems:
                    header = gui.QTreeWidgetItem()
                    header.setText(0, '<>' + elems[-1][0])
                    self.addTopLevelItem(header)
                    header.setExpanded(True)
                else:
                    self.colorize_header(header, rightonly, leftonly, difference)
                    if len(elems) > len(current_elems):
                        parent = header
                    elif len(elems) < len(current_elems):
                        parent = header.parent().parent()
                    else:
                        parent = header.parent()
                    header = gui.QTreeWidgetItem()
                    header.setText(0, '<> ' + elems[-1][0])
                    parent.addChild(header)
                current_elems = elems
                rightonly = leftonly = difference = False
            if attr == '':
                header.setText(1, lvalue)
                header.setText(2, rvalue)
                if lvalue == '':
                    rightonly = True
                if rvalue == '':
                    leftonly = True
                if lvalue and rvalue and lvalue != rvalue:
                    difference = True
                continue
            child = gui.QTreeWidgetItem()
            child.setText(0, attr)
            if lvalue is None: lvalue = '(no value)'
            if lvalue == '':
                rightonly = True
                child.setTextColor(0, rightonly_colour)
                child.setTextColor(2, rightonly_colour)
            child.setText(1, lvalue)
            if rvalue is None: rvalue = '(no value)'
            if rvalue == '':
                leftonly = True
                child.setTextColor(0, leftonly_colour)
                child.setTextColor(1, leftonly_colour)
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
                child.setTextColor(0, difference_colour)
                child.setTextColor(1, difference_colour)
                child.setTextColor(2, difference_colour)
            child.setText(2, rvalue)
            header.addChild(child)
        self.colorize_header(header, rightonly, leftonly, difference)

    def colorize_header(self, header, rightonly, leftonly, difference):
        if rightonly and not leftonly:
            header.setTextColor(0, rightonly_colour)
        if leftonly and not rightonly:
            header.setTextColor(0, leftonly_colour)
        if difference or (leftonly and rightonly):
            header.setTextColor(0, difference_colour)

class MainWindow(gui.QMainWindow):

    def __init__(self, parent, args):
        self.inifile = os.path.join(os.path.dirname(os.path.abspath(__file__)),
            "actif.ini")
        super().__init__(parent)
        ## gui.QMainWindow.__init__(self, parent)
        f = self.readini()
        self.linkerpad ,self.rechterpad = args
        self.data = {}
        self.selected_option = ''
        self.linkerpad = ''
        self.rechterpad = ''
        self.selectiontype = ''
        self.menuactions = {}

        self.resize(1024,600)
        self.setWindowTitle('Vergelijken van ini files')
        self.setWindowIcon(gui.QIcon('inicomp.ico'))
        self.sb = self.statusBar()
        self.setup_menu()
        self.win = ShowComparison(self)
        self.setCentralWidget(self.win)

        if self.linkerpad and self.rechterpad:
            self.doit()
        else:
            self.about()
            self.open()
        self.show()

    def setup_menu(self):
        # Setting up the menu.
        self.menu_bar = self.menuBar()
        menu = self.menu_bar.addMenu("&File")
        act = gui.QAction("&Open", self)
        act.triggered.connect(self.open)
        act.setShortcut('Ctrl+O')
        act.setStatusTip(" Bepaal de te vergelijken ini files")
        menu.addAction(act)
        self.menuactions[ID_OPEN] = act
        act = gui.QAction("&Vergelijk", self)
        act.triggered.connect(self.doit)
        act.setStatusTip(" Orden en vergelijk de ini files")
        menu.addAction(act)
        self.menuactions[ID_DOIT] = act
        menu.addSeparator()
        act = gui.QAction("E&xit", self)
        act.triggered.connect(self.exit)
        act.setShortcut('Ctrl+Q')
        act.setStatusTip("Terminate the program")
        menu.addAction(act)
        self.menuactions[ID_EXIT] = act

        menu = self.menu_bar.addMenu("&Help")
        act = gui.QAction("&About", self)
        act.setShortcut('F1')
        act.triggered.connect(self.about)
        act.setStatusTip(" Information about this program")
        menu.addAction(act)
        self.menuactions[ID_ABOUT] = act

    def readini(self):
        # inlezen mru-gegevens
        self.mru_left = []
        self.mru_right = []
        self.horizontal = True

        s = ConfigParser()
        s.read(self.inifile)
        if s.has_section("leftpane"):
            for i in range(len(s.options("leftpane"))):
                ky = ("file%i"  % (i+1))
                self.mru_left.append(s.get("leftpane",ky))
        if s.has_section("rightpane"):
            for i in range(len(s.options("rightpane"))):
                ky = ("file%i"  % (i+1))
                self.mru_right.append(s.get("rightpane",ky))
        ## if s.has_section("options"):
            ## if s.has_option("options","LeftRight"):
                ## if s.getboolean("options","LeftRight"):
                    ## self.horizontal = False

    def schrijfini(self):
        s = ConfigParser()
        if len(self.mru_left) > 0:
            s.add_section("leftpane")
            for x in enumerate(self.mru_left):
                i = x[0]+1
                s.set("leftpane",("file%i" % i),x[1])
        if len(self.mru_right) > 0:
            s.add_section("rightpane")
            for x in enumerate(self.mru_right):
                s.set("rightpane",("file%i" % (x[0]+1)),x[1])
        ## s.add_section("options")
        ## s.set("options","LeftRight",str(self.LeftRight))
        with open(self.inifile,"w") as _out:
            s.write(_out)

    def open(self, event=None):
        dlg = AskOpenFiles(self).exec_()
        if dlg == gui.QDialog.Accepted:
            self.doit()

    def doit(self, event=None):
        mld = check_input(self.linkerpad, self.rechterpad, self.selectiontype)
        if mld:
            gui.QMessageBox.critical(self, apptitel, 'Nog geen bestanden en '
                'vergelijkingsmethode gekozen')
            return
        if self.do_compare():
            if self.linkerpad in self.mru_left:
                self.mru_left.remove(self.linkerpad)
            self.mru_left.insert(0,self.linkerpad)
            if self.rechterpad in self.mru_right:
                self.mru_right.remove(self.rechterpad)
            self.mru_right.insert(0,self.rechterpad)
            self.schrijfini()
            if self.data:
                self.selected_option = self.data[0]
            self.win.refresh_tree()

    def do_compare(self):
        compare_func = comparetypes[self.selectiontype][1]
        try:
            self.data = compare_func(self.linkerpad,self.rechterpad)
        except Exception as err:
            error, msg, tb = sys.exc_info()
            #fout = ["An error occurred.\n",
            ## if error == ParseError:
                ## fout.append("Misschien heb je de verkeerde vergelijkingsmethode "
                    ## "gekozen.\n")
            ## elif error == MissingSectionHeaderError:
                ## fout.append("
            #    "\n"] + traceback.format_exception(error, msg, tb)
            #text = '<pre>{}</pre>'.format('<br>'.join(fout))
            #gui.QMessageBox.critical(self, apptitel, text)
            box = gui.QMessageBox(self)
            box.setWindowTitle(apptitel)
            if error == ParseError:
                info = "bevat geen correcte XML"
            elif error == MissingSectionHeaderError:
                info = "begint niet met een header"
            else:
                info = "geeft een fout"
            box.setText("Tenminste één file " + info)
            box.setInformativeText('<pre>{}</pre>'.format(''.join(
                traceback.format_exception(error, msg, tb))))
            box.exec_()
            return False
        return True

    def about(self, event=None):
        dlg = gui.QMessageBox.information(self, apptitel, '\n'.join((
            "Met dit programma kun je twee ini files met elkaar vergelijken,",
            "maakt niet uit hoe door elkaar de secties en entries ook zitten.",
            "",
            "Het is ook bruikbaar voor XML bestanden.")))

    def keyPressEvent(self, evt):
        """Make it possible to use Esc to quit the application
        """
        if evt.key() == core.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(evt)

    def exit(self, event):
        self.close()


def main(a1=None, a2=None):
    #~ print a1, a2
    app = gui.QApplication(sys.argv)
    appargs = (a1,a2)
    frame = MainWindow(None, appargs)
    sys.exit(app.exec_())

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        main(a1=sys.argv[1], a2=sys.argv[2])
    else:
        main()
        ## main(a1="actif.ini", a2="testing.ini")
