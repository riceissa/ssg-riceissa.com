#!/bin/python

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

site_dir = "_site/"
tags_dir = "tags/" # relative to site_dir


class Route(object):
    '''
    Each Route object is a function Filepath -> Filepath
    '''
    def __init__(self, route):
        self.route = route

class Compiler(object):
    '''
    Each Compiler object is a function (Item, Rules) -> Item
    '''
    def __init__(self, compiler):
        self.compiler = compiler


def to_dir(site_dir):
    '''
    Site_dir(str) -> Filepath -> Filepath
    '''
    @Route
    def f(filepath):
        return Filepath(site_dir + filepath.filename())
    return f


site_dir_route = to_dir(site_dir)

@Route
def my_route(filepath):
    return filepath.route_with(set_extension("")).route_with(drop_one_parent_dir_route).route_with(site_dir_route)

@Route
def standard_tags_route(filepath):
    '''
    Filepath -> Filepath
    Here filepath is just Filepath(tag.name) for a tag.
    '''
    return filepath.route_with(to_dir(site_dir + tags_dir))

@Compiler
def copy_file_compiler(item, rules):
    '''
    (Item, Route) -> Item
    Basically, ignore the rules and return the item.
    '''
    return item



class AbsolutePathException(Exception):
    pass

class Configuration(object):
    pass


def split_path(path):
    # See http://stackoverflow.com/a/15050936/3422337
    a, b = os.path.split(path)
    return (split_path(a) if len(a) and len(b) else []) + [b]

@Route
def drop_one_parent_dir_route(filepath):
    return Filepath('/'.join([i for i in split_path(filepath.path)[1:]]))

class Filepath(object):
    '''
    Specify a single item.
    '''
    def __init__(self, path):
        if path.startswith('/'):
            raise AbsolutePathException("path is absolute; must be relative")
        self.path = path

    def filename(self):
        return os.path.split(self.path)[1]

    def directory(self):
        return os.path.split(self.path)[0] + "/"

    def path_lst(self):
        return split_path(self.path)

    def route_with(self, route):
        return route.route(self)

    def go_to_other(self, other):
        path1 = os.path.normpath(self.path)
        path2 = os.path.normpath(other.path)
        depth = len(Filepath(path1).path_lst()) - 1
        return Filepath("../" * depth + path2)

    def relative_to(self, other):
        return other.go_to_other(self)

    def to_item(self):
        with open(self.path, 'r') as f:
            return Item(self, f.read())



class Item(object):
    '''
    '''
    def __init__(self, filepath, body):
        self.filepath = filepath
        self.body = body
    def set_body(self, new_body):
        self.body = new_body
    def compile_with(self, compiler, rules):
        '''
        (Item, Compiler, Rules) -> Item
        '''
        return compiler.compiler(self, rules)

class Rules(object):
    '''
    Each Rules object contains rules for compiling an Item object.
    '''
    def __init__(self, route=site_dir_route, compiler=copy_file_compiler, tags_route=standard_tags_route):
        self.route = route
        self.compiler = compiler
        self.tags_route = tags_route


# so do like Item(Filepath('pages/hello.md'), "hello world!")


@Compiler
def self_reference_compiler(item, rules):
    '''
    (Item, Rules) -> Item
    This is a silly example to show why compilers need route;
    in short, since Item only contains where it currently is and
    the body, it won't know where it *will* be.  But sometimes we
    want to know where it *will* be, and reference it in the output.
    Use like so:
        item = ...
        route = ...
        compiler = Compiler(self_reference_compiler)
        rules = Rules(route, compiler)
        item.compile_with(compiler, rules)
    '''
    body = "I will be stored in " + item.filepath.route_with(rules.route).path
    return Item(item.filepath, body)

@Compiler
def markdown_to_html_compiler(item, rules):
    '''
    (Item, Rules) -> Item
    '''
    filename = item.filepath.filename
    command = "pandoc -f markdown -t json -s {path}".format(path=item.filepath.path)
    json_lst = json.loads(c.run_command(command))
    # This will return a dict {'json': ..., 'tags': ...}
    file_dict = organize_tags(json_lst, tag_synonyms, tag_implications)
    json_lst = file_dict['json']
    tags = [Tag(t) for t in file_dict['tags']]
    command = "pandoc -f json -t html --mathjax --base-header-level=2"
    html_output = c.run_command(command, pipe_in=json.dumps(json_lst, separators=(',',':'))).encode('utf-8')
    env = Environment(loader=FileSystemLoader('.'))
    skeleton = env.get_template('templates/skeleton.html')

    # Get metadata ready
    ctx = Context(
        title = get_metadata_field(json_lst, "title"),
        math = get_metadata_field(json_lst, "math"),
        license = get_metadata_field(json_lst, "license"),
    )

    final_filepath = item.filepath.route_with(rules.route)
    tags_lst = []
    for tag in tags:
        tag_filepath = Filepath(tag.name).route_with(rules.tags_route)
        rel_path = tag_filepath.relative_to(final_filepath).path
        tags_lst.append({'name': tag.name, 'path': rel_path})
    new_body = skeleton.render(body=html_output, title=ctx.title, tags=tags_lst, license=ctx.license, math=ctx.math).encode('utf-8')

    # We keep the original filepath
    return Item(item.filepath, new_body)

def match(pattern, rules):
    '''
    (Pattern(str), Rules) -> IO
    '''
    paths_lst = glob.glob(pattern)
    for path in paths_lst:
        output = Filepath(path).to_item().compile_with(rules.compiler, rules).body
        write_to = Filepath(path).route_with(rules.route).path
        with open(write_to, 'w') as f:
            f.write(output)

def create(path, base_item, rules):
    '''
    (Path(str), Item, Rules) -> IO
    '''
    output = base_item.compile_with(rules.compiler, rules).body
    write_to = Filepath(path).path # Filepath makes sure the path is relative
    with open(write_to, 'w') as f:
        f.write(output)

@Compiler
def all_tags_page_compiler(item, rules):
    global tags_dir
    tags_lst_of_dicts = []
    for tag in tags_lst:
        tag_dict = {'title': tag, 'url': (tagsdir + tag)}
        tags_lst_of_dicts.append(tag_dict)
    env = Environment(loader=FileSystemLoader('.'))
    page_list = env.get_template('templates/page-list.html')
    pagesdir_depth = len(split_path(pagesdir[:-1]))
    print pagesdir_depth*"../"
    output = page_list.render(pages=tags_lst_of_dicts)
    for i in tags_lst_of_dicts:
        print pagesdir_depth*"../" + i['url']
    skeleton = env.get_template('templates/skeleton.html')
    final = skeleton.render(body=output, title="List of all tags", license='CC0').encode('utf-8')
    return final

@Compiler
def tag_page_compiler(item, rules):
    pass


def set_extension(extension):
    '''
    Extension(str) -> Filepath -> Filepath
    '''
    @Route
    def f(filepath):
        '''
        Filepath -> Filepath
        '''
        return Filepath(os.path.splitext(filepath.path)[0] + extension)
    return f

@Route
def id_route(filepath):
    '''
    Filepath -> Filepath
    '''
    return filepath





class Context(object):
    '''
    So you can do things like x = Context(title="hello, world!", math="true") then access with x.title, x.math and so on.
    FIXME: add some default fields.
    '''
    def __init__(self, title="", math="True", tags=[], license="CC-BY", **kwargs):
        self.title = title
        if type(math) is bool:
            if math:
                self.math = "True"
            else:
                self.math = "False"
        else:
            self.math = math
        self.tags = tags
        self.license = license
        for key in kwargs:
            self.__setattr__(key, kwargs[key])



class Tag(object):
    def __init__(self, name):
        self.name = name
    def get_pages_using(self, items):
        '''
        (Tag, [Item]) -> [Item]
        '''
        final = []
        for item in items:
            json_lst = json.loads(c.run_command("pandoc -f markdown -t json", pipe_in=item.body))
            if self.name in get_metadata_field(json_lst, "tags"):
                final.append(item)
        return final

def get_items_from_pattern(pattern):
    '''
    Pattern(str) -> [Item]
    '''
    paths = glob.glob(pattern)
    final = []
    for path in paths:
        with open(path, 'r') as f:
            body = f.read()
            final.append(Item(Filepath(path), body))
    return final

if __name__ == "__main__":
    # The end-user should be able to use this program like so:
    fi = Filepath("pages/hello.md").to_item()
    ro = my_route
    co = markdown_to_html_compiler
    ru = Rules(ro, co)
    #print fi.compile_with(co, ru).filepath.path
    #print fi.filepath.route_with(ro).path
    #print fi.compile_with(co, ru).body
    #match("pages/*.md", ru)
    x = Tag("chemistry").get_pages_using(get_items_from_pattern("pages/*.md"))
    for i in x:
        print i.filepath.path
