#! /usr/bin/env python3
"""starter for Compare Tool

use two FILE arguments to compare two files;
use one to compare a file tracked by git with the version in the repo
"""
import argparse
from src import main


parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                 description=__doc__)
parser.add_argument('-m', '--method', choices=main.comparetypes, help='comparison type')
parser.add_argument('input', metavar='FILE', nargs='*')
args = parser.parse_args()
main.Comparer((args.input), args.method)
