# -*- coding: utf-8 -*-
import os

TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates")
LOCALE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../locale")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../db")
TRANSLATOR_LEVELS = ['Adminstrator', 'Basic', 'Expert', 'PDQ', 'Delete']
LOCALE_NAME = 'epistemonikos'
ASSETS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../assets")
LANGUAGES = [
    ('ar', 'العربية'),
	('de', 'Deutsch'),
	('en', 'English') ,
	('es', 'Español' ),
	('fr', 'Français'),
	('it', 'Italiano'),
	('nl', 'Nederlands'),  ('pt', 'Português'),
	('zh', '中文')
]
