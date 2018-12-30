import click

import sass
from os import walk
from socketserver import TCPServer
from http.server import SimpleHTTPRequestHandler

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from jinja2 import Environment, FileSystemLoader

from src import data

PORT = 8000
SRC_DIR = 'src'
DIST_DIR = 'dist'
SRC_SASS = f'{SRC_DIR}/sass'
SRC_HTML = f'{SRC_DIR}/templates'
SRC_MEDIA = f'{SRC_DIR}/media'
DIST_ASSETS = f'{DIST_DIR}/assets'
DIST_JS = f'{DIST_ASSETS}/js'
DIST_CSS = f'{DIST_ASSETS}/css'
DIST_MEDIA = f'{DIST_ASSETS}/media'

env = Environment(loader=FileSystemLoader(SRC_HTML))


def compile_all_templates():
    for root, dirs, files in walk(SRC_HTML):
        for file in files:
            template = env.get_template(file)
            with open(f'{DIST_DIR}/{file}', 'w') as f:
                f.write(template.render(data=data))


def compile_all_styles():
    sass.compile(dirname=(SRC_SASS, 'css'), output_style='compressed')


def compile_all_files():
    compile_all_templates()
    compile_all_styles()


class OutputHTTPRequestHandler(SimpleHTTPRequestHandler):
    '''
    All files should be served from DIST_DIR.
    This Handler enables us to do that.
    '''

    def translate_path(self, path):
        return f'{DIST_DIR}/{path}'


class TemplateEventHandler(FileSystemEventHandler):
    '''
    A watchdog event handler class to compile template files
    '''
    def on_any_event(self, event):
        if not event.src_path.endswith('.html'):
            return
        print("TemplateEventHandler: ", event.event_type, event.src_path)
        compile_all_templates()


class SASSEventHandler(FileSystemEventHandler):
    '''
    A watchdog event handler class to compile template files
    '''
    def on_any_event(self, event):
        if not event.src_path.endswith('.sass'):
            return
        print("SASSEventHandler: ", event.event_type, event.src_path)
        compile_all_styles()


@click.command()
def cli():
    """Example script."""
    click.echo('Hello World!')


if __name__ == "__main__":
    observer = Observer()
    observer.schedule(TemplateEventHandler(), SRC_HTML, recursive=True)
    observer.schedule(SASSEventHandler(), SRC_SASS, recursive=True)
    observer.start()
    httpd = TCPServer(("", PORT), OutputHTTPRequestHandler)
    compile_all_files()
    print("serving at port", PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
