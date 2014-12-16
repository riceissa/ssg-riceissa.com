
# hack to get unicode working with jinja2
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

import glob
import metadata as meta
from tag_ontology import *
import commands as c
import json

from jinja2 import Template, Environment, FileSystemLoader
import os

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
    body = c.run_command("pandoc -f json -t html", pipe_in=json_str).decode('utf-8')
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
    #print "tags_lst:", tags_lst
    #print "tags:", tags
    #print "TAGNAME:", tags[0]['name'], type(tags[0]['name'])
    #print "TAGPATH:", type(tags[0])
    #print "TITLETYPE:", type(title)
    #print "LICENSETYPE:", license, type(license)
    #print "MATHTYPE:", type(math)
    #print "BODYTYPE:", type(body)
    final = skeleton.render(body=body, title=title, license=license, math=math, tags=tags)
    inter = os.path.split(os.path.splitext(page)[0])[1]
    write_to = "_site/" + inter
    page_data.append((title, inter, tags_lst))

    with open(write_to, 'w') as f:
        f.write(final.encode('utf-8'))

#all_tags = list(set(all_tags))

#for tag in all_tags:
    #pages = []
    #for page_tuple in page_data:
        #if tag in page_tuple[2]:
            #pages.append({'title': page_tuple[0], 'url': "../" + page_tuple[1]})
    #write_to = "_site/tags/" + tag.encode('utf-8')
    #env = Environment(loader=FileSystemLoader('.'))
    #page_list = env.get_template('templates/page-list.html')
    #body = page_list.render(pages=pages)
    #skeleton = env.get_template('templates/skeleton.html')
    #final = skeleton.render(body=body, title="Tag page for " + tag)

    #with open(write_to, 'w') as f:
        #f.write(final.encode('utf-8'))

#env = Environment(loader=FileSystemLoader('.'))
#page_list = env.get_template('templates/page-list.html')
#pages = [{'title': tag.decode('utf-8'), 'url': tag.decode('utf-8')} for tag in all_tags]
#body = page_list.render(pages=pages).decode('utf-8')
#skeleton = env.get_template('templates/skeleton.html')
#final = skeleton.render(title="All tags".decode('utf-8'), body=body)
#with open("_site/tags/index", 'w') as f:
    #f.write(final.encode('utf-8'))

#env = Environment(loader=FileSystemLoader('.'))
#page_list = env.get_template('templates/page-list.html')
#pages = [{'title': page_tup[0], 'url': page_tup[1]} for page_tup in page_data]
#body = page_list.render(pages=pages)
#skeleton = env.get_template('templates/skeleton.html')
#final = skeleton.render(title="All pages on the site", body=body)
#with open("_site/all", 'w') as f:
    #f.write(final.encode('utf-8'))
