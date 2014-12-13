#!/bin/python

import json, sys
from pandocfilters import Str, Space
import pandocfilters
import commands as c

def get_metadata_field(json_lst, field):
    '''
    Take a JSON list and a field name (str) and return a 
    the field value.
    '''
    x = json_lst[0]['unMeta'].get(field, {})
    return walk_metadata(x)

def walk_metadata(x):
    '''
    x is a JSON dictionary of pandoc metadata
    Walks down a JSON dictionary in the pandoc metadata, returning a
    more manageable representation.
    FIXME: Maybe formatting for e.g. math should be retained instead of
    converting to a string?
    '''
    if x['t'] == 'MetaBool':
        return x['c']
    elif x['t'] == 'MetaInlines':
        return pandocfilters.stringify(x).encode('utf-8')
    elif x['t'] == 'MetaString':
        return pandocfilters.stringify(x).encode('utf-8')
    elif x['t'] == 'MetaList':
        lst = []
        for i in x['c']:
            lst.append(walk_metadata(i))
        return lst

def id_route(filepath):
    return filepath

def cool_uri_route(filepath):
    return os.path.splitext(filepath)[0]

def drop_one_parent_dir_route(filepath):
    pass

def create(compiler, filename, outdir="_site/"):
    write_to = outdir + filename
    output = compiler()
    with open(write_to, "w") as f:
        f.write(output)

def match(route, compiler, file_pattern, outdir="_site/"):
    lst_filepaths = glob.glob(file_pattern)
    for filepath in lst_filepaths:
        output = compiler(filepath)
        write_to = outdir + route(filepath)
        with open(write_to, 'w') as f:
            f.write(output)

json_lst = json.loads(c.run_command("pandoc -f markdown -t json {filename}".format(filename="pages/hello.md")))
for i in ["title", "tags", "tags2", "tags3", "math", "math2"]:
    print(get_metadata_field(json_lst, i))
    print(type(get_metadata_field(json_lst, i)))
    print("")
