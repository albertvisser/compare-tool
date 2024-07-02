"""Compare logic for xml files

1e kolom: tree position
2e kolom: value left
3e kolom: value right

xml: element tree - uitbreiden met attribuut naam bv
bij <x><y1 a1='1' a2='2'></y1><y2><z1>gragl</z1></y2></x>
(((x, y1), ),'', '')
(((x, y1), a1),'1', '')
(((x, y1), a2),'2', '')
(((x, y2, z1), ),'gargl', '')
"""
import xml.etree.ElementTree as et


def sort_xmldata(fn):
    """sorteert op elementnaam en daarbinnen op waarde van het eerste element
    (instelbaar maken zodat je kunt kiezen op welk attribuut geordend wordt)
    """
    result = []
    tree = et.parse(fn)
    root = tree.getroot()
    # build the root element for the comparison list
    nodevalue = [(root.tag, 0)]         # elements
    if root.items():
        for attr_name, datavalue in sorted(root.items()):
            result.append((nodevalue, attr_name, datavalue))
    else:
        attr_name = datavalue = ''
        result.append((nodevalue, attr_name, datavalue))
    # get a sorted list of the subelement names
    current_element_list = [(root, 0), ]
    process_subelements(result, current_element_list)
    return result


def process_subelements(result, current_element_list):
    """recursive routine to walk through the XML DOM tree
    """
    current_element = current_element_list[-1]
    subelements = sorted(set(x.tag for x in list(current_element[0])))
    for name in subelements:
        ## print(name)
        ## nodevalue = [x for x in current_element_list] + [name]
        element_list = current_element[0].findall(name)
        if len(element_list) > 1:
            # nu eerst subelementen in volgorde leggen maw element_list herordenen
            element_list = sorted(element_list, key=getattrval)
        for ix, element in enumerate(element_list):
            ## print(element.text, [x for x in element.items()])
            nodevalue = [(x[0].tag, x[1]) for x in current_element_list]
            nodevalue.append((name, ix))
            attr_name = ''
            datavalue = element.text
            if datavalue is not None:
                datavalue = datavalue.strip()
            result.append((nodevalue, attr_name, datavalue))
            for attr in sorted(element.items()):
                attr_name, datavalue = attr
                result.append((nodevalue, attr_name, datavalue))
            current_element_list.append((element, ix))
            process_subelements(result, current_element_list)
            current_element_list.pop()
    # return result, current_element_list  # - wellicht werkt het al zonder dit


def getattrval(element):
    """return value of "identifying" attribute

    """
    default = retval = ''
    for attr, val in element.items():
        if not default:
            default = val
        for name in ('id', 'name'):
            if attr == name:
                retval = val
                break
    if not retval:
        retval = default
    return retval


def compare_xmldata(fn1, fn2):
    """compare two similar xml documents
    """
    result = []
    gen1 = (x for x in sort_xmldata(fn1))
    gen2 = (x for x in sort_xmldata(fn2))
    eof_gen1, elem1, attr1, val1 = gen_next(gen1)
    eof_gen2, elem2, attr2, val2 = gen_next(gen2)
    while True:
        if eof_gen1 and eof_gen2:
            break
        get_from_1 = get_from_2 = False
        ## print((sect1, opt1), (sect2, opt2))
        # probleem:dit werkt niet als de elem lijsten ongelijk van lengte zijn want dan
        # is de langste eigenlijk de "kleinste"
        if (eof_gen1, elem1, attr1) < (eof_gen2, elem2, attr2):
            result.append(((elem1, attr1), val1, ''))
            if not eof_gen1:
                get_from_1 = True
        elif (eof_gen1, elem1, attr1) > (eof_gen2, elem2, attr2):
            result.append(((elem2, attr2), '', val2))
            if not eof_gen2:
                get_from_2 = True
        elif (eof_gen1, elem1) < (eof_gen2, elem2):
            result.append(((elem1, attr1), val1, ''))
            if not eof_gen1:
                get_from_1 = True
        elif (eof_gen1, elem1) > (eof_gen2, elem2):
            result.append(((elem2, attr2), '', val2))
            if not eof_gen2:
                get_from_2 = True
        elif attr1 < attr2:
            result.append(((elem1, attr1), val1, ''))
            get_from_1 = True
        elif attr1 > attr2:
            result.append(((elem2, attr2), '', val2))
            get_from_2 = True
        else:
            result.append(((elem1, attr1), val1, val2))
            get_from_1 = True
            get_from_2 = True
        if get_from_1:
            eof_gen1, elem1, attr1, val1 = gen_next(gen1)
        if get_from_2:
            eof_gen2, elem2, attr2, val2 = gen_next(gen2)
    return result


def gen_next(gen):
    "generator to get next values from data collection"
    eof = False
    try:
        elem, attr, val = next(gen)
    except StopIteration:
        eof = True
        elem = attr = val = ''
    return eof, elem, attr, val


def refresh_xmlcompare(self):
    """(re)do the XML compare
     """
    self.gui.init_tree('Element/Attribute', self.parent.lhs_path, self.parent.rhs_path)
    current_elems = []
    rightonly = leftonly = difference = False
    for x in self.parent.data:
        node, lvalue, rvalue = x
        elems, attr = node
        if elems != current_elems:
            if not current_elems:
                header = self.gui.build_header('<>' + elems[-1][0])
            else:
                self.gui.colorize_header(header, rightonly, leftonly, difference)
                if len(elems) > len(current_elems):
                    parent = header
                elif len(elems) < len(current_elems):
                    parent = self.gui.get_parent(self.gui.get_parent(header))
                else:
                    parent = self.gui.get_parent(header)
                header = self.gui.build_child(parent, '<> ' + elems[-1][0])
            current_elems = elems
            rightonly = leftonly = difference = False
        if attr == '':
            self.gui.set_node_text(header, 1, lvalue)
            self.gui.set_node_text(header, 2, rvalue)
            if lvalue == '':
                rightonly = True
            if rvalue == '':
                leftonly = True
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
            continue
        child = self.gui.build_child(header, attr)
        if lvalue is None:
            lvalue = '(no value)'
        if lvalue == '':
            rightonly = True
            self.gui.colorize_child(child, rightonly, leftonly, difference)
        self.gui.set_node_text(child, 1, lvalue)
        if rvalue is None:
            rvalue = '(no value)'
        if rvalue == '':
            leftonly = True
            self.gui.colorize_child(child, rightonly, leftonly, difference)
        if lvalue and rvalue and lvalue != rvalue:
            difference = True
            self.gui.colorize_child(child, rightonly, leftonly, difference)
        self.gui.set_node_text(child, 2, rvalue)
    if self.parent.data:
        self.gui.colorize_header(header, rightonly, leftonly, difference)
