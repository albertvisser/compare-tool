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


I'm currently writing a variant that makes it possible to compare XML files in a
similar fashion.
