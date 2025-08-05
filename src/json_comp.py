"""compare logic for json files

output naar hoofdprogramma: list van 3-tuples
1e waarde: node (list of parent elements)
2e waarde: entry in linkerfile
3e waarde: entry in rechterfile
"""
import json


def compare_jsondata(oldfile, newfile):
    """reorder the input files and build the comparison output
    """
    result = []
    leftgen = (x for x in readjson(oldfile))
    rightgen = (x for x in readjson(newfile))
    eof_gen1, leftitems = gen_next(leftgen)
    eof_gen2, rightitems = gen_next(rightgen)
    while True:
        if eof_gen1 and eof_gen2:
            break
        get_from_1 = get_from_2 = False
        if (eof_gen1, leftitems) < (eof_gen2, rightitems):
            result.append((leftitems, 'left'))
            if not eof_gen1:
                get_from_1 = True
        elif (eof_gen1, leftitems) > (eof_gen2, rightitems):
            result.append((rightitems, 'right'))
            if not eof_gen2:
                get_from_2 = True
        else:
            result.append((leftitems, 'both'))
            get_from_1 = True
            get_from_2 = True
        if get_from_1:
            eof_gen1, leftitems = gen_next(leftgen)
        if get_from_2:
            eof_gen2, rightitems = gen_next(rightgen)
    return result


def refresh_jsoncompare(comparer):
    """redo the comparison (visually)
    """
    # print(newdata, flush=True)
    comparer.gui.init_tree('key/value', comparer.parent.lhs_path, comparer.parent.rhs_path)
    parentdict = {}
    for item in prepare_values(comparer.parent.data):
        elements, lvalue, rvalue = item
        keylist = []
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
        if lvalue:
            comparer.gui.set_node_text(node, 1, lvalue)
        if rvalue:
            comparer.gui.set_node_text(node, 2, rvalue)
        comparer.gui.colorize_child(node, rvalue and not lvalue, lvalue and not rvalue,
                                    lvalue and rvalue and lvalue != rvalue)
        for level in range(len(keylist) -1, 0, -1):
            key = tuple(keylist[:level])
            comparer.gui.colorize_header(parentdict[key], rvalue and not lvalue,
                                         lvalue and not rvalue,
                                         lvalue and rvalue and lvalue != rvalue)


def prepare_values(data):
    """preprocess the comparison data, combining values from left and right side where applicable
    """
    newdata = []
    prev_line = ''
    prev_line_data = ([], '', '')  # (prev_elements, prev_value, prev_side)
    line_to_append = []
    for line in data:
        elements, side = line
        if prev_line and elements[:-1] != prev_line_data[0]:
            newdata.append(line_to_append)
            line_to_append = []
        value = elements.pop()
        if not line_to_append:
            line_to_append = [elements, '', '']
        if side in ('left', 'both'):
            line_to_append[1] = value
        if side in ('right', 'both'):
            line_to_append[2] = value
        prev_line = line
        prev_line_data = (elements, value, side)
    if prev_line:
        newdata.append(line_to_append)
    return newdata


def readjson(filename):
    """read a json file to produce a "data collection"
    """
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
    return read_dict(data)


def read_dict(data):
    "process a dictionary (sub)structure"
    result = []
    for key, dataitem in {x: data[x] for x in sorted(data)}.items():
        if isinstance(dataitem, dict):
            for item in read_dict(dataitem):
                result.append([key, *item])
        elif isinstance(dataitem, list):
            for item in read_list(dataitem):
                result.append([key, *item])
        else:
            result.append([key, str(dataitem)])
    return result


def read_list(data):
    "provcess a list substructure"
    result = []
    for ix, dataitem in enumerate(sorted(data)):
        if isinstance(dataitem, dict):
            for item in read_dict(dataitem):
                result.append([f'listitem{ix:03}', *item])
        elif isinstance(dataitem, list):
            for item in read_list(dataitem):
                result.append([f'listitem{ix:03}', *item])
        else:
            result.append([f'listitem{ix:03}', str(dataitem)])
    return result


def gen_next(gen):
    "generator to get next values from data collection"
    eof = False
    try:
        items = next(gen)
    except StopIteration:
        eof = True
        items = []
    return eof, items
