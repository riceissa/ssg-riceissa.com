import os
import glob


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
        self.directory, self.filename = os.path.split(path)
        self.directory += "/"
        self.path_lst = split_path(path)

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
    def __init__(self, route, compiler):
        self.route = route
        self.compiler = compiler

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

def copy_file_compiler(item, rules):
    '''
    (Item, (Filepath -> Filepath)) -> Item
    Basically, ignore the rules and return the item.
    '''
    return item

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
        Rules(route, self_reference_compiler(item, route))
    '''
    body = "I will be stored in " + item.filepath.route_with(rules.route).path
    return Item(item.filepath, body)

def markdown_to_html_compiler(item, route):
    '''
    Item -> Item
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
        output = Filepath(path).to_item().compile_with(rules.compiler(rules.route)).body
        write_to = Filepath(path).route_with(rules.route).path
        with open(write_to, 'w') as f:
            f.write(output)

def create(path, rules):
    output = rules.compiler.body
    with open(path, 'w') as f:
        f.write(output)



def set_extension(extension):
    '''
    str -> Filepath -> Filepath
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

def to_site_dir_route(filepath, site_dir):
    pass


class Pattern(object):
    pass



class Context(object):
    pass



class Tags(object):
    pass


if __name__ == "__main__":
    fi = Item(Filepath("pages/hello.md"), "hello world!")
    ro = Route(set_extension(".html"))
    co = Compiler(self_reference_compiler)
    #co = Compiler(copy_file_compiler)
    ru = Rules(ro, co)
    #print ru.compiler.compiler
    #print ru.route.route
    print fi.compile_with(co, ru).body
