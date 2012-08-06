# -*- coding: utf-8 -*-
import os
import site
import sys
import ConfigParser
import site

ALLDIRS = ['/home/translate/envs/pydev/lib/python2.7/site-packages/']

# Remember original sys.path.
prev_sys_path = list(sys.path)

# Add each new site-packages directory.
for directory in ALLDIRS:
    site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path


import bottle
from bottle import run, default_app, route, error, request
from bottle import PasteServer
from language_middleware import LanguageMiddleware
import sqlite3

from episte_web.libs.exceptions import NotFoundException, NotAllowedException
from episte_web.configs import LANGUAGES, LOCALE_NAME, LOCALE_PATH
from web_translator.configs.routes import ROUTES
from web_translator.configs import DB_PATH
from episte_web.libs.bottle_plugins.exceptions_handler import ExceptionsHandlerPlugin

ALLDIRS = ['/home/translate/envs/pydev/lib/python2.7/site-packages/']

# Remember original sys.path.
prev_sys_path = list(sys.path)

# Add each new site-packages directory.
for directory in ALLDIRS:
    site.addsitedir(directory)

# Reorder sys.path so new directories at the front.
new_sys_path = []
for item in list(sys.path):
    if item not in prev_sys_path:
        new_sys_path.append(item)
        sys.path.remove(item)
sys.path[:0] = new_sys_path

    
def not_found(html):
    return 'not found'

def not_allowed(html):
    return 'not allowed'

def process_routes(routes):
    for config in routes:
        route(config["url"], method=config["method"])(config["controller"])
    #comment the following two lines for debugging
    error(404)(not_found)
    error(405)(not_allowed)
    # error(500)(handle_exception)

class StripPathMiddleware(object):
    def __init__(self, app):
        self.app = app
    def __call__(self, env, start_response):
        env['PATH_INFO'] = env['PATH_INFO'].rstrip('/')
        return self.app(env, start_response)

class DBMiddleware(object):
    def __init__(self,app):
        self.app = app
    def __call__(self, env, start_response):
        request.db = sqlite3.connect(DB_PATH)
        request.db_cursor = request.db.cursor()
        return_ = self.app(env,start_response)
        request.db.commit()
        request.db_cursor.close()
        request.db.close()
        return return_

if os.environ.get('EPISTEMONIKOS_WEB_CONFIG'):
    config_path = os.environ.get('EPISTEMONIKOS_WEB_CONFIG')
elif len(sys.argv) >1:
    config_path = sys.argv[1]
else:
    config_path = '/home/translate/repos/po-web-translator/scripts/localhost.cfg'

#Reading config file
config = ConfigParser.ConfigParser()
config.read(config_path)
web_config = config.__dict__.get('_sections').get('web', {})

default_app.push()

exception_handler = ExceptionsHandlerPlugin()
bottle.install(exception_handler)


process_routes(ROUTES)

application = default_app.pop()
application.catchall = False


bottle.debug(True)
application = DBMiddleware(LanguageMiddleware(
                        StripPathMiddleware(application),
                        default_language = 'en',
                        valid_languages = map(lambda x: x[0], LANGUAGES),
                        clean_url = True,
                        locale_path = LOCALE_PATH,
                        locale_name = LOCALE_NAME
                ))

def main():
    reload = 'True' in web_config.get('reload', 'True')
    web_port = int(web_config.get('port', '8080'))
    run(app=application, host='0.0.0.0', port=web_port, server=PasteServer, reloader=reload)

if __name__ == "__main__":
    main()
