#!/bin/python

import glob
from subprocess import call
import os

lst_filepaths = glob.glob("pages/*.md")
lst_filenames = [os.path.basename(i) for i in lst_filepaths]
lst_routenames = [os.path.splitext(i)[0] for i in lst_filenames]

def generate_html():
    for n, filepath in enumerate(lst_filepaths):
        command = "pandoc -f markdown -t html -s --base-header-level=2 -o _site/{routename} {filepath}".format(filepath=filepath, routename=lst_routenames[n])
        print command
        #call(command, shell=True)

if os.path.exists("_site/"):
    generate_html()

