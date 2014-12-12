#!/bin/python

import glob
from subprocess import call, check_output, Popen, PIPE, STDOUT
import subprocess
import os
import meta
import json
from jinja2 import Template

lst_filepaths = glob.glob("pages/*.md")
#lst_filenames = [os.path.basename(i) for i in lst_filepaths]
#lst_routenames = [os.path.splitext(i)[0] for i in lst_filenames]

def markdown_to_json(filepath):
    command = "pandoc -f markdown -t json -s {filepath}".format(filepath=filepath)
    return check_output(command, shell=True)

def convert_single_file(filepath, outdir="_site/"):
    if os.path.exists(outdir):
        filename = os.path.basename(filepath)
        routename = os.path.splitext(filename)[0]
        myjson = json.loads(markdown_to_json(filepath))
        myjson = meta.organize_tags(myjson, meta.tag_synonyms, meta.tag_implications)
        #print myjson['tags']
        all_tags.extend(myjson['tags'])
        myjson = myjson['json_dump']
        command = "pandoc -f json -t html -s --template=skeleton.html --base-header-level=2 -o {outdir}{routename}".format(routename=routename, outdir=outdir)
        print command
        # See http://stackoverflow.com/a/165662/3422337
        ps = Popen(command.split(' '), stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = ps.communicate(input=myjson)[0]
        #print(output)
        #call(command, stdin=myjson, shell=True)
        return all_tags
    else:
        print("{outdir} does not exist!".format(outdir=outdir))

def generate_html():
    for filepath in lst_filepaths:
        convert_single_file(filepath, outdir="_site/")

def make_tag_pages(tags):
    for tag in tags:
        template = Template("""Tag: {{ tag }}
{% for item in seq %}{{ item }}
{% endfor %}""")
        print template.render(tag=tag, seq=tags)

all_tags = []
#generate_html()
#print list(set(all_tags))
make_tag_pages(["a", "b", "hakyll"])

