"""Python "vergelijking" - eerste aanzet
in deze versie wordt slechts een source file gelezen en heel globaal geanalyseerd weergegeven
"""
import sys
import pprint

class ReadPyfile:
    def __init__(self, filename):
        with open(filename) as pyfile:
            self.pylines = pyfile.readlines()
        self.contents = {'filename': filename, 'docstring': [], 'imports': [],
                         'module-level code': [], 'symbols': [], 'functions': [], 'classes': []}
        self.in_docstring = self.handle_construct = self.handle_function = self.handle_class = False
        self.docstring_delim = ''

    def process(self):
        "main line"
        # breakpoint()
        for line in self.pylines:
            line = line.rstrip()
            if not line:
                continue
            if self.in_docstring and not (self.handle_function or self.handle_class):
                line = self.do_docstring_line(line)
                if line:
                    self.contents['docstring'].append(line)
                continue
            if line.lstrip() == line:  # not indented
                if self.is_line_module_docstring_start(line):
                    continue
                if line.startswith(('import', 'from')):   # TODO: import over meer regels
                    self.contents['imports'].append(line)
                elif line.startswith('def'):
                    self.do_function_start(line)
                elif line.startswith('class'):
                    self.do_class_start(line)
                else:
                    if self.handle_construct:
                        self.save_prev_construct()
                    self.do_construct(line)
            else:
                if self.handle_class:
                    self.do_class_line(line)
                elif self.handle_construct:
                    self.add_to_construct(line)
                elif self.handle_function:
                    self.do_function_line(line)
        if self.handle_construct:
            self.save_prev_construct()

    def do_docstring_line(self, line):
        """handle a line in a docstring, also handle the end of the docstring
        """
        if self.docstring_delim in line:
            self.in_docstring = False
            line = line.removesuffix(self.docstring_delim)
            self.docstring_delim = ''
        return line

    def is_line_module_docstring_start(self, line):
        """check for the start of a docstring
        """
        for docstring_delim in ('"""', "'''", '"', "'"):
            if line.startswith(docstring_delim):
                self.in_docstring = True
                self.docstring_delim = docstring_delim
                self.contents['docstring'].append(line.removeprefix(docstring_delim))
                return True
        return False

    def do_function_start(self, line):
        """handle the start of a function definition
        """
        self.handle_function = True
        self.handle_construct = self.handle_class = False
        self.function_docstring = []
        self.function_body = []
        self.contents['functions'].append((line, self.function_docstring, self.function_body))

    def do_class_start(self, line):
        """handle the start of a class definition
        """
        self.handle_class = True
        self.handle_construct = self.handle_function = False
        self.class_docstring = []
        self.class_body = []
        self.contents['classes'].append((line, self.class_docstring, self.class_body))

    def do_construct(self, line):
        """handle the start of a new non-class / non-function definition
        """
        self.handle_construct = True
        self.handle_function = self.handle_class = False
        self.construct = [line]

    def save_prev_construct(self):
        """add the previous definition to the appropriate collection
        """
        if len(self.construct) == 1:
            self.contents['symbols'].append(self.construct[0])
        else:
            self.contents['module-level code'].append(self.construct)

    def add_to_construct(self, line):
        """handle a line for a non-class / non-function definition
        """
        self.construct.append(line)

    def do_function_line(self, line):
        """handle a line for a function definition
        """
        if self.in_docstring:
            line = self.do_docstring_line(line)
            if line:
                self.contents['functions'][-1][1].append(line)
            return
        for docstring_delim in ('"""', "'''", '"', "'"):
            if line.lstrip().startswith(docstring_delim):
                self.in_docstring = True
                self.docstring_delim = docstring_delim
                self.contents['functions'][-1][1].append(line.lstrip().removeprefix(docstring_delim))
                return
        self.contents['functions'][-1][2].append(line)

    def do_class_line(self, line):
        """handle a line for a class definition
        """
        if self.in_docstring:
            line = self.do_docstring_line(line)
            if line:
                self.contents['classes'][-1][1].append(line)
            return
        for docstring_delim in ('"""', "'''", '"', "'"):
            if line.lstrip().startswith(docstring_delim):
                self.in_docstring = True
                self.docstring_delim = docstring_delim
                self.contents['classes'][-1][1].append(line.lstrip().removeprefix(docstring_delim))
                return
        # maar nou wil ik in de class ook de methoden apart dus het volgende is niet voldoende
        # ik kan hier de indicatoren voor function en construct natuurlijk hergebruiken
        self.contents['classes'][-1][2].append(line)
