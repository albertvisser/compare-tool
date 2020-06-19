"""Compare logic for ini files

sort sections and options before comparing
"""
import pathlib
import pprint
from configparser import ConfigParser, MissingSectionHeaderError


def sort_inifile(fn):
    """define a generator that yields the sorted options
    """
    test = ConfigParser(allow_no_value=True, interpolation=None)
    try:
        test.read(fn)
    except UnicodeDecodeError:
        test.read(fn, encoding='latin-1')  # fallback for MS Windows
    for sect in sorted(test.sections()):
        for opt in sorted(test.options(sect)):
            yield sect, opt, test[sect][opt]


def check_inifile(fn):
    """copy to a temporary file, making sure first line contains a section header

    returns the name of the temporary file
    """
    fn = pathlib.Path(fn)
    hlpfn = pathlib.Path('/tmp') / fn.name
    try_again = False
    with fn.open() as f_in, hlpfn.open('w') as f_out:
        try:
            first = True
            for line in f_in:
                if first:
                    if not line.startswith('['):
                        f_out.write('[  --- generated first header ---  ]\n')
                    first = False
                f_out.write(line)
        except UnicodeDecodeError:  # fallback for Windows
            try_again = True
    if try_again:
        with fn.open(encoding='latin-1') as f_in, hlpfn.open('w') as f_out:
            first = True
            for line in f_in:
                if first:
                    if not line.startswith('['):
                        f_out.write('[  --- generated first header ---  ]\n')
                    first = False
                f_out.write(line)
    return str(hlpfn)


def build_options_list(fn):
    """return a sorted list of options
    """
    result = []
    gen = sort_inifile(fn)
    while True:
        try:
            result.append(next(gen))
        except StopIteration:
            break
    return result


def compare_configs(fn1, fn2):
    """compare two ini files
    """
    result = []
    gen1 = sort_inifile(fn1)
    gen2 = sort_inifile(fn2)

    def gen_next(gen):
        "generator to get next item from file"
        eof = False
        try:
            sect, opt, val = next(gen)
        except StopIteration:
            eof = True
            sect = opt = val = ''
        return eof, sect, opt, val
    eof_gen1, sect1, opt1, val1 = gen_next(gen1)
    eof_gen2, sect2, opt2, val2 = gen_next(gen2)
    # nog leuke trucjes met itertools mogelijk?
    while True:
        if eof_gen1 and eof_gen2:
            break
        get_from_1 = get_from_2 = False
        if (eof_gen1, sect1) < (eof_gen2, sect2):
            result.append(((sect1, opt1), val1, ''))
            if not eof_gen1:
                get_from_1 = True
        elif (eof_gen1, sect1) > (eof_gen2, sect2):
            result.append(((sect2, opt2), '', val2))
            if not eof_gen2:
                get_from_2 = True
        else:
            if opt1 < opt2:
                result.append(((sect1, opt1), val1, ''))
                get_from_1 = True
            elif opt1 > opt2:
                result.append(((sect2, opt2), '', val2))
                get_from_2 = True
            else:
                result.append(((sect1, opt1), val1, val2))
                get_from_1 = True
                get_from_2 = True
        if get_from_1:
            eof_gen1, sect1, opt1, val1 = gen_next(gen1)
        if get_from_2:
            eof_gen2, sect2, opt2, val2 = gen_next(gen2)
    return result


def compare_configs_2(fn1, fn2):
    """compare two ini files, allowing for missing headers
    """
    fn1 = check_inifile(fn1)
    fn2 = check_inifile(fn2)
    return compare_configs(fn1, fn2)


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
