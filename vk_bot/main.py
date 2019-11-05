from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from vk_bot.core.sql.sqlgame import *
from loadevn import *
from concurrent.futures import ThreadPoolExecutor, wait, as_completed
import vk_api
import requests
import sys
from vk_bot.core.sql.vksql import *
import pylibmc
import logging
from vk_bot.core.utils.botutil import sqlcache
from economy import *
import mods


def mainlobby(vk, mc, event, upload):
    events = event.type.name.lower()
    try:
        response = {"message": None}
        if "text" in dir(event) and "user_id" in dir(event):
            if event.from_me:
                uid = recipient
            else:
                uid = event.user_id
            if str(uid) in allowuser and "chat_id" not in dir(event):
                text = event.text.split()
                try:
                    requests = text[0].lower()
                    uberequests = " ".join(text[0:]).lower()
                except IndexError:
                    return
                if event.from_me:
                    uid = recipient
                else:
                    uid = event.user_id
                mc2 = sqlcache(mc, uid)
                givemoney(uid, mc2)
                prefix = mc2["prefix"]
                for module in mods.modules:
                    run = False
                    if module.included and events in module.vktypes and mc2[module.available_for]:
                        if module.types == "command":
                            if requests in module.command:
                                run = True
                        elif module.types == "runalways":
                            run = True
                        if run:
                            module = module(vk, vk, upload)
                            module.givedata(uid=uid, text=text, event=event, mc2=mc2,
                                            prefix=prefix, peer="", mc=mc)
                            module.main()
    except KeyboardInterrupt:
        sys.exit()
def checkthread():
    global futures
    for x in as_completed(futures):
        if x.exception() != None:
            logging.error(x.exception())
        futures.remove(x)
vk_session = vk_api.VkApi(token=token22)
vk = vk_session.get_api()
upload = vk_api.VkUpload(vk_session)
longpoll = VkLongPoll(vk_session)
mc = pylibmc.Client(["127.0.0.1"])
pool = ThreadPoolExecutor(8)
logging.basicConfig(level=logging.INFO)
futures = []
for event in longpoll.listen():
    futures.append(pool.submit(mainlobby, vk, mc, event, upload))
    pool.submit(checkthread)
