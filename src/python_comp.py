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
    contents = []
    for key in sorted(construct_dict):
        contents.extend(construct_dict[key])
    return contents


def compare_pydata(oldfile, newfile):
    """reorder the input files and build the comparison output
    """
    diff = difflib.Differ()
    oldfile_lines = read_pyfile(oldfile)
    newfile_lines = read_pyfile(newfile)
    return diff.compare(oldfile_lines, newfile_lines)

def refresh_pycompare(comparer):
    """redo the comparison
    """
    comparer.gui.init_tree('code in both', f'code in {comparer.parent.lhs_path}',
                           f'code in {comparer.parent.rhs_path}')
    prev_indent = 0
    prev_node = ''
    # parents = {-1: None}
    parents = []
    for line in  comparer.parent.data:
        line_prefix = line[:2]
        line_data = line[2:]
        nodevalue = lvalue = rvalue = ''
        if line_prefix == '  ':
            nodevalue = line_data
        elif line_prefix == '- ':
            lvalue = line_data
        elif line_prefix == '+ ':
            rvalue = line_data
        else:  # bv. '? '
            continue
        indent = len(line_data) - len(line_data.strip())
        if indent == 0:
            prev_node = comparer.gui.build_header(nodevalue)
            if lvalue:
                comparer.gui.set_node_text(prev_node, 0, lvalue)
                comparer.gui.set_node_text(prev_node, 1, lvalue)
            if rvalue:
                comparer.gui.set_node_text(prev_node, 0, rvalue)
                comparer.gui.set_node_text(prev_node, 2, rvalue)
            parents = []
        else:
            if indent > prev_indent:
                parents.append(prev_node)
            elif indent < prev_indent:
                parents.pop()
            prev_node = comparer.gui.build_child(parents[-1], nodevalue)
            if lvalue:
                comparer.gui.set_node_text(prev_node, 1, lvalue)
            if rvalue:
                comparer.gui.set_node_text(prev_node, 2, rvalue)
        prev_indent = indent
