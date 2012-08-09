# -*- coding: utf-8 -*-
from random import random
from hashlib import sha256

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
        sql_query += ",user_level text, url text, obsolete int)"
        request.db_cursor.execute(sql_query)

    table_exists = request.db_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='links';")
    if not table_exists.fetchone():
        request.db_cursor.execute("create table links(hash text not null primary key, role text not null, lang_to text not null)")

    request.db_cursor.execute("update messages set obsolete=1")
    for lang in LANGUAGES:
        messages = [e for e in pofile(LOCALE_PATH + '/' + lang[0] + '/LC_MESSAGES/epistemonikos.po') if not e.obsolete]
        for msg in messages:
            exists = request.db_cursor.execute("Select 1 from messages where id=?", (msg.msgid,))
            if exists.fetchone():
                request.db_cursor.execute("update messages set " + lang[0] + "=? where id=?", (msg.msgstr, msg.msgid))
            else:
                request.db_cursor.execute("insert into messages(" + lang[0] + ",id) values(?, ?)", (msg.msgstr, msg.msgid))
            request.db_cursor.execute("update messages set obsolete=0 where id=?",(msg.msgid,))

    return 'Database generated'


def scrub(name):
    return ''.join( chr for chr in name if chr.isalnum() )

#@secure('admin','system-translator')
def system_translate(lang_to):
    if lang_to in [lang[0] for lang in LANGUAGES]:
        messages = request.db_cursor.execute("select id, " + lang_to + ", user_level, url, obsolete from messages where user_level is not ?", ('Delete',))
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
                                      + "=? where id=?",
                                        (msgstrs[i].decode('utf-8'),
                                         msgids[i].decode('utf-8')))
            if msglvl and msgurl:
                request.db_cursor.execute("UPDATE messages set user_level=?,url=? where id=?",
                                        (msglvl[i].decode('utf-8'),
                                         msgurl[i].decode('utf-8'),
                                         msgids[i].decode('utf-8')))

        return 'Saved messages saved for %s' % [lang[1] for lang in LANGUAGES if lang[0] == lang_to][0]

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
        msg += generate_po_from_db(lang[0]) +'<br/>'
    return msg

def panel():
    return render_template("panel.html", roles = TRANSLATOR_LEVELS)

def generate_link():
    role = request.POST.get('role')
    lang_to = request.POST.get('lang_to')
    seed = random()
    hash = sha256(str(seed)).hexdigest()
    alreadyindb = request.db_cursor.execute("Select 1 from links where hash=?",(hash,))
    if alreadyindb.fetchone():
        return generate_link(role)
    request.db_cursor.execute("insert into links(hash,role,lang_to) values(?,?,?)",(hash,role,lang_to))
    return 'http://' + request.headers.get('host','') + '/filtered_translate/' + hash

def decode_url(hash):
    params = request.db_cursor.execute("select role, lang_to from links where hash=?",(hash,)).fetchone()
    if params:
        return system_translate_by_role(params[1], params[0])
    return "Not Found"

def deleted():
    messages = request.db_cursor.execute("select id from messages where user_level=?",('Delete',))
    return render_template("deleted.html", msgs=messages)

def undelete():
    message = request.POST.get('msg', None)
    if message is not None:
        request.db_cursor.execute("update messages set user_level=null where id=?",(message,))