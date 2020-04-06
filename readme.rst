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


I've also included the possibilty to compare XML files in a similar fashion, and to do a simple lini-by-line text comparison (after sorting all the lines in the files).

Usage
-----

Execute ``actif.py``. When executed from the command line, the --help switch gives you the following information::

 usage: actif.py [-h] [-m {ini,ini2,xml,txt}] FILE FILE

 starter for Compare Tool

 positional arguments:
   FILE

 optional arguments:
   -h, --help            show this help message and exit
   -m {ini,ini2,xml,txt}, --method {ini,ini2,xml,txt}
                         comparison method

showing that you can specify the files to compare and the method to use when calling the tool. Without (all necessary) arguments, you start with a dialog where you can choose your options.

Requirements
------------

- Python
- PyQt(5) / wxPython (Phoenix)
