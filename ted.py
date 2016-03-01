# -*- coding: utf8 -*-
import json
import os
import urllib2

def GetSubtitles(talkID, languageCode):
  subtitleUrl = "http://www.ted.com/talks/subtitles/id/%s/lang/%s" % (talkID, languageCode
  response = urllib2.urlopen(subtitleUrl)
  html = response.read() 
  return json.loads(html)["captions"]


def json2srt(subtitles):


  def conv(t):
    return '%02d:%02d:%02d,%03d' % (
        t / 1000 / 60 / 60,
        t / 1000 / 60 % 60,
        t / 1000 % 60,
        t % 1000)


  for i, item in enumerate(subtitles):
    print (i,
           conv(item['startTime']),
           conv(item['startTime'] + item['duration'] - 1),
           item['content'])

def difference( num1, num2 ):
  return abs( num1 - num2 )

def hasContainsEndMark(content):
  if len( content) < 2:
    return False

  endMarks = [ '.', '?', '!', '。', '？', '！' ]
  for i in endMarks:
    if content[-1].encode('utf8') == i:
      return True

  return False

def ResetStartTime(arr):
  for i in range(len(arr)):
    arr[i]['startTime'] -= arr[0]['startTime']
    arr[i]['startTime'] /= 1000
    arr[i]['duration'] /= 1000

  return arr

def hasEvenQuotes( content ):
  return content.count('"') % 2 == 0 

def hasPairChar( content ):
  leftChars =  [ u'「', u'(', u'（', u'{', u'【', u'｛', u'[']
  rightChars = [ u'」', u')', u'）', u'}', u'】', u'｝', u']']
  
  for i in range(len(leftChars)):
    if ( content.count(leftChars[i].encode('utf8')) == content.count(rightChars[i].encode('utf8')) ):
      return True

  return False

def createSubtitle( startTime, duration, content ):
  return { "startTime" : startTime, "duration" : duration, "content" : content }

def endTime( obj ):
  return obj['startTime'] + obj['duration']

talkURL = "http://www.ted.com/talks/richard_st_john_s_8_secrets_of_success"
##talkURL = "http://www.ted.com/talks/kenneth_cukier_big_data_is_better_data"
talkTitle = talkURL.split('/')[-1].replace('_',' ')

print talkTitle
print '\n\n'
command = "curl -s %s | grep source=facebook | awk -F '=' '{print $3}' | awk -F '&' '{print $1}'" % ( talkURL )
talkID = '45'#os.popen(command).readlines()[0].strip()
print "talkID :", talkID


chineselanguageCode = 'zh-tw'
englishlanguageCode = 'en'



engSubtitles = ResetStartTime(GetSubtitles( talkID, englishlanguageCode ))
chineseSubtitles = ResetStartTime(GetSubtitles( talkID, chineselanguageCode ))
#print json2srt(subtitles)
print len(engSubtitles),len(chineseSubtitles)
charCount = 0

filteredEnglishSubtitles = []
filteredChineseSubtitles = []
englishSentence = ''
chineseSentence = ''
maxCharInSentence = 50
lastAddedChar = ' '


matchedIndexsAtEnglishSubtitles = []

idxForChineseSubtitles = 0
idxForEnglishSubtitles = 0
lengthForChineseSubtitles = len(chineseSubtitles)
lengthForEnglishSubtitles = len(engSubtitles)
durationTolerance = 1500

durationInParagraph = 0
firstSentenceInParagraph = True
if False:
  for i in engSubtitles:
    print i["startTime"]
    print i["duration"]
    print i["content"].encode('utf8')
    print 
  exit(0)
  exit(0)

print "-"*10

duration = 0
isEnd = False
lastAddedIndex = 0
durationInParagraph = 0
startTimeInParagraph = 0
while idxForChineseSubtitles < lengthForChineseSubtitles:
  #idxForEnglishSubtitles = idxForChineseSubtitles
  
  chineseSubtitle = chineseSubtitles[idxForChineseSubtitles]
  newParagraph = chineseSubtitle["startOfParagraph"]
  newParagraph = newParagraph or len(chineseSentence) > maxCharInSentence
  newParagraph = newParagraph and hasEvenQuotes(chineseSentence)
  newParagraph = newParagraph and hasContainsEndMark(chineseSentence)
  newParagraph = newParagraph and hasPairChar(chineseSentence.encode('utf8'))
  newParagraph = newParagraph and len(chineseSentence) != 0


  #print idxForEnglishSubtitles, duration, chineseSubtitle['duration']
  #print idxForChineseSubtitles, lengthForChineseSubtitles, firstSentenceInParagraph, newParagraph, chineseSentence.encode('utf8')
  if firstSentenceInParagraph:
    if idxForChineseSubtitles == 0:
      startTimeInParagraph = chineseSubtitle["startTime"]
    else:
      startTimeInParagraph = chineseSubtitles[idxForChineseSubtitles-1]["startTime"]
    firstSentenceInParagraph = False
  if newParagraph:
    #print startTimeInParagraph, durationInParagraph
  
    chineseSentence = chineseSentence.replace('\n', '')
    
    subtitle = createSubtitle( startTimeInParagraph, durationInParagraph, chineseSentence )
    filteredChineseSubtitles.append(subtitle)
    chineseSentence = chineseSubtitle["content"] #+ ' '


    startTimeInParagraph = 0
    durationInParagraph = 0
    firstSentenceInParagraph = True
    lastAddedIndex = idxForChineseSubtitles
    #print duration, chineseDuration, difference(duration,chineseDuration)
    #myChineseSubtitles.append(chineseSentence)
    #chineseSentence = chineseSubtitles[i]["content"] + lastAddedChar
  else:
    chineseSentence += chineseSubtitle["content"]# + ' '
    durationInParagraph = endTime(chineseSubtitle)
    #

  
  idxForChineseSubtitles += 1

if lastAddedIndex < lengthForChineseSubtitles:
  subtitle = createSubtitle( startTimeInParagraph, durationInParagraph, chineseSentence )
  filteredChineseSubtitles.append(subtitle)

if False:
  for i in range(len(filteredChineseSubtitles)):
    #print filteredEnglishSubtitles[i].encode('utf8')
    print filteredChineseSubtitles[i]["startTime"]
    print filteredChineseSubtitles[i]["duration"]
    print filteredChineseSubtitles[i]["content"].encode('utf8')
    print
    print

  #exit(0)

idxForChineseSubtitles = 0
idxForEnglishSubtitles = 0
durationInParagraph = 0
startTimeInParagraph = 0
lengthForChineseSubtitles = len(filteredChineseSubtitles)
englishSentence = ''

while idxForChineseSubtitles < lengthForChineseSubtitles:
  chineseDuration = filteredChineseSubtitles[idxForChineseSubtitles]["duration"]
  #print filteredChineseSubtitles[idxForChineseSubtitles]["startTime"]
  #print chineseDuration
  minDurationDifference = 10000
  currentDurationDifference = 0
 
  idxForLastEnglishSubtitles = idxForEnglishSubtitles

  while idxForLastEnglishSubtitles < lengthForEnglishSubtitles:
    durationInParagraph = endTime(engSubtitles[idxForLastEnglishSubtitles])
    preDurationDifference = currentDurationDifference
    currentDurationDifference = chineseDuration - durationInParagraph
    #print chineseDuration, durationInParagraph

    if currentDurationDifference <= 0:
      if abs(preDurationDifference) < abs(currentDurationDifference):
        break
      else:
        idxForLastEnglishSubtitles += 1
        break



    idxForLastEnglishSubtitles += 1


  while idxForEnglishSubtitles < idxForLastEnglishSubtitles:
    englishSentence += engSubtitles[idxForEnglishSubtitles]["content"].replace('\n',' ') + ' '
    idxForEnglishSubtitles += 1


  print englishSentence
  print filteredChineseSubtitles[idxForChineseSubtitles]["content"].encode("utf8")
  print "\n\n"  

  englishSentence = ''
  idxForChineseSubtitles += 1





if False:
  for i in range(len(filteredChineseSubtitles)):
    #print filteredEnglishSubtitles[i].encode('utf8')
    print filteredChineseSubtitles[i]["startTime"]
    print filteredChineseSubtitles[i]["duration"]
    print filteredChineseSubtitles[i]["content"].encode('utf8')
    print
    print