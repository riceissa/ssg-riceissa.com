#!/bin/python

import glob
from subprocess import call, check_output, Popen, PIPE, STDOUT
import subprocess
import os
import meta
import json
from jinja2 import Template, Environment, FileSystemLoader
import shlex

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
        all_tags[routename] = myjson['tags']
        myjson = myjson['json_dump']
        command = "pandoc -f json -t html -s --template=skeleton.html --base-header-level=2 -o {outdir}{routename}".format(routename=routename, outdir=outdir)
        print command
        # See http://stackoverflow.com/a/165662/3422337
        ps = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = ps.communicate(input=myjson)[0]
        #print(output)
        #call(command, stdin=myjson, shell=True)
        return all_tags
    else:
        print("{outdir} does not exist!".format(outdir=outdir))

def generate_html():
    for filepath in lst_filepaths:
        convert_single_file(filepath, outdir="_site/")

def create_tag_pages(tags_dict):
    tags = list(set([val for subl in tags_dict.values() for val in subl]))
    print tags
    print tags_dict
    for tag in tags:
        pages_with_tag = [page for page, page_tags in tags_dict.items() if tag in page_tags]
        print str(pages_with_tag) + " has " + tag
        template = Template("""Tag: {{ tag }}

{% for page in pages_with_tag %}- [{{ page }}](./{{ page }})
{% endfor %}""")
        doc = template.render(tag=tag, pages_with_tag=pages_with_tag)
        command = 'pandoc -f markdown -t html -o _site/tags/{tag}'.format(tag=tag)
        ps = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = ps.communicate(input=doc)[0]

def create_all_tags_page(tags):
        template = Template("""Tags:

{% for tag in tags %}- [{{ tag }}](./{{ tag }})
{% endfor %}""")
        doc = template.render(tags=tags)
        command = "pandoc -f markdown -t html"
        ps = Popen(shlex.split(command), stdout=PIPE, stdin=PIPE, stderr=STDOUT)
        output = ps.communicate(input=doc)[0]
        env = Environment(loader=FileSystemLoader('.'))
        pagetemp = env.get_template('skeleton.html')
        final = pagetemp.render(body=output, title="hello")
        with open("_site/tags/index", "w") as f:
            f.write(final.encode('utf-8'))

all_tags = {}
#generate_html()
print list(set(all_tags))
d = {"article1": ["a", "b"], "article2": ["b", "hakyll"]}
#create_tag_pages(d)
create_all_tags_page(list(set([i for subl in d.values() for i in subl])))


