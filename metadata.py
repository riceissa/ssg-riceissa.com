#!/bin/python
# -*- coding: utf-8 -*-

import json, sys
reload(sys)
sys.setdefaultencoding('utf-8')
import glob
from pandocfilters import Str, Space
import pandocfilters
import commands as c
from jinja2 import Template, Environment, FileSystemLoader
import os
from tag_ontology import tag_synonyms, tag_implications

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
        return str(pandocfilters.stringify(x))
    elif x['t'] == 'MetaString':
        return str(pandocfilters.stringify(x))
    elif x['t'] == 'MetaList':
        lst = []
        for i in x['c']:
            lst.append(walk_metadata(i))
        return lst


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
    tags = standardize_tags(tags, tag_synonyms)
    tags = imply_tags(tags, tag_implications)
    keep_tags = list(tags)
    tags_dict = json_lst[0]['unMeta'].get('tags', {})
    tags_dict['t'] = 'MetaList'
    tags_dict['c'] = pack_tags(tags)
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
    global tagsdir
    filename = os.path.basename(filepath)
    command = "pandoc -f markdown -t json -s {filepath}".format(filepath=filepath)
    json_lst = json.loads(c.run_command(command))
    # This will return a dict {'json': ..., 'tags': ...}
    file_dict = organize_tags(json_lst, tag_synonyms, tag_implications)
    json_lst = file_dict['json']
    tags = file_dict['tags']
    # all_tags is global
    #all_tags[routename] = file_dict['tags']
    command = "pandoc -f json -t html --mathjax --base-header-level=2"
    html_output = c.run_command(command, pipe_in=json.dumps(json_lst, separators=(',',':'))).encode('utf-8')
    env = Environment(loader=FileSystemLoader('.'))
    skeleton = env.get_template('templates/skeleton.html')

    # Get metadata ready
    title = get_metadata_field(json_lst, "title")
    math = get_metadata_field(json_lst, "math")
    license = get_metadata_field(json_lst, "license")

    final = skeleton.render(body=html_output, title=title, tags=tags, tagsdir=tagsdir, license=license, math=math).encode('utf-8')
    return final

def all_tags_page_compiler(tags_lst, outdir="_site/"):
    '''
    Compiler for a single page that lists and links to each of the tags
    that are used throughout the website (included in the tags_lst
    parameter).
    '''
    global baseurl
    tags_lst_of_dicts = []
    for tag in tags_lst:
        tag_dict = {'title': tag, 'url': (outdir + "tags/" + tag)}
        tags_lst_of_dicts.append(tag_dict)
    env = Environment(loader=FileSystemLoader('.'))
    page_list = env.get_template('templates/page-list.html')
    output = page_list.render(pages=tags_lst_of_dicts, baseurl=baseurl)
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
    global baseurl
    env = Environment(loader=FileSystemLoader('.'))
    page_list = env.get_template('templates/page-list.html')
    output = page_list.render(pages=tag_data['pages'], baseurl=baseurl)
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
        file_dict = organize_tags(json_lst, tag_synonyms, tag_implications)
        json_lst = file_dict['json']
        title = get_metadata_field(json_lst, "title")
        url = os.path.splitext(os.path.basename(page))[0]
        tags = file_dict['tags']
        all_tags.extend([i for i in tags])
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

tagsdir = "../tags/"
sitedir = "_site/"
baseurl = "../pages/"
pandoc_options = ""

for tag_data in generate_all_tag_data(file_pattern="pages/*.md"):
    create(compiled=tag_page_compiler(tag_data), filename=tag_data['tag'], outdir="_site/tags/")

create(compiled=all_tags_page_compiler(all_tags), filename="index", outdir="_site/tags/")

match(route=cool_uri_route, compiler=markdown_to_html_compiler, file_pattern="pages/*.md", outdir="_site/")

#json_lst = json.loads(c.run_command("pandoc -f markdown -t json {filename}".format(filename="pages/hello.md")))
#for i in ["title", "tags", "tags2", "tags3", "math", "math2"]:
    #print(get_metadata_field(json_lst, i))
    #print(type(get_metadata_field(json_lst, i)))
    #print("")
