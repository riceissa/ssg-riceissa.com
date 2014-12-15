import os
import glob

site_dir = "_site/"
tags_dir = "tags/" # relative to site_dir

def site_dir_route(filepath):
    global site_dir
    return to_dir(site_dir)(filepath)

def copy_file_compiler(item, rules):
    '''
    (Item, Route) -> Item
    Basically, ignore the rules and return the item.
    '''
    return item


def to_dir(site_dir):
    '''
    Site_dir(str) -> Filepath -> Filepath
    '''
    def f(filepath):
        return Filepath(site_dir + filepath.filename())
    return f

class AbsolutePathException(Exception):
    pass

class Configuration(object):
    pass


def split_path(path):
    # See http://stackoverflow.com/a/15050936/3422337
    a, b = os.path.split(path)
    return (split_path(a) if len(a) and len(b) else []) + [b]

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
    def __init__(self, route=site_dir_route, compiler=copy_file_compiler, tags_route=to_dir(site_dir + tags_dir)):
        self.route = route
        self.compiler = compiler
        self.tags_route = tags_route

class Compiler(object):
    '''
    Each Compiler object is a function (Item, Rules) -> Item
    '''
    def __init__(self, compiler):
        self.compiler = compiler

class Route(object):
    '''
    Each Route object is a function Filepath -> Filepath
    '''
    def __init__(self, route):
        self.route = route

# so do like Item(Filepath('pages/hello.md'), "hello world!")


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
    tags = file_dict['tags']
    command = "pandoc -f json -t html --mathjax --base-header-level=2"
    html_output = c.run_command(command, pipe_in=json.dumps(json_lst, separators=(',',':'))).encode('utf-8')
    env = Environment(loader=FileSystemLoader('.'))
    skeleton = env.get_template('templates/skeleton.html')

    # Get metadata ready
    title = get_metadata_field(json_lst, "title")
    math = get_metadata_field(json_lst, "math")
    license = get_metadata_field(json_lst, "license")

    # Each tag page is going to be at sitedir + tagsdir + tag.  But if we reference this location from a file that is in a place other than sitedir, then it will point to sitedir + otherdir + tagsdir + tag or something weird.
    # To solve this problem, we have to figure out how deep tagsdir is, relative to sitedir.

    item.filepath
    rules.route
    where_this_file_will_go = item.filepath.route_with(rules.route)
    # FIXME
    where_tags_will_go = Filepath(tagname).route_with(rules.tags_route)
    tagsdir_depth = len(split_path(tagsdir[:-1])) # the [:-1] removes the trailing slash
    final = skeleton.render(body=html_output, title=title, tags=tags, tagsdir=tagsdir_depth*"../"+tagsdir, license=license, math=math).encode('utf-8')
    return final

    new_body = something(item.body)
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
    output = rules.compiler(base_item, rules).body
    write_to = Filepath(path).path # this makes sure the path is relative
    with open(write_to, 'w') as f:
        f.write(output)



def set_extension(extension):
    '''
    Extension(str) -> Filepath -> Filepath
    '''
    def f(filepath):
        '''
        Filepath -> Filepath
        '''
        return Filepath(os.path.splitext(filepath.path)[0] + extension)
    return f

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
    def __init__(self, **kwargs):
        for key in kwargs:
            self.__setattr__(key, kwargs[key])



class Tag(object):
    def __init__(self, name):
        self.name = name
    def get_pages(self):
        pass


if __name__ == "__main__":
    # The end-user should be able to use this program like so:
    fi = Item(Filepath("pages/hello.md"), "hello world!")
    ro = Route(set_extension(".html"))
    co = Compiler(self_reference_compiler)
    #co = Compiler(copy_file_compiler)
    ru = Rules(ro, co)
    #print ru.compiler.compiler
    #print ru.route.route
    print fi.compile_with(co, ru).filepath.path
    print fi.filepath.route_with(ro).path
    print fi.filepath.directory(), fi.filepath.filename(), fi.filepath.path_lst()
