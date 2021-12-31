"""Compare-tool GUI-independent code
"""
import sys
import traceback
import pathlib
from configparser import ConfigParser
# import exception types so they can be caught in calling modules
from conf_comp import (compare_configs, compare_configs_2, refresh_inicompare,
    MissingSectionHeaderError)
from xml_comp import compare_xmldata, refresh_xmlcompare, ParseError
from txt_comp import compare_txtdata, refresh_txtcompare
from html_comp import compare_htmldata, refresh_htmlcompare
ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
apptitel = "Albert's Compare Tool voor Ini Files"
comparetypes = {'ini': ('ini files', compare_configs, refresh_inicompare),
                'ini2': ('ini files, allowing for missing first header', compare_configs_2,
                         refresh_inicompare),
                'xml': ('XML files', compare_xmldata, refresh_xmlcompare),
                'html': ('HTML files', compare_htmldata, refresh_htmlcompare),
                'txt': ('Simple text comparison', compare_txtdata, refresh_txtcompare)}
catchables = (MissingSectionHeaderError, ParseError)


class Comparer:
    """Application class
    """
    def __init__(self, args):
        self.comp = ShowComparison(self)
        self.win = gui.MainWindow(self)
        self.lhs_path, self.rhs_path = shared.get_input_paths(args)

        self.ini = shared.IniFile(str(pathlib.Path(__file__).parent.resolve() / "actif.ini"))
        self.hier = getcwd()
        self.ini = shared.IniFile(self.hier + "/actif.ini")

        self.ini.read()
        self.data = {}
        self.selected_option = ''
        self.comparetype = ''  # = method in wx version
        if method and method in shared.comparetypes:
            self.comparetype = method
        if self.lhs_path and self.rhs_path:
            if not self.comparetype:
                extl = pathlib.Path(self.lhs_path).suffix[1:]
                extr = pathlib.Path(self.rhs_path).suffix[1:]
                if extl == extr and extl.lower() in shared.comparetypes:
                    self.comparetype = extl.lower()
            self.doit(first_time=True)
        else:
            self.about()
            self.open()

        win.go()

    def setup_menu(self):
        self.gui.setup_menu(("&File", (
                (shared.ID_OPEN, "&Open/kies", "Ctrl+O", "Bepaal de te vergelijken (ini) files",
                    self.open),
                (shared.ID_DOIT, "&Vergelijk", "F5", "Orden en vergelijk de (ini) files"),
                    self.doit),
                (),
                (shared.ID_EXIT, "E&xit", "Ctrl+Q", " Terminate the program", self.exit)),
            ("&Help", ((shared.ID_ABOUT, "&About", "F1", " Information about this program",i
                self.about))))

    def open(self):
        # TODO: doit() geeft ook terug dat het comparetype nog niet is opgegeven
        if gui.open_files():
            self.doit()

    def doit(self, event=none, first_time=false):
        """perform action
        """
        mld = shared.check_input(self.lhs_path, self.rhs_path, self.comparetype)
        if mld:
            self.gui.meld(...)
            if first_time:
                self.open()
            return True
        ok, data = shared.do_compare(self.lhs_path, self.rhs_path, self.comparetype)
        if not ok:  # qt versie
        if not ok or not data:  # wx versie
            self.gui.meld2(...)
            return True  # True brengt ons terug in de invoerlus in open()
        if self.lhs_path in self.ini.mru_left:
            self.ini.mru_left.remove(self.lhs_path)
        self.ini.mru_left.insert(0, self.lhs_path)
        if self.rhs_path in self.ini.mru_right:
            self.ini.mru_right.remove(self.rhs_path)
        self.ini.mru_right.insert(0, self.rhs_path)
        self.ini.write()
        self.data = data
        if self.data:
            self.selected_option = self.data[0]
        self.gui.refresh()
        return False

    def about(self, event=None):
        """opening blurb
        """
        self.gui.meld3(
        qtw.QMessageBox.information(self, shared.apptitel, '\n'.join((
            "Met dit programma kun je twee (ini) files met elkaar vergelijken,",
            "maakt niet uit hoe door elkaar de secties en entries ook zitten.",
            "",
            "Het is ook bruikbaar voor XML bestanden.")))

    def exit(self):
        "quit"
        self.gui.exit()


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
    comparetypes[self.parent.comparetype][2](self)
    # if self.parent.comparetype in ('ini', 'ini2'):
    #     refresh_inicompare(self)
    # elif self.parent.comparetype == 'xml':
    #     refresh_xmlcompare(self)
    # elif self.parent.comparetype == 'html':
    #     refresh_htmlcompare(self)
    # elif self.parent.comparetype == 'txt':
    #     refresh_txtcompare(self)


class IniFile:
    """interface to file containing program settings
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
