#! /usr/bin/env python3
"""starter for Compare Tool
"""
import argparse
from shared import comparetypes
from toolkit import toolkit
if toolkit == 'qt':
    from qt_gui import main
elif toolkit == 'wx':
    from wx_gui import main

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-m', '--method', choices=comparetypes, help='comparison method')
parser.add_argument('-i', '--input', metavar='FILE', nargs=2)
args = parser.parse_args()
main(args)
