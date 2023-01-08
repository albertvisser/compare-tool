Files in this directory
-----------------------

actif.py
    the actual starting point of the application. In my scripts directory I have a symlink to this.

    it parses the arguments given, determines which GUI toolkit to use and then starts up the main function from the gui module.

conf.comp.py
    module containing code to compare configuration (.ini) files

html_comp.py
    module containing code to compare html files

inicomp.ico
    icon for the application

python_comp.py
    first draft for a comparer for Python code (not tracked yet)

qt_gui.py
    the application variant as written for PyQt5

readme.rst
    the obligatory application description

shared.py
    common code shared between the application variants

show_stuff.py
    a helper script to display the comparison data before it is transformed into a visual tree structure, to be used during development (not tracked)

toolkit.py
    configuration file containing the setting which gui toolkit to use

txt_comp.py
    module containing code to do a simple text compare

wx_gui.py
    the application variant as written for wxPython (4)

xml_comp.py
    module containing code to compare xml files
