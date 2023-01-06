import pytest
import txt_comp as testee

def test_gen_next():
    assert testee.gen_next((x for x in [])) == (True, '')
    assert testee.gen_next((x for x in ['next line'])) == (False, 'next line')

def test_get_file(monkeypatch, capsys, tmp_path):
    fname = 'filename'
    as_utf = tmp_path / f'{fname}_unicode'
    as_utf.write_text('this\nis\nsome\ntëxt\n', encoding='utf-8')
    as_latin = tmp_path / f'{fname}_latin8'
    as_latin.write_text('this\nis\nsome\ntëxt\n', encoding='latin-1')
    assert testee.get_file(as_utf) == ['is\n', 'some\n', 'this\n', 'tëxt\n']
    assert testee.get_file(as_latin) == ['is\n', 'some\n', 'this\n', 'tëxt\n']


def _test_compare_txtdata(monkeypatch, capsys):
    testee.compare_txtdata(fn1, fn2)


def _test_refresh_txtcompare(monkeypatch, capsys):
    testee.refresh_txtcompare(self)

