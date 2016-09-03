import xml.etree.ElementTree as et
import collections
import pprint
ParseError = et.ParseError

"""

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

def sort_xmldata(fn):
    """sorteert op elementnaam en daarbinnen op waarde van het eerste element
    (instelbaar maken zodat je kunt kiezen op welk attribuut geordend wordt)
    """
    def getattrval(element):
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
    def process_subelements():
        nonlocal result, current_element_list
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
                retlist = process_subelements()
                current_element_list.pop()
    result = []
    tree = et.parse(fn)
    root = tree.getroot()
    # build the root element for the comparison list
    nodevalue = [(root.tag, 0)]         # elements
    if root.items():
        attr_name, datavalue = root.items()[0]  # name/value of (in this case first) attribute
    else:
        attr_name = datavalue = ''
    result.append((nodevalue, attr_name, datavalue))
    # get a sorted list of the subelement names
    current_element_list = [(root, 0),]
    process_subelements()
    return result

def compare_xmldata(fn1, fn2):
    """compare two similar xml documents
    """
    result = []
    gen1 = (x for x in sort_xmldata(fn1))
    gen2 = (x for x in sort_xmldata(fn2))
    def gen_next(gen):
        eof = False
        try:
            elem, attr, val = next(gen)
        except StopIteration:
            eof = True
            elem = attr = val = ''
        return eof, elem, attr, val
    current_elem = current_attr = ''
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
            if (eof_gen1, elem1)  < (eof_gen2, elem2):
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


def main():
    ## pprint.pprint(compare_xmldata('.lmmsrc.xml', '.lmmsrc_o.xml'))
    ## pprint.pprint(sort_xmldata('.lmmsrc.xml'))
    with open('bezettingen_current', 'w') as _o:
        pprint.pprint(sort_xmldata('/home/albert/magiokis/data/songs/'
            'magiokis_songs_xmldata/Bezettingen.xml'), stream=_o)
    with open('bezettingen_backup', 'w') as _o:
        pprint.pprint(sort_xmldata('/home/albert/magiokis/data/songs/'
            'magiokis_songs_xmldata/Bezettingen.xml.bak'), stream=_o)
    with open('bezettingen_compare', 'w') as _o:
        pprint.pprint(compare_xmldata('/home/albert/magiokis/data/songs/'
            'magiokis_songs_xmldata/Bezettingen.xml', '/home/albert/magiokis/'
            'data/songs/magiokis_songs_xmldata/Bezettingen.xml.bak'), stream=_o)

if __name__ == '__main__':
    main()
