"""Presentation logic for Compare Tool - Qt version
"""
import sys
import os.path
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as gui
import PyQt6.QtCore as core

nocolour = gui.QBrush(core.Qt.GlobalColor.black)
rightonly_colour = gui.QBrush(core.Qt.GlobalColor.blue)
leftonly_colour = gui.QBrush(core.Qt.GlobalColor.darkGreen)
difference_colour = gui.QBrush(core.Qt.GlobalColor.red)
## inversetext_colour = core.Qt.white


class MainWindow(qtw.QMainWindow):
    """Application screen
    """
    def __init__(self, master):  # parent, args, method=None):
        self.master = master
        self.app = qtw.QApplication(sys.argv)
        parent = None
        super().__init__(parent)
        self.menuactions = {}

        self.resize(1024, 600)
        self.setWindowTitle(self.master.apptitel)  # 'Vergelijken van ini files')
        self.setWindowIcon(gui.QIcon('inicomp.png'))
        # self.sb = self.statusBar()
        self.setup_menu()

    def setup_menu(self):
        """Setting up the menu
        """
        def add_action_to_menu(name, callback, shortcut, statustext, menu):
            """build a menu line
            """
            act = gui.QAction(name, self)
            act.triggered.connect(callback)
            act.setShortcut(shortcut)
            act.setStatusTip(statustext)
            menu.addAction(act)
            return act
        self.menu_bar = self.menuBar()
        for title, options in self.master.menudict.items():
            menu = self.menu_bar.addMenu(title)
            for item in options:
                if not item:
                    menu.addSeparator()
                    continue
                item_id, itemtitle, shortcut, text, callback = item
                self.menuactions[item_id] = add_action_to_menu(itemtitle, callback, shortcut,
                                                               text, menu)

    def go(self):   # , leftpath, rightpath, method):
        "display the screen and start the event loop"
        self.win = self.master.showcomp.gui
        self.setCentralWidget(self.win)
        self.show()
        mld = self.master.inputgetter.check_input()
        if mld:
            qtw.QMessageBox.critical(self, self.master.apptitel, mld)
            self.master.open()
        else:
            self.master.doit()
        sys.exit(self.app.exec())

    def meld_vergelijking_fout(self, message, data):
        "show comparison error(s)"
        # print(data)
        box = qtw.QMessageBox(self)
        box.setWindowTitle(self.master.apptitel)
        box.setText(message)
        if data:
            # box.setTextFormat(core.Qt.TextFormat.PlainText)
            # box.setInformativeText(f'<pre>{"".join(data)}</pre>')
            box.setTextFormat(core.Qt.TextFormat.MarkdownText)
            box.setInformativeText(f'```\n{"".join(data)}```\n')
        box.exec()

    def meld(self, melding):
        "show a message"
        qtw.QMessageBox.information(self, self.master.apptitel, melding)

    def refresh(self):
        "redisplay the subscreen"
        self.win.refresh_tree()

    def keyPressEvent(self, evt):
        """reimplemented standard event handler: Make it possible to use Esc to quit the application
        """
        if evt.key() == core.Qt.Key.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(evt)

    def exit(self):
        "quit"
        self.close()


def show_dialog(master, parent):
    """show a dialog and return the result

    parent argument is voor compatibiliteit met wx versie
    """
    # dlg.update_typeselector()
    master.gui.update_typeselector()
    # ok = dlg.exec()
    ok = master.gui.exec()
    return ok == qtw.QDialog.DialogCode.Accepted


class AskOpenFilesGui(qtw.QDialog):
    """dialog om de te vergelijken bestanden op te geven

    voor elk file een combobox om direct een filenaam op te geven of te kiezen
    uit een lijst met eerder gebruikte, met een button ernaast om de filenaam te
    selecteren met behulp van een file selector dialoog
    de te tonen lijsten worden bewaard in een bestand aangegeven door self.inifile
    """
    def __init__(self, master, size, title):
        self.master = master
        super().__init__(master.parent.gui)
        ## self.resize(size)  # (680, 400)
        self.setWindowTitle(title)
        self.vsizer = qtw.QVBoxLayout()
        self.setLayout(self.vsizer)

    def add_ask_for_filename(self, size, label, browse, path, tooltip, title, history, value):
        "create a widget for selecting a file"
        hsizer = qtw.QHBoxLayout()
        fbb = FileBrowseButton(self, caption=label, button=browse, text=value, items=history)
        hsizer.addWidget(fbb)
        self.vsizer.addLayout(hsizer)
        return fbb

    def create_fileselector_grid(self, linedefs):
        "build a grid for the file selector widgets"
        gsizer = qtw.QGridLayout()
        for ix, linedef in enumerate(linedefs):
            caption, selector = linedef
            lbl = qtw.QLabel(caption)
            # lbl.setMinimumWidth(120)
            # lbl.setMaximumWidth(120)
            gsizer.addWidget(lbl, ix, 0)
            gsizer.addWidget(selector, ix, 1)
        self.vsizer.addLayout(gsizer)

    def build_typeselector(self, comparetext, choices):
        "build a collection of radiobuttons"
        hsizer = qtw.QHBoxLayout()
        hsizer.addSpacing(10)
        gsizer = qtw.QGridLayout()
        gsizer.addWidget(qtw.QLabel(comparetext), 0, 0)
        optionlist = []
        for ix, cmptype in enumerate(sorted(choices)):
            text = choices[cmptype][0]
            rb = qtw.QRadioButton(text, self)
            gsizer.addWidget(rb, ix, 1)
            optionlist.append((rb, cmptype))
        hsizer.addLayout(gsizer)
        hsizer.addStretch()
        self.vsizer.addLayout(hsizer)
        return optionlist

    def add_buttons(self, oktext, canceltext):
        "add the confirm / reject buttons"
        # ok/canceltext zijn tuples van button text en tooltip text
        buttonbox = qtw.QDialogButtonBox()
        buttonbox.addButton(qtw.QDialogButtonBox.StandardButton.Ok)
        buttonbox.addButton(qtw.QDialogButtonBox.StandardButton.Cancel)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)
        hsizer = qtw.QHBoxLayout()
        hsizer.addStretch()
        hsizer.addWidget(buttonbox)
        hsizer.addStretch()
        self.vsizer.addLayout(hsizer)

    def update_typeselector(self):
        "gebruikte vergelijkingsmethode aangeven bij uitsturen"
        for rb, cmptype in self.master.options:
            rb.setChecked(False)
            if cmptype == self.master.parent.comparetype:
                rb.setChecked(True)

    def accept(self):
        """transmit the chosen data
        """
        mld = self.master.check_input()
        if mld:
            qtw.QMessageBox.critical(self, self.master.parent.apptitel, mld)
        else:
            super().accept()

    def get_fbb_result(self, fbb):
        """return the filebrowsebutton's selcted / entered name
        """
        return fbb.input.currentText()

    def get_radiobox_value(self, rb):
        """return the radiobutton's value (checked or not)
        """
        return rb.isChecked()


class ShowComparisonGui(qtw.QTreeWidget):
    """Part of the main window showing the comparison as a tree
    """
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent.gui)
        self.setColumnCount(3)
        #  hoef ik de kleuren hier niet in te stellen?
        hdr = self.header()
        hdr.resizeSection(0, 200)
        ## hdr.resizeSection(0, 350)
        hdr.resizeSection(1, 350)

    def setup_nodata_columns(self, root_text, leftcaption, rightcaption):
        "set header texts when there's no data to be shown"
        root = qtw.QTreeWidgetItem()
        # root.setText(0, root_text)  # moet deze er ook nog niet bij?
        root.setText(1, leftcaption)
        root.setText(2, rightcaption)
        self.addTopLevelItem(root)
        return root  # for testing

    def show_tree(self):
        "render the area"
        self.show()

    def refresh_tree(self):
        """after (re)doing the comparison
        """
        # no extra action needed

    # API methods to be called from the specific refresh functions
    def init_tree(self, caption, *args):  # left_title, right_title):
        "setup empty tree with given titles"
        self.clear()
        left_title, right_title = self.parent.get_titles(*args)
        self.setHeaderLabels([caption, left_title, right_title])

    def build_header(self, section):
        """create a header item
        """
        header = qtw.QTreeWidgetItem()
        self.set_node_text(header, 0, section)
        self.addTopLevelItem(header)
        header.setForeground(0, nocolour)
        return header

    def colorize_header(self, node, rightonly, leftonly, difference):
        """visualize the difference by coloring the header
        """
        testcolour = node.foreground(0)
        colour_to_set = None
        if testcolour == nocolour:
            if rightonly and not leftonly:
                colour_to_set = rightonly_colour
            elif leftonly and not rightonly:
                colour_to_set = leftonly_colour
            elif difference or (leftonly and rightonly):
                colour_to_set = difference_colour
        elif testcolour == leftonly_colour:
            if rightonly or difference:
                colour_to_set = difference_colour
        elif testcolour == rightonly_colour:
            if leftonly or difference:
                colour_to_set = difference_colour
        if colour_to_set:
            node.setForeground(0, colour_to_set)
            if node.text(1):
                node.setForeground(1, colour_to_set)
            if node.text(2):
                node.setForeground(2, colour_to_set)

    def build_child(self, header, option):
        """create a child under this header
        """
        child = qtw.QTreeWidgetItem()
        self.set_node_text(child, 0, option)
        child.setForeground(0, nocolour)
        header.addChild(child)
        return child

    def colorize_child(self, node, rightonly, leftonly, difference):
        """visualize the difference by coloring the child texts
        self is only used for API's sake
        """
        if leftonly:  # and not rightonly:
            columns = (0, 1)
            colour = leftonly_colour
        elif rightonly:  # and not leftonly:
            columns = (0, 2)
            colour = rightonly_colour
        elif difference:  # or (leftonly and rightonly):
            columns = (0, 1, 2)
            colour = difference_colour
        else:
            columns = ()
        for colno in columns:
            node.setForeground(colno, colour)

    def set_node_text(self, node, column, value):
        """set tooltip as well as text so that truncated text can be viewed in full
        self is only used for API's sake
        """
        node.setText(column, value)
        node.setTextAlignment(column, core.Qt.AlignmentFlag.AlignTop)
        node.setToolTip(column, value)

    def get_parent(self, node):
        """retrieve parent of current node
        """
        return node.parent()


class FileBrowseButton(qtw.QFrame):
    """Combination widget showing a text field and a button
    making it possible to either manually enter a filename or select
    one using a FileDialog
    """
    def __init__(self, parent, caption="", button="", text="", items=None):
        self.parent = parent
        if items is None:
            items = []
        super().__init__(parent)
        self.setFrameStyle(qtw.QFrame.Shape.Panel | qtw.QFrame.Shadow.Raised)
        vbox = qtw.QVBoxLayout()
        box = qtw.QHBoxLayout()
        ## self.input = gui.QLineEdit(text, self)
        self.input = qtw.QComboBox(self)
        self.input.setEditable(True)
        self.input.setMaximumWidth(300)
        self.input.addItems(items)
        self.input.setEditText(text)
        box.addWidget(self.input)
        self.button = qtw.QPushButton(button, self, clicked=self.browse)
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
