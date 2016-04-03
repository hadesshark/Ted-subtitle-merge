# -*- coding: utf8 -*-
import json
import urllib.request as request


def getjsoncapions(url):
    return json.loads(request.urlopen(url).read().decode('utf-8'))['captions']


def isstartOfParagraph(item):
    return True if item['startOfParagraph'] else False


def content(item):
    return item['content']


def getcontents(url):
    capions = getjsoncapions(url)
    temp_content = ''
    for item in capions:
        if isstartOfParagraph(item):
            temp_content += '\n\n'
        temp_content += content(item)
    return temp_content


def main():
    en_url = "http://www.ted.com/talks/subtitles/id/33/lang/en"
    tw_url = "http://www.ted.com/talks/subtitles/id/33/lang/zh-tw"
    content = ''

    content += getcontents(en_url)
    content += getcontents(tw_url)

    with open("test_TED.txt", "wb") as txt_file:
        txt_file.write(content.encode('utf-8'))

if __name__ == '__main__':
    main()
