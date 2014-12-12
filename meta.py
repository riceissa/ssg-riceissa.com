#!/bin/python
# this script uses pandocfilters: https://github.com/jgm/pandocfilters
# the walk function in particular is a modified version of the one there. see the pandocfilters license (3-clause BSD) at: https://github.com/jgm/pandocfilters/blob/master/LICENSE

import json, sys
from pandocfilters import Str, Space
import pandocfilters
import collections

# Below, (a, [b]) means that the tag a implies tag b; so if you have a
# page with tag a, it will automatically also be applied the tag b.
# Note that the order here is important.  Let's say we also have
#    (b, [c])
# then doing tag a should also imply tag c, since the implication chain
# goes a -> b -> c.  In other words, tag implication should be
# transitive, in that a -> b and b -> c together mean a -> c.  This
# means though that you should put (a, [b]) before (b, [c]), since then
# the first will be applied, leaving you with the tags a and b, and then
# the second will be applied, leaving you with tags a, b, and c. (This
# is an OrderedDict so that the above works.)
tag_implications = collections.OrderedDict([
    ("hakyll", ["haskell"]),
    ("python", ["programming"]),
    ("latex", ["linux"]),
    ("qs", ["quantified-self"]),
    ("lesswrong", ["rationality"]),
    ("logic", ["math"]),
    ("physics", ["science"]),
    ("atmospheric-sciences", ["science"]),
    ("astronomy", ["science"]),
    ("chemistry", ["science"]),
    ("analysis", ["math"]),
    ("haskell", ["programming"]),
    ("depression", ["psychology"]),
])

tag_synonyms = {
    "effective-altruism": ["ea", "effective altruism", "effectivealtruism"],
    "university-of-washington": ["uw", "uwashington", "university of washington"],
    "set-theory": ["set theory"],
    "lesswrong": ["lw", "less-wrong", "less wrong"],
    "cognito-mentoring": ["cm", "cognito mentoring", "cognito"],
    "math": ["maths", "mathematics"],
    "link-collection": ["link collection", "resources", "links"],
    "atmopsheric-sciences": ["atmos"],
    "chemistry": ["chem"],
    "computer-science": ["cs", "computer science"],
}

def imply_tags(tags, tag_implications):
    '''
    Take a list of tags along with a dictionary of tag implications.
    Return a new list of tags that includes all the implciations.
    '''
    result = list(tags)
    for key in tag_implications:
        if key in result:
            result.extend(tag_implications.get(key))
    return list(set(result))

def standardize_tags(tags, tag_synonyms):
    '''
    Take a list of tags ("tags") along with a dictionary of tag synonyms
    and return a new list of tags, where all synonymous tags are
    standardized according to tag_synonyms.  For instance, if
    tag_synonyms contains the line
        "university-of-washington": ["uw", "uwashington"],
    and if tags contains "uw" or "uwashington", then this will be
    replaced by "university-of-washington".
    '''
    result = []
    for tag in tags:
        canonical = [key for key, value in tag_synonyms.items() if tag in value]
        if not canonical:
            canonical = [tag]
        result.extend(canonical)
    return result

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

def do_nothing(key, val, f, meta):
    pass

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
                array.append(pandocfilters.walk(x[0], do_nothing, format, meta))
            elif isinstance(res, list):
                for z in res:
                    array.append(pandocfilters.walk(z, do_nothing, format, meta))
            else:
                array.append(pandocfilters.walk(res, do_nothing, format, meta))
        else:
            array.append(pandocfilters.walk(x[0], do_nothing, format, meta))

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

def listify(x):
    '''
    Take a YAML-JSON list or string of comma-delimited tags,
    and return a cleaned list.
    '''
    if x['t'] == 'MetaInlines':
        w = [i.strip(',') for i in stringify(x) if i is not ' ']
        return w
    elif x['t'] == 'MetaList':
        return stringify(x)

def intersperse(iterable, delimiter):
    '''See http://stackoverflow.com/a/5656097/3422337 '''
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x

def pack_tags(tags):
    '''
    Take a list of tags ("tags") and return a YAML-JSON list of the tags
    '''
    result = []
    for tag in tags:
        tag_dict = {'t': 'MetaInlines', 'c': [Str(tag)]}
        result.append(tag_dict)
    return result
    #return list(intersperse([Str(i) for i in tags], Space()))

def organize_tags(filepath, tag_synonyms, tag_implications):
    '''
    Takes the filepath of a JSON file (str filepath) and returns
    a JSON tree of the file with its tags organized according to
    tag_synonyms and tag_implications.
    '''
    with open(filepath, 'r') as f:
        x = f.next()
        data = json.loads(x)
        tags = data[0]['unMeta'].get('tags', {})
        w = listify(tags)
        #print w
        w = standardize_tags(w, tag_synonyms)
        #print w
        w = imply_tags(w, tag_implications)
        tags['c'] = pack_tags(w)
        tags['t'] = 'MetaList'
        #array = []
        #altered = walk(data, caps, "", data[0]['unMeta'])
        json.dump(data, sys.stdout)

organize_tags("hello.json", tag_synonyms, tag_implications)

    #if len(sys.argv) > 1:
        #format = sys.argv[1]
    #else:
        #format = ""
    #print altered
    #print json.dumps(altered, indent=2)

