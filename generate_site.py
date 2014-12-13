
# hack to get unicode working with jinja2
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import glob
import commands as c
from jinja2 import Template, Environment, FileSystemLoader
import os
from tag_ontology import tag_synonyms, tag_implications
from metadata import *


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
