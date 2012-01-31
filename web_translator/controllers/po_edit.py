# -*- coding: utf-8 -*-
from polib import pofile, POEntry, POFile
from bottle import request

from web_translator.libs.templates import render_template
from episte_web.libs.auth import secure
from episte_web.configs import LOCALE_PATH, LANGUAGES
from web_translator.configs import TRANSLATOR_LEVELS


def generate_db():
    table_exists = request.db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages';")
    if not table_exists.fetchone():
        sql_query = "CREATE table messages(id text not null primary key"
        for lang in LANGUAGES:
            sql_query += "," + lang[0] + " text"
        sql_query += ",user_level text)"
        request.db_cursor.execute(sql_query)

    for lang in LANGUAGES:
        messages = [e for e in pofile(LOCALE_PATH + '/' + lang[0] + '/LC_MESSAGES/epistemonikos.po') if not e.obsolete]
        for msg in messages:
            exists = request.db_cursor.execute("Select 1 from messages where id=?", (msg.msgid,))
            if exists.fetchone():
                request.db_cursor.execute("update messages set " + lang[0] + "=? where id=?", (msg.msgstr, msg.msgid))
            else:
                request.db_cursor.execute("insert into messages(" + lang[0] + ",id) values(?, ?)", (msg.msgstr, msg.msgid))


def scrub(name):
    return ''.join( chr for chr in name if chr.isalnum() )

#@secure('admin','system-translator')
def system_translate(lang_to):
    if lang_to:
        messages = request.db_cursor.execute("select id, " + scrub(lang_to) + ", user_level from messages")
        print messages.fetchone()
        return render_template('system_translation.html', msgs=messages, lang_to=lang_to, levels=TRANSLATOR_LEVELS)
    else:
        raise BadRequestException()

#@secure('admin','system-translator')
def select_language():
    return render_template('select_language.html')

#@secure('admin','system-translator')
def save_po(lang_to):
    lang_to_messages = pofile(LOCALE_PATH + '/' + lang_to + '/LC_MESSAGES/epistemonikos.po', check_for_duplicates=True)
    print request.POST.keys()
    for msgid in request.POST.keys():
        if msgid not in ['submit','lang_to']:
            lang_to_messages.append(POEntry(msgid=msgid,msgstr=request.POST.get(msgid)))

    lang_to_messages.save()
    
    return select_language()
    
