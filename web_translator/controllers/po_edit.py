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
        sql_query += ",user_level text, url text)"
        request.db_cursor.execute(sql_query)

    for lang in LANGUAGES:
        messages = [e for e in pofile(LOCALE_PATH + '/' + lang[0] + '/LC_MESSAGES/epistemonikos.po') if not e.obsolete]
        for msg in messages:
            exists = request.db_cursor.execute("Select 1 from messages where id=?", (msg.msgid,))
            if exists.fetchone():
                request.db_cursor.execute("update messages set " + lang[0] + "=? where id=?", (msg.msgstr, msg.msgid))
            else:
                request.db_cursor.execute("insert into messages(" + lang[0] + ",id) values(?, ?)", (msg.msgstr, msg.msgid))

    return 'Database generated'


def scrub(name):
    return ''.join( chr for chr in name if chr.isalnum() )

#@secure('admin','system-translator')
def system_translate(lang_to):
    if lang_to in [lang[0] for lang in LANGUAGES]:
        messages = request.db_cursor.execute("select id, " + lang_to + ", user_level, url from messages")
        return render_template('system_translation.html', msgs=messages, lang_to=lang_to, levels=TRANSLATOR_LEVELS)
    else:
        raise BadRequestException()

def system_translate_by_role(lang_to, role):
    if lang_to in [lang[0] for lang in LANGUAGES]:
        messages = request.db_cursor.execute("select id, " + lang_to + ", user_level, url from messages where user_level=?", (role,))
        return render_template('system_translation.html', msgs=messages, lang_to=lang_to, role=role)
    else:
        raise BadRequestException()


#@secure('admin','system-translator')
def select_language():
    return render_template('select_language.html')

#@secure('admin','system-translator')
def save_translation(lang_to):
    if lang_to in [lang[0] for lang in LANGUAGES]:
        msgids = request.POST.dict.get('msgid[]')
        msgstrs = request.POST.dict.get('msg[]')
        msglvl = request.POST.dict.get('msglvl[]')
        msgurl = request.POST.dict.get('msgurl[]')
        for i in range(len(msgids)):
            request.db_cursor.execute("UPDATE messages set "
                                      + lang_to.decode('utf-8')
                                      + "=?, user_level=?, url=? where id=?",
                                        (msgstrs[i].decode('utf-8'),
                                         msglvl[i].decode('utf-8'),
                                         msgurl[i].decode('utf-8'),
                                         msgids[i].decode('utf-8')))

        return 'Translated messages saved for %s' % [lang[1] for lang in LANGUAGES if lang[0] == lang_to][0]

def generate_po_from_db(lang_to):
    if lang_to in [lang[0] for lang in LANGUAGES]:
        po_path = LOCALE_PATH + '/' + lang_to + '/LC_MESSAGES/epistemonikos.po'
        mo_path = LOCALE_PATH + '/' + lang_to + '/LC_MESSAGES/epistemonikos.mo'
        messages = request.db_cursor.execute("select id, " + lang_to + " from messages")
        new_file = POFile()
        for msg in messages.fetchall():
            new_file.append(POEntry(msgid=msg[0],msgstr=msg[1]))
        new_file.save(po_path)
        new_file.save_as_mofile(mo_path)

        return '.po file generated and compiled for %s' % [lang[1] for lang in LANGUAGES if lang[0] == lang_to][0]

def generate_all_po():
    msg = ''
    for lang in LANGUAGES:
        msg += generate_po_from_db(lang[0]) +'/n'
    return msg