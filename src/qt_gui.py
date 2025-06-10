"""Presentation logic for Compare Tool - Qt version
"""
import sys
import os.path
import PyQt6.QtWidgets as qtw
import PyQt6.QtGui as gui
import PyQt6.QtCore as core

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

    def go(self):
        "display the screen and start the event loop"
        self.win = self.master.showcomp.gui
        self.setCentralWidget(self.win)
        self.show()
        sys.exit(self.app.exec())

    def meld_input_fout(self, mld):
        "show invalid input message"
        qtw.QMessageBox.critical(self, self.master.apptitel, mld)

    def meld_vergelijking_fout(self, message, data):
        "show comparison error(s)"
        box = qtw.QMessageBox(self)
        box.setWindowTitle(self.master.apptitel)
        box.setText(message)
        if data:
            box.setInformativeText(f'<pre>{"".join(data)}</pre>')
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


def show_dialog(parent, cls):
    """show a dialog and return the result

    parent argument is voor compatibiliteit met wx versie
    """
    ok = cls.exec()
    return ok == qtw.QDialog.DialogCode.Accepted


class AskOpenFilesGui(qtw.QDialog):
    """dialog om de te vergelijken bestanden op te geven

    voor elk file een combobox om direct een filenaam op te geven of te kiezen
    uit een lijst met eerder gebruikte, met een button ernaast om de filenaam te
    selecteren met behulp van een file selector dialoog
    de te tonen lijsten worden bewaard in een bestand aangegeven door self.inifile
    """
    def __init__(self, master, size):
        self.master = master
        super().__init__(master.parent.gui)
        ## self.resize(size)  # (680, 400)

    def add_ask_for_filename(self, size, label, browse, path, tooltip, title, history, value):
        "add a line for selecting a file"
        return FileBrowseButton(self, caption=label, button=browse, text=value, items=history)

    def build_screen(self, leftfile, rightfile, comparetext, choices, oktext, canceltext):
        "do the screen layout"
        self.sizer = qtw.QVBoxLayout()

        hsizer = qtw.QHBoxLayout()
        hsizer.addWidget(leftfile)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse1 = leftfile

        hsizer = qtw.QHBoxLayout()
        hsizer.addWidget(rightfile)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse2 = rightfile

        hsizer = qtw.QHBoxLayout()
        hsizer.addSpacing(10)
        gsizer = qtw.QGridLayout()
        gsizer.addWidget(qtw.QLabel(comparetext), 0, 0)
        self.sel = []
        for ix, type_ in enumerate(sorted(choices)):
            text = choices[type_][0]
            rb = qtw.QRadioButton(text, self)
            gsizer.addWidget(rb, ix, 1)
            if self.master.parent.comparetype == type_:
                rb.setChecked(True)
            self.sel.append((rb, type_))
        hsizer.addLayout(gsizer)
        hsizer.addStretch()
        self.sizer.addLayout(hsizer)

        # eigenlijk hier ook die oktext en canceltext gebruiken
        buttonbox = qtw.QDialogButtonBox()
        buttonbox.addButton(qtw.QDialogButtonBox.StandardButton.Ok)
        buttonbox.addButton(qtw.QDialogButtonBox.StandardButton.Cancel)
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
            # print('   ', ix)
            if sel[0].isChecked():
                selectiontype = sel[1]
                break
        mld = self.master.check_input(linkerpad, rechterpad, selectiontype)
        if mld:
            qtw.QMessageBox.critical(self, self.master.parent.apptitel, mld)
            return
        self.master.parent.lhs_path = linkerpad
        self.master.parent.rhs_path = rechterpad
        self.master.parent.comparetype = selectiontype
        super().accept()


class ShowComparisonGui(qtw.QTreeWidget):
    """Part of the main window showing the comparison as a tree
    """
    def __init__(self, parent):
        self.parent = parent
        super().__init__(parent)
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

    def finish_init(self):
        "render the area"
        self.show()

    def refresh_tree(self):
        """after (re)doing the comparison
        """
        # no extra action needed

    # API methods to be called from the specific refresh functions
    def init_tree(self, caption, left_title, right_title):
        "setup empty tree with given titles"
        self.clear()
        self.setHeaderLabels([caption, left_title, right_title])

    def build_header(self, section):
        """create a header item
        """
        header = qtw.QTreeWidgetItem()
        self.set_node_text(header, 0, section)
        self.addTopLevelItem(header)
        return header

    def colorize_header(self, node, rightonly, leftonly, difference):
        """visualize the difference by coloring the header
        """
        if rightonly and not leftonly:
            node.setForeground(0, rightonly_colour)
        if leftonly and not rightonly:
            node.setForeground(0, leftonly_colour)
        if difference or (leftonly and rightonly):
            node.setForeground(0, difference_colour)

    def build_child(self, header, option):
        """create a child under this header
        """
        child = qtw.QTreeWidgetItem()
        self.set_node_text(child, 0, option)
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
        lbl = qtw.QLabel(caption)
        lbl.setMinimumWidth(120)
        lbl.setMaximumWidth(120)
        box.addWidget(lbl)
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
