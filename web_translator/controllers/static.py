# -*- coding: utf-8 -*-

from bottle import static_file

from web_translator.configs import ASSETS_PATH

def get_file(filename):
    return static_file(filename, root=ASSETS_PATH)