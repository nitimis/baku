import logging
from os import walk
try:
    # Python 3
    from socketserver import TCPServer
    from http.server import SimpleHTTPRequestHandler
except ImportError:
    # Python 2
    from SocketServer import TCPServer
    from SimpleHTTPServer import SimpleHTTPRequestHandler

import sass
import click
from watchdog.observers import Observer
from jinja2 import Environment, FileSystemLoader
from watchdog.events import FileSystemEventHandler

from baku_data import data

PORT = 8000
SRC_DIR = 'src'
DIST_DIR = 'dist'
SRC_SASS = '%s/sass' % SRC_DIR
SRC_HTML = '%s/templates' % SRC_DIR
SRC_MEDIA = '%s/media' % SRC_DIR
DIST_ASSETS = '%s/assets' % DIST_DIR
DIST_JS = '%s/js' % DIST_ASSETS
DIST_CSS = '%s/css' % DIST_ASSETS
DIST_MEDIA = '%s/media' % DIST_ASSETS
FORMAT = '%(asctime)-15s %(message)s'

env = Environment(loader=FileSystemLoader(SRC_HTML))
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)


def build_templates():
    for root, dirs, files in walk(SRC_HTML):
        for file in files:
            template = env.get_template(file)
            with open("%s/%s" % (DIST_DIR, file), 'w') as f:
                f.write(template.render(data=data))


def build_styles():
    sass.compile(dirname=(SRC_SASS, 'css'), output_style='compressed')


def _build():
    logger.info('Building templates and styles')
    build_templates()
    build_styles()


class OutputHTTPRequestHandler(SimpleHTTPRequestHandler):
    '''
    All files should be served from DIST_DIR.
    This Handler enables us to do that.
    '''

    def translate_path(self, path):
        return "%s/%s" % (DIST_DIR, path)


class TemplateEventHandler(FileSystemEventHandler):
    '''
    A watchdog event handler class to compile template files
    '''
    def on_any_event(self, event):
        if not event.src_path.endswith('.html'):
            return
        logger.info("TemplateEventHandler: %s %s" % (
            event.event_type, event.src_path))
        build_templates()


class StyleEventHandler(FileSystemEventHandler):
    '''
    A watchdog event handler class to compile template files
    '''
    def on_any_event(self, event):
        if not event.src_path.endswith('.sass'):
            return
        logger.info("StyleEventHandler: %s %s" % (
            event.event_type, event.src_path))
        build_styles()


@click.group()
def cli():
    pass


@click.group()
def init():
    # Initialize baku directory
    pass


@cli.command()
def build():
    _build()


@cli.command()
def serve():
    _build()
    observer = Observer()
    observer.schedule(TemplateEventHandler(), SRC_HTML, recursive=True)
    observer.schedule(StyleEventHandler(), SRC_SASS, recursive=True)
    observer.start()
    httpd = TCPServer(("", PORT), OutputHTTPRequestHandler)
    logger.info("serving at port: %s" % PORT)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
