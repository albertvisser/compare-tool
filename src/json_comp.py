import sys
import json
import pathlib
import difflib
import pprint


def compare_jsondata(oldfile, newfile):
    """reorder the input files and build the comparison output
    """
    # ik wil eigenlijk iets anders dan pprint omdat deze zoveel mogelijk op een regel wil proppen
    # en deze afbreekt als ze te lang worden. Dus een geneste structtur wordt bv.
    #   {'components': {'Achtuur.AchtuurCore': {'Author': 'Achtuur',
    # in plaats vam
    #   {
    #    'components': {
    #      'Achtuur.AchtuurCore': {
    #         'Author':
    #            'Achtuur',
    oldpath = pathlib.Path('/tmp/oldresult')
    newpath = pathlib.Path('/tmp/newresult')
    with oldpath.open('w') as out:
        pprint.pprint(readjson(oldfile), width=100, stream=out)
    with newpath.open('w') as out:
        pprint.pprint(readjson(newfile), width=100, stream=out)
    diff = difflib.Differ()
    result = diff.compare(oldpath.read_text().split('\n'), newpath.read_text().split('\n'))
    return result


def refresh_jsoncompare(comparer):
    """redo the comparison
    """
    comparer.gui.init_tree('key/value', comparer.parent.lhs_path, comparer.parent.rhs_path)
    for line in comparer.parent.data:
        node = comparer.gui.build_header(line)


def readjson(filename):
    with open(filename) as jsonfile:
        data = json.load(jsonfile)
    return read_dict(data)


def read_dict(data):
    result = {x: data[x] for x in sorted(data)}
    for key, dataitem in result.items():
        if isinstance(dataitem, dict):
            result[key] = read_dict(dataitem)
        elif isinstance(dataitem, list):
            result[key] = read_list(dataitem)
    return result


def read_list(data):
    result = sorted(data)
    return result
