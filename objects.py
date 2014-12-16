# Just sketches; not to be run

class Tag(object):
    name :: str

class FilePath(object):
    path :: str

class Content(object):
    (markup :: str, body :: str)

class Item(object):
    (FilePath, Content)

class Route(object)
    FilePath -> FilePath
    def __call__(self, filepath):
        run filepath through the route

class ItemCompiler(object):
    Item -> Item



################
# Here's how the enduser might use the program

match(
    pattern="site.hs",
    route=site_dir_route,
    compiler=copy_file_compiler,
)

match(
    pattern="css/*",
    route=site_dir_route,
    compiler=compress_css_compiler,
)

match(
    pattern="static/*",
    route=site_dir_route,
    compiler=copy_file_compiler,
)

match(
    pattern="images/*",
    # You can also define this route outside as
    # @Route
    # def my_route(fp):
    #     return fp.route_with(drop_one_parent_dir_route).route_with(site_dir_route)
    #route=Route(lambda fp: fp.route_with(drop_one_parent_dir_route).route_with(site_dir_route)),
    route=route_in_turn_from_left(drop_one_parent_dir_route, site_dir_route),
    #route=route_in_turn_from_right(site_dir_route, drop_one_parent_dir),
    compiler=copy_file_compiler,
)

match(
    pattern="pages/*.md",
    #route=cool_page_route,
    route=route_in_turn_from_left(drop_one_parent_dir_route, set_extension(""), site_dir_route),
    compiler=,
)
