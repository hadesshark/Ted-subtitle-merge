# -*- coding: utf8 -*-
import json
import urllib.request as request
import pprint

class Setting(object):
    def __init__(self, url="http://ck101.com/forum-3419-1.html"):
        self.url = url

    def get_res(self):
        return request.urlopen(self.url)

    # is str
    def requests_text(self):
        return self.get_res().read()


def main():
    en_url = "http://www.ted.com/talks/subtitles/id/33/lang/en"
    tw_url = "http://www.ted.com/talks/subtitles/id/33/lang/zh-tw"
    en_data = json.loads(Setting(en_url).requests_text().decode('utf-8'))
    tw_data = json.loads(Setting(tw_url).requests_text().decode('utf-8'))
    contest = ''
    for index in range(len(en_data['captions'])):
    	if en_data['captions'][index]['startOfParagraph']:
    		contest += '\n\n'

    		# if tw_data['captions'][index]['startOfParagraph']:
	    	# 	contest += '\n\n'
	    	# contest += tw_data['captions'][index]['content']

    	contest += en_data['captions'][index]['content']
	    	

    with open("test_TED.txt", "wb") as txt_file:
    	txt_file.write(contest.encode('utf-8'))


if __name__ == '__main__':
    main()