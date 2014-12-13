#!/bin/python
# -*- coding: utf-8 -*-

import json, sys
from pandocfilters import Str, Space
import pandocfilters
import commands as c
from jinja2 import Template, Environment, FileSystemLoader
import os
import meta

def get_metadata_field(json_lst, field):
    '''
    Take a JSON list and a field name (str) and return a 
    the field value.
    '''
    try:
        x = json_lst[0]['unMeta'].get(field, {})
        return walk_metadata(x)
    except KeyError:
        return ''

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

def get_tags(x):
    '''
    Take a YAML-JSON list or string of comma-delimited tags,
    and return a cleaned list of the tags.
    '''
    tags = get_metadata_field(x, "tags")
    if type(tags) is str:
        return [tag.strip(" ") for tag in tags.split(",")]
    elif type(tags) is list:
        return tags

def organize_tags(json_lst, tag_synonyms, tag_implications):
    '''
    Takes a JSON list, a dict of tag_synonyms, and an OrderedDict of
    tag_implications.  Returns a dictionary with two entries:
    under 'json', the JSON string/dump of data with its tags
    organized according to tag_synonyms and tag_implications is stored;
    under 'tags' a list of the cleaned/organized (same as in the JSON
    dump) tags is stored.
    '''
    tags = get_tags(json_lst)
    tags = meta.standardize_tags(tags, tag_synonyms)
    tags = meta.imply_tags(tags, tag_implications)
    keep_tags = list(tags)
    tags_dict = json_lst[0]['unMeta'].get('tags', {})
    tags_dict['t'] = 'MetaList'
    tags_dict['c'] = meta.pack_tags(tags)
    return {'json': json_lst,
            'tags': keep_tags}



def id_route(filepath):
    return filepath

def cool_uri_route(filepath):
    return os.path.splitext(filepath)[0]

def drop_one_parent_dir_route(filepath):
    pass

def create(compiled, filename, outdir="_site/"):
    if os.path.exists(outdir):
        write_to = outdir + filename
        output = compiled
        with open(write_to, "w") as f:
            f.write(output)
    else:
        print("{outdir} does not exist!".format(outdir=outdir))


def match(route, compiler, file_pattern, outdir="_site/"):
    if os.path.exists(outdir):
        lst_filepaths = glob.glob(file_pattern)
        for filepath in lst_filepaths:
            output = compiler(filepath)
            write_to = outdir + route(filepath)
            with open(write_to, 'w') as f:
                f.write(output)
    else:
        print("{outdir} does not exist!".format(outdir=outdir))

def markdown_to_html_compiler(filepath):
    filename = os.path.basename(filepath)
    command = "pandoc -f markdown -t json -s {filepath}".format(filepath=filepath)
    json_lst = json.loads(c.run_command(command))
    # This will return a dict {'json_dump': ..., 'tags': ...}
    file_dict = organize_tags(json_lst, meta.tag_synonyms, meta.tag_implications)
    json_lst = file_dict['json']
    tags = file_dict['tags']
    # all_tags is global
    #all_tags[routename] = file_dict['tags']
    command = "pandoc -f json -t html --mathjax --base-header-level=2"
    html_output = c.run_command(command, pipe_in=json.dumps(json_lst, separators=(',',':'))).decode('utf-8')
    env = Environment(loader=FileSystemLoader('.'))
    skeleton = env.get_template('templates/skeleton.html')

    # Get metadata ready
    title = get_metadata_field(json_lst, "title").decode('utf-8')
    math = get_metadata_field(json_lst, "math")
    license = get_metadata_field(json_lst, "license").decode('utf-8')

    final = skeleton.render(body=html_output, title=title, tags=tags, license=license, math=math).encode('utf-8')
    return final

def all_tags_page_compiler(tags_lst, outdir="_site/"):
    tags_lst_of_dicts = []
    for tag in tags_lst:
        tag_dict = {'title': tag.decode('utf-8'), 'url': (outdir + "tags/" + tag).decode('utf-8')}
        tags_lst_of_dicts.append(tag_dict)
    env = Environment(loader=FileSystemLoader('.'))
    page_list = env.get_template('templates/page-list.html')
    output = page_list.render(pages=tags_lst_of_dicts)
    skeleton = env.get_template('templates/skeleton.html')
    final = skeleton.render(body=output, title="List of all tags", license='CC0').encode('utf-8')
    return final

json_lst = json.loads(c.run_command("pandoc -f markdown -t json {filename}".format(filename="pages/hello.md")))
compiled = all_tags_page_compiler(["a", "b", "c"])
create(compiled=compiled, filename="index", outdir="_site/tags/")
#for i in ["title", "tags", "tags2", "tags3", "math", "math2"]:
    #print(get_metadata_field(json_lst, i))
    #print(type(get_metadata_field(json_lst, i)))
    #print("")
