"""compare logic for html files

output naar hoofdprogramma: list van 3-tuples
1e waarde: node (list of construct names)
2e waarde: list of code lines in linkerfile
3e waarde: list of code lines in rechterfile
"""
import difflib


def read_pyfile(filename):
    """read and input file and reorder the lines

    gather lines for module level and under:
    first the code on the level itself (in the order as they appear in the input)
    then all defs on this level in alphabetical order
    then all classes on this level in alphabetical order
    """
    with open(filename) as pyfile:
        pylines = pyfile.readlines()
    # contents = {'': []}
    # current = {}
    current_indent = 0
    current_construct = []
    construct_dict = {(): []}
    in_construct = False
    for line in pylines:
        if not line.strip() or line.strip().startswith('#'):
            continue
        if line.strip() == line.rstrip():
            indent = 0
            # if current:
            #     contents[current['name']] = current['contents']
            #     current = {}
            if line.startswith(('def', 'class')):
                current_construct = [get_construct_name(line)]
                construct_dict[tuple(current_construct)] = [line.rstrip()]
                in_construct = True
            else:
                current_construct = []
                construct_dict[tuple(current_construct)].append(line.rstrip())
                in_construct = False
        elif in_construct:
            current_indent = calc_indent(line)
            if current_indent < indent and current_construct:
                while current_indent <= calc_indent(current_construct[-1]):
                    current_construct.pop()
            indent = current_indent
            if line.lstrip().startswith(('def', 'class')):
                current_construct.append(get_construct_name(line))
                construct_dict[tuple(current_construct)] = [line.rstrip()]
            else:
                construct_dict[tuple(current_construct)].append(line.rstrip())
        else:
            construct_dict[tuple(current_construct)].append(line.rstrip())
    return construct_dict


def calc_indent(line):
    "calculeate number of leading spaces on line"
    return len(line) - len(line.lstrip())


def get_construct_name(line):
    "determine name of class or function def"
    return line.rsplit('(')[0] if '(' in line else line.rsplit(':')[0]


def compare_pydata(oldfile, newfile):
    """reorder the input files and build the comparison output
    """
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
    diff = difflib.Differ()
    comparer.gui.init_tree('construct', f'code in {comparer.parent.lhs_path}',
                           f'code in {comparer.parent.rhs_path}')
    parentdict = {}
    for line in prepare_values(comparer.parent.data):
        elements, lvalues, rvalues = line
        if not elements:
            elements = ['module level']
        keylist = []
        for level in elements:
            keylist.append(level)
            key = tuple(keylist)
            if key not in parentdict:
                parentdict[key] = add_new_parentnode(comparer, parentdict, key)
        if lvalues and not rvalues:
            add_functionbody_nodes_one_side(comparer, parentdict[key], lvalues, 'left')
        elif rvalues and not lvalues:
            add_functionbody_nodes_one_side(comparer, parentdict[key], rvalues, 'right')
        elif lvalues and rvalues:
            difflines = diff.compare(lvalues, rvalues)
            add_functionbody_nodes_both_sides(comparer, parentdict[key], difflines)


def prepare_values(data):
    """preprocess comparison data, combining values from left and right side where applicable
    """
    newdata = []
    dataitem = []
    for item in sorted(data):
        newkey = item[0] != dataitem[0] if dataitem else True
        if dataitem and newkey:
            newdata.append(tuple(dataitem))
        if newkey:
            dataitem = [item[0], [], []]
        if item[1]:
            dataitem[1] = item[1]
        if item[2]:
            dataitem[2] = item[2]
    if dataitem:
        newdata.append(tuple(dataitem))
    return newdata


def add_new_parentnode(comparer, parentdict, key):
    """add a node for a construct if it doesn't exist yet
    """
    if len(key) == 1:
        node = comparer.gui.build_header(key[-1])
        # comparer.gui.colorize_header(node, side == 'right', side == 'left', False)
    else:
        # parentlist = keylist[:-1]
        # parentkey = tuple(parentlist)
        parentkey = key[:-1]
        node = comparer.gui.build_child(parentdict[parentkey], key[-1].lstrip())
        # comparer.gui.colorize_child(node, side == 'right', side == 'left', False)
    return node


def add_functionbody_nodes_one_side(comparer, parent, values, side):
    """add nodes for the function body when it's only on one side
    """
    top = comparer.gui.build_child(parent, 'function body')
    if side == 'left':
        pos, leftonly, rightonly = 1, True, False
    else:
        pos, leftonly, rightonly = 2, False, True
    # comparer.gui.set_node_text(top, pos, '')
    comparer.gui.colorize_child(top, rightonly, leftonly, False)
    for line in values:
        node = comparer.gui.build_child(top, '')
        comparer.gui.set_node_text(node, pos, line)
        comparer.gui.colorize_child(node, rightonly, leftonly, False)


def add_functionbody_nodes_both_sides(comparer, parent, difflines):
    """add nodes for the function body after comparing the lines
    """
    top = comparer.gui.build_child(parent, 'function body')
    for line in difflines:
        if line[:2] == '? ':
            continue
        leftonly = line[:2] == '- '
        rightonly = line[:2] == '+ '
        value = line[2:]
        node = comparer.gui.build_child(top, '')
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
