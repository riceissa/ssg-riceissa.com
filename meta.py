#!/bin/python
# this script uses pandocfilters: https://github.com/jgm/pandocfilters
# the walk function in particular is a modified version of the one there. see the pandocfilters license (3-clause BSD) at: https://github.com/jgm/pandocfilters/blob/master/LICENSE

import json, sys
from pandocfilters import Str, Space
import pandocfilters
import collections

# Dictionary of tag synonyms or "shortcuts" to be used with
# standardize_tags.  This is mostly useful when
# a tag can be spelled in multiple ways or has common abbreviations.
# This should be used before doing tag implications.
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

def standardize_tags(tags, tag_synonyms):
    '''
    Take a list of tags (tags :: list) along with a dictionary of tag
    synonyms (tag_synonyms :: dict) and return a new list of tags, where
    all synonymous tags are standardized according to tag_synonyms.  For
    instance, if tag_synonyms contains the line
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

# List of tag implications to be used with imply_tags.  Below, (a, [b])
# means that the tag a implies tag b; so if you have a page with tag a,
# it will automatically also be applied the tag b.  Note that the order
# here is important.  Let's say we also have
#    (b, [c])
# then doing tag a should also imply tag c, since the implication chain
# goes a -> b -> c.  In other words, tag implication should be
# transitive, in that a -> b and b -> c together mean a -> c.  This
# means though that you should put (a, [b]) before (b, [c]), since then
# the first will be applied, leaving you with the tags a and b, and then
# the second will be applied, leaving you with tags a, b, and c. (This
# is an OrderedDict so that the above works.)  It is also assumed here
# that everything in tag_implications is standardized.
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

def imply_tags(tags, tag_implications):
    '''
    Take a list of tags (tags :: list) along with an OrderedDict of tag
    implications (tag_implications :: OrderedDict).  Return a new list
    of tags that includes all the implications.  Apply this after
    standardizing tags.
    '''
    result = list(tags)
    for key in tag_implications:
        if key in result:
            result.extend(tag_implications.get(key))
    return list(set(result))

def stringify(x):
    """
    Modified version of the pandocfilters stringify, where instead of a
    string, a list is returned.
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

    # FIXME: maybe this has to be the modified walk in unused.py...
    pandocfilters.walk(x, go, "", {})
    #return ''.join(result)
    return result

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

def pack_tags(tags):
    '''
    Take a list of tags (tags :: list) and return a YAML-JSON list of
    the tags.
    '''
    result = []
    for tag in tags:
        tag_dict = {'t': 'MetaInlines', 'c': [Str(tag)]}
        result.append(tag_dict)
    return result
    #return list(intersperse([Str(i) for i in tags], Space()))

def get_meta_field(data, field):
    '''
    Take a JSON object (data) and a field name (str) and return a string
    of the field value according to pandocfilters' stringify.
    FIXME: Maybe formatting for e.g. math should be retained instead of
    converting to a string?
    '''
    x = data[0]['unMeta'].get(field, {})
    return pandocfilters.stringify(x)

def organize_tags(data, tag_synonyms, tag_implications):
    '''
    Takes a JSON object (data), a list of tag_synonyms, and a list of
    tag_implications. Returns a dictionary with two key-value pairs:
    under 'json_dump', the JSON string/dump of data with its tags
    organized according to tag_synonyms and tag_implications is stored;
    under 'tags' a list of the cleaned/organized (same as in the JSON
    dump) tags is stored.
    '''
    tags = data[0]['unMeta'].get('tags', {})
    w = listify(tags)
    w = standardize_tags(w, tag_synonyms)
    w = imply_tags(w, tag_implications)
    keep_tags = list(w)
    tags['c'] = pack_tags(w)
    tags['t'] = 'MetaList'
    return {'json_dump': json.dumps(data, separators=(',',':')),
            'tags': keep_tags}

# FIXME: In pandocfilters, this is how format is set; in the script
# above, we just set it to "", but maybe this will cause problems
# somewhere.
#if len(sys.argv) > 1:
    #format = sys.argv[1]
#else:
    #format = ""
