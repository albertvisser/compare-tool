"""Compare-tool GUI-independent code
"""
from configparser import ConfigParser
ID_OPEN = 101
ID_DOIT = 102
ID_EXIT = 109
ID_ABOUT = 120
apptitel = "Albert's compare-tool voor ini-files"


def get_input_paths(fileargs):
    leftpath = rightpath = ''
    if len(fileargs) > 0:
        leftpath = fileargs[0]
    if len(fileargs) > 1:
        rightpath = fileargs[1]
        if len(fileargs) > 2:
            print('excessive filename arguments truncated')
    return leftpath, rightpath


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
