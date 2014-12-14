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
        return route(self)

    def compile_with(self, compiler):
        return compiler(self)

    def to_item(self):
        return Item(self, )


class Rules(object):
    def __init__(self, route, compiler):
        self.route= route
        self.compiler = compiler


class Item(object):
    '''
    '''
    def __init__(self, item_filepath, item_body):
        self.item_filepath = item_filepath
        self.item_body = item_body
    def set_body(self, new_body):
        self.item_body = new_body
    def with_item_body(self, compiler):
        pass

# so do like Item(Filepath('pages/hello.md'), "hello world!")

def copy_file_compiler(item):
    '''
    Item -> Item
    '''
    return item

def match(pattern, rules):
    '''
    Pattern(str) -> Rules -> IO
    '''
    paths_lst = glob.glob(pattern)
    for path in paths_lst:
        output = Filepath(path).compile_with(rule.compiler).content
        write_to = Filepath(path).route_with(rules.route).path
        with open(write_to, 'w') as f:
            f.write(output)

def create():
    pass


#class Route(object):
    #def __init__(self, route_rule):
        #self.route_rule = route_rule
    #def compose_with(self, other):
        #return Route(self.)

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


class Pattern(object):
    pass


class Compiler(object):
    pass

class Context(object):
    pass



class Tags(object):
    pass
