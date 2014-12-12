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
