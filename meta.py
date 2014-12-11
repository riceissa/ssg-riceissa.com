#!/bin/python

import json
from pandocfilters import walk, Str
import pandocfilters

def stringify(x):
    """Walks the tree x and returns concatenated string content,
    leaving out all formatting.
    """
    result = []

    def go(key, val, format, meta):
        if key == 'Str':
            result.append(val)
        elif key == 'Code':
            result.append(val[1])
        elif key == 'Math':
            result.append(val[1])
        elif key == 'LineBreak':
            result.append(" ")
        elif key == 'Space':
            result.append(" ")

    walk(x, go, "", {})
    #return ''.join(result)
    return result


def go(key, val, format, meta):
    if key == 'Str':
        return Str(val + "yo")
    elif key == 'Code':
        return Str(val)
    elif key == 'Math':
        return Str(val)
    elif key == 'LineBreak':
        return Str(val)
    elif key == 'Space':
        return Str(val)


with open('hello.json','r') as f:
    x = f.next()
    data = json.loads(x)
    tags = data[0]['unMeta']['tags']
    tags2 = data[0]['unMeta']['tags2']
    tags3 = data[0]['unMeta']['tags3']
    tags4 = data[0]['unMeta']['tags4']
    #print stringify(tags)
    #print stringify(tags2)
    #print stringify(tags3)
    #print stringify(tags4)
    altered = pandocfilters.walk(data, go, "", data[0]['unMeta'])
    print altered

