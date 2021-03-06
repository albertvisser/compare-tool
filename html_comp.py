"""compre logic for html files

output naar hoofdprogramma: list van 3-tuples
1e waarde: node (element, attribuut, tekst)
2e waarde: entry in linkerfile
3e waarde: entry in rechterfile
"""

import sys
import bs4 as bs
import pprint

# hoofdroutine: compare_htmldata - kan misschien overgenomen worden uit xml vergelijking en dan
# gefinetuned

# lezen html bestand - m.b.v. BeautifulSoup - generator die afdalend in de boomstructuur
# - in volgorde van het document de elementen opsomt die erin voorkomen (alleen de tagnaam)
# - de bijbehorende attributen sorteert op naam en naam + waarde teruggeeft
# - de gevonden string of strings toont in volgorde van het document
# - de volgorde van elementen en teksten moet intact blijven
# - attributen van een element moeten wel gesorteerd worden


def compare_htmldata(fn1, fn2):
    """compare two similar html documents
    """
    result = []
    gen1 = (x for x in get_htmldata(fn1))
    gen2 = (x for x in get_htmldata(fn2))

    def gen_next(gen):
        "generator to get next values from data collection"
        eof = False
        try:
            elem, attr, val = next(gen)
        except StopIteration:
            eof = True
            elem = attr = val = ''
        return eof, elem, attr, val
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
        else:
            if (eof_gen1, elem1) < (eof_gen2, elem2):
                result.append(((elem1, attr1), val1, ''))
                if not eof_gen1:
                    get_from_1 = True
            elif (eof_gen1, elem1) > (eof_gen2, elem2):
                result.append(((elem2, attr2), '', val2))
                if not eof_gen2:
                    get_from_2 = True
            else:
                if attr1 < attr2:
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


def get_htmldata(filename, strip_newlines=True, fix_selfclosing=True):
    """read data from document using BeautifulSoup

    extra parameters to avoid a lot of blank lines in the output - possible to override
    """
    with open(filename) as _in:
        data = _in.readlines()  # [x for x in _in]
        if strip_newlines:
            data = [x.strip() for x in data]
        html = ''.join(data)
        if fix_selfclosing:
            html = html.replace('<br/>', '<br />').replace('<hr/>', '<hr />')
        soup = bs.BeautifulSoup(html, 'lxml')
        # soup = bs.BeautifulSoup(_in, 'lxml')
    return get_next_level_data(soup)


def get_next_level_data(element, level=0):
    "read data under an element"
    result = []
    for item in element.children:
        if isinstance(item, bs.Tag):
            element_tag = (level, '<{}>'.format(item.name))
            result.append([element_tag, '', ''])
            if item.attrs is not None:
                # eerst even ongesorteerd
                for name in sorted(item.attrs):
                    value_list = item.get_attribute_list(name)
                    for value in sorted(value_list):
                        result.append([element_tag, name, value])
            result.extend(get_next_level_data(item, level + 1))
        elif isinstance(item, bs.Comment):
            result.append([(level, '<!>'), '', item.string])
        elif isinstance(item, bs.NavigableString):
            result.append([(level, '<"">'), '', item.string])
        else:
            result.append(["Oops, what's this?" + str(item), '', ''])
    return result


def refresh_htmlcompare(self):
    """(re)do the HTML compare
     """
    self.init_tree('Element/Attribute', self.parent.lhs_path, self.parent.rhs_path)
    current_elems = []
    parents = {-1: None}
    for item, lvalue, rvalue in self.parent.data:
        node, attr_name = item
        level, elem_name = node
        if not attr_name:
            my_parent = parents[level - 1]
            node_text = elem_name
        else:
            my_parent = parents[level]
            node_text = ' ' + attr_name
        rightonly = leftonly = difference = False
        if my_parent:
            new_node = self.build_child(my_parent, node_text)
        else:
            new_node = self.build_header(node_text)
        if not attr_name:
            parents[level] = new_node
        if lvalue:
            self.set_node_text(new_node, 1, lvalue)
        if rvalue:
            self.set_node_text(new_node, 2, rvalue)
        if attr_name or not elem_name:
            if lvalue == '':
                rightonly = True
                self.colorize_child(new_node, rightonly, leftonly, difference)
            if rvalue == '':
                leftonly = True
                self.colorize_child(new_node, rightonly, leftonly, difference)
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
                self.colorize_child(new_node, rightonly, leftonly, difference)
            # if my_parent:
            #     self.colorize_header(my_parent, rightonly, leftonly, difference)

