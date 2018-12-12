"""Presentation logic for Compare Tool - PyQT5 version
"""
import sys
from configparser import ConfigParser
import os.path
import pathlib
import traceback
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as gui
import PyQt5.QtCore as core
from conf_comp import compare_configs, compare_configs_2, MissingSectionHeaderError
from xml_comp import compare_xmldata, ParseError
from txt_comp import compare_txtdata

ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
apptitel = "Albert's compare-tool voor ini-files"
rightonly_colour = gui.QBrush(core.Qt.blue)
leftonly_colour = gui.QBrush(core.Qt.green)
difference_colour = gui.QBrush(core.Qt.red)
## inversetext_colour = core.Qt.white
comparetypes = {
    'ini': ('ini files', compare_configs),
    'ini2': ('ini files, allowing for missing first header', compare_configs_2),
    'xml': ('XML files', compare_xmldata),
    'txt': ('Simple text comparison', compare_txtdata)}


def check_input(linkerpad, rechterpad, seltype):
    """parse input
    """
    if linkerpad == "":
        return 'Geen linkerbestand opgegeven'
    else:
        if not pathlib.Path(linkerpad).exists():
            return 'Bestand {} kon niet gevonden/geopend worden'.format(
                linkerpad)
    if rechterpad == "":
        return 'Geen rechterbestand opgegeven'
    else:
        if not pathlib.Path(rechterpad).exists():
            return 'Bestand {} kon niet gevonden/geopend worden'.format(
                rechterpad)
    if rechterpad == linkerpad:
        return "Bestandsnamen zijn gelijk"
    if seltype not in comparetypes:
        return 'Geen vergelijkingsmethode gekozen'


def colorize_header(header, rightonly, leftonly, difference):
    """visualize the difference by coloring the header
    """
    if rightonly and not leftonly:
        header.setForeground(0, rightonly_colour)
    if leftonly and not rightonly:
        header.setForeground(0, leftonly_colour)
    if difference or (leftonly and rightonly):
        header.setForeground(0, difference_colour)


def set_text(node, column, value):
    """set tooltip as well as text so that truncated text can be viewed in full
    """
    node.setText(column, value)
    node.setToolTip(column, value)


class FileBrowseButton(qtw.QFrame):
    """Combination widget showing a text field and a button
    making it possible to either manually enter a filename or select
    one using a FileDialog
    """
    def __init__(self, parent, caption="", text="", items=None):
        self.parent = parent
        if items is None:
            items = []
        super().__init__(parent)
        self.setFrameStyle(qtw.QFrame.Panel | qtw.QFrame.Raised)
        vbox = qtw.QVBoxLayout()
        box = qtw.QHBoxLayout()
        ## self.input = gui.QLineEdit(text, self)
        self.input = qtw.QComboBox(self)
        self.input.setEditable(True)
        self.input.setMaximumWidth(300)
        self.input.addItems(items)
        self.input.setEditText(text)
        lbl = qtw.QLabel(caption)
        lbl.setMinimumWidth(100)
        lbl.setMaximumWidth(100)
        box.addWidget(lbl)
        box.addWidget(self.input)
        self.button = qtw.QPushButton('Browse', self, clicked=self.browse)
        self.button.setMaximumWidth(68)
        box.addWidget(self.button)
        vbox.addLayout(box)
        self.setLayout(vbox)

    def browse(self):
        """callback for the "Browse" button
        """
        startdir = str(self.input.currentText()) or os.getcwd()
        path = qtw.QFileDialog.getOpenFileName(self, 'Kies een bestand', startdir)
        if path[0]:
            self.input.setEditText(path[0])


class AskOpenFiles(qtw.QDialog):
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
        self.sizer = qtw.QVBoxLayout()

        hsizer = qtw.QHBoxLayout()
        browse = FileBrowseButton(self, caption='Linker bestand:  ',
                                  text=self.parent.linkerpad,
                                  items=self.parent.mru_left)
        hsizer.addWidget(browse)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse1 = browse

        hsizer = qtw.QHBoxLayout()
        browse = FileBrowseButton(self, caption='Rechter bestand: ',
                                  text=self.parent.rechterpad,
                                  items=self.parent.mru_right)
        hsizer.addWidget(browse)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse2 = browse

        hsizer = qtw.QHBoxLayout()
        hsizer.addSpacing(10)
        gsizer = qtw.QGridLayout()
        gsizer.addWidget(qtw.QLabel('Soort vergelijking:'), 0, 0)
        self.sel = []
        for ix, type in enumerate(sorted(comparetypes)):
            text = comparetypes[type][0]
            rb = qtw.QRadioButton(text, self)
            gsizer.addWidget(rb, ix, 1)
            if self.parent.selectiontype == type:
                rb.setChecked(True)
            self.sel.append((rb, type))
        hsizer.addLayout(gsizer)
        hsizer.addStretch()
        self.sizer.addLayout(hsizer)

        buttonbox = qtw.QDialogButtonBox()
        buttonbox.addButton(qtw.QDialogButtonBox.Ok)
        buttonbox.addButton(qtw.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        hsizer = qtw.QHBoxLayout()
        hsizer.addStretch()
        hsizer.addWidget(buttonbox)
        hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.setLayout(self.sizer)

    def accept(self):
        """transmit the chosen data
        """
        linkerpad = self.browse1.input.currentText()
        rechterpad = self.browse2.input.currentText()
        selectiontype = ''
        for ix, sel in enumerate(self.sel):
            if sel[0].isChecked():
                selectiontype = sel[1]
                break
        mld = check_input(linkerpad, rechterpad, selectiontype)
        if mld:
            qtw.QMessageBox.critical(self, apptitel, mld)
            return
        self.parent.linkerpad = linkerpad
        self.parent.rechterpad = rechterpad
        self.parent.selectiontype = selectiontype
        super().accept()


class ShowComparison(qtw.QTreeWidget):
    """Part of the main window showing the comparison as a tree
    """
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
        self.setColumnCount(3)
        self.setHeaderLabels(['Document structure', 'value in "lefthand-side" file',
                              'value in "righthand-side" file'])
        hdr = self.header()
        hdr.resizeSection(0, 100)
        ## hdr.resizeSection(0, 350)
        hdr.resizeSection(1, 350)
        root = qtw.QTreeWidgetItem()
        root.setText(1, 'nothing to show')
        root.setText(2, 'also nothing to show')
        self.addTopLevelItem(root)
        self.show()

    def refresh_tree(self):
        """(re)do the comparison
        """
        if self.parent.selectiontype in ('ini', 'ini2'):
            self.refresh_inicompare()
        elif self.parent.selectiontype == 'xml':
            self.refresh_xmlcompare()
        elif self.parent.selectiontype == 'txt':
            self.refresh_txtcompare()

    def refresh_inicompare(self):
        """(re)do comparing the ini files
        """
        self.setHeaderLabels(['Section/Option', self.parent.linkerpad,
                              self.parent.rechterpad])
        self.clear()
        current_section = ''
        for x in self.parent.data:
            node, lvalue, rvalue = x
            section, option = node
            if section != current_section:
                if current_section:
                    colorize_header(header, rightonly, leftonly, difference)
                header = qtw.QTreeWidgetItem()
                set_text(header, 0, section)
                self.addTopLevelItem(header)
                current_section = section
                rightonly = leftonly = difference = False
            child = qtw.QTreeWidgetItem()
            set_text(child, 0, option)
            if lvalue is None:
                lvalue = '(no value)'
            if lvalue == '':
                rightonly = True
                child.setForeground(0, rightonly_colour)
                child.setForeground(2, rightonly_colour)
            set_text(child, 1, lvalue)
            if rvalue is None:
                rvalue = '(no value)'
            if rvalue == '':
                leftonly = True
                child.setForeground(0, leftonly_colour)
                child.setForeground(1, leftonly_colour)
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
                child.setForeground(0, difference_colour)
                child.setForeground(1, difference_colour)
                child.setForeground(2, difference_colour)
            set_text(child, 2, rvalue)
            header.addChild(child)
        if self.parent.data:
            colorize_header(header, rightonly, leftonly, difference)

    def refresh_xmlcompare(self):
        """(re)do the XML compare
        """
        self.setHeaderLabels(['Element/Attribute', self.parent.linkerpad,
                              self.parent.rechterpad])
        self.clear()
        current_elems = []
        for x in self.parent.data:
            node, lvalue, rvalue = x
            elems, attr = node
            if elems != current_elems:
                if not current_elems:
                    header = qtw.QTreeWidgetItem()
                    set_text(header, 0, '<>' + elems[-1][0])
                    self.addTopLevelItem(header)
                    header.setExpanded(True)
                else:
                    colorize_header(header, rightonly, leftonly, difference)
                    if len(elems) > len(current_elems):
                        parent = header
                    elif len(elems) < len(current_elems):
                        parent = header.parent().parent()
                    else:
                        parent = header.parent()
                    header = qtw.QTreeWidgetItem()
                    set_text(header, 0, '<> ' + elems[-1][0])
                    parent.addChild(header)
                current_elems = elems
                rightonly = leftonly = difference = False
            if attr == '':
                set_text(header, 1, lvalue)
                set_text(header, 2, rvalue)
                if lvalue == '':
                    rightonly = True
                if rvalue == '':
                    leftonly = True
                if lvalue and rvalue and lvalue != rvalue:
                    difference = True
                continue
            child = qtw.QTreeWidgetItem()
            set_text(child, 0, attr)
            if lvalue is None:
                lvalue = '(no value)'
            if lvalue == '':
                rightonly = True
                child.setForeground(0, rightonly_colour)
                child.setForeground(2, rightonly_colour)
            set_text(child, 1, lvalue)
            if rvalue is None:
                rvalue = '(no value)'
            if rvalue == '':
                leftonly = True
                child.setForeground(0, leftonly_colour)
                child.setForeground(1, leftonly_colour)
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
                child.setForeground(0, difference_colour)
                child.setForeground(1, difference_colour)
                child.setForeground(2, difference_colour)
            set_text(child, 2, rvalue)
            header.addChild(child)
        if self.parent.data:
            colorize_header(header, rightonly, leftonly, difference)

    def refresh_txtcompare(self):
        """(re)do the text compare
        """
        self.setHeaderLabels(['Text in both files', self.parent.linkerpad,
                              self.parent.rechterpad])
        self.clear()
        for x in self.parent.data:
            bvalue, lvalue, rvalue = x
            node = qtw.QTreeWidgetItem()
            set_text(node, 0, bvalue)
            set_text(node, 1, lvalue)
            set_text(node, 2, rvalue)
            if lvalue:
                node.setForeground(1, leftonly_colour)
            if rvalue:
                node.setForeground(2, rightonly_colour)
            self.addTopLevelItem(node)


class MainWindow(qtw.QMainWindow):
    """Application screen
    """
    def __init__(self, parent, args, method=None):
        self.inifile = str(pathlib.Path(__file__).parent.resolve() / "actif.ini")
        super().__init__(parent)
        self.readini()
        self.linkerpad, self.rechterpad = args
        self.data = {}
        self.selected_option = ''
        self.selectiontype = ''
        self.menuactions = {}

        self.resize(1024, 600)
        self.setWindowTitle('Vergelijken van ini files')
        self.setWindowIcon(gui.QIcon('inicomp.ico'))
        self.sb = self.statusBar()
        self.setup_menu()
        self.win = ShowComparison(self)
        self.setCentralWidget(self.win)

        if method and method in comparetypes:
            self.selectiontype = method
        if self.linkerpad and self.rechterpad:
            if not self.selectiontype:
                extl = pathlib.Path(self.linkerpad).suffix[1:]
                extr = pathlib.Path(self.rechterpad).suffix[1:]
                if extl == extr and extl.lower() in comparetypes:
                    self.selectiontype = extl.lower()
            self.doit(first_time=True)
        else:
            self.about()
            self.open()

    def add_action_to_menu(self, name, callback, shortcut, statustext, menu):
        """build a menu line
        """
        act = qtw.QAction(name, self)
        act.triggered.connect(callback)
        act.setShortcut(shortcut)
        act.setStatusTip(statustext)
        menu.addAction(act)
        return act

    def setup_menu(self):
        """Setting up the menu
        """
        self.menu_bar = self.menuBar()
        menu = self.menu_bar.addMenu("&File")

        self.menuactions[ID_OPEN] = self.add_action_to_menu(
            "&Open", self.open, 'Ctrl+O', " Bepaal de te vergelijken ini files", menu)
        self.menuactions[ID_DOIT] = self.add_action_to_menu(
            "&Vergelijk", self.doit, 'F5', " Orden en vergelijk de ini files", menu)
        menu.addSeparator()
        self.menuactions[ID_EXIT] = self.add_action_to_menu(
            "E&xit", self.exit, 'Ctrl+Q', "Terminate the program", menu)

        menu = self.menu_bar.addMenu("&Help")
        self.menuactions[ID_ABOUT] = self.add_action_to_menu(
            "&About", self.about, 'F1', " Information about this program", menu)

    def readini(self):
        """inlezen mru-gegevens
        """
        self.mru_left = []
        self.mru_right = []
        self.horizontal = True

        s = ConfigParser()
        s.read(self.inifile)
        if s.has_section("leftpane"):
            for i in range(len(s.options("leftpane"))):
                ky = ("file%i" % (i + 1))
                self.mru_left.append(s.get("leftpane", ky))
        if s.has_section("rightpane"):
            for i in range(len(s.options("rightpane"))):
                ky = ("file%i" % (i + 1))
                self.mru_right.append(s.get("rightpane", ky))

    def schrijfini(self):
        """save parameters
        """
        s = ConfigParser()
        if len(self.mru_left) > 0:
            s.add_section("leftpane")
            for x in enumerate(self.mru_left):
                i = x[0] + 1
                s.set("leftpane", "file%i" % i, x[1])
        if len(self.mru_right) > 0:
            s.add_section("rightpane")
            for x in enumerate(self.mru_right):
                s.set("rightpane", "file%i" % (x[0] + 1), x[1])
        with open(self.inifile, "w") as _out:
            s.write(_out)

    def open(self, event=None):
        """ask for files to compare
        """
        dlg = AskOpenFiles(self).exec_()
        if dlg == qtw.QDialog.Accepted:
            self.doit()

    def doit(self, event=None, first_time=False):
        """perform action
        """
        mld = check_input(self.linkerpad, self.rechterpad, self.selectiontype)
        if mld:
            qtw.QMessageBox.critical(self, apptitel, mld)
            if first_time:
                self.open()
            return
        if self.do_compare():
            if self.linkerpad in self.mru_left:
                self.mru_left.remove(self.linkerpad)
            self.mru_left.insert(0, self.linkerpad)
            if self.rechterpad in self.mru_right:
                self.mru_right.remove(self.rechterpad)
            self.mru_right.insert(0, self.rechterpad)
            self.schrijfini()
            if self.data:
                self.selected_option = self.data[0]
            self.win.refresh_tree()

    def do_compare(self):
        """do the actual comparison
        """
        compare_func = comparetypes[self.selectiontype][1]
        try:
            self.data = compare_func(self.linkerpad, self.rechterpad)
        except Exception:  # as err:
            error, msg, tb = sys.exc_info()
            box = qtw.QMessageBox(self)
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
        """opening blurb
        """
        qtw.QMessageBox.information(self, apptitel, '\n'.join((
            "Met dit programma kun je twee (ini) files met elkaar vergelijken,",
            "maakt niet uit hoe door elkaar de secties en entries ook zitten.",
            "",
            "Het is ook bruikbaar voor XML bestanden.")))

    def keyPressEvent(self, evt):
        """reimplemented standard event handler: Make it possible to use Esc to quit the application
        """
        if evt.key() == core.Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(evt)

    def exit(self):
        "quit"
        self.close()


def main(args):  # left="", right="", method=""):
    "main function"
    app = qtw.QApplication(sys.argv)
    win = MainWindow(None, (args.input), method=args.method)
    win.show()
    sys.exit(app.exec_())
