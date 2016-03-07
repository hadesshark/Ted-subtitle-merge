# -*- coding: utf8 -*-
import json
import os
import urllib2

class TedSubtitle(object):
  """docstring for TedSubtitle"""
  def __init__(self, startOfParagraph = True, startTime = 0, duration = 0, content = ''):
    super(TedSubtitle, self).__init__()
    self.startOfParagraph = startOfParagraph
    self.startTime = startTime / 1000
    self.duration = duration / 1000
    self.content = content
    self.endTime = self.startTime + self.duration



  def Description(self):
    return '\n'.join(["startTime : " + str(self.startTime),
                      "duration  : " + str(self.duration),
                      "content   : " + self.content.encode('utf8'),
                      ''])    


  def TrimNewLine(self):
    self.content = self.content.replace('\n','')




def GetSubtitles(talkID, languageCode):
  subtitleUrl = "http://www.ted.com/talks/subtitles/id/%s/lang/%s" % (talkID, languageCode)
  response = urllib2.urlopen(subtitleUrl)
  html = response.read() 
  subtitles = json.loads(html)["captions"]
  tedSubtitles = []
  for subtitle in subtitles:
    tedSubtitle = TedSubtitle(subtitle["startOfParagraph"], 
                              subtitle["startTime"], 
                              subtitle["duration"], 
                              subtitle["content"])
    tedSubtitles.append(tedSubtitle)

  return tedSubtitles




def json2srt(subtitles):

  def conv(t):
    return '%02d:%02d:%02d,%03d' % (
        t / 1000 / 60 / 60,
        t / 1000 / 60 % 60,
        t / 1000 % 60,
        t % 1000)


  for i, item in enumerate(subtitles):
    print (i,
           conv(item.startTime),
           conv(item.startTime + item.duration - 1),
           item.content)

def Difference( num1, num2 ):
  return abs( num1 - num2 )

def HasContainsEndMark(content):
  if len( content) < 2:
    return False

  endMarks = [ '.', '?', '!', '。', '？', '！' ]
  for i in endMarks:
    if content[-1].encode('utf8') == i:
      return True

  return False


def PrintSubtitles(subtitles):
 for i in range(len(subtitles)):
    print subtitles[i].Description()
    

def ResetStartTime(arr):
  for i in range(len(arr)):
    arr[i].startTime -= arr[0].startTime

  return arr

def HasEvenQuotes( content ):
  return content.count('"') % 2 == 0 

def HasPairChar( content ):
  leftChars =  [ u'「', u'(', u'（', u'{', u'【', u'｛', u'[']
  rightChars = [ u'」', u')', u'）', u'}', u'】', u'｝', u']']
  
  for i in range(len(leftChars)):
    if ( content.count(leftChars[i].encode('utf8')) == content.count(rightChars[i].encode('utf8')) ):
      return True

  return False

def IsNewParagraph(isStartOfParagraph, sentence):
  maxCharInSentence = 50
  
  newParagraph = isStartOfParagraph
  newParagraph = newParagraph or len(sentence) > maxCharInSentence
  newParagraph = newParagraph and HasEvenQuotes(sentence)
  newParagraph = newParagraph and HasContainsEndMark(sentence)
  newParagraph = newParagraph and HasPairChar(sentence.encode('utf8'))
  newParagraph = newParagraph and len(sentence) != 0
  return newParagraph
  


talkURL = "http://www.ted.com/talks/richard_st_john_s_8_secrets_of_success"
##talkURL = "http://www.ted.com/talks/kenneth_cukier_big_data_is_better_data"
talkTitle = talkURL.split('/')[-1].replace('_',' ')

#print talkTitle
#print '\n\n'
command = "curl -s %s | grep source=facebook | awk -F '=' '{print $3}' | awk -F '&' '{print $1}'" % ( talkURL )
talkID = '49'#os.popen(command).readlines()[0].strip()
print "talkID :", talkID


chineselanguageCode = 'zh-tw'
englishlanguageCode = 'en'



engSubtitles = ResetStartTime(GetSubtitles( talkID, englishlanguageCode ))
chineseSubtitles = ResetStartTime(GetSubtitles( talkID, chineselanguageCode ))



def GroupToParagraph(subtitles):
  lastAddedIndex = 0
  lastAddedChar = ' '
  paragraphs = []
  paragraph = TedSubtitle()

  for i in xrange(len(subtitles)):
    subtitle = subtitles[i]

    

    
    if paragraph.startOfParagraph:
      if i == 0:
        paragraph.startTime = subtitle.startTime
      else:
        paragraph.startTime = subtitles[i-1].startTime

      paragraph.startOfParagraph = False
    
    
    if IsNewParagraph(subtitle.startOfParagraph, paragraph.content):
      paragraph.TrimNewLine()
      if paragraph.duration == 0:
        paragraph.duration = subtitles[i-1].endTime


      paragraphs.append(paragraph)
      paragraph = TedSubtitle(content = subtitle.content)
      lastAddedIndex = i
    else:
      paragraph.content += subtitle.content
      paragraph.duration = subtitle.endTime
      

  if lastAddedIndex < len(subtitles):
    paragraphs.append(paragraph)


  return paragraphs




filteredChineseSubtitles = GroupToParagraph(chineseSubtitles)

for i in filteredChineseSubtitles:
  print i.Description()
  print

def MergeSubtitles( filteredChineseSubtitles, engSubtitles ):

  idxForEnglishSubtitles = 0
  lengthForChineseSubtitles = len(filteredChineseSubtitles)
  lengthForEnglishSubtitles = len(engSubtitles)
  paragraph = TedSubtitle()

  filteredEnglishSubtitles = []
  for chineseSubtitle in filteredChineseSubtitles:
    currentDurationDifference = 0

    idxForLastEnglishSubtitles = idxForEnglishSubtitles


    print chineseSubtitle.content.encode('utf8')
  
    while idxForLastEnglishSubtitles < lengthForEnglishSubtitles:

      paragraph.duration = engSubtitles[idxForLastEnglishSubtitles].endTime
      preDurationDifference = currentDurationDifference
      currentDurationDifference = chineseSubtitle.duration - paragraph.duration

      print chineseSubtitle.duration , paragraph.duration
      print
      if currentDurationDifference <= 0:
        if abs(preDurationDifference) < abs(currentDurationDifference):

          break
        else:
          idxForLastEnglishSubtitles += 1
          break

      idxForLastEnglishSubtitles += 1

    print "idx: ", idxForEnglishSubtitles, idxForLastEnglishSubtitles
    contents = [e.content for e in engSubtitles[idxForEnglishSubtitles:idxForLastEnglishSubtitles]]

    for k in contents:
    
      print k

    print '-' * 20
    paragraph.content += ' '.join(contents)
    idxForEnglishSubtitles = idxForLastEnglishSubtitles

    paragraph.content = paragraph.content.replace('\n',' ')
    filteredEnglishSubtitles.append(paragraph)
    paragraph = TedSubtitle()

  return filteredEnglishSubtitles

filteredEnglishSubtitles = MergeSubtitles( filteredChineseSubtitles, engSubtitles )
if False:
  for i in xrange(len(filteredChineseSubtitles)):
    print filteredEnglishSubtitles[i].content
    print filteredChineseSubtitles[i].content.encode('utf8')
    print
    print
    print

