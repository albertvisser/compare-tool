"""unittests for ./src/xml_comp.py
"""
import types
import textwrap
import pytest
from src import xml_comp as testee


def test_getattrval():
    """unittest for xml_comp.getattrval
    """
    class MockElement:
        """stub
        """
        def __init__(self, attrs):
            self._attrs = attrs
        def items(self):
            return self._attrs.items()
    assert testee.getattrval(MockElement({})) == ''
    assert testee.getattrval(MockElement({'x': 'xxx', 'a': 'aaa'})) == 'xxx'
    assert testee.getattrval(MockElement({'data': 'xxx', 'id': 'yyy'})) == 'yyy'
    assert testee.getattrval(MockElement({'name': 'xxx', 'value': 'yyy'})) == 'xxx'


# 61->63
def test_process_subelements(monkeypatch, capsys):
    """unittest for xml_comp.process_subelements
    """
    class MockElement:
        """stub
        """
        def __init__(self, name):
            self.tag = name
            if '-' in name:
                self.children = []
            else:
                self.children = [MockElement(f'{name}-3'), MockElement(f'{name}-1'),
                                 MockElement(f'{name}-1')]
            self.text = f"{name}-text"
        def repr(self):
            return f"<Element '{self.tag}'"
        def __iter__(self):
            return (x for x in self.children)
        def __lt__(self, other):
            return self.tag < other.tag

        def findall(self, name):
            print(f"called Element.findall with arg '{name}'")
            return [x for x in self.children if x.tag == name]
        def items(self):
            print(f"called Element.items with arg '{self.tag}'")
            return [(f'{self.tag}-attr2', 'yyy'), (f'{self.tag}-attr1', 'xxx')]
    def mock_getattrval(name):
        print(f"called getattrval with arg '{name}'")
        return name
    monkeypatch.setattr(testee, 'getattrval', mock_getattrval)
    root_element = MockElement('root_tag')
    root_node = [(root_element.tag, 0)]
    result = [(root_node, '', '')]
    current_element_list = [(root_element, 0)]
    testee.process_subelements(result, current_element_list)
    assert result == [([('root_tag', 0)], '', ''),
                      ([('root_tag', 0), ('root_tag-1', 0)], '', 'root_tag-1-text'),
                      ([('root_tag', 0), ('root_tag-1', 0)], 'root_tag-1-attr1', 'xxx'),
                      ([('root_tag', 0), ('root_tag-1', 0)], 'root_tag-1-attr2', 'yyy'),
                      ([('root_tag', 0), ('root_tag-1', 1)], '', 'root_tag-1-text'),
                      ([('root_tag', 0), ('root_tag-1', 1)], 'root_tag-1-attr1', 'xxx'),
                      ([('root_tag', 0), ('root_tag-1', 1)], 'root_tag-1-attr2', 'yyy'),
                      ([('root_tag', 0), ('root_tag-3', 0)], '', 'root_tag-3-text'),
                      ([('root_tag', 0), ('root_tag-3', 0)], 'root_tag-3-attr1', 'xxx'),
                      ([('root_tag', 0), ('root_tag-3', 0)], 'root_tag-3-attr2', 'yyy')]
    assert current_element_list == [(root_element, 0),]
    assert capsys.readouterr().out == ("called Element.findall with arg 'root_tag-1'\n"
                                       f"called getattrval with arg '{root_element.children[1]}'\n"
                                       f"called getattrval with arg '{root_element.children[2]}'\n"
                                       "called Element.items with arg 'root_tag-1'\n"
                                       "called Element.items with arg 'root_tag-1'\n"
                                       "called Element.findall with arg 'root_tag-3'\n"
                                       "called Element.items with arg 'root_tag-3'\n")


def test_sort_xmldata(monkeypatch, capsys):
    """unittest for xml_comp.sort_xmldata
    """
    class MockElement:
        """stub
        """
        def __init__(self):
            print('called etree.Element')
            self.tag = 'root'
        def items(self):
            print('called etree.Element.items')
            return []
    class MockTree:
        """stub
        """
        def __init__(self, *args):
            print('called etree.ElementTree with args', args)
        def getroot(self):
            print('called etree.ElementTree.getroot')
            return MockElement()
    def mock_parse(*args):
        print('called etree,parse with args', args)
        return MockTree()
    def mock_process(*args):
        print('called process_subelements')  # with args', args)
        args[0].append('processed subelements')
    def mock_items(self):
        print('called etree.Element.items')
        return [('b', 'yyy'), ('a', 'xxx')]
    monkeypatch.setattr(testee.et, 'parse', mock_parse)
    monkeypatch.setattr(testee, 'process_subelements', mock_process)
    assert testee.sort_xmldata('fname') == [([('root', 0)], '', ''), 'processed subelements']
    assert capsys.readouterr().out == (
            "called etree,parse with args ('fname',)\n"
            "called etree.ElementTree with args ()\n"
            "called etree.ElementTree.getroot\n"
            "called etree.Element\n"
            "called etree.Element.items\n"
            "called process_subelements\n")
    monkeypatch.setattr(MockElement, 'items', mock_items)
    assert testee.sort_xmldata('fname') == [([('root', 0)], 'a', 'xxx'),
                                            ([('root', 0)], 'b', 'yyy'),
                                            'processed subelements']
    assert capsys.readouterr().out == (
            "called etree,parse with args ('fname',)\n"
            "called etree.ElementTree with args ()\n"
            "called etree.ElementTree.getroot\n"
            "called etree.Element\n"
            "called etree.Element.items\n"
            "called process_subelements\n")


def test_gen_next():
    """unittest for xml_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, '', '', '')
    assert testee.gen_next(x for x in [(1, 2, 3)]) == (False, 1, 2, 3)


# 109->137, 113->137
def test_compare_xmldata(monkeypatch, capsys, expected_output):
    """unittest for xml_comp.compare_xmldata
    """
    def mock_sort(fname):
        print(f"called sort_xmldata with arg '{fname}'")
        return ['data']
    counter = 0
    def mock_next(gen):
        nonlocal counter
        counter += 1
        gen = 'left' if counter == 1 else 'right'
        result = (False, gen, 'x', 'y')
        print(f'called gen_next from {gen} side returning {result}')
        return result
    def mock_next_2(gen):
        nonlocal counter
        _data = [(False, [('top', 0)], '', '', 'left'),
                 (False, [('top', 0)], '', '', 'right'),
                 (False, [('top', 0), ('dat', 0)], '', 'contents2', 'left'),
                 (False, [('top', 0), ('daaro', 0)], '', '', 'right'),
                 (False, [('top', 0), ('daaro', 0), ('niet-hiero', 0)], '', None, 'right'),
                 (False, [('top', 0), ('deze', 0)], '', "", 'right'),
                 (False, [('top', 0), ('deze', 0)], '', 'dinges', 'left'),
                 (False, [('top', 0), ('dit', 0)], '', 'contents1', 'left'),
                 (False, [('top', 0), ('die', 0)], '', 'met inhoud', 'right'),
                 (False, [('top', 0), ('die', 0)], 'iets', 'niets', 'right'),
                 (False, [('top', 0), ('dit', 0)], '', 'met niks', 'right'),
                 (False, [('top', 0), ('dit', 0)], 'attr1', 'xxx', 'left'),
                 (True, '', '', '', 'right'),
                 (False, [('top', 0), ('dit', 0)], 'attr2', 'yyy', 'left'),
                 (True, '', '', '', 'left')][counter]
        result = ('EOF' if _data[0] else '', _data[:-1])
        print(f'called gen_next from {_data[-1]} side returning {result}')
        counter += 1
        return _data[:-1]
    monkeypatch.setattr(testee, 'sort_xmldata', mock_sort)
    monkeypatch.setattr(testee, 'gen_next', mock_next)
    with pytest.raises(ValueError) as exc:
        assert testee.compare_xmldata('left', 'right') == []
    assert str(exc.value) == ('deze applicatie voorziet vooralsnog nog niet in het vergelijken'
                             ' van xmls met verschillende root elementen')
    assert capsys.readouterr().out == (
            "called sort_xmldata with arg 'left'\n"
            "called sort_xmldata with arg 'right'\n"
            "called gen_next from left side returning (False, 'left', 'x', 'y')\n"
            "called gen_next from right side returning (False, 'right', 'x', 'y')\n")
    counter = 0
    monkeypatch.setattr(testee, 'gen_next', mock_next_2)
    assert testee.compare_xmldata('left', 'right') == [
            (([('top', 0)], ''), '', ''),
            (([('top', 0), ('daaro', 0)], ''), '', ''),
            (([('top', 0), ('daaro', 0), ('niet-hiero', 0)], ''), '', None),
            (([('top', 0), ('dat', 0)], ''), 'contents2', ''),
            (([('top', 0), ('deze', 0)], ''), 'dinges', ''),
            (([('top', 0), ('die', 0)], ''), '', 'met inhoud'),
            (([('top', 0), ('die', 0)], 'iets'), '', 'niets'),
            (([('top', 0), ('dit', 0)], ''), 'contents1', 'met niks'),
            (([('top', 0), ('dit', 0)], 'attr1'), 'xxx', ''),
            (([('top', 0), ('dit', 0)], 'attr2'), 'yyy', '')]
    assert capsys.readouterr().out == expected_output['compare']


def test_refresh_xmlcompare(capsys, expected_output):
    """unittest for xml_comp.refresh_xmlcompare
    """
    class MockItem:
        """dummy class to keep track of parent-child relations
        """
        def __init__(self, text, parent=None):
            self._name = text
            self.parent = parent
        def __repr__(self):
            return f'<Item "{self._name}">'
        def __str__(self):
            return self._name
    class MockCompareGui:
        """stub
        """
        def __init__(self, arg):
            print('called ComparerGui.__init__')
        def init_tree(self, *args):
            print('called ComparerGui.init_tree with args', args)
        def build_header(self, node_text):
            print('called ComparerGui.build_header with arg', node_text)
            return MockItem(f"header for '{node_text}'")
        def colorize_header(self, *args):
            print('called ComparerGui.colorize_header with args', args)
        def build_child(self, *args):
            print('called ComparerGui.build_child with args', args)
            option = args[1]
            return MockItem(f"child for '{option}'", parent=args[0])
        def get_parent(self, element):
            print(f'called ComparerGui.get_parent with arg "{element}"')
            return element.parent
        def colorize_child(self, *args):
            print('called ComparerGui.colorize_child with args', args)
        def set_node_text(self, *args):
            print('called ComparerGui.set_node_text with args', args)
    class MockComparer:
        """stub
        """
        def __init__(self):
            print('called Comparer.__init__')
            self.gui = MockCompareGui(self)
            self.parent = types.SimpleNamespace()
    comparer = MockComparer()
    assert capsys.readouterr().out == "called Comparer.__init__\ncalled ComparerGui.__init__\n"
    comparer.parent.lhs_path = 'old file'
    comparer.parent.rhs_path = 'new file'
    comparer.parent.data = []
    testee.refresh_xmlcompare(comparer)
    assert capsys.readouterr().out == (
            "called ComparerGui.init_tree with args ('Element/Attribute', 'old file', 'new file')\n")
    comparer.parent.data = [
            (([('top', 0)], ''), '', ''),
            (([('top', 0), ('daaro', 0)], ''), '', ''),
            (([('top', 0), ('daaro', 0), ('niet-hiero', 0)], ''), '', None),
            (([('top', 0), ('dat', 0)], ''), 'contents2', ''),
            (([('top', 0), ('deze', 0)], ''), 'dinges', ''),
            (([('top', 0), ('die', 0)], ''), '', 'met inhoud'),
            (([('top', 0), ('die', 0)], 'iets'), '', 'niets'),
            (([('top', 0), ('dit', 0)], ''), 'contents1', 'met niks'),
            (([('top', 0), ('dit', 0)], 'attr1'), 'xxx', ''),
            (([('top', 0), ('dit', 0)], 'attr2'), 'xxx', None),
            (([('top', 0), ('dit', 0)], 'attr3'), 'yyy', 'yyy'),
            (([('top', 0), ('dit', 0)], 'attr4'), '', 'zzz'),
            (([('top', 0), ('dit', 0)], 'attr5'), None, 'zzz')]
    testee.refresh_xmlcompare(comparer)
    assert capsys.readouterr().out == expected_output['refresh']

compare_output = """\
called sort_xmldata with arg 'left'
called sort_xmldata with arg 'right'
called gen_next from left side returning ('', (False, [('top', 0)], '', ''))
called gen_next from right side returning ('', (False, [('top', 0)], '', ''))
called gen_next from left side returning ('', (False, [('top', 0), ('dat', 0)], '', 'contents2'))
called gen_next from right side returning ('', (False, [('top', 0), ('daaro', 0)], '', ''))
called gen_next from right side returning ('', (False, [('top', 0), ('daaro', 0), ('niet-hiero', 0)], '', None))
called gen_next from right side returning ('', (False, [('top', 0), ('deze', 0)], '', ''))
called gen_next from left side returning ('', (False, [('top', 0), ('deze', 0)], '', 'dinges'))
called gen_next from left side returning ('', (False, [('top', 0), ('dit', 0)], '', 'contents1'))
called gen_next from right side returning ('', (False, [('top', 0), ('die', 0)], '', 'met inhoud'))
called gen_next from right side returning ('', (False, [('top', 0), ('die', 0)], 'iets', 'niets'))
called gen_next from right side returning ('', (False, [('top', 0), ('dit', 0)], '', 'met niks'))
called gen_next from left side returning ('', (False, [('top', 0), ('dit', 0)], 'attr1', 'xxx'))
called gen_next from right side returning ('EOF', (True, '', '', ''))
called gen_next from left side returning ('', (False, [('top', 0), ('dit', 0)], 'attr2', 'yyy'))
called gen_next from left side returning ('EOF', (True, '', '', ''))
"""
refresh_output = """\
called ComparerGui.init_tree with args ('Element/Attribute', 'old file', 'new file')
called ComparerGui.build_header with arg <> top
called ComparerGui.set_node_text with args (<Item "header for '<> top'">, 1, '')
called ComparerGui.set_node_text with args (<Item "header for '<> top'">, 2, '')
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.build_child with args (<Item "header for '<> top'">, '<> daaro')
called ComparerGui.set_node_text with args (<Item "child for '<> daaro'">, 1, '')
called ComparerGui.set_node_text with args (<Item "child for '<> daaro'">, 2, '')
called ComparerGui.get_parent with arg "child for '<> daaro'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, True, False)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.build_child with args (<Item "child for '<> daaro'">, '<> niet-hiero')
called ComparerGui.set_node_text with args (<Item "child for '<> niet-hiero'">, 1, '')
called ComparerGui.set_node_text with args (<Item "child for '<> niet-hiero'">, 2, None)
called ComparerGui.get_parent with arg "child for '<> niet-hiero'"
called ComparerGui.colorize_header with args (<Item "child for '<> daaro'">, True, False, False)
called ComparerGui.get_parent with arg "child for '<> daaro'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, False, False)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.get_parent with arg "child for '<> niet-hiero'"
called ComparerGui.get_parent with arg "child for '<> daaro'"
called ComparerGui.build_child with args (<Item "header for '<> top'">, '<> dat')
called ComparerGui.set_node_text with args (<Item "child for '<> dat'">, 1, 'contents2')
called ComparerGui.set_node_text with args (<Item "child for '<> dat'">, 2, '')
called ComparerGui.get_parent with arg "child for '<> dat'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, False, True, False)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.get_parent with arg "child for '<> dat'"
called ComparerGui.build_child with args (<Item "header for '<> top'">, '<> deze')
called ComparerGui.set_node_text with args (<Item "child for '<> deze'">, 1, 'dinges')
called ComparerGui.set_node_text with args (<Item "child for '<> deze'">, 2, '')
called ComparerGui.get_parent with arg "child for '<> deze'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, False, True, False)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.get_parent with arg "child for '<> deze'"
called ComparerGui.build_child with args (<Item "header for '<> top'">, '<> die')
called ComparerGui.set_node_text with args (<Item "child for '<> die'">, 1, '')
called ComparerGui.set_node_text with args (<Item "child for '<> die'">, 2, 'met inhoud')
called ComparerGui.build_child with args (<Item "child for '<> die'">, 'iets')
called ComparerGui.colorize_child with args (<Item "child for 'iets'">, True, False, False)
called ComparerGui.get_parent with arg "child for 'iets'"
called ComparerGui.colorize_header with args (<Item "child for '<> die'">, True, False, False)
called ComparerGui.get_parent with arg "child for '<> die'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, False, False)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.set_node_text with args (<Item "child for 'iets'">, 1, '')
called ComparerGui.set_node_text with args (<Item "child for 'iets'">, 2, 'niets')
called ComparerGui.get_parent with arg "child for '<> die'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, False, False)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.get_parent with arg "child for '<> die'"
called ComparerGui.build_child with args (<Item "header for '<> top'">, '<> dit')
called ComparerGui.set_node_text with args (<Item "child for '<> dit'">, 1, 'contents1')
called ComparerGui.set_node_text with args (<Item "child for '<> dit'">, 2, 'met niks')
called ComparerGui.build_child with args (<Item "child for '<> dit'">, 'attr1')
called ComparerGui.set_node_text with args (<Item "child for 'attr1'">, 1, 'xxx')
called ComparerGui.colorize_child with args (<Item "child for 'attr1'">, False, True, True)
called ComparerGui.get_parent with arg "child for 'attr1'"
called ComparerGui.colorize_header with args (<Item "child for '<> dit'">, False, True, True)
called ComparerGui.get_parent with arg "child for '<> dit'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, False, True, True)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.set_node_text with args (<Item "child for 'attr1'">, 2, '')
called ComparerGui.build_child with args (<Item "child for '<> dit'">, 'attr2')
called ComparerGui.set_node_text with args (<Item "child for 'attr2'">, 1, 'xxx')
called ComparerGui.colorize_child with args (<Item "child for 'attr2'">, False, True, True)
called ComparerGui.get_parent with arg "child for 'attr2'"
called ComparerGui.colorize_header with args (<Item "child for '<> dit'">, False, True, True)
called ComparerGui.get_parent with arg "child for '<> dit'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, False, True, True)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.set_node_text with args (<Item "child for 'attr2'">, 2, '(no value)')
called ComparerGui.build_child with args (<Item "child for '<> dit'">, 'attr3')
called ComparerGui.set_node_text with args (<Item "child for 'attr3'">, 1, 'yyy')
called ComparerGui.set_node_text with args (<Item "child for 'attr3'">, 2, 'yyy')
called ComparerGui.build_child with args (<Item "child for '<> dit'">, 'attr4')
called ComparerGui.colorize_child with args (<Item "child for 'attr4'">, True, True, True)
called ComparerGui.get_parent with arg "child for 'attr4'"
called ComparerGui.colorize_header with args (<Item "child for '<> dit'">, True, True, True)
called ComparerGui.get_parent with arg "child for '<> dit'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, True, True)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.set_node_text with args (<Item "child for 'attr4'">, 1, '')
called ComparerGui.set_node_text with args (<Item "child for 'attr4'">, 2, 'zzz')
called ComparerGui.build_child with args (<Item "child for '<> dit'">, 'attr5')
called ComparerGui.set_node_text with args (<Item "child for 'attr5'">, 1, '(no value)')
called ComparerGui.colorize_child with args (<Item "child for 'attr5'">, True, True, True)
called ComparerGui.get_parent with arg "child for 'attr5'"
called ComparerGui.colorize_header with args (<Item "child for '<> dit'">, True, True, True)
called ComparerGui.get_parent with arg "child for '<> dit'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, True, True)
called ComparerGui.get_parent with arg "header for '<> top'"
called ComparerGui.set_node_text with args (<Item "child for 'attr5'">, 2, 'zzz')
called ComparerGui.get_parent with arg "child for '<> dit'"
called ComparerGui.colorize_header with args (<Item "header for '<> top'">, True, True, True)
called ComparerGui.get_parent with arg "header for '<> top'"
"""


@pytest.fixture
def expected_output():
    "langere output voorspellingen"
    return {'compare': compare_output, 'refresh': refresh_output}
