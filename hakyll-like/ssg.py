import os


class AbsolutePathException(Exception):
    pass

class Configuration(object):
    pass


def split_path(p):
    # See http://stackoverflow.com/a/15050936/3422337
    a, b = os.path.split(p)
    return (split_path(a) if len(a) and len(b) else []) + [b]

class Filepath(object):
    '''
    Specify a single item.
    '''
    def __init__(self, path):
        if path.startswith('/'):
            raise AbsolutePathException("path is absolute; must be relative")
        self.path = path
    def route(self, route_rule):
        return route_rule(self)



#class Route(object):
    #def __init__(self, route_rule):
        #self.route_rule = route_rule
    #def compose_with(self, other):
        #return Route(self.)

def set_extension(extension):
    '''
    str -> Filepath -> Filepath
    '''
    def f(path):
        '''
        Filepath -> Filepath
        '''
        return Filepath(os.path.splitext(path.path)[0] + extension)
    return f

def id_route(path):
    '''
    Filepath -> Filepath
    '''
    return path


class Pattern(object):
    pass


class Compiler(object):
    pass

class Context(object):
    pass

class Item(object):
    '''
    '''
    def __init__(self, item_identifier, item_body):
        self.item_identifier = item_identifier
        self.item_body = item_body
    def set_body(self, new_body):
        self.item_body = new_body
    def with_item_body(self, compiler):
        pass

class Rules(object):
    pass

class Tags(object):
    pass
