# -*- coding: utf8 -*-
import requests
from lxml import etree
import json
import sys


class Setting(object):
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Windows NT 6.1) Chrome/44.0.2403.157 Safari/537.36'}

    def __init__(self, url="http://ck101.com/forum-3419-1.html"):
        self.url = url

    def get_res(self):
        return requests.get(self.url, headers=self.headers)

    # is str
    def requests_text(self):
        return self.get_res().text.encode('utf-8')


class JSONItem(object):
    """docstring for JSONItem"""

    def __init__(self):
        with open("setting.json", encoding="utf-8") as json_file:
            self.json_data = json.load(json_file)

    def title(self):
        return self.json_data[0]['title']

    def url(self):
        return self.json_data[0]['url']


class APageInformation(object):
    __slots__ = ["html_page"]

    def __init__(self, url="http://ck101.com/thread-2826010-1-1.html"):
        try:
            self.html_page = etree.HTML(Setting(url).requests_text())
        except:
            sys.stderr.write('self.temp_tage is error')

    def content(self):
        temp_page = ''
        xpath_for_content = u"//p[@class='talk-transcript__para']/span//text()"
        for item in self.html_page.xpath(xpath_for_content):
            temp_page += item
        return temp_page


def main():
    en_url = JSONItem().url() + '/transcript?language=en'
    tw_url = JSONItem().url() + '/transcript?language=zh-tw'
    english_content = APageInformation(en_url).content()
    tw_content = APageInformation(tw_url).content()
    with open(JSONItem().title() + '_en.txt', "w") as txt_file:
        txt_file.write(english_content)
    with open(JSONItem().title() + '_tw.txt', "w", encoding='utf-8') as txt_file:
        txt_file.write(tw_content)

if __name__ == '__main__':
    main()
