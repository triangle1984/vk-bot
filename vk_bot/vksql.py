import pymysql
from token2 import ip, tablechat
from vk_api.utils import get_random_id
from pymysql.cursors import DictCursor
from contextlib import closing
from photo import yourpic
def auth():
    conn = pymysql.connect(host=ip,
                             user="root",
                             password="123",
                             db="mydb",
                             cursorclass=DictCursor)
    return conn
def sendall(vk, text, attachment=None):
    if attachment == None:
        text = " ".join(text[1:])
    conn = auth()
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {tablechat}"
        cursor.execute(query)
        result = cursor.fetchall()
        for a in result:
            vk.messages.send(chat_id=a["id"], random_id=get_random_id(),
                             message=text, attachment=attachment)
def checktable(table, value, should):
    conn = auth()
    with conn.cursor() as cursor:
        query = f"SELECT * FROM {table} WHERE {value} = '{should}'"
        cursor.execute(query)
    return cursor.fetchone()
def tableadd(table, value, add, one=False):
    conn = auth()
    try:
        with conn.cursor() as cursor:
            query = f"INSERT INTO {table} ({value}) VALUES ({add})"
            cursor.execute(query)
            conn.commit()
    except pymysql.err.InternalError:
        return
def tablerm(table, value, rm):
    conn = auth()
    with conn.cursor() as cursor:
        query = f"DELETE FROM {table} WHERE {value} = '{rm}'"
        cursor.execute(query)
        conn.commit()
def nametoid2(vk, names):
    uid = []
    for convert in names:
        r = vk.utils.resolveScreenName(screen_name=convert)
        if r:
            if r["type"] == "group":
                uid.append(f"-{r['object_id']}")
            else:
                uid.append(r["object_id"])
        else:
            uid.append(convert)
    return uid
def saveload(uid, uname):
    conn = auth()
    with conn.cursor() as cursor:
        query = f"SELECT * FROM prefix WHERE id = '{uid}'"
        cursor.execute(query)
        # если нет, записать
        if cursor.fetchone() == None:
            with conn.cursor() as cursor:
                query = f"INSERT INTO prefix (id, name) VALUES ({uid}, '{uname}')"
                cursor.execute(query)
                conn.commit()
        # в любом случае получить запись из бд, даже ежели ее не было и мы
        # только записали
        with conn.cursor() as cursor:
            query = f"SELECT * FROM prefix WHERE id = '{uid}'"
            cursor.execute(query)
            return cursor.fetchone()
def update(uid, name, text):
    saveload(uid, name)
    conn = auth()
    newname = " ".join(text[1:])
    if len(newname) > 29:
        return {"message":"максимальная длинна префикса: 30 символов"}
    with conn.cursor() as cursor:
        query = f"UPDATE prefix SET name = '{newname}' WHERE id = '{uid}'"
        cursor.execute(query)
        conn.commit()
    return {"message":"се ваш префикс сменен"}
def ban(uid):
    conn = auth()
    if checktable("ban", "id", uid) == None:
        with conn.cursor() as cursor:
            query = f"INSERT INTO ban (id) VALUES ({uid})"
            cursor.execute(query)
            conn.commit()
def unban(uid):
    conn = auth()
    with conn.cursor() as cursor:
        query = f"DELETE FROM ban WHERE id = {uid}"
        cursor.execute(query)
        conn.commit()
def checkban(uid):
    conn = auth()
    with conn.cursor() as cursor:
        query = f"SELECT * FROM ban WHERE id = '{uid}'"
        cursor.execute(query)
        if cursor.fetchone():
            return "kill him"
def smehdb(ss,uid, db=False):
    check = checktable("smehgen","id", uid)
    if db:
        value = f"id, count, smeh, smehslova"
        add = f"{uid}, {ss.count}, '{ss.smex}', '{ss.smexslova}'"
        if check:
            tablerm("smehgen", "id", uid)
        tableadd("smehgen", value, add)
    else:
        if check:
            ss.count = check["count"]
            ss.smex = check["smeh"]
            ss.smexslova = check["smehslova"]
            return ss
def checkchat(event):
    check = checktable(tablechat, 'id', event.chat_id)
    if check == None:
        tableadd(tablechat, 'id', event.chat_id)
def photoadd(vk, uid, text):
    try:
        command = text[1]
        public = "".join(text[2:]);public = public.split(",")
        public = ",".join(nametoid2(vk, public))
    except IndexError:
        return {"message": """ Это личные альбомы. Их смысл в том, что каждый человек,
                может создать себе личную команду с пикчами из указанных пабликов.
                Эта команда будет работать только у него(хотя другой человек может создать свою, с таким же названием, конфликта не будет)
                /альбомы <команда> <айди пабликов, через запятую>
                например: /альбомы /шедевр mtt_resort,rimworld (паблик можно и один указать)
                и потом можно ее вызывать на /шедевр
                так же можно использовать ключи для количества
                /шедевр -c 10 - скинет 10 пикч с вашей команды
                (10 максимум в вк)"""}
    if checktable("yourphoto","id", uid):
        tablerm("yourphoto", "id", uid)
    tableadd("yourphoto", "id,command,public",f"{uid}, '{command}','{public}'")
    return {"message":f"Ваш личный альбом настроен, паблики: {public}, команда: {command}"}
def setmessages(uid):
    conn = auth()
    if checktable('messages', 'id', uid) == None:
        tableadd('messages', 'id, msg', f"{uid}, 0")
    with conn.cursor() as cursor:
        query = f"UPDATE messages SET msg = (msg + 1) WHERE id ='{uid}' "
        cursor.execute(query)
        conn.commit()
def getcommand(uid):
    check = checktable("yourphoto", "id", uid)
    if check:
        return check["command"]
    else:
        return 666
def sendyourphoto(vk, text, uid):
    check = checktable("yourphoto", "id", uid)
    if check:
        public = check["public"]
        public = public.split(",")
        return yourpic(vk, text, public)
def hellosql(chathello, uid, text):
    conn = auth()
    if checktable(chathello, 'id', uid) == None:
        tableadd(chathello, 'id', f"{uid}")
    with conn.cursor() as cursor:
        query = f"UPDATE {chathello} SET hello = '{text}' WHERE id ='{uid}' "
        cursor.execute(query)
        conn.commit()
