"""unittests for ./src//html_comp.py
"""
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


def _test_get_next_level_data(monkeypatch, capsys):
    """unittest for html_comp.get_next_level_data
    """


def test_gen_next():
    """unittest for html_comp.gen_next
    """
    assert testee.gen_next(x for x in []) == (True, '', '', '')
    assert testee.gen_next(x for x in [(1, 2, 3)]) == (False, 1, 2, 3)


def _test_compare_htmldata(monkeypatch, capsys):
    """unittest for html_comp.compare_htmldata
    """


def _test_convert_levels_to_keys(monkeypatch, capsys):
    """unittest for html_comp.convert_levels_to_keys
    """


def _test_level2key(monkeypatch, capsys):
    """unittest for html_comp.level2key
    """


def _test_refresh_htmlcompare(monkeypatch, capsys):
    """unittest for html_comp.refresh_htmlcompare
    """
