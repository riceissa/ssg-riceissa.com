# Just sketches; not to be run

class Tag(object):
    name :: str

class Filepath(object):
    path :: str

class Content(object):
    (markup :: str, body :: str)

class Item(object):
    (Filepath, Content)

class Route(object)
    Filepath -> Filepath
    def __call__(self, filepath):
        run filepath through the route

class ItemCompiler(object):
    Item -> Item

class Site(object):
    def __init__(self, ):
        

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
    route=route_in_turn_from_left(drop_one_parent_dir_route, site_dir_route),
    compiler=copy_file_compiler,
)

match(
    pattern="pages/*.md",
    route=route_in_turn_from_left(
        drop_one_parent_dir_route,
        set_extension(""),
        site_dir_route
    ),
    compiler=markdown_to_html_compiler(tags_route),
    metadata=Metadata(
    ),
)

tags = list of tags

for tag in tags:
    create(
        path = str(tag),
        route = route_in_turn_from_left(
            to_dir("tags/"),
            site_dir_route,
        ),
        metadata = Metadata(
            title = "Tag: " + str(tag),
        ),
        compiler=tag_page_compiler,
    )

create(
    path = "tags/index",
    route = site_dir_route,
    compiler = ,
    metadata = Metadata(
        title = "List of tags",
    ),
)

create(
    path = "all"
    route = site_dir_route,
    compiler = list_pages_compiler(load_all("pages/*.md")),
    metadata = Metadata(
        title = "All pages",
    ),
)
