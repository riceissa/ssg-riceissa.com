# Now unused functions that came up during the writing of meta.py.

def gogo(key, val, f, meta):
    '''
    Experimental filter.
    '''
    if key == 'MetaInLines':
        result = meta.get("tags", {}).get('t', {})
        if 'MetaInLines' in result:
            return Str(val + "yo")

def caps(key, val, f, meta):
    '''
    Caps filter from pandocfilters.
    '''
    if key == 'Str':
        return Str(val.upper())

def do_nothing(key, val, f, meta):
    '''
    Filter that does nothing.
    '''
    pass

def walk(x, action, format, meta):
    """
    Modified version of walk from pandocfilters.  This version will
    separate out the metadata from the rest of the file, and will apply
    do_nothing to it (i.e. will leave the metadata unchanged) while
    applying action to the body of the file.
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

def intersperse(iterable, delimiter):
    '''See http://stackoverflow.com/a/5656097/3422337 '''
    it = iter(iterable)
    yield next(it)
    for x in it:
        yield delimiter
        yield x


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
