"""unittests for ./src//html_comp.py
"""
import types
import textwrap
from src import html_comp as testee


def test_get_htmldata(monkeypatch, capsys, tmp_path):
    """unittest for html_comp.get_htmldata
    """
    def mock_bs(*args):
        """stub
        """
        print('called Beautifulsoup with args', args)
        return args[0]
    def mock_get_data(*args):
        """stub
        """
        print('called get_next_level_data with args', args)
        return args[0]
    monkeypatch.setattr(testee.bs, 'BeautifulSoup', mock_bs)
    monkeypatch.setattr(testee, 'get_next_level_data', mock_get_data)
    datafile = tmp_path / 'test_get_htmldata'
    htmldata = '<body>\n  <br/>\n  <br />\n  <hr />\n  <hr/>\n</body>'
    htmldata_raw = r'<body>\n  <br/>\n  <br />\n  <hr />\n  <hr/>\n</body>'
    datafile.write_text(htmldata)
    assert testee.get_htmldata(str(datafile), False, False) == htmldata
    assert capsys.readouterr().out == (
            f"called Beautifulsoup with args ('{htmldata_raw}', 'lxml')\n"
            f"called get_next_level_data with args ('{htmldata_raw}',)\n")
    htmldata_stripped_1 = '<body><br/><br /><hr /><hr/></body>'
    assert testee.get_htmldata(str(datafile), True, False) == htmldata_stripped_1
    assert capsys.readouterr().out == (
            f"called Beautifulsoup with args ('{htmldata_stripped_1}', 'lxml')\n"
            f"called get_next_level_data with args ('{htmldata_stripped_1}',)\n")
    htmldata_stripped_2 = '<body>\n  <br />\n  <br />\n  <hr />\n  <hr />\n</body>'
    assert testee.get_htmldata(str(datafile), False, True) == htmldata_stripped_2


# 104->110
def test_get_next_level_data(monkeypatch, capsys):
    """unittest for html_comp.get_next_level_data
    """
    el = ('<html lang="en"><head><title>head</title></head>'
          '<body class="body"><p>text</p></body></html>')
    data = testee.bs.BeautifulSoup(el, 'lxml')
    # breakpoint()
    assert testee.get_next_level_data(data) == [
           [(0, '<html>'), '', ''],
           [(0, '<html>'), 'lang', 'en'],
           [(1, '<head>'), '', ''],
           [(2, '<title>'), '', ''],
           [(3, '(text)'), '', 'head'],
           [(1, '<body>'), '', ''],
           [(1, '<body>'), 'class', 'body'],
           [(2, '<p>'), '', ''],
           [(3, '(text)'), '', 'text'] ]

    el = '<div id="one" class="this that"><div id="two"><p>something</p><p>more</p></div></div>'
    assert testee.get_next_level_data(testee.bs.BeautifulSoup(el, 'lxml')) == [
            [(0, '<html>'), '', ''],
            [(1, '<body>'), '', ''],
            [(2, '<div>'), '', ''],
            [(2, '<div>'), 'class', 'that'],
            [(2, '<div>'), 'class', 'this'],
            [(2, '<div>'), 'id', 'one'],
            [(3, '<div>'), '', ''],
            [(3, '<div>'), 'id', 'two'],
            [(4, '<p>'), '', ''],
            [(5, '(text)'), '', 'something'],
            [(4, '<p>'), '', ''],
            [(5, '(text)'), '', 'more']]

    el = '<p><!-- this is a comment --></p>'
    assert testee.get_next_level_data(testee.bs.BeautifulSoup(el, 'lxml')) == [
            [(0, '<html>'), '', ''],
            [(1, '<body>'), '', ''],
            [(2, '<p>'), '', ''],
            [(3, '<!>'), '', ' this is a comment ']]

    el = types.SimpleNamespace(children=[None])  # to illustrate failsafe
    assert testee.get_next_level_data(el) == [["Oops, what's this? None", '', '']]


def test_gen_next():
    """unittest for html_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, '', '', '')
    assert testee.gen_next(x for x in [(1, 2, 3)]) == (False, 1, 2, 3)


def _test_compare_htmldata(monkeypatch, capsys):
    """unittest for html_comp.compare_htmldata
    """


def test_convert_levels_to_keys(monkeypatch, capsys):
    """unittest for html_comp.convert_levels_to_keys
    """
    def mock_level2key(*args):
        print('called level2key with args', args)
        return ['key', 'from', 'level']
    monkeypatch.setattr(testee, 'level2key', mock_level2key)
    data = [['x', 'y'], ['a', 'b'], ['q', 'r']]
    new_data = testee.convert_levels_to_keys(data)
    assert new_data == [[['key', 'from', 'level'], 'y'], [['key', 'from', 'level'], 'b'],
                        [['key', 'from', 'level'], 'r']]
    assert capsys.readouterr().out == (
            "called level2key with args ('x', '')\n"
            "called level2key with args ('a', ['key', 'from', 'level'], 'b', 'x', 'y')\n"
            "called level2key with args ('q', ['key', 'from', 'level'], 'r', 'a', 'b')\n")


def test_level2key(monkeypatch, capsys):
    """unittest for html_comp.level2key
    """
    leveldata = (0, 'html')
    old_key = testee.level2key(leveldata, '')
    assert old_key == [(0, 'html')]
    old_key = testee.level2key(leveldata, old_key, attr_name='lang')
    assert old_key == [(0, 'html'), (0, '(attr:lang)')]
    old_leveldata, leveldata = leveldata, (1, 'head')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'head')]
    old_leveldata, leveldata = leveldata, (2, '<title>')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'head'), (2, '<title>')]
    old_leveldata, leveldata = leveldata, (3, '(text)')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'head'), (2, '<title>'), (3, '(text)')]
    old_leveldata, leveldata = leveldata, (1, 'body')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'body')]
    old_key = testee.level2key(leveldata, old_key, attr_name='class')
    assert old_key == [(0, 'html'), (1, 'body'), (1, '(attr:class)')]
    old_key = testee.level2key(leveldata, old_key, attr_name='id')
    assert old_key == [(0, 'html'), (1, 'body'), (1, '(attr:id)')]
    old_leveldata, leveldata = leveldata, (2, '<p>')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'body'), (2, '<p>')]
    old_leveldata, leveldata = leveldata, (3, '(text)')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'body'), (2, '<p>'), (3, '(text)')]
    old_leveldata, leveldata = leveldata, (2, '<hr>')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'body'), (2, '<hr>')]
    old_leveldata, leveldata = leveldata, (2, '<br>')
    old_key = testee.level2key(leveldata, old_key, prev_leveldata=old_leveldata)
    assert old_key == [(0, 'html'), (1, 'body'), (2, '<hr>')]


# 193->159
def test_refresh_htmlcompare(monkeypatch, capsys):
    """unittest for html_comp.refresh_htmlcompare
    """
    class MockCompareGui:
        """stub
        """
        def __init__(self, arg):
            print('called ComparerGui.__init__')
        def init_tree(self, *args):
            print('called ComparerGui.init_tree with args', args)
        def build_header(self, node_text):
            print('called ComparerGui.build_header with arg', node_text)
            return f"header for '{node_text}'"
        def colorize_header(self, *args):
            print('called ComparerGui.colorize_header with args', args)
        def build_child(self, *args):
            print('called ComparerGui.build_child with args', args)
            option = args[1]
            return f"child for '{option}'"
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
    comparer.parent.data = [
           [((0, '<html>'), ''), '', ''],
           [((0, '<html>)'), 'lang'), '', 'en'],
           [((1, '<head>'), ''), '', ''],
           [((2, '<title>'), ''), '', ''],
           [((3, '(text)'), ''), 'heading', 'head'],
           [((1, '<body>'), ''), '', ''],
           [((1, '<body>'), 'class'), 'body', ''],
           [((2, '<p>'), ''), '', ''],
           [((3, '(text)'), ''), '', 'text']]
    testee.refresh_htmlcompare(comparer)
    assert capsys.readouterr().out == textwrap.dedent("""\
            called ComparerGui.init_tree with args ('Element/Attribute', 'old file', 'new file')
            called ComparerGui.build_header with arg <html>
            called ComparerGui.build_child with args ("header for '<html>'", ' lang')
            called ComparerGui.set_node_text with args ("child for ' lang'", 2, 'en')
            called ComparerGui.colorize_child with args ("child for ' lang'", True, False, False)
            called ComparerGui.colorize_header with args ("header for '<html>'", True, False, False)
            called ComparerGui.build_child with args ("header for '<html>'", '<head>')
            called ComparerGui.build_child with args ("child for '<head>'", '<title>')
            called ComparerGui.build_child with args ("child for '<title>'", '(text)')
            called ComparerGui.set_node_text with args ("child for '(text)'", 1, 'heading')
            called ComparerGui.set_node_text with args ("child for '(text)'", 2, 'head')
            called ComparerGui.colorize_child with args ("child for '(text)'", False, False, True)
            called ComparerGui.colorize_header with args ("child for '<title>'", False, False, True)
            called ComparerGui.build_child with args ("header for '<html>'", '<body>')
            called ComparerGui.build_child with args ("child for '<body>'", ' class')
            called ComparerGui.set_node_text with args ("child for ' class'", 1, 'body')
            called ComparerGui.colorize_child with args ("child for ' class'", False, True, False)
            called ComparerGui.colorize_header with args ("child for '<body>'", False, True, False)
            called ComparerGui.build_child with args ("child for '<body>'", '<p>')
            called ComparerGui.build_child with args ("child for '<p>'", '(text)')
            called ComparerGui.set_node_text with args ("child for '(text)'", 2, 'text')
            called ComparerGui.colorize_child with args ("child for '(text)'", True, False, False)
            called ComparerGui.colorize_header with args ("child for '<p>'", True, False, False)
            """)
