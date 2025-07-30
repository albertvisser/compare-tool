import sys
import os
import difflib
import pprint


def read_pyfile(filename):
    """read and input file and reorder the lines

    gather lines for module level and under:
    first the code on the level itself (in the order as they appear in the input)
    then all defs on this level in alphabetical order
    then all classes on this level in alphabetical order
    """
    def calc_indent(line):
        return len(line) - len(line.lstrip())
    with open(filename) as pyfile:
        pylines = pyfile.readlines()
    # breakpoint()
    contents = {'': []}
    # defs = {}
    # classes = {}
    current = {}  # 'name': '', 'contents': []}
    current_indent = 0
    current_construct = []
    construct_dict = {(): []}
    in_construct = False
    for line in pylines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        if line.strip() == line.rstrip():
            indent = 0
            if current:
                contents[current['name']] = current['contents']
                current = {}
            if line.startswith('def'):
                current_construct = [line.split('(')[0]]
                construct_dict[tuple(current_construct)] = [line.rstrip()]
                in_construct = True
            elif line.startswith('class'):
                if '(' in line:
                    current_construct = [line.rsplit('(')[0]]
                else:
                    current_construct = [line.rsplit(':')[0]]
                construct_dict[tuple(current_construct)] = [line.rstrip()]
                in_construct = True
            else:
                current_construct = []
                construct_dict[tuple(current_construct)].append(line.rstrip())
                in_construct = False
        elif in_construct:
            current_indent = calc_indent(line)  # len(line) - len(line.lstrip())
            if current_indent < indent and current_construct:
                while current_indent <= calc_indent(current_construct[-1]):
                # len(current_construct[-1]) - len(current_construct[-1].lstrip())
                    current_construct.pop()
            indent = current_indent
            if line.lstrip().startswith('def'):
                current_construct.append(line.split('(')[0])
                construct_dict[tuple(current_construct)] = [line.rstrip()]
            elif line.lstrip().startswith('class'):
                if '(' in line:
                    current_construct.append(line.rsplit('(')[0])
                else:
                    current_construct.append(line.rsplit(':')[0])
                construct_dict[tuple(current_construct)] = [line.rstrip()]
            else:
                construct_dict[tuple(current_construct)].append(line.rstrip())
        else:
            construct_dict[tuple(current_construct)].append(line.rstrip())
    if in_construct:
        construct_dict[tuple(current_construct)].append(line.rstrip())
    else:
        construct_dict[()].append(line.rstrip())
    return construct_dict
    # contents = []
    # for key in sorted(construct_dict):
    #     contents.extend(construct_dict[key])
    # for key, item in construct_dict.items():
    #     print(f'{key=}\n  {item=}')
    # return contents


def compare_pydata(oldfile, newfile):
    """reorder the input files and build the comparison output
    """
    # diff = difflib.Differ()yy
    # oldfile_lines = read_pyfile(oldfile)
    # newfile_lines = read_pyfile(newfile)
    # return diff.compare(oldfile_lines, newfile_lines)
    # ordenen per key; alleen diffen wat links en rechts onder dezelfde key zit
    # breakpoint()
    result = []
    # wat we gaan vergelijken is alleen de keys
    leftdict = read_pyfile(oldfile)
    rightdict = read_pyfile(newfile)
    leftgen = (x for x in leftdict)
    rightgen = (x for x in rightdict)
    eof_gen1, leftitems = gen_next(leftgen)
    eof_gen2, rightitems = gen_next(rightgen)
    while True:
        if eof_gen1 and eof_gen2:
            break
        get_from_1 = get_from_2 = False
        if (eof_gen1, leftitems) < (eof_gen2, rightitems):
            result.append((leftitems, leftdict[leftitems], []))
            if not eof_gen1:
                get_from_1 = True
        elif (eof_gen1, leftitems) > (eof_gen2, rightitems):
            result.append((rightitems, [], rightdict[rightitems]))
            if not eof_gen2:
                get_from_2 = True
        else:
            result.append((leftitems, leftdict[leftitems], rightdict[rightitems]))
            get_from_1 = True
            get_from_2 = True
        if get_from_1:
            eof_gen1, leftitems = gen_next(leftgen)
        if get_from_2:
            eof_gen2, rightitems = gen_next(rightgen)
    return result


def refresh_pycompare(comparer):
    """redo the comparison (visually)
    """
    # voorbewerking
    newdata = []
    dataitem = []
    # breakpoint()
    for item in sorted(comparer.parent.data):
        newkey = item[0] != dataitem[0] if dataitem else True
        if dataitem and newkey:
            newdata.append(tuple(dataitem))
        if newkey:
            dataitem = [item[0], [], []]
        if item[1]:
            dataitem[1] = item[1]
        if item[2]:
            dataitem[2] = item[2]
    newdata.append(tuple(dataitem))



    diff = difflib.Differ()
    comparer.gui.init_tree('construct', f'code in {comparer.parent.lhs_path}',
                           f'code in {comparer.parent.rhs_path}')
    prev_indent = 0
    prev_node = ''
    # parents = {-1: None}
    parents = []
    # in de nieuwe variant hebben we per item:
    #   een sleutel, regels voor de linkerkant, en regels voor de rechterkant
    # parents aanmaken net als bij jsoncompare
    # als alleen links of rechts: alle regels aanmaken als children
    # als beide: difflib loslaten op de sets met regels, resultaat aanmaken als children
    parentdict = {}
    for line in newdata:
        # print(line, flush=True)
        elements, lvalues, rvalues = line
        if not elements:
            elements = ['module level']
        keylist = []
        # breakpoint()
        for level in elements:
            keylist.append(level)
            key = tuple(keylist)
            if key not in parentdict:
                if len(key) == 1:
                    node = comparer.gui.build_header(key[-1])
                    # comparer.gui.colorize_header(node, side == 'right', side == 'left', False)
                else:
                    parentlist = keylist[:-1]
                    parentkey = tuple(parentlist)
                    node = comparer.gui.build_child(parentdict[parentkey], key[-1])
                    # comparer.gui.colorize_child(node, side == 'right', side == 'left', False)
                parentdict[key] = node
        if lvalues and not rvalues:
            for line in lvalues:
                node = comparer.gui.build_child(parentdict[key], '')
                comparer.gui.set_node_text(node, 1, line)
                comparer.gui.colorize_child(node, False, True, False)
        elif rvalues and not lvalues:
            for line in rvalues:
                node = comparer.gui.build_child(parentdict[key], '')
                comparer.gui.set_node_text(node, 2, line)
                comparer.gui.colorize_child(node, True, False, False)
        elif lvalues and rvalues:
            difflines = diff.compare(lvalues, rvalues)
            for line in difflines:
                if line[:2] == '? ':
                    continue
                leftonly = line[:2] == '- '
                rightonly = line[:2] == '+ '
                value = line[2:]
                node = comparer.gui.build_child(parentdict[key], '')
                if not leftonly:
                    comparer.gui.set_node_text(node, 2, value)
                if not rightonly:
                    comparer.gui.set_node_text(node, 1, value)
                comparer.gui.colorize_child(node, rightonly, leftonly, False)


def gen_next(gen):
    "generator to get next values from data collection"
    eof = False
    try:
        items = next(gen)
    except StopIteration:
        eof = True
        items = []
    return eof, items
