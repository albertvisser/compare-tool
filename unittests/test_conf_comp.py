import pytest
import conf_comp as testee

def test_gen_next():
    assert testee.gen_next((x for x in [])) == (True, '', '', '')
    assert testee.gen_next((x for x in [(1, 2, 3)])) == (False, 1, 2, 3)

def _test_sort_inifile(monkeypatch, capsys):
    testee.sort_inifile(fn)


def _test_check_inifile(monkeypatch, capsys):
    testee.check_inifile(fn)


def _test_compare_configs(monkeypatch, capsys):
    testee.compare_configs(fn1, fn2)


def test_compare_configs_safe(monkeypatch, capsys):
    def mock_check(fname):
        print(f'called check_inifile with arg `{fname}`')
        return fname
    def mock_compare(*args):
        print('called compare_configs with args', args)
        return 'configs_compared'
    monkeypatch.setattr(testee, 'check_inifile', mock_check)
    monkeypatch.setattr(testee, 'compare_configs', mock_compare)
    assert testee.compare_configs_safe('left', 'right') == 'configs_compared'
    assert capsys.readouterr().out == ('called check_inifile with arg `left`\n'
                                       'called check_inifile with arg `right`\n'
                                       "called compare_configs with args ('left', 'right')\n")


def _test_refresh_inicompare(monkeypatch, capsys):
    testee.refresh_inicompare(self)

