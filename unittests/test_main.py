import pytest
import main

def test_determine_comparetype(monkeypatch, capsys):
    monkeypatch.setattr(main, 'comparetypes', ['x'])
    assert main.auto_determine_comparetype('test1', 'test2') == ''
    assert main.auto_determine_comparetype('test1.x', 'test2.y') == ''
    assert main.auto_determine_comparetype('test1.x', 'test2.x') == 'x'


def test_get_input_paths(capsys):
    assert main.get_input_paths([]) == ('', '')
    assert capsys.readouterr().out == ''
    assert main.get_input_paths(['left'])
    assert capsys.readouterr().out == ''
    assert main.get_input_paths(['left', 'right'])
    assert capsys.readouterr().out == ''
    assert main.get_input_paths(['left', 'right', ''])
    assert capsys.readouterr().out == 'excessive filename arguments truncated\n'

def test_do_compare(monkeypatch, capsys):
    def mock_compare(left, right):
        print(f'called compare_method with args `{left}` and `{right}`')
        return ['compare output']
    def mock_compare_miss(left, right):
        print(f'called compare_method with args `{left}` and `{right}`')
        raise main.MissingSectionHeaderError('xxxx', 1, 1)
    def mock_compare_parse(left, right):
        print(f'called compare_method with args `{left}` and `{right}`')
        raise main.ParseError('yyyy')
    monkeypatch.setattr(main, 'comparetypes', {'x': ('', mock_compare, '')})
    assert main.do_compare('left', 'right', 'x') == (True, ['compare output'])
    assert capsys.readouterr().out == 'called compare_method with args `left` and `right`\n'
    monkeypatch.setattr(main, 'comparetypes', {'x': ('', mock_compare_miss, '')})
    assert main.do_compare('left', 'right', 'x') == (False, [
        'Tenminste één file begint niet met een header', [
            'Traceback (most recent call last):\n',
            '  File "/home/albert/projects/compare-tool/main.py", line 151, in do_compare\n'
            '    data = compare_func(leftpath, rightpath)\n',
            '  File "/home/albert/projects/compare-tool/unittests/test_main.py",'
                                                   ' line 27, in mock_compare_miss\n'
            "    raise main.MissingSectionHeaderError('xxxx', 1, 1)\n",
            'configparser.MissingSectionHeaderError: File contains no section headers.\n'
            "file: 'xxxx', line: 1\n"
            '1\n']])
    assert capsys.readouterr().out == 'called compare_method with args `left` and `right`\n'
    monkeypatch.setattr(main, 'comparetypes', {'x': ('', mock_compare_parse, '')})
    assert main.do_compare('left', 'right', 'x') == (
            False, ['Tenminste één file bevat geen correcte XML', [
                'Traceback (most recent call last):\n',
                '  File "/home/albert/projects/compare-tool/main.py", line 151, in do_compare\n'
                '    data = compare_func(leftpath, rightpath)\n',
                '  File "/home/albert/projects/compare-tool/unittests/test_main.py", line '
                '30, in mock_compare_parse\n'
                "    raise main.ParseError('yyyy')\n",
                'xml.etree.ElementTree.ParseError: yyyy\n']])
    assert capsys.readouterr().out == 'called compare_method with args `left` and `right`\n'

