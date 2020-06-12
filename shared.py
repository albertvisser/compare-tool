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
