#!/bin/python

import glob
from subprocess import call, check_output
import os
import meta
import json

lst_filepaths = glob.glob("pages/*.md")
#lst_filenames = [os.path.basename(i) for i in lst_filepaths]
#lst_routenames = [os.path.splitext(i)[0] for i in lst_filenames]

def markdown_to_json(filepath):
    command = "pandoc -f markdown -t json -s {filepath}".format(filepath=filepath)
    return check_output(command, shell=True)

def convert_single_file(filepath, outdir="_site/"):
    if os.path.exists(outdir):
        filename = os.path.basename(filepath)
        routename = os.path.splitext(filename)
        command = "pandoc -f markdown -t html -s --base-header-level=2 -o {outdir}{routename} {filepath}".format(filepath=filepath, routename=routename, outdir=outdir)
        print command
        #call(command, shell=True)
    else:
        print("{outdir} does not exist!".format(outdir=outdir))

def generate_html():
    for filepath in lst_filepaths:
        convert_single_file(filepath)

#myjson = json.loads(markdown_to_json("hello.md"))
#print myjson
#meta.organize_tags(myjson, meta.tag_synonyms, meta.tag_implications)

generate_html()

