# -*- coding: utf-8 -*-
from web_translator.controllers import po_edit

ROUTES = [
    {'url': '/', 'method': 'GET', 'controller': po_edit.select_language},
    {'url': '/translate/:lang_to', 'method':'GET', 'controller': po_edit.system_translate},
    {'url': '/translate/:lang_to', 'method': 'POST', 'controller': po_edit.save_po},
    {'url': '/generate_db', 'method': 'GET', 'controller': po_edit.generate_db}
]
