"""Compare-tool GUI-independent code
"""
import sys
import traceback
import pathlib
from configparser import ConfigParser
import subprocess
from . import gui
from .conf_comp import compare_configs, compare_configs_safe, refresh_inicompare
from .xml_comp import compare_xmldata, refresh_xmlcompare
from .txt_comp import compare_txtdata, refresh_txtcompare
from .html_comp import compare_htmldata, refresh_htmlcompare
from .python_comp import compare_pydata, refresh_pycompare
from .json_comp import compare_jsondata, refresh_jsoncompare
from .json5_comp import compare_json5data, refresh_json5compare

ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
ID_COLORS = 121
comparetypes = {'ini': ('ini files', compare_configs, refresh_inicompare),
                'ini2': ('ini files, allowing for missing first header', compare_configs_safe,
                         refresh_inicompare),
                'xml': ('XML files', compare_xmldata, refresh_xmlcompare),
                'html': ('HTML files', compare_htmldata, refresh_htmlcompare),
                'txt': ('Simple text comparison', compare_txtdata, refresh_txtcompare),
                'py': ('Python modules', compare_pydata, refresh_pycompare),
                'json': ('JSON files', compare_jsondata, refresh_jsoncompare),
                'json5': ('JSON files, JSON5 spec (more lenient)', compare_json5data,
                          refresh_json5compare)}
abouttext = """\
Met dit programma kun je twee (ini) files met elkaar vergelijken,
maakt niet uit hoe door elkaar de secties en entries ook zitten.

Het is ook bruikbaar voor XML en JSON bestanden, HTML documenten en Python code.

Het is zelfs mogelijk om voor een bestand dat in een GIT repository getracked wordt
de versie in de working tree te vergelijken met de versie in de repo head.
"""
colors_text = """\
Rood: aan beide kanten aanwezig, verschillend
Groen: alleen aanwezig in linkerfile
Blauw: alleen aanwezig in rechterfile"""
TMPROOT = '/tmp/compare-tool'


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
                                   (ID_EXIT, "E&xit", "Ctrl+Q", "Terminate the program",
                                    self.exit)),
                         "&Help": ((ID_ABOUT, "&About", "Ctrl+H", "Information about this program",
                                    self.about),
                                   (ID_COLORS, "&Legenda", "F1", "What do the colors indicate?",
                                    self.legend), )}
        self.data = {}
        self.comparetype = ''
        self.gui = gui.MainWindow(self)
        self.lhs_path = 'value in `lefthand-side` file'
        self.rhs_path = 'value in `righthand-side` file'
        self.showcomp = ShowComparison(self)
        # print(fileargs)
        if method and method in comparetypes:
            self.comparetype = method
        self.lhs_path, self.rhs_path = get_input_paths(fileargs)
        # if not self.comparetype:
        #     self.comparetype = self.auto_determine_comparetype(self.lhs_path, self.rhs_path)

        self.ini = IniFile(str(pathlib.Path(__file__).parent.parent.resolve() / "actif.ini"))
        self.ini.read()
        self.inputgetter = AskOpenFiles(self)
        if not self.lhs_path or not self.rhs_path:
            self.about()
            # self.open()
        self.gui.go()  # self.lhs_path, self.rhs_path, self.comparetype)

    def open(self, event=None):
        "show open dialog"
        # ok = gui.show_dialog(self.inputgetter, self.inputgetter.gui)
        ok = gui.show_dialog(self.inputgetter, self.gui)
        if ok:
            self.doit()
        # return ok

    @staticmethod
    def auto_determine_comparetype(leftpath, rightpath):
        "try to guess the comparison type from the file extension (only if they match)"
        extl = pathlib.Path(leftpath).suffix[1:] if leftpath else ''
        extr = pathlib.Path(rightpath).suffix[1:] if rightpath else ''
        if extl == extr and extl.lower() in comparetypes:
            return extl.lower()
        return ''

    def doit(self, event=None):   # , first_time=False):
        """perform action
        """
        if not self.comparetype:
            return
        ok, data = do_compare(self.lhs_path, self.rhs_path, self.comparetype)
        if not ok:
            message, data = data[0], data[1]
        elif not data:
            ok = False
            message = 'Vergelijking mislukt'
        if not ok:
            self.gui.meld_vergelijking_fout(message, data)
            return
        if self.lhs_path in self.ini.mru_left:
            self.ini.mru_left.remove(self.lhs_path)
        self.ini.mru_left.insert(0, self.lhs_path)
        if self.rhs_path in self.ini.mru_right:
            self.ini.mru_right.remove(self.rhs_path)
        self.ini.mru_right.insert(0, self.rhs_path)
        self.ini.write()
        self.data = data
        self.showcomp.refresh()

    def get_titles(self, *args):
        """return 2 provided input strings as titles or "calculate" them
        """
        if args:
            left_title, right_title = args
        else:
            left_title = self.lhs_path
            if self.rhs_path.startswith(TMPROOT):
                right_title = 'repository version'
            else:
                right_title = self.rhs_path
        return left_title, right_title

    def about(self, event=None):
        """opening blurb
        """
        self.gui.meld(abouttext)

    def legend(self, event=None):
        """explanation of the colors used
        """
        self.gui.meld(colors_text)

    def exit(self, event=None):
        "quit"
        self.gui.exit()


def get_input_paths(fileargs):
    "split up incoming file arguments"
    leftpath = rightpath = ''
    if fileargs:
        # if len(fileargs) > noargs:
        leftpath = fileargs[0]
        if len(fileargs) > 1:
            rightpath = fileargs[1]
            if len(fileargs) > 2:
                print('excessive filename arguments truncated')
        else:
            if repofile := is_tracked_file(fileargs[0]):
                repodir, repofile = repofile
                tmploc = pathlib.Path(f'{TMPROOT}/{repodir.name}/{repofile}')
                tmploc.parent.mkdir(parents=True, exist_ok=True)
                with tmploc.open('w') as f_out:
                    try:
                        subprocess.run(['git', 'show', f'master:{repofile}'],  # capture_output=True,
                                       stdout=f_out,
                                       cwd=repodir.expanduser(),
                                       check=True)
                    except subprocess.CalledProcessError:
                        raise ValueError(f'{fileargs[0]} is not a tracked file in a repository')
                leftpath, rightpath = str(tmploc), leftpath
    return leftpath, rightpath


def is_tracked_file(filename):
    """check if path is a file tracked in a git repo.
    If so, return a tuple of the name of the repo and the file's location within the repo
    """
    repodir = repofile = ''
    path = pathlib.Path(filename).resolve()
    # quick & dirty versie
    # try:
    #     newpath = path.relative_to(pathlib.Path('~/projects').expanduser())
    # except ValueError:
    #     return ()
    # reponame = newpath.parents[-1].resolve().name
    # nette(re) versie
    # walk up the path to check for a gt repo
    for parent in path.parents:
        for pth in parent.iterdir():
            if pth.name == '.git' and pth.is_dir():
                repodir = parent
                repofile = path.relative_to(parent)
                break
        if repodir:
            break
    return (repodir, str(repofile)) if repodir else ()


def do_compare(leftpath, rightpath, selectiontype):
    "do the actual comparison"
    compare_func = comparetypes[selectiontype][1]
    try:
        data = compare_func(leftpath, rightpath)
        result = True
    # except (MissingSectionHeaderError, ParseError):  # specifieke exceptions horen eigenlijk in de
    #     error, msg, tb = sys.exc_info()              # compare routine thuis
    except Exception:
        error, msg, tb = sys.exc_info()
        data = ['Something went wrong:', traceback.format_exception(error, msg, tb)]
        result = False
    return result, data


class AskOpenFiles:
    """gui-onafhankelijke master class voor dialog om de te vergelijken bestanden op te geven
    """
    def __init__(self, parent):
        self.parent = parent
        self.gui = gui.AskOpenFilesGui(self, size=(400, 200), title=self.parent.apptitel)

        tooltip = ("Geef hier de naam van het {} te vergelijken ini file "
                   "of kies er een uit een lijst met recent gebruikte")
        title = "Selecteer het {} ini file"
        self.lhs_file = self.gui.add_ask_for_filename(size=(450, -1), label='Vergelijk:',
                                                      browse='Zoek', path='linker',
                                                      tooltip=tooltip, title=title,
                                                      history=self.parent.ini.mru_left,
                                                      value=self.parent.lhs_path)
        self.rhs_file = self.gui.add_ask_for_filename(size=(450, -1), label='Met:',
                                                      browse='Zoek', path='rechter',
                                                      tooltip=tooltip, title=title,
                                                      history=self.parent.ini.mru_right,
                                                      value=self.parent.rhs_path)

        self.gui.create_fileselector_grid([('Vergelijk:', self.lhs_file), ('Met:', self.rhs_file)])
        types_to_select = dict(comparetypes)
        types_to_select[''] = ('Autodetect', )
        self.options = self.gui.build_typeselector('Soort vergelijking:', types_to_select)
        self.gui.update_typeselector()
        self.gui.add_buttons(("&Gebruiken", "Klik hier om de vergelijking uit te voeren"),
                             ("&Afbreken", "Klik hier om zonder wijzigingen terug te gaan naar het"
                              " hoofdscherm"))

    def check_input(self):
        """parse input
        """
        linkerpad = self.gui.get_fbb_result(self.lhs_file)
        rechterpad = self.gui.get_fbb_result(self.rhs_file)
        selectiontype = ''
        for rb, cmptype in self.options[1:]:
            if self.gui.get_radiobox_value(rb):
                selectiontype = cmptype
                break
        else:
            selectiontype = self.parent.auto_determine_comparetype(linkerpad, rechterpad)
        mld = ''
        if linkerpad == "":
            mld = 'Geen linkerbestand opgegeven'
        elif rechterpad == "":
            mld = 'Geen rechterbestand opgegeven'
        elif not pathlib.Path(linkerpad).exists():
            mld = f'Bestand {linkerpad} kon niet gevonden/geopend worden'
        elif not pathlib.Path(rechterpad).exists():
            mld = f'Bestand {rechterpad} kon niet gevonden/geopend worden'
        elif rechterpad == linkerpad:
            mld = "Bestandsnamen zijn gelijk"
        elif selectiontype not in comparetypes:
            mld = 'Geen vergelijkingsmethode gekozen en niet automatisch te bepalen'
        else:
            self.parent.lhs_path = linkerpad
            self.parent.rhs_path = rechterpad
            self.parent.comparetype = selectiontype
        return mld


class ShowComparison:
    """Gui-independent master class for the main window part showing the comparison as a tree
    """
    def __init__(self, parent):
        self.parent = parent
        self.gui = gui.ShowComparisonGui(parent)
        # self.gui.init_tree("Sectie / Optie:", f"waarde in {self.parent.lhs_path}",
        #                   f"waarde in {self.parent.rhs_path}")
        self.gui.init_tree('Document structure', 'value in `lefthand-side` file',
                           'value in `righthand-side` file')
        if not self.parent.data:
            self.gui.setup_nodata_columns('geen bestanden geladen', "niks om te laten zien",
                                          "hier ook niet")
        else:
            self.refresh()
        self.gui.show_tree()

    def refresh(self):
        """(re)do the comparison
        """
        # print('in refresh_tree', self.parent.comparetype)
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
        self.horizontal = True

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
