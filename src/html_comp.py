"""compare logic for html files

output naar hoofdprogramma: list van 3-tuples
1e waarde: node (element, attribuut, tekst)
2e waarde: entry in linkerfile
3e waarde: entry in rechterfile
"""

import bs4 as bs

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
    # gen1 = (x for x in convert_levels_to_keys(get_htmldata(fn1)))
    gen1 = (x for x in get_htmldata(fn1))
    # gen2 = (x for x in convert_levels_to_keys(get_htmldata(fn2)))
    gen2 = (x for x in get_htmldata(fn2))
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


def get_htmldata(filename, strip_newlines=True, fix_selfclosing=True):
    """read data from document using BeautifulSoup

    extra parameters to avoid a lot of blank lines in the output - possible to override
    """
    with open(filename) as _in:
        data = _in.readlines()  # [x for x in _in]
        if strip_newlines:  # doet eigenlijk strip alles, maar het gaat om de newlines
            data = [x.strip() for x in data]
        html = ''.join(data)
        if fix_selfclosing:
            html = html.replace('<br/>', '<br />').replace('<hr/>', '<hr />')
        soup = bs.BeautifulSoup(html, 'lxml')
        # soup = bs.BeautifulSoup(_in, 'lxml')
    return get_next_level_data(soup)


def get_next_level_data(element, level=0):
    "read data under an element recursively"
    result = []
    for item in element.children:
        if isinstance(item, bs.Tag):
            element_tag = (level, f'<{item.name}>')
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
            result.append([(level, '(text)'), '', item.string])
        else:
            result.append([f"Oops, what's this? {item}", '', ''])
    return result


def convert_levels_to_keys(data):
    "expand level info (tuple of level number and element name) to make better comparison possible"
    current_key = ''
    for item in data:
        leveldata, attrname = item[0], item[1]
        if not current_key:
            item[0] = current_key = level2key(leveldata, current_key)
        else:
            item[0] = current_key = level2key(leveldata, current_key, attrname,
                                              prev_leveldata, prev_attrname)
        prev_leveldata, prev_attrname = leveldata, attrname
    return data


def level2key(leveldata, old_key, attr_name='', prev_leveldata='', prev_attrname=''):
    "add parent levels to level info"
    if old_key == '':
        return [leveldata]
    newlevel, element_name = leveldata
    oldlevel = prev_leveldata[0] if prev_leveldata else newlevel
    if old_key[-1][1].startswith('(attr'):
        old_key.pop(-1)
    if newlevel > oldlevel:
        old_key.append(leveldata)
    elif newlevel < oldlevel:
        while oldlevel - newlevel >= 0:
            old_key.pop(-1)
            oldlevel -= 1
        old_key.append(leveldata)
    elif attr_name:
        old_key.append((newlevel, f'(attr:{attr_name})'))
    return old_key


def refresh_htmlcompare(comparer):
    """(re)do the HTML compare
     """
    comparer.gui.init_tree('Element/Attribute', comparer.parent.lhs_path, comparer.parent.rhs_path)
    parents = {-1: None}
    for item, lvalue, rvalue in comparer.parent.data:
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
            new_node = comparer.gui.build_child(my_parent, node_text)
        else:
            new_node = comparer.gui.build_header(node_text)
        if not attr_name:
            parents[level] = new_node
        if lvalue:
            comparer.gui.set_node_text(new_node, 1, lvalue)
        if rvalue:
            comparer.gui.set_node_text(new_node, 2, rvalue)
        if attr_name or elem_name == '(text)':  # not elem_name:
            if lvalue == '':
                rightonly = True
                comparer.gui.colorize_child(new_node, rightonly, leftonly, difference)
            if rvalue == '':
                leftonly = True
                comparer.gui.colorize_child(new_node, rightonly, leftonly, difference)
            if lvalue and rvalue and lvalue != rvalue:
                difference = True
                comparer.gui.colorize_child(new_node, rightonly, leftonly, difference)
            # geen idee waarom dit uit stond maar dit kleurt de directe parent mee
            # wat gebeurt er als er meer verschillen onder de parent zitten?
            # (dan pakt-ie de kleur van het laatste child)
            # zouden hoger liggende parents niet ook mee (of altijd rood) moeten kleuren?
            if my_parent:
                comparer.gui.colorize_header(my_parent, rightonly, leftonly, difference)
