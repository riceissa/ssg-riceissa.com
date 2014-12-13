#!/bin/python
# -*- coding: utf-8 -*-

# FIXME: this is a quick hack to get the encoding errors to go away
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import glob
from subprocess import call, check_output, Popen, PIPE, STDOUT
import subprocess
import os
import meta
import json
from jinja2 import Template, Environment, FileSystemLoader
import shlex

lst_filepaths = glob.glob("pages/*.md")

def generate_html(lst_filepaths, outdir="_site/"):
    '''
    Take each filepath in lst_filepaths and convert each to HTML.
    '''
    for filepath in lst_filepaths:
        convert_single_file(filepath, outdir)

def convert_single_file(filepath, outdir="_site/"):
    '''
    Convert a single file from markdown to HTML.  Here filepath is the
    filepath to the markdown file, and outdir is the directory where the
    HTML should go.
    '''
    if os.path.exists(outdir):
        filename = os.path.basename(filepath)
        routename = os.path.splitext(filename)[0]
        myjson = json.loads(markdown_to_json(filepath))
        # This will return a dict {'json_dump': ..., 'tags': ...}
        file_dict = meta.organize_tags(myjson, meta.tag_synonyms, meta.tag_implications)
        # all_tags is global
        all_tags[routename] = file_dict['tags']
        myjson = file_dict['json_dump']
        command = "pandoc -f json -t html --mathjax --base-header-level=2".format(routename=routename, outdir=outdir)
        #print command
        # See http://stackoverflow.com/a/165662/3422337
        ps = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE,
            stderr=STDOUT)
        output = ps.communicate(input=myjson)[0]
        output = output.decode('utf-8')
        env = Environment(loader=FileSystemLoader('.'))
        pagetemp = env.get_template('templates/skeleton.html')
        #print output
        title = meta.get_meta_field(json.loads(myjson), "title").decode('utf-8')
        #print(file_dict['tags'])
        tags = file_dict['tags']
        print json.loads(myjson)
        # FIXME: for some reason, math: yes without quotes is turning into a boolean in pandoc's json representation, while math: "yes" with quotes works fine...
        math = meta.get_meta_field(json.loads(myjson), "math")
        print math
        final = pagetemp.render(body=output, title=title, tags=tags, license='cc', math=math).encode('utf-8')
        with open("{outdir}{routename}".format(outdir=outdir,
            routename=routename), "w") as f:
            f.write(final)
        #print(output)
        return all_tags
    else:
        print("{outdir} does not exist!".format(outdir=outdir))


all_tags = {}
#generate_html(lst_filepaths)
#print(list(set(all_tags)))
d = {"article1": ["a", "b"], "article2": ["b", "hakyll"]}
convert_single_file("pages/hello.md")
#create_tag_pages(d)
#create_all_tags_page(list(set([i for subl in d.values() for i in subl])))


