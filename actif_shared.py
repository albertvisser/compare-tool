"""Compare-tool GUI-independent code
"""
import sys
import traceback
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
catchables = (MissingSectionHeaderError, ParseError)


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


def do_compare(leftpath, rightpath, selectiontype):
    "do the actual comparison"
    compare_func = comparetypes[selectiontype][1]
    try:
        data = compare_func(leftpath, rightpath)
        return True, data
    except catchables:
        error, msg, tb = sys.exc_info()
        # set data to info to show in message
        if error == catchables[0]:
            info = "begint niet met een header"
        elif error == catchables[1]:
            info = "bevat geen correcte XML"
        else:
            info = "geeft een fout"
        data = ['Tenminste één file {}'.format(info)]
        data.append(traceback.format_exception(error, msg, tb))
        return False, data


def refresh_tree(self):
    """(re)do the comparison
    """
    print('in refresh_tree', self.parent.comparetype)
    if self.parent.comparetype in ('ini', 'ini2'):
        refresh_inicompare(self)
    elif self.parent.comparetype == 'xml':
        refresh_xmlcompare(self)
    elif self.parent.comparetype == 'txt':
        refresh_txtcompare(self)


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
    current_elems = []
    for x in self.parent.data:
        node, lvalue, rvalue = x
        elems, attr = node
        if elems != current_elems:
            if not current_elems:
                header = self.build_header('<>' + elems[-1][0])
            else:
                self.colorize_header(header, rightonly, leftonly, difference)
                if len(elems) > len(current_elems):
                    parent = header
                elif len(elems) < len(current_elems):
                    parent = self.get_parent(self.get_parent(header))
                else:
                    parent = self.get_parent(header)
                header = self.build_child(parent, '<> ' + elems[-1][0])
            current_elems = elems
            rightonly = leftonly = difference = False
        if attr == '':
            self.set_node_text(header, 1, lvalue)
            self.set_node_text(header, 2, rvalue)
            if lvalue == '':
                rightonly = True
            if rvalue == '':
                leftonly = True
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
            continue
        child = self.build_child(header, attr)
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


def refresh_txtcompare(self):
    """(re)do the text compare
    """
    self.init_tree('Text in both files', self.parent.lhs_path, self.parent.rhs_path)
    for x in self.parent.data:
        bvalue, lvalue, rvalue = x
        rightonly = leftonly = difference = False
        node = self.build_header(bvalue)
        self.set_node_text(node, 1, lvalue)
        self.set_node_text(node, 2, rvalue)
        if lvalue:
            leftonly = True
        if rvalue:
            rightonly = True
        self.colorize_child(node, rightonly, leftonly, difference)


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
