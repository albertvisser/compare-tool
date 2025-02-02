"""unittests for ./src/python_comp.py
"""
from src import python_comp as testee


class TestReadPyfile:
    """unittest for python_comp.ReadPyfile
    """
    def setup_testobj(self, monkeypatch, capsys):
        """stub for python_comp.ReadPyfile object

        create the object skipping the normal initialization
        intercept messages during creation
        return the object so that other methods can be monkeypatched in the caller
        """
        def mock_init(self, *args):
            """stub
            """
            print('called ReadPyfile.__init__ with args', args)
        monkeypatch.setattr(testee.ReadPyfile, '__init__', mock_init)
        testobj = testee.ReadPyfile()
        assert capsys.readouterr().out == 'called ReadPyfile.__init__ with args ()\n'
        return testobj

    def test_init(self, tmp_path):
        """unittest for ReadPyfile.__init__
        """
        testfile = tmp_path / 'sample_data'
        testfile.write_text('xxx\nyyy\nzzz\n')
        testobj = testee.ReadPyfile(testfile)
        assert testobj.pylines == ['xxx\n', 'yyy\n', 'zzz\n']
        assert testobj.contents == {'filename': testfile, 'docstring': [], 'imports': [],
                                    'module-level code': [], 'symbols': [], 'functions': [],
                                    'classes': []}
        assert not testobj.in_docstring
        assert not testobj.handle_construct
        assert not testobj.handle_function
        assert not testobj.handle_class
        assert testobj.docstring_delim == ''

    def test_process(self, monkeypatch, capsys):
        """unittest for ReadPyfile.process
        """
        def mock_do_docstr(line):
            print(f"called testobj.do_docstring_line with arg {line}")
            return ''
        def mock_do_docstr_2(line):
            print(f"called testobj.do_docstring_line with arg {line}")
            return line
        def mock_is_docstr(line):
            print(f"called testobj.is_line_module_docstring_start with arg {line}")
            return True
        def mock_is_docstr_2(line):
            print(f"called testobj.is_line_module_docstring_start with arg {line}")
            return False
        def mock_fun_start(line):
            print(f"called testobj.do_function_start with arg {line}")
        def mock_cls_start(line):
            print(f"called testobj.do_class_start with arg {line}")
        def mock_save():
            print("called testobj.save_prev_construct")
        def mock_construct(line):
            print(f"called testobj.do_construct with arg {line}")
        def mock_add(line):
            print(f"called testobj.add_to_construct with arg '{line}'")
        def mock_fun_line(line):
            print(f"called testobj.do_function_line with arg '{line}'")
        def mock_cls_line(line):
            print(f"called testobj.do_class_line with arg '{line}'")

        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.do_docstring_line = mock_do_docstr
        testobj.is_line_module_docstring_start = mock_is_docstr
        testobj.do_function_start = mock_fun_start
        testobj.do_class_start = mock_cls_start
        testobj.save_prev_construct = mock_save
        testobj.do_construct = mock_construct
        testobj.add_to_construct = mock_add
        testobj.do_function_line = mock_fun_line
        testobj.do_class_line = mock_cls_line
        testobj.handle_construct = False
        testobj.pylines = ['', '\n']
        testobj.process()
        assert capsys.readouterr().out == ""

        testobj.contents = {'docstring': []}
        testobj.in_docstring = True
        testobj.handle_function = False
        testobj.handle_class = False
        testobj.pylines = ['xxxx', 'yyyy']
        testobj.process()
        assert not testobj.contents['docstring']
        assert capsys.readouterr().out == ("called testobj.do_docstring_line with arg xxxx\n"
                                           "called testobj.do_docstring_line with arg yyyy\n")
        testobj.do_docstring_line = mock_do_docstr_2
        testobj.process()
        assert testobj.contents['docstring'] == ['xxxx', 'yyyy']
        assert capsys.readouterr().out == ("called testobj.do_docstring_line with arg xxxx\n"
                                           "called testobj.do_docstring_line with arg yyyy\n")

        testobj.contents = {'imports': []}
        testobj.in_docstring = False
        testobj.pylines = ['xxxx']
        testobj.process()
        assert capsys.readouterr().out == (
                "called testobj.is_line_module_docstring_start with arg xxxx\n")
        testobj.is_line_module_docstring_start = mock_is_docstr_2
        testobj.pylines = ['import this', 'from chaos import order', 'def function', 'class Class']
        testobj.process()
        assert capsys.readouterr().out == (
                "called testobj.is_line_module_docstring_start with arg import this\n"
                "called testobj.is_line_module_docstring_start with arg from chaos import order\n"
                "called testobj.is_line_module_docstring_start with arg def function\n"
                "called testobj.do_function_start with arg def function\n"
                "called testobj.is_line_module_docstring_start with arg class Class\n"
                "called testobj.do_class_start with arg class Class\n")
        testobj.pylines = ['xxxx']
        testobj.process()
        assert capsys.readouterr().out == (
                "called testobj.is_line_module_docstring_start with arg xxxx\n"
                "called testobj.do_construct with arg xxxx\n")
        testobj.handle_construct = True
        testobj.pylines = ['xxxx']
        testobj.process()
        assert capsys.readouterr().out == (
                "called testobj.is_line_module_docstring_start with arg xxxx\n"
                "called testobj.save_prev_construct\n"
                "called testobj.do_construct with arg xxxx\n"
                "called testobj.save_prev_construct\n")

        testobj.pylines = ['    xxxx']
        testobj.process()
        assert capsys.readouterr().out == ("called testobj.add_to_construct with arg '    xxxx'\n"
                                           "called testobj.save_prev_construct\n")
        testobj.handle_construct = False
        testobj.handle_class = True
        testobj.process()
        assert capsys.readouterr().out == "called testobj.do_class_line with arg '    xxxx'\n"
        testobj.handle_class = False
        testobj.handle_function = True
        testobj.process()
        assert capsys.readouterr().out == "called testobj.do_function_line with arg '    xxxx'\n"
        testobj.handle_function = False
        testobj.process()
        assert capsys.readouterr().out == ""

    def test_do_docstring_line(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_docstring_line
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.in_docstring = True
        testobj.docstring_delim = '"""'
        assert testobj.do_docstring_line("expected result") == "expected result"
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"""'
        assert testobj.do_docstring_line('expected result """') == 'expected result '
        assert not testobj.in_docstring
        assert testobj.docstring_delim == ''
        testobj.in_docstring = True
        testobj.docstring_delim = '"""'
        assert testobj.do_docstring_line('expected """ result') == 'expected """ result'
        assert not testobj.in_docstring
        assert testobj.docstring_delim == ''

    def test_is_line_module_docstring_start(self, monkeypatch, capsys):
        """unittest for ReadPyfile.is_line_module_docstring_start
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.docstring_delim = ''
        testobj.in_docstring = False
        testobj.contents = {'docstring': []}
        assert not testobj.is_line_module_docstring_start("expected result")
        assert testobj.docstring_delim == ''
        assert not testobj.in_docstring
        assert not testobj.contents['docstring']
        assert not testobj.is_line_module_docstring_start('e"""xpected result')
        assert testobj.docstring_delim == ''
        assert not testobj.in_docstring
        assert not testobj.contents['docstring']
        assert testobj.is_line_module_docstring_start('"""expected result')
        assert testobj.docstring_delim == '"""'
        assert testobj.in_docstring
        assert testobj.contents['docstring'] == ['expected result']
        testobj.docstring_delim = ''
        testobj.in_docstring = False
        testobj.contents = {'docstring': []}
        assert testobj.is_line_module_docstring_start("'''expected result")
        assert testobj.docstring_delim == "'''"
        assert testobj.in_docstring
        assert testobj.contents['docstring'] == ['expected result']
        testobj.docstring_delim = ''
        testobj.in_docstring = False
        testobj.contents = {'docstring': []}
        assert testobj.is_line_module_docstring_start('"expected result')
        assert testobj.docstring_delim == '"'
        assert testobj.in_docstring
        assert testobj.contents['docstring'] == ['expected result']
        testobj.docstring_delim = ''
        testobj.in_docstring = False
        testobj.contents = {'docstring': []}
        assert testobj.is_line_module_docstring_start("'expected result")
        assert testobj.docstring_delim == "'"
        assert testobj.in_docstring
        assert testobj.contents['docstring'] == ['expected result']

    def test_do_function_start(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_function_start
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.handle_function = False
        testobj.handle_class = True
        testobj.handle_construct = True
        testobj.contents = {'functions': []}
        testobj.do_function_start("a line")
        assert testobj.handle_function
        assert not testobj.handle_class
        assert not testobj.handle_construct
        assert testobj.contents['functions'] == [('a line', [], [])]

    def test_do_class_start(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_class_start
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.handle_class = False
        testobj.handle_function = True
        testobj.handle_construct = True
        testobj.contents = {'classes': []}
        testobj.do_class_start("a line")
        assert testobj.handle_class
        assert not testobj.handle_function
        assert not testobj.handle_construct
        assert testobj.contents['classes'] == [('a line', [], [])]

    def test_do_construct(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_construct
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.handle_construct = False
        testobj.handle_class = True
        testobj.handle_function = True
        testobj.do_construct("a line")
        assert testobj.handle_construct
        assert not testobj.handle_class
        assert not testobj.handle_function
        assert testobj.construct == ['a line']

    def test_save_prev_construct(self, monkeypatch, capsys):
        """unittest for ReadPyfile.save_prev_construct
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.contents = {'symbols': ['a'], 'module-level code': ['b']}
        testobj.construct = ['x']
        testobj.save_prev_construct()
        assert testobj.contents['symbols'] == ['a', 'x']
        testobj.construct = ['x', 'y']
        testobj.save_prev_construct()
        assert testobj.contents['module-level code'] == ['b', ['x', 'y']]

    def test_add_to_construct(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_function_line
        """
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.construct = ['a']
        testobj.add_to_construct('b')
        assert testobj.construct == ['a', 'b']

    def test_do_function_line(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_function_line
        """
        def mock_do(arg):
            print(f"called ReadPyFile.do_docstring_line with arg '{arg}'")
            return ''
        def mock_do_2(arg):
            print(f"called ReadPyFile.do_docstring_line with arg '{arg}'")
            return arg
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.in_docstring = True
        testobj.contents = {'functions': [(), ('x', ['y'], ['z'])]}
        testobj.do_docstring_line = mock_do
        testobj.do_function_line('line')
        assert testobj.contents['functions'] == [(),  ('x', ['y'], ['z'])]
        assert capsys.readouterr().out == "called ReadPyFile.do_docstring_line with arg 'line'\n"
        testobj.do_docstring_line = mock_do_2
        testobj.do_function_line('line')
        assert testobj.contents['functions'] == [(),  ('x', ['y', 'line'], ['z'])]
        assert capsys.readouterr().out == "called ReadPyFile.do_docstring_line with arg 'line'\n"

        testobj.in_docstring = False
        testobj.contents['functions'] = [(), ('x', [], ['z'])]
        testobj.do_function_line('"""')
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"""'
        assert testobj.contents['functions'] == [(),  ('x', [''], ['z'])]
        testobj.contents['functions'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_function_line('"""line')
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"""'
        assert testobj.contents['functions'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['functions'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_function_line("'''line")
        assert testobj.in_docstring
        assert testobj.docstring_delim == "'''"
        assert testobj.contents['functions'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['functions'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_function_line('"line')
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"'
        assert testobj.contents['functions'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['functions'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_function_line("'line")
        assert testobj.in_docstring
        assert testobj.docstring_delim == "'"
        assert testobj.contents['functions'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['functions'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_function_line('line')
        assert testobj.contents['functions'] == [(),  ('x', [], ['z', 'line'])]

    def test_do_class_line(self, monkeypatch, capsys):
        """unittest for ReadPyfile.do_class_line
        """
        def mock_do(arg):
            print(f"called ReadPyFile.do_docstring_line with arg '{arg}'")
            return ''
        def mock_do_2(arg):
            print(f"called ReadPyFile.do_docstring_line with arg '{arg}'")
            return arg
        testobj = self.setup_testobj(monkeypatch, capsys)
        testobj.in_docstring = True
        testobj.contents = {'classes': [(), ('x', ['y'], ['z'])]}
        testobj.do_docstring_line = mock_do
        testobj.do_class_line('line')
        assert testobj.contents['classes'] == [(),  ('x', ['y'], ['z'])]
        assert capsys.readouterr().out == "called ReadPyFile.do_docstring_line with arg 'line'\n"
        testobj.do_docstring_line = mock_do_2
        testobj.do_class_line('line')
        assert testobj.contents['classes'] == [(),  ('x', ['y', 'line'], ['z'])]
        assert capsys.readouterr().out == "called ReadPyFile.do_docstring_line with arg 'line'\n"

        testobj.in_docstring = False
        testobj.contents['classes'] = [(), ('x', [], ['z'])]
        testobj.do_class_line('"""')
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"""'
        assert testobj.contents['classes'] == [(),  ('x', [''], ['z'])]
        testobj.contents['classes'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_class_line('"""line')
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"""'
        assert testobj.contents['classes'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['classes'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_class_line("'''line")
        assert testobj.in_docstring
        assert testobj.docstring_delim == "'''"
        assert testobj.contents['classes'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['classes'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_class_line('"line')
        assert testobj.in_docstring
        assert testobj.docstring_delim == '"'
        assert testobj.contents['classes'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['classes'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_class_line("'line")
        assert testobj.in_docstring
        assert testobj.docstring_delim == "'"
        assert testobj.contents['classes'] == [(),  ('x', ['line'], ['z'])]
        testobj.contents['classes'] = [(), ('x', [], ['z'])]
        testobj.in_docstring = False
        testobj.do_class_line('line')
        assert testobj.contents['classes'] == [(),  ('x', [], ['z', 'line'])]
