# -*- coding: utf-8 -*-
import os
import gettext

from bottle import MakoTemplate
from bottle import request, response
from pymongo import Connection

from episte_dal.account import Account
from web_translator.configs import LANGUAGES, TEMPLATES_PATH, LOCALE_NAME, LOCALE_PATH
from episte_web.libs.auth import get_account
from episte_web.libs.utils import get_messages
from episte_web.libs.html import html_escape

def _check_if_template_exists(name):
    abs_path = os.path.join(TEMPLATES_PATH, name)
    if os.path.exists(abs_path):
        return True
    return False

def get_final_path(name, start_w_slash = True):
    name_path = os.path.join(name)
    if _check_if_template_exists(name_path):
        name = name_path
    name_path = os.path.join('multisite', name)
    if _check_if_template_exists(name_path):
        name = name_path
    if start_w_slash and name[0:] != ["/"]:
        name = '/'+name
    return name

def render_template(name, error = False, **kwargs):
    active_language = request.headers.get('Active-Language')
    target_name = get_final_path(name, start_w_slash = False)
    template =  MakoTemplate(name=target_name, lookup=[TEMPLATES_PATH], default_filters=['decode.utf8'], imports=['from episte_web.libs.templates import get_final_path'])
    search_classification = request.GET.get('classification', 'all')
#    if error:
#        try:
#            get_account(request.mongodb)
#        except:
#            request.account = None
#    else:
#        get_account(request.mongodb)
    kwargs['messages'] = get_messages(kwargs.get('messages'))
    for key in kwargs:
        kwargs[key] = html_escape(kwargs[key])
    return template.render(language = active_language,
                           languages = LANGUAGES,
                           search_classification = search_classification,
                           **kwargs)
