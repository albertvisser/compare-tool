"""Compare-tool GUI-independent code
"""
import pathlib
from configparser import ConfigParser
# import exception types so they can be caught in calling modules
from conf_comp import compare_configs, compare_configs_2, MissingSectionHeaderError
from xml_comp import compare_xmldata, ParseError
from txt_comp import compare_txtdata
ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
apptitel = "Albert's Compare Tool voor Ini Files"
comparetypes = {
    'ini': ('ini files', compare_configs),
    'ini2': ('ini files, allowing for missing first header', compare_configs_2),
    'xml': ('XML files', compare_xmldata),
    'txt': ('Simple text comparison', compare_txtdata)}


def get_input_paths(fileargs):
    "split up incoming file arguments"
    leftpath = rightpath = ''
    if len(fileargs) > 0:
        leftpath = fileargs[0]
    if len(fileargs) > 1:
        rightpath = fileargs[1]
        if len(fileargs) > 2:
            print('excessive filename arguments truncated')
    return leftpath, rightpath


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
    return ''


def refresh_inicompare(self):
    """(re)do comparing the ini files
    """
    self.init_tree('Section/Option', self.parent.lhs_path, self.parent.rhs_path)
    current_section = ''
    for x in self.parent.data:
        node, lvalue, rvalue = x
        section, option = node
        if section != current_section:
            if current_section:
                self.colorize_header(header, rightonly, leftonly, difference)
            header = self.build_header(section)
            current_section = section
            rightonly = leftonly = difference = False
        child = self.build_child(header, option)
        if lvalue is None:
            lvalue = '(no value)'
        if lvalue == '':
            rightonly = True
            self.colorize_child(child, rightonly, leftonly, difference)
        self.set_node_text(child, 1, lvalue)
        if rvalue is None:
            rvalue = '(no value)'
        if rvalue == '':
            leftonly = True
            self.colorize_child(child, rightonly, leftonly, difference)
        if lvalue and rvalue and lvalue != rvalue:
            difference = True
            self.colorize_child(child, rightonly, leftonly, difference)
        self.set_node_text(child, 2, rvalue)
    if self.parent.data:
        self.colorize_header(header, rightonly, leftonly, difference)


def refresh_xmlcompare(self):
    """(re)do the XML compare
     """
    self.init_tree('Element/Attribute', self.parent.lhs_path, self.parent.rhs_path)
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
                self.colorize_header(header, rightonly, leftonly, difference)
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
        self.colorize_header(header, rightonly, leftonly, difference)


def refresh_txtcompare(self):
    """(re)do the text compare
    """
    self.init_tree('Text in both files', self.parent.lhs_path, self.parent.rhs_path)
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


class IniFile:
    """interface to file conatining program settings
    """
    def __init__(self, fileref):
        self.fname = fileref

    def read(self):
        """inlezen mru-gegevens
        """
        self.mru_left = []
        self.mru_right = []
        self.horizontal = True     # heet self.orient_vert in wx version

        sett = ConfigParser()
        sett.read(self.fname)
        if sett.has_section("leftpane"):
            for subscript, _ in enumerate(sett.options("leftpane")):
                ky = "file%i" % (subscript + 1)
                self.mru_left.append(sett.get("leftpane", ky))
        if sett.has_section("rightpane"):
            for subscript, _ in enumerate(sett.options("rightpane")):
                ky = "file%i" % (subscript + 1)
                self.mru_right.append(sett.get("rightpane", ky))
        ## if s.has_section("options"):
            ## if s.has_option("options","orient_vert"):
                ## if s.getboolean("options","orient_vert"):
                    ## self.orient_vert = True

    def write(self):
        """terugschrijven mru-gegevens
        """
        sett = ConfigParser()
        if self.mru_left:
            sett.add_section("leftpane")
            for x in enumerate(self.mru_left):
                i = x[0] + 1
                sett.set("leftpane", "file%i" % i, x[1])
        if self.mru_right:
            sett.add_section("rightpane")
            for x in enumerate(self.mru_right):
                sett.set("rightpane", "file%i" % (x[0] + 1), x[1])
        ## sett.add_section("options")
        ## sett.set("options","orient_vert",str(self.orient_vert))
        with open(self.fname, "w") as _out:
            sett.write(_out)
