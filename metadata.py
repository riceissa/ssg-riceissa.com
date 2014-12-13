#!/bin/python
# -*- coding: utf-8 -*-

import json, sys
import glob
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
    '''
    Take the filepath of a single markdown file and compile to HTML.
    '''
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
    '''
    Compiler for a single page that lists and links to each of the tags
    that are used throughout the website (included in the tags_lst
    parameter).
    '''
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

def tag_page_compiler(tag_data):
    '''
    Compiler for the tag page for a single tag.  The tag page will
    contain a list of all the pages with the tag name tag_date['tag'].
    Here tag_data = {
        'tag': <tagname>,
        'pages': [
            {'title': <pagename>, 'url': <page_base_url>},
            ...
        ]
    }
    '''
    env = Environment(loader=FileSystemLoader('.'))
    page_list = env.get_template('templates/page-list.html')
    output = page_list.render(pages=tag_data['pages'])
    skeleton = env.get_template('templates/skeleton.html')
    final = skeleton.render(body=output, title="Tag: " + tag_data['tag'], license='CC0').encode('utf-8')
    return final

all_tags = []
def generate_all_tag_data(file_pattern="pages/*.md"):
    global all_tags
    # List of all the tag_data where each tag_data is of the form:
    #     tag_data = {
    #         'tag': <tagname>,
    #         'pages': [
    #             {'title': <pagename>, 'url': <page_base_url>},
    #             ...
    #         ]
    #     }
    all_tag_data = []
    lst_pages = glob.glob(file_pattern)
    page_data = []
    all_tags = []
    for page in lst_pages:
        json_lst = json.loads(c.run_command("pandoc -f markdown -t json {page}".format(page=page)))
        file_dict = organize_tags(json_lst, meta.tag_synonyms, meta.tag_implications)
        json_lst = file_dict['json']
        title = get_metadata_field(json_lst, "title")
        url = os.path.splitext(os.path.basename(page))[0]
        tags = file_dict['tags']
        all_tags.extend(tags)
        page_data.append((title, url, tags))
    all_tags = list(set(all_tags))
    for tag in all_tags:
        pages = []
        for page_tuple in page_data:
            if tag in page_tuple[2]:
                pages.append({'title': page_tuple[0], 'url': page_tuple[1]})
        all_tag_data.append({'tag': tag, 'pages': pages})
    return all_tag_data


#### Actually generate the site

for tag_data in generate_all_tags_data(file_pattern="pages/*.md"):
    create(compiled=tag_page_compiler(tag_data), filename=tag_data['tag'], outdir="_site/tags/")

create(compiled=all_tags_page_compiler(all_tags), filename="index", outdir="_site/tags/")

match(route=id_route, compiler=markdown_to_html_compiler, file_pattern="pages/*.md" outdir="_site/"):

#json_lst = json.loads(c.run_command("pandoc -f markdown -t json {filename}".format(filename="pages/hello.md")))
#for i in ["title", "tags", "tags2", "tags3", "math", "math2"]:
    #print(get_metadata_field(json_lst, i))
    #print(type(get_metadata_field(json_lst, i)))
    #print("")
