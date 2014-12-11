#!/bin/python

import json, sys
from pandocfilters import Str
import pandocfilters

# a: [b] means that the tag a implies tag b; so if you have a page with tag a, it will automatically also be applied the tag b.
# note that the order here is important. let's say we also have
#    b: [c]
# then doing tag a should also do tag c, since a->b->c. this means that you should put the line 'a: [b]' before the line 'b: [c]', since then the first will be applied, leaving you with the tags 'a b', and then the second will be applied, leaving you with 'a b c'.
tag_implication = {
    "hakyll": ["haskell"],
    "python": ["programming"],
    "latex": ["linux"],
    "haskell": ["programming"],
}

tag_synonyms = {
    "effective-altruism": ["ea", "effective altruism", "effectivealtruism"],
    "university-of-washington": ["uw", "uwashington"],
}

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


def gogo(key, val, f, meta):
    if key == 'MetaInLines':
        result = meta.get("tags", {}).get('t', {})
        if 'MetaInLines' in result:
            return Str(val + "yo")
    #elif key == 'Code':
        #return Str(val)
    #elif key == 'Math':
        #return Str(val)
    #elif key == 'LineBreak':
        #return Str(val)
    #elif key == 'Space':
        #return Str(val)

def caps(key, val, f, meta):
    if key == 'Str':
        return Str(val.upper())


def walk(x, action, format, meta):
    """Walk a tree, applying an action to every object.
    Returns a modified tree.
    """
    if isinstance(x, list):
        #print "list!"
        array = []
        if isinstance(x[0], dict) and 't' in x[0]:
            res = action(x[0]['t'], x[0]['c'], format, meta)
            if res is None:
                array.append(pandocfilters.walk(x[0], action, format, meta))
            elif isinstance(res, list):
                for z in res:
                    array.append(pandocfilters.walk(z, action, format, meta))
            else:
                array.append(pandocfilters.walk(res, action, format, meta))
        else:
            array.append(pandocfilters.walk(x[0], action, format, meta))

        for item in x[1:]:
            if isinstance(item, dict) and 't' in item:
                res = action(item['t'], item['c'], format, meta)
                if res is None:
                    array.append(pandocfilters.walk(item, action, format, meta))
                elif isinstance(res, list):
                    for z in res:
                        array.append(pandocfilters.walk(z, action, format, meta))
                else:
                    array.append(pandocfilters.walk(res, action, format, meta))
            else:
                array.append(pandocfilters.walk(item, action, format, meta))
        return array
    elif isinstance(x, dict):
        #print "dict!"
        obj = {}
        for k in x:
            obj[k] = pandocfilters.walk(x[k], action, format, meta)
        return obj
    else:
        return x

with open('hello.json','r') as f:
    x = f.next()
    data = json.loads(x)
    #print json.dumps(data, indent=2)
    tags = data[0]['unMeta']['tags']
    tags2 = data[0]['unMeta']['tags2']
    tags3 = data[0]['unMeta']['tags3']
    tags4 = data[0]['unMeta']['tags4']
    #print data[0]['unMeta'].get('tags', {})
    #print stringify(tags)
    #print stringify(tags2)
    #print stringify(tags3)
    #print stringify(tags4)
    #if len(sys.argv) > 1:
        #format = sys.argv[1]
    #else:
        #format = ""
    array = []
    altered = walk(data, caps, "", data[0]['unMeta'])
    print altered
    #json.dump(altered, sys.stdout)

