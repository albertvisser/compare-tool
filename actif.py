#! /usr/bin/env python3
"""starter for Compare Tool
"""
import argparse
from actif_shared import comparetypes
from actif_qt import main
# from actif_wx import main

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-m', '--method', choices=comparetypes, help='comparison method')
parser.add_argument('input', metavar='FILE', nargs=2)
args = parser.parse_args()
main(args)
