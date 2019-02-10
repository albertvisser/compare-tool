"""out-of-sequence tekst vergelijking

eenvoudigweg sorteren en daarna vergelijken
geen diff-logica als whitespace negeren e.d. (voor nu)
"""


def get_file(fn):
    """return a sorted list of lines from the file
    """
    data = []
    f_in = open(fn)
    try:
        with f_in:
            data = sorted(f_in.readlines())
    except UnicodeDecodeError:
        f_in = open(fn, encoding='latin-1')
        with f_in:
            data = sorted(f_in.readlines())
    return data


def compare_txtdata(fn1, fn2):
    """compare two text files
    """
    left_data = get_file(fn1)
    right_data = get_file(fn2)
    result = []
    gen1 = (x.rstrip() for x in left_data)
    gen2 = (x.rstrip() for x in right_data)

    def gen_next(gen):
        "generator to get next item from file"
        eof = False
        try:
            nextline = next(gen)
        except StopIteration:
            nextline = ''
            eof = True
        return eof, nextline
    eof1, line1 = gen_next(gen1)
    eof2, line2 = gen_next(gen2)
    while True:
        if eof1 and eof2:
            break
        get_from_1 = get_from_2 = False
        if (eof1, line1) < (eof2, line2):
            result.append(['', line1, ''])
            get_from_1 = True
        elif (eof1, line1) > (eof2, line2):
            result.append(['', '', line2])
            get_from_2 = True
        else:
            result.append([line1, '', ''])
            get_from_1 = True
            get_from_2 = True
        if get_from_1:
            if not eof1:
                eof1, line1 = gen_next(gen1)
        if get_from_2:
            if not eof2:
                eof2, line2 = gen_next(gen2)
    return result
