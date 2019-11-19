from vk_bot.core.modules.basicplug import BasicPlug
from bs4 import BeautifulSoup
import requests


class Bash(BasicPlug):
    command = ["/баш"]
    doc = "рандом цитата из баша"
    def main(self):
        resp = requests.get("https://bash.im/random")
        soup = BeautifulSoup(resp.text, 'lxml')
        text = soup.find("div", {"class": "quote__body"})
        text = str(text)
        text = text.replace('<div class=\"quote__body\">', "")
        text = text.replace('</div>', "")
        text = text.replace('<br/>', "\n")
        self.sendmsg(text)