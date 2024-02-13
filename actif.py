#! /usr/bin/env python3
"""starter for Compare Tool
"""
import argparse
from src import main

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('-m', '--method', choices=main.comparetypes, help='comparison method')
parser.add_argument('-i', '--input', metavar='FILE', nargs=2)
args = parser.parse_args()
main.Comparer((args.input), args.method)
