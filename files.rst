Files in this directory
-----------------------

actif.ini (not tracked)
    contains the mru-data for the path selectors

actif.py
    the actual starting point of the application. In my scripts directory I have a symlink to this.

    it parses the arguments given and then starts up the application from the main module.

conf.comp.py
    module containing code to compare configuration (.ini) files

files.rst
    this file

gui.py
    determines which GUI toolkit to use and imports the widgets from the appropriate module 

html_comp.py
    module containing code to compare html files

inicomp.ico
    icon for the application

main.py
    gui-independent application code                    

python_comp.py
    first draft for a comparer for Python code (not tracked yet)

qt_gui.py
    gui toolkit-specific code for the PyQT5 variant

readme.rst
    the obligatory application description

.rurc
    configuration file for my unittests launcher

.sessionrc
    configuration file for my "DEI" (development environment integration)

show_stuff.py
    a helper script to display the comparison data before it is transformed into a visual tree structure, to be used during development (not tracked)

toolkit.py
    configuration file containing the setting which gui toolkit to use

txt_comp.py
    module containing code to do a simple text compare

wx_gui.py
    gui-toolkit specific code for the wxPython variant

xml_comp.py
    module containing code to compare xml files
