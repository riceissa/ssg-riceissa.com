#!/bin/python

import glob

lst_filepaths = glob.glob("pages/*.md")

def generate_html(lst_filepaths, outdir="_site/"):
    '''
    Take each filepath in lst_filepaths and convert each to HTML.
    '''
    for filepath in lst_filepaths:
        convert_single_file(filepath, outdir)

def convert_single_file(filepath, outdir="_site/"):
        # This will return a dict {'json_dump': ..., 'tags': ...}
        file_dict = meta.organize_tags(myjson, meta.tag_synonyms, meta.tag_implications)
        myjson = file_dict['json_dump']
        command = "pandoc -f json -t html --mathjax --base-header-level=2".format(routename=routename, outdir=outdir)
        #print command


all_tags = {}
#generate_html(lst_filepaths)
#print(list(set(all_tags)))
d = {"article1": ["a", "b"], "article2": ["b", "hakyll"]}
convert_single_file("pages/hello.md")
#create_tag_pages(d)
#create_all_tags_page(list(set([i for subl in d.values() for i in subl])))


