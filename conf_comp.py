import sys
import os
import collections
import pprint
# vergelijk entries in config file

from configparser import ConfigParser, MissingSectionHeaderError

def sort_inifile(fn):
    """define a generator that yields the sorted options
    """
    test = ConfigParser(allow_no_value=True, interpolation=None)
    test.read(fn)
    for sect in sorted(test.sections()):
    ## for sect in test.sections():
        for opt in sorted(test.options(sect)):
        ## for opt in test.options(sect):
            ## print(sect, opt, test[sect][opt])
            yield sect, opt, test[sect][opt]

def check_inifile(fn):
    """copy to a temporary file, making sure first line contains a section header

    returns the name of the temporary file
    """
    hlpfn = os.path.join('/tmp', os.path.basename(fn))
    with open(fn,encoding='latin-1') as f_in, open(hlpfn, 'w') as f_out:
        first = True
        for line in f_in:
            if first:
                if not line.startswith('['):
                    f_out.write('[  --- generated first header ---  ]\n')
                first = False
            f_out.write(line)
    return hlpfn

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
        eof = False
        try:
            sect, opt, val = next(gen)
        except StopIteration:
            eof = True
            sect = opt = val = ''
        return eof, sect, opt, val
    current_sect = current_opt = ''
    eof_gen1, sect1, opt1, val1 = gen_next(gen1)
    eof_gen2, sect2, opt2, val2 = gen_next(gen2)
    # nog leuke trucjes met itertools mogelijk?
    while True:
        if eof_gen1 and eof_gen2:
            break
        get_from_1 = get_from_2 = False
        ## print((sect1, opt1), (sect2, opt2))
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

if __name__ == "__main__":
    f1 = "actif.ini"
    ## f1 = check_inifile(f1)
    ## pprint.pprint(build_options_list(f1))
    ## print()
    f2 = "testing.ini"
    ## f2 = check_inifile(f2)
    ## pprint.pprint(build_options_list(f2))
    ## print()
    f2 = "jvscompare.ini"
    pprint.pprint(compare_configs(f1, f2))
    ## compare_configs(f1, f2)
    ## fn = "wincmd.ini"
    ## pprint.pprint(build_options_list(fn))

    ## test_afrift(f1, f2)
    ## test_readini(f1)
    ## test_readini(f2)
    ## fn = "wincmd.ini"
    ## test_myNCP(fn)
    ## test_myCP(fn)
    ## test_readini(fn)
