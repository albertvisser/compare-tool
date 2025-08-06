Compare Tool
============

This program intends to let you compare files in an out-of-order sequence. It was
originally written to be able to compare settings files in which the sections and
options could be in different order.

E.g.::

    [test]                          [unicorn]
    option1 = something             horns = 1
    option2 = something else
                                    [ahem]
    [ahem]                          hello = universe
    hello = world
                                    [test]
    [unicorn]                       option1 = anything
    horns = 1

is compared as::

    [ahem]                          [ahem]
    hello = world                   hello = universe

    [test]                          [test]
    option1 = something             option1 = anything
    option2 = something else

    [unicorn]                       [unicorn]
    horns = 1                       horns = 1


I also included the possibilty to compare XML files in a similar fashion, and to do a simple line-by-line text comparison (after sorting all the lines in the files).

Since then I expanded on this idea to include comparisons for HTML, Python code and json data.

Each have a somewhat different implementation of "out-of-sequence", obviously related to the type of comparison. 

The result is shown in a tree structure. The elements are colorized to highlight the differences.


Usage
-----

Execute ``actif.py`` in the project root directory. When executed from the command line, the --help switch gives you the following information::

 usage: actif.py [-h] [-m {ini,ini2,xml,txt,py,json}] [-i FILE FILE]

 starter for Compare Tool

 options:
   -h, --help            show this help message and exit
   -m, --method {ini,ini2,xml,html,txt,py,json}
                         comparison method
   -i, --input FILE FILE

showing that you can specify the files to compare and the method to use when calling the tool. Without (all necessary) arguments, you start with a dialog where you can choose your options.
You can call up this dialog at any time to start a new comparison.

The comparison method can be automatically selected if both files have the same extension that matches one of the methods.

Requirements
------------

- Python
- PyQt / wxPython (Phoenix)
- BeautifulSoup for the HTML comparison
