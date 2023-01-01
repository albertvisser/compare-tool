"""Compare-tool GUI-independent code
"""
import sys
import traceback
import pathlib
from configparser import ConfigParser
import gui
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
    def __init__(self, fileargs, method):
        self.apptitel = "Albert's Compare Tool voor Ini Files"
        self.menudict = {"&File": ((ID_OPEN, "&Open/kies", "Ctrl+O",
                                    "Bepaal de te vergelijken (ini) files", self.open),
                                   (ID_DOIT, "&Vergelijk", "F5",
                                    "Orden en vergelijk de (ini) files", self.doit),
                                   (),
                                   (ID_EXIT, "E&xit", "Ctrl+Q", " Terminate the program",
                                    self.exit)),
                         "&Help": ((ID_ABOUT, "&About", "F1", " Information about this program",
                                    self.about), )}
        self.data = {}
        self.selected_option = ''
        self.comparetype = ''  # = method in wx version
        self.gui = gui.MainWindow(self)
        self.showcomp = ShowComparison(self)
        print(fileargs)
        self.lhs_path, self.rhs_path = get_input_paths(fileargs)

        self.ini = IniFile(str(pathlib.Path(__file__).parent.resolve() / "actif.ini"))

        self.ini.read()
        if method and method in comparetypes:
            self.comparetype = method
        if self.lhs_path and self.rhs_path:
            if not self.comparetype:
                extl = pathlib.Path(self.lhs_path).suffix[1:]
                extr = pathlib.Path(self.rhs_path).suffix[1:]
                if extl == extr and extl.lower() in comparetypes:
                    self.comparetype = extl.lower()
            self.doit(first_time=True)
        else:
            self.about()
            if self.open():
                self.doit()

        self.gui.go()

    def open(self):
        # TODO: doit() geeft ook terug dat het comparetype nog niet is opgegeven
        get_input = AskOpenFiles(self)
        ok = gui.show_dialog(self, self.gui)
        return ok
        # if ok:
        #     self.doit()

    def doit(self, event=None, first_time=False):
        """perform action
        """
        mld = check_input(self.lhs_path, self.rhs_path, self.comparetype)
        if mld:
            self.gui.meld_input_fout(mld)  # qt: critical; wx: unspecified
        else:
            ok, data = do_compare(self.lhs_path, self.rhs_path, self.comparetype)
            if not ok:
                message, data = data[0], data[1]
            elif not data:
                ok = False
                message = 'Vergelijking mislukt'
            if not ok:
                self.gui.meld_vergelijking_fout(message, data)
                mld = 'fout'
        if mld:
            return
        if self.lhs_path in self.ini.mru_left:
            self.ini.mru_left.remove(self.lhs_path)
        self.ini.mru_left.insert(0, self.lhs_path)
        if self.rhs_path in self.ini.mru_right:
            self.ini.mru_right.remove(self.rhs_path)
        self.ini.mru_right.insert(0, self.rhs_path)
        self.ini.write()
        self.data = data
        self.selected_option = self.data[0]
        self.showcomp.refresh()

    def about(self, event=None):
        """opening blurb
        """
        self.gui.meld('\n'.join((
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
    if fileargs:
        if len(fileargs) > 0:
            leftpath = fileargs[0]
        if len(fileargs) > 1:
            rightpath = fileargs[1]
            if len(fileargs) > 2:
                print('excessive filename arguments truncated')
    return leftpath, rightpath


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


class AskOpenFiles:
    def __init__(self, parent):
        self.parent = parent
        self.gui = gui.AskOpenFilesGui(self, size=(400, 200))
        tooltip = ("Geef hier de naam van het {} te vergelijken ini file "
                   "of kies er een uit een lijst met recent gebruikte")
        title = "Selecteer het {} ini file"
        lhs_file = self.gui.add_ask_for_filename(size=(450, -1), label='Vergelijk:',
                                                 browse='Zoek', path='linker',
                                                 tooltip=tooltip, title=title,
                                                 history=self.parent.ini.mru_left,
                                                 value=self.parent.lhs_path)
        rhs_file = self.gui.add_ask_for_filename(size=(450, -1), label='Met:',
                                                 browse='Zoek', path='rechter',
                                                 tooltip=tooltip, title=title,
                                                 history=self.parent.ini.mru_left,
                                                 value=self.parent.lhs_path)
        self.gui.build_screen(lhs_file, rhs_file, 'Soort vergelijking:', comparetypes,
                              oktext= ("&Gebruiken", "Klik hier om de vergelijking uit te voeren"),
                              canceltext=("&Afbreken", "Klik hier om zonder wijzigingen terug te"
                                          " gaan naar het hoofdscherm"))

    def check_input(self, linkerpad, rechterpad, seltype):
        """parse input
        """
        if linkerpad == "":
            return 'Geen linkerbestand opgegeven'
        else:
            if not pathlib.Path(linkerpad).exists():
                return f'Bestand {linkerpad} kon niet gevonden/geopend worden'
        if rechterpad == "":
            return 'Geen rechterbestand opgegeven'
        else:
            if not pathlib.Path(rechterpad).exists():
                return f'Bestand {rechterpad} kon niet gevonden/geopend worden'
        if rechterpad == linkerpad:
            return "Bestandsnamen zijn gelijk"
        if seltype not in comparetypes:
            return 'Geen vergelijkingsmethode gekozen'
        return ''


class ShowComparison:
    def __init__(self, parent):
        self.parent = parent
        self.gui = gui.ShowComparisonGui(parent.gui)
        # self.gui.init_tree("Sectie / Optie:", f"waarde in {self.parent.lhs_path}",
        #                   f"waarde in {self.parent.rhs_path}")
        self.gui.init_tree('Document structure', 'value in "lefthand-side" file',
                              'value in "righthand-side" file')
        if not self.parent.data:
            self.gui.setup_nodata_columns('geen bestanden geladen', "niks om te laten zien",
                                          "hier ook niet")
        else:
            self.refresh()
        self.gui.finish_init()

    def refresh(self):
        """(re)do the comparison
        """
        print('in refresh_tree', self.parent.comparetype)
        comparetypes[self.parent.comparetype][2](self)
        self.gui.refresh_tree()


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
                self.mru_left.append(sett.get("leftpane", f"file{subscript + 1}"))
        if sett.has_section("rightpane"):
            for subscript, _ in enumerate(sett.options("rightpane")):
                self.mru_right.append(sett.get("rightpane", f"file{subscript + 1}"))
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
                sett.set("leftpane", f"file{x[0] + 1}", x[1])
        if self.mru_right:
            sett.add_section("rightpane")
            for x in enumerate(self.mru_right):
                sett.set("rightpane", f"file{x[0] + 1}", x[1])
        ## sett.add_section("options")
        ## sett.set("options","orient_vert",str(self.orient_vert))
        with open(self.fname, "w") as _out:
            sett.write(_out)
