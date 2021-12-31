"""Presentation logic for Compare Tool - PyQT5 version
"""
import sys
import os.path
import pathlib
import PyQt5.QtWidgets as qtw
import PyQt5.QtGui as gui
import PyQt5.QtCore as core
import shared

rightonly_colour = gui.QBrush(core.Qt.blue)
leftonly_colour = gui.QBrush(core.Qt.darkGreen)
difference_colour = gui.QBrush(core.Qt.red)
## inversetext_colour = core.Qt.white


class MainWindow(qtw.QMainWindow):
    """Application screen
    """
    def __init__(self, master):  # parent, args, method=None):
        self.app = qtw.QApplication(sys.argv)
        super().__init__(parent)
        self.menuactions = {}

        self.resize(1024, 600)
        self.setWindowTitle(shared.apptitel)  # 'Vergelijken van ini files')
        self.setWindowIcon(gui.QIcon('inicomp.ico'))
        # self.sb = self.statusBar()
        self.setup_menu()
        self.win = self.master.comp
        self.setCentralWidget(self.win)

    def go(self):
        self.show()
        sys.exit(self.app.exec_())

    def open_files(self):
        """ask for files to compare
        """
        dlg = AskOpenFiles(self).exec_()
        return dlg == qtw.QDialog.Accepted

    def setup_menu(self, menudict):
        """Setting up the menu
        """
        def add_action_to_menu(name, callback, shortcut, statustext, menu):
            """build a menu line
            """
            act = qtw.QAction(name, self)
            act.triggered.connect(callback)
            act.setShortcut(shortcut)
            act.setStatusTip(statustext)
            menu.addAction(act)
            return act
        self.menu_bar = self.menuBar()
        for title, options in menudict.items():
            menu = self.menu_bar.addMenu(title)
            for item in options:
                if not item:
                    menu.addSeparator()
                    continue
                item_id, title, shortcut, text, callback = item
                self.menuactions[item_id] = add_action_to_menu(title, callback, shortcut,
                                                               text, menu)


    def meld(self, mld):
        qtw.QMessageBox.critical(self, shared.apptitel, mld)

    def meld2(self, data):
        box = qtw.QMessageBox(self)
        box.setWindowTitle(shared.apptitel)
        box.setText(data[0])
        box.setInformativeText('<pre>{}</pre>'.format(''.join(data[1])))
        box.exec_()

    def meld3(self, melding):
        qtw.QMessageBox.information(self, shared.apptitel, melding)

    def refresh(self):
        self.win.refresh_tree()

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
                                  text=self.parent.lhs_path,
                                  items=self.parent.ini.mru_left)
        hsizer.addWidget(browse)
        ## self.paths.append((name, browse))
        ## hsizer.addStretch()
        self.sizer.addLayout(hsizer)
        self.browse1 = browse

        hsizer = qtw.QHBoxLayout()
        browse = FileBrowseButton(self, caption='Rechter bestand: ',
                                  text=self.parent.rhs_path,
                                  items=self.parent.ini.mru_right)
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
        for ix, type in enumerate(sorted(shared.comparetypes)):
            text = shared.comparetypes[type][0]
            rb = qtw.QRadioButton(text, self)
            gsizer.addWidget(rb, ix, 1)
            if self.parent.comparetype == type:
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
        mld = shared.check_input(linkerpad, rechterpad, selectiontype)
        if mld:
            qtw.QMessageBox.critical(self, shared.apptitel, mld)
            return
        self.parent.lhs_path = linkerpad
        self.parent.rhs_path = rechterpad
        self.parent.comparetype = selectiontype
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
        hdr.resizeSection(0, 200)
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
        shared.refresh_tree(self)

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
        node.setTextAlignment(column, core.Qt.AlignTop)
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


