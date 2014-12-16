
# hack to get unicode working with jinja2
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

import glob
import metadata as meta
from tag_ontology import *
import commands as c
import json
from collections import OrderedDict

from jinja2 import Template, Environment, FileSystemLoader
import os

def to_unicode(string):
    if isinstance(string, str):
        return string.decode('utf-8')
    if isinstance(string, bool):
        if string:
            return "True".decode('utf-8')
        else:
            return "False".decode('utf-8')
    if isinstance(string, unicode):
        return string
    else:
        return "".decode("utf-8")

def to_string(unic):
    if isinstance(unic, unicode):
        return unic.encode('utf-8')
    if isinstance(unic, bool):
        if unic:
            return "True"
        else:
            return "False"
    if isinstance(unic, str):
        return unic
    else:
        return ""

pages_pat = "pages/*.md"
pages_lst = glob.glob(pages_pat)

all_tags = []
page_data = []
for page in pages_lst:
    #print "on page " + page
    output = c.run_command("pandoc -f markdown -t json {page}".format(page=page))
    json_lst = json.loads(output)
    file_dict = meta.organize_tags(json_lst, tag_synonyms, tag_implications)
    tags_lst = meta.get_tags(file_dict['json'])
    tags_lst = [i.decode('utf-8') for i in tags_lst]
    all_tags.extend(tags_lst)
    json_str = json.dumps(file_dict['json'], separators=(',',':'))
    body = c.run_command("pandoc -f json -t html --toc --template=templates/toc.html --mathjax --base-header-level=2", pipe_in=json_str).decode('utf-8')
    title = meta.get_metadata_field(json_lst, "title")
    #print "TITLETYPE0:", type(title)
    title = title.decode('utf-8') if not isinstance(title, unicode) else title
    math = meta.get_metadata_field(json_lst, "math")
    if isinstance(math, bool):
        if math:
            math = "True"
        else:
            math = "False"
    math = math.decode('utf-8') if not isinstance(math, type(None)) else unicode('', 'utf-8')
    license = meta.get_metadata_field(json_lst, "license")
    license = license.decode('utf-8') if not isinstance(license, type(None)) else unicode('', 'utf-8')

    env = Environment(loader=FileSystemLoader('.'))
    skeleton = env.get_template('templates/skeleton.html')
    tags = []
    for tag in tags_lst:
        tags.append({'name': tag.decode('utf-8'), 'path': ("tags/" + tag).decode('utf-8')})
    tags = sorted(tags, key=lambda t: t['name'])
    final = skeleton.render(body=body, title=title, license=license, math=math, tags=tags)
    inter = os.path.split(os.path.splitext(page)[0])[1]
    write_to = "_site/" + inter
    page_data.append((title, inter, tags_lst))

    with open(write_to, 'w') as f:
        f.write(final.encode('utf-8'))

all_tags = list(set(all_tags))

for tag in all_tags:
    pages = []
    for page_tuple in page_data:
        if tag in page_tuple[2]:
            pages.append({'title': page_tuple[0], 'url': "../" + page_tuple[1]})
    pages = sorted(pages, key=lambda t: t['title'])
    write_to = "_site/tags/" + tag.encode('utf-8')
    env = Environment(loader=FileSystemLoader('.'))
    page_list = env.get_template('templates/page-list.html')
    body = page_list.render(pages=pages)
    skeleton = env.get_template('templates/skeleton.html')
    final = skeleton.render(body=body, title="Tag page for " + tag)

    with open(write_to, 'w') as f:
        f.write(final.encode('utf-8'))

# Make page with all tags
env = Environment(loader=FileSystemLoader('.'))
page_list = env.get_template('templates/page-list.html')
pages = [{'title': tag.decode('utf-8'), 'url': tag.decode('utf-8')} for tag in all_tags]
pages = sorted(pages, key=lambda t: t['title'])
body = page_list.render(pages=pages).decode('utf-8')
skeleton = env.get_template('templates/skeleton.html')
final = skeleton.render(title="All tags".decode('utf-8'), body=body)
with open("_site/tags/index", 'w') as f:
    f.write(final.encode('utf-8'))

# Make page with all pages
env = Environment(loader=FileSystemLoader('.'))
page_list = env.get_template('templates/page-list.html')
#print "len(page_list)", len(page_list)
pages = [{'title': to_unicode(page_tup[0]), 'url': to_unicode(page_tup[1])} for page_tup in page_data]
pages = sorted(pages, key=lambda t: t['title'])
#for i in pages:
    #print i['title']
    #print i['url']
    #print ""
#print "len(pages)", len(pages)
body = page_list.render(pages=pages)
skeleton = env.get_template('templates/skeleton.html')
final = skeleton.render(title=to_unicode("All pages on the site"), body=body)
with open("_site/all", 'w') as f:
    f.write(to_string(final))
